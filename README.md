# ATS Resume Checker

A professional web application to check ATS (Applicant Tracking System) compatibility of resumes using AI analysis.

## Features

- **Two Analysis Modes:**
  - **Direct ATS Check**: General resume analysis without job description
  - **Job Description Match**: Compare resume against specific job requirements

- **Comprehensive Analysis:**
  - ATS Score (0-100)
  - Strengths (Pros)
  - Areas for Improvement (Cons)
  - Downloadable Reports

- **Demo Mode:** Works without API key for demonstrations

## Demo Mode vs API Mode

### Demo Mode (Currently Active)
The application is currently running in **DEMO MODE**, which means:
- ✅ No API key required
- ✅ Works perfectly for demonstrations
- ✅ Generates realistic, consistent results
- ✅ Results are based on resume content analysis
- ✅ Perfect for showcasing the application

### Switching to API Mode

When you have a valid Google Gemini API key:

1. Open `app.py`
2. Find line 25:
   ```python
   DEMO_MODE = True  # Set to False when you have a valid API key
   ```
3. Change to:
   ```python
   DEMO_MODE = False
   ```
4. Update your API key on line 24:
   ```python
   API_KEY = "your-new-api-key-here"
   ```
5. Restart the application

## Installation

1. Install dependencies:
   ```bash
   pip install flask flask-cors PyPDF2 google-generativeai
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open browser to:
   ```
   http://127.0.0.1:5000
   ```

## How to Use

1. **Select Analysis Mode:**
   - Choose "Direct ATS Check" for general analysis
   - Choose "Job Description Match" and paste job description for targeted analysis

2. **Upload Resume:**
   - Click to upload or drag-and-drop PDF file
   - Maximum file size: 16MB

3. **Get Results:**
   - View your ATS score
   - Read strengths and improvement areas
   - Download detailed report

## Demo Mode Benefits

Perfect for:
- Presentations and demos
- Testing the application
- Showing potential clients
- Development without API costs

The demo mode generates intelligent, consistent results based on:
- Resume length and structure
- Presence of contact information
- Content quality indicators
- Job description matching (when provided)

## Technical Details

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **AI:** Google Gemini API (with demo fallback)
- **PDF Processing:** PyPDF2
- **Caching:** File-based caching system

## Notes

- Demo mode results are deterministic (same resume = same score)
- All features work in both demo and API modes
- API automatically falls back to demo mode if it fails
- Cache system works in both modes

## Future Enhancements

- Multiple file format support
- Batch processing
- Historical analysis tracking
- Custom scoring criteria

---

**Current Status:** Demo Mode Active ✅

For API mode, get a Google Gemini API key from: https://ai.google.dev/

A professional web application that analyzes resumes using AI to provide ATS (Applicant Tracking System) scores and detailed feedback.

## Features

- 📄 PDF Resume Upload
- 🎯 ATS Score Calculation (0-100)
- ✅ Strengths Analysis
- 🔍 Improvement Suggestions
- ⚡ Instant AI-Powered Analysis
- 🎨 Professional, Modern UI

## Installation

1. Install dependencies:
```bash
pip install Flask PyPDF2 google-genai flask-cors
```

2. Make sure you have your Gemini API key configured in `app.py`

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload your resume (PDF format) and get instant feedback!

## Project Structure

```
atsresume/
├── app.py                 # Flask backend
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   └── style.css         # Styling
└── uploads/              # Temporary file storage (auto-created)
```

## Technologies Used

- **Backend**: Flask (Python)
- **AI**: Google Gemini API
- **PDF Processing**: PyPDF2
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Modern gradient design with responsive layout

## How It Works

1. User uploads a PDF resume
2. Backend extracts text using PyPDF2
3. Text is sent to Google Gemini AI for analysis
4. AI provides ATS score, pros, and cons
5. Results are displayed in a beautiful interface

## Security Note

⚠️ The API key in the code should be moved to environment variables for production use:

```python
import os
API_KEY = os.environ.get('GEMINI_API_KEY')
```

## License

Free to use for personal and educational purposes.
