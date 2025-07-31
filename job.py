from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os #works with file paths and fodler creation
import fitz  # PyMuPDF-extracts text from pdfs
import docx #reads .docx files
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Job(db.Model):  # Changed from Jobs to Job
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    company = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Job {self.title}>'



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        description = request.form['description']

        # Save to DB
        job = Job(title=title, company=company, description=description)
        db.session.add(job)
        db.session.commit()

        return redirect(url_for('job_detail', job_id=job.id))

    return render_template('job/index.html')
@app.route('/jobs')
def job_list():
    jobs = Job.query.all()
    return render_template('jobOffer/job.html', jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job/detail.html', job=job)

if __name__ == '__main__':
    app.run(debug=True)