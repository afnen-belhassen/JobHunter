from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models import Job

job_bp = Blueprint('job', __name__, template_folder='templates/jobOffer')


# Note: Do NOT create Flask app here or call app.run()

# You will need to initialize db in app.py and import it here or pass it in (common pattern)

@job_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        description = request.form['description']

        job = Job(title=title, company=company, description=description)
        db.session.add(job)
        db.session.commit()

        return redirect(url_for('job.job_detail', job_id=job.id))

    return render_template('resume/index.html')

@job_bp.route('/')
def job_list():
    jobs = Job.query.all()
    return render_template('job.html', jobs=jobs)
    
@job_bp.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('jobOffer/detail.html', job=job)