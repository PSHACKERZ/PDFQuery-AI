# PDFQuery AI

PDFQuery AI is an intelligent PDF conversation companion that allows users to upload PDF documents and interact with their content through a natural language interface, powered by Google's Gemini AI.

## Features

* 📄 PDF Upload & Processing (up to 16MB)
* 💬 Interactive Chat Interface with Suggested Prompts
* 🤖 AI-Powered Document Analysis using Gemini 1.5
* 📱 Responsive Design with Modern UI
* 🎨 Beautiful Gradient Styling
* ⚡ Real-time Response Generation
* 🔒 Secure File Handling

## Tech Stack

* **Frontend:**
  * HTML5
  * CSS3 (Tailwind CSS)
  * JavaScript (Vanilla)
  * Font Awesome Icons

* **Backend:**
  * Flask (Python Web Framework)
  * Google Generative AI (Gemini 1.5)
  * PyPDF2 (PDF Processing)
  * Tenacity (Retry Logic)

## Prerequisites

* Python 3.8+
* Google Gemini API Key

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd pdfquery-ai
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory and add:
```env
GEMINI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Open the application in your web browser
2. Click "Upload PDF" to select your PDF file (max 16MB)
3. Wait for the upload confirmation
4. Start asking questions about the PDF content
5. Use suggested prompts or type your own questions

## Security Features

* Secure file handling with automatic cleanup
* Session management
* File size restrictions
* Secure cookie configuration
* Input validation and sanitization

## Limitations

* Maximum file size: 16MB
* Supports only text-based PDF files
* Maximum content length: 10,000 characters
* Requires internet connection for AI processing

## Error Handling

The application includes comprehensive error handling for:
* File size limitations
* File type validation
* PDF text extraction
* API communication
* Server errors

## Contributing

We welcome contributions to PDFQuery AI! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:

* 🐛 Bug Reports and Feature Requests
* 🔀 Pull Request Process
* 📝 Code Style Guidelines
* 📜 Licensing Information

For major changes, please open an issue first to discuss what you would like to change.

## Contact

For support or queries, contact us on Telegram: [@PS_Hacker](https://t.me/PS_Hacker)

## License

[MIT License](LICENSE)

---

Made with ❤️ by P.S. Hackerz