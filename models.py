# models.py
from datetime import datetime
from extensions import db


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    company = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Job {self.title}>'

class ResumeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    job_description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ResumeAnalysis {self.filename}>'
