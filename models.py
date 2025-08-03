# models.py
from datetime import datetime
from extensions import db


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    company = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(50))  # full-time, part-time, contract, etc.
    experience_level = db.Column(db.String(50))  # entry-level, mid-level, senior, etc.
    location = db.Column(db.String(200))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    contact_email = db.Column(db.String(200))
    deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
