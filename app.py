from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os #works with file paths and fodler creation
import fitz  # PyMuPDF-extracts text from pdfs
import docx #reads .docx files
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<ResumeAnalysis {self.filename}>'
# Create DB tables
with app.app_context():
    db.create_all()




os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#opens a pdf file and extracts text from its pages
def extract_text_from_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text
#reads a docx file and extracts text parg by parag
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

            # Sauvegarde dans la base de données
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

if __name__ == '__main__':
    app.run(debug=True)
