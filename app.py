import os
os.environ['GRPC_PYTHON_LOG_LEVEL'] = '2'
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
from PyPDF2 import PdfReader
from flask import Flask, request, render_template, jsonify, session
from werkzeug.utils import secure_filename
import time
import traceback
from datetime import timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=API_KEY)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception)
)
def get_ai_response(prompt, context=""):
    try:
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
        )

        full_prompt = f"""Based on this PDF content:
{context}

Question: {prompt}

Provide a detailed answer using markdown formatting. Include:

Headers where appropriate (using #, ##, ###)
Lists (using * for bullet points)
Bold for emphasis
Italics for technical terms
code for any technical elements

If the information isn't in the document, say "I cannot find that information in the document."
""" if context else prompt

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error in get_ai_response: {str(e)}")
        raise

def read_pdf(file_path):
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_CONTENT_LENGTH:
            raise ValueError(f"File size {file_size} bytes exceeds maximum allowed size of {MAX_CONTENT_LENGTH} bytes")

        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_temp_files():
    try:
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                try:
                    retries = 3
                    for attempt in range(retries):
                        try:
                            os.remove(file_path)
                            break
                        except PermissionError:
                            print(f"PermissionError when removing file {file_path}. Attempt {attempt + 1}/{retries}")
                            time.sleep(0.5)
                            continue
                    else:
                        print(f"Could not remove file {file_path} after multiple attempts, likely still in use")
                except Exception as e:
                    print(f"Error removing file {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error cleaning temp files: {str(e)}")

@app.route('/')
def home():
    clean_temp_files()
    return render_template('index.html')

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            pdf_text = read_pdf(filepath)
            
            if not pdf_text.strip():
                os.remove(filepath)
                return jsonify({'error': 'Could not extract text from PDF. Please ensure the PDF contains readable text'}), 400
            
            if len(pdf_text) > 10000:
                os.remove(filepath)
                return jsonify({'error': 'PDF content is too large for processing. Please use a smaller document or use text chunking.'}), 400
            
            session['pdf_content'] = pdf_text
            
            return jsonify({'message': 'PDF uploaded successfully. You can now ask questions about it.'})
            
        finally:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Error removing file: {str(e)}")

    except Exception as e:
        print(f"Error in upload_pdf: {str(e)}")
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Please enter a message'}), 400
        
        pdf_content = session.get('pdf_content')
        if not pdf_content:
            return jsonify({'error': 'No PDF content found. Please upload a PDF first'}), 400
        
        if 'pdf_content' not in session:
            return jsonify({'error': 'Session expired. Please upload the PDF again'}), 401
        
        response = get_ai_response(user_message, pdf_content)
        if not response:
            return jsonify({'error': 'Could not generate response. Please try again'}), 500
        
        return jsonify({'response': response})

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File is too large. Maximum size is 16MB'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'An internal server error occurred. Please try again later'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled exception: {str(e)}")
    traceback.print_exc()
    return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use Render's PORT or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
