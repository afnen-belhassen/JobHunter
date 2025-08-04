from flask import Flask, render_template, request, redirect, url_for
import os
import fitz
import docx
from extensions import db
from job import job_bp
from models import ResumeAnalysis, Job
from datetime import datetime

UPLOAD_FOLDER = 'uploads'

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(job_bp, url_prefix='/jobs')

    # Create upload folder if missing
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    with app.app_context():
        db.create_all()

    # Resume processing routes
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            resume_file = request.files['resume']

            if resume_file:
                filename = resume_file.filename
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume_file.save(path)

                resume_text = extract_text(path)
                # Extract skills from the resume text
                extracted_skills = extract_skills_section(resume_text)

                analysis = ResumeAnalysis(
                    filename=filename,
                    extracted_text=resume_text,
                )
                db.session.add(analysis)
                db.session.commit()

                # Pass skills via query string (or store in session/db for more complex use)
                return redirect(url_for('result', id=analysis.id))

        return render_template('resume/index.html')

    @app.route('/result/<int:id>')
    def result(id):
        analysis = ResumeAnalysis.query.get_or_404(id)
        # Extract skills for display/comparison
        extracted_skills = extract_skills_section(analysis.extracted_text)

        # Fetch all jobs from the database
        jobs = Job.query.all()
        job_matches = []
        for job in jobs:
            # Parse job requirements into a list of skills (split by line, comma, or semicolon)
            if job.requirements:
                import re
                req_lines = [l.strip() for l in job.requirements.splitlines() if l.strip()]
                req_skills = []
                for line in req_lines:
                    if ',' in line or ';' in line:
                        req_skills.extend([s.strip() for s in re.split(r",|;", line) if s.strip()])
                    else:
                        req_skills.append(line)
                # Normalize for comparison (case-insensitive)
                user_skills_set = set([s.lower() for s in extracted_skills])
                req_skills_set = set([s.lower() for s in req_skills])
                matched = sorted([s for s in req_skills if s.lower() in user_skills_set])
                missing = sorted([s for s in req_skills if s.lower() not in user_skills_set])
            else:
                req_skills = []
                matched = []
                missing = []
            job_matches.append({
                'job': job,
                'required_skills': req_skills,
                'matched_skills': matched,
                'missing_skills': missing
            })

        return render_template('resume/result.html',
                               resume_text=analysis.extracted_text,
                               extracted_skills=extracted_skills,
                               job_matches=job_matches)

    return app

# Text extraction functions (outside the factory)
def extract_text_from_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text(path):
    if path.endswith('.pdf'):
        return extract_text_from_pdf(path)
    elif path.endswith('.docx'):
        return extract_text_from_docx(path)
    elif path.endswith('.txt'):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "Format non supporté."

# --- Skills extraction helper ---
def extract_skills_section(text):
    import re
    # Possible section headers in English and French
    headers = [
        r"skills", r"technical skills", r"compétences techniques", r"compétences", r"skills & abilities"
    ]
    # Build regex for section header (case-insensitive, start of line)
    header_regex = re.compile(r"^.*(?:" + "|".join(headers) + r").*$", re.IGNORECASE | re.MULTILINE)
    matches = list(header_regex.finditer(text))
    if not matches:
        return []
    # Take the first match as the start of the section
    start = matches[0].end()
    # Find the next section header (all-caps or line with colon, or 2+ blank lines)
    next_header = re.search(r"\n\s*([A-Z][A-Z\s\-&]+:?)\n|\n{2,}", text[start:])
    end = start + next_header.start() if next_header else len(text)
    section = text[start:end].strip()
    # Split section into lines, remove empty, split by comma or semicolon if needed
    lines = [l.strip() for l in section.splitlines() if l.strip()]
    skills = []
    for line in lines:
        # Split by comma or semicolon if present
        if ',' in line or ';' in line:
            skills.extend([s.strip() for s in re.split(r",|;", line) if s.strip()])
        else:
            skills.append(line)
    # Remove duplicates, keep order
    seen = set()
    unique_skills = []
    for skill in skills:
        if skill.lower() not in seen:
            unique_skills.append(skill)
            seen.add(skill.lower())
    return unique_skills

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
