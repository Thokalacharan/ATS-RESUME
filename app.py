from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import PyPDF2
import google.generativeai as genai
import os
import hashlib
import json
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
CACHE_FOLDER = 'cache'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CACHE_FOLDER, exist_ok=True)

# Gemini API configuration from environment variables
API_KEY = os.getenv('GEMINI_API_KEY', '')

# Demo mode - load from environment or default to True
DEMO_MODE = os.getenv('DEMO_MODE', 'True').lower() in ('true', '1', 'yes')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_text_hash(text):
    """Generate MD5 hash of text for caching"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def generate_demo_analysis(resume_text, job_description=None):
    """
    Generate realistic demo ATS analysis without using API
    This is used when DEMO_MODE is True or when API fails
    """
    import random
    
    # Generate a consistent score based on text length and content
    text_length = len(resume_text.split())
    has_email = '@' in resume_text
    has_phone = any(char.isdigit() for char in resume_text)
    
    # Base score calculation for consistency
    base_score = min(85, 40 + (text_length // 20))
    if has_email:
        base_score += 5
    if has_phone:
        base_score += 5
    
    # Add some variance based on text hash for consistency
    text_hash_int = int(get_text_hash(resume_text)[:8], 16)
    variance = (text_hash_int % 20) - 10
    final_score = max(35, min(95, base_score + variance))
    
    if job_description:
        # Mode 2: Job description match
        pros = [
            "Strong alignment with key job requirements",
            "Relevant industry experience clearly highlighted",
            "Technical skills match the job description well",
            "Professional formatting that ATS can easily parse",
            "Clear and concise presentation of qualifications"
        ]
        
        cons = [
            "Could include more specific examples matching job requirements",
            "Consider adding metrics that demonstrate impact in similar roles",
            "Some job-specific keywords could be incorporated more frequently",
            "Work experience descriptions could emphasize relevant achievements",
            "Skills section could be reordered to prioritize job requirements"
        ]
    else:
        # Mode 1: Direct ATS check
        pros = [
            "Well-structured format that ATS systems can easily read",
            "Clear contact information and professional summary",
            "Strong use of action verbs in experience descriptions",
            "Relevant technical skills are properly listed",
            "Education credentials are clearly presented"
        ]
        
        cons = [
            "Add more industry-specific keywords to improve matching",
            "Include quantifiable achievements with specific metrics",
            "Consider adding a skills section if missing",
            "Work experience could include more detailed accomplishments",
            "Ensure consistent formatting throughout the document"
        ]
    
    # Randomize which pros/cons to show (3-5 items)
    random.seed(text_hash_int)
    num_pros = random.randint(3, 5)
    num_cons = random.randint(3, 5)
    
    selected_pros = random.sample(pros, num_pros)
    selected_cons = random.sample(cons, num_cons)
    
    return {
        'score': final_score,
        'pros': selected_pros,
        'cons': selected_cons
    }

def get_cached_result(text_hash):
    """Retrieve cached analysis result if exists"""
    cache_file = os.path.join(CACHE_FOLDER, f"{text_hash}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_cached_result(text_hash, result):
    """Save analysis result to cache"""
    cache_file = os.path.join(CACHE_FOLDER, f"{text_hash}.json")
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from all pages of a PDF file.
    """
    extracted_text = ""
    
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text
        
        return extracted_text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def analyze_resume_with_gemini(resume_text, job_description=None):
    """
    Analyze resume using Google Gemini API
    Falls back to demo mode if API fails or DEMO_MODE is True
    """
    # Use demo mode if enabled
    if DEMO_MODE:
        return generate_demo_analysis(resume_text, job_description)
    
    try:
        client = genai.Client(api_key=API_KEY)
        
        if job_description:
            # Mode 2: With job description
            prompt = f"""
        You are an expert ATS (Applicant Tracking System) resume analyzer. 
        Analyze the following resume against the provided job description.
        
        SCORING CRITERIA (Total 100 points):
        - Job Description Match & Relevant Keywords (30 points)
        - Work Experience Relevance (25 points)
        - Skills Match (20 points)
        - Contact Information & Formatting (10 points)
        - Education Relevance (10 points)
        - Achievements & Metrics (5 points)
        
        Provide:
        1. ATS Score (out of 100) - Be consistent and objective based on job match
        2. Pros (at least 3-5 strengths specific to this job)
        3. Cons (at least 3-5 areas for improvement to better match the job)
        
        Format your response EXACTLY as:
        ATS Score: [score]/100
        
        PROS:
        - [pro 1]
        - [pro 2]
        - [pro 3]
        
        CONS:
        - [con 1]
        - [con 2]
        - [con 3]
        
        Job Description:
        {job_description}
        
        Resume Content:
        {resume_text}
        """
        else:
            # Mode 1: Direct ATS check (general)
            prompt = f"""
        You are an expert ATS (Applicant Tracking System) resume analyzer. 
        Analyze the following resume objectively and consistently using these criteria:
        
        SCORING CRITERIA (Total 100 points):
        - Contact Information & Formatting (15 points)
        - Keywords & Industry Terms (25 points)
        - Work Experience Quality (25 points)
        - Skills Section (15 points)
        - Education (10 points)
        - Achievements & Metrics (10 points)
        
        Provide:
        1. ATS Score (out of 100) - Be consistent and objective
        2. Pros (at least 3-5 strengths)
        3. Cons (at least 3-5 areas for improvement)
        
        IMPORTANT: Analyze the same resume consistently. Base your score on objective criteria.
        
        Format your response EXACTLY as:
        ATS Score: [score]/100
        
        PROS:
        - [pro 1]
        - [pro 2]
        - [pro 3]
        
        CONS:
        - [con 1]
        - [con 2]
        - [con 3]
        
        Resume Content:
        {resume_text}
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                'temperature': 0.0,  # Completely deterministic
                'top_p': 0.95,
                'top_k': 1
            }
        )
        
        return parse_gemini_response(response.text)
    except Exception as e:
        print(f"API Error: {e}. Falling back to demo mode.")
        # Fallback to demo mode if API fails
        return generate_demo_analysis(resume_text, job_description)

def parse_gemini_response(response_text):
    """
    Parse Gemini response to extract score, pros, and cons
    """
    lines = response_text.strip().split('\n')
    score = 0
    pros = []
    cons = []
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Extract score
        if 'ATS Score:' in line or 'Score:' in line:
            try:
                score_part = line.split(':')[1].strip()
                score = int(''.join(filter(str.isdigit, score_part.split('/')[0])))
            except:
                score = 0
        
        # Detect sections
        if 'PROS:' in line.upper() or 'STRENGTHS:' in line.upper():
            current_section = 'pros'
        elif 'CONS:' in line.upper() or 'AREAS FOR IMPROVEMENT:' in line.upper() or 'WEAKNESSES:' in line.upper():
            current_section = 'cons'
        elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
            # Extract bullet points
            clean_line = line.lstrip('-•* ').strip()
            if clean_line and current_section == 'pros':
                pros.append(clean_line)
            elif clean_line and current_section == 'cons':
                cons.append(clean_line)
    
    return {
        'score': score,
        'pros': pros if pros else ['Professional formatting', 'Clear information', 'Good structure'],
        'cons': cons if cons else ['Add more keywords', 'Improve formatting', 'Include metrics']
    }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', demo_mode=DEMO_MODE)

@app.route('/demo-status')
def demo_status():
    """Return demo mode status"""
    return jsonify({'demo_mode': DEMO_MODE})

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """Analyze uploaded resume"""
    try:
        # Check if file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Get job description if provided (Mode 2)
        job_description = request.form.get('job_description', '').strip()
        analysis_mode = 'with_job_description' if job_description else 'direct'
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(filepath)
        
        if not resume_text.strip():
            os.remove(filepath)
            return jsonify({'error': 'Could not extract text from PDF. Please ensure the PDF contains text.'}), 400
        
        # Generate hash of resume text + job description (if provided)
        cache_key = resume_text + (job_description if job_description else '')
        text_hash = get_text_hash(cache_key)
        
        # Check if we have cached result for this exact resume
        cached_result = get_cached_result(text_hash)
        if cached_result:
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'score': cached_result['score'],
                'pros': cached_result['pros'],
                'cons': cached_result['cons'],
                'mode': analysis_mode,
                'resume_filename': file.filename,
                'cached': True  # Indicator that this was from cache
            })
        
        # Analyze with Gemini (only if not cached)
        analysis = analyze_resume_with_gemini(resume_text, job_description if job_description else None)
        
        # Save to cache for future identical resumes
        save_cached_result(text_hash, analysis)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'score': analysis['score'],
            'pros': analysis['pros'],
            'cons': analysis['cons'],
            'mode': analysis_mode,
            'resume_filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
