from flask import Flask, render_template, request, redirect, url_for
import os
import fitz
import docx
from extensions import db
from job import job_bp
from models import ResumeAnalysis
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
            job_text = request.form['job_description']

            if resume_file:
                filename = resume_file.filename
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume_file.save(path)

                resume_text = extract_text(path)

                analysis = ResumeAnalysis(
                    filename=filename,
                    extracted_text=resume_text,
                    job_description=job_text
                )
                db.session.add(analysis)
                db.session.commit()

                return redirect(url_for('result', id=analysis.id))

        return render_template('resume/index.html')

    @app.route('/result/<int:id>')
    def result(id):
        analysis = ResumeAnalysis.query.get_or_404(id)
        return render_template('resume/result.html',
                               resume_text=analysis.extracted_text,
                               job_text=analysis.job_description)

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

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
