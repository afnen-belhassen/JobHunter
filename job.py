from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Job
from datetime import datetime
import markupsafe

job_bp = Blueprint('job', __name__, template_folder='templates/jobOffer')

# Custom Jinja2 filter for newline to line break conversion
def nl2br(value):
    if value:
        return markupsafe.Markup(value.replace('\n', '<br>'))
    return value

# Register the filter
job_bp.add_app_template_filter(nl2br, 'nl2br')

# Note: Do NOT create Flask app here or call app.run()

# You will need to initialize db in app.py and pass it in (common pattern)

@job_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def index():
    if current_user.user_type != 'job_offerer':
        flash('Only job offerers can post jobs.', 'error')
        return redirect(url_for('job.job_list'))
        
    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        description = request.form['description']

        job = Job(title=title, company=company, description=description)
        db.session.add(job)
        db.session.commit()

        return redirect(url_for('job.job_detail', job_id=job.id))

    return render_template('resume/index.html')

@job_bp.route('/jobs')
def job_list():
    jobs = Job.query.all()
    return render_template('job.html', jobs=jobs)
    
@job_bp.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('jobOffer/detail.html', job=job)

@job_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_job():
    # Check if user is a job offerer
    if current_user.user_type != 'job_offerer':
        flash('Only job offerers can post jobs. Please contact support if you need to change your account type.', 'error')
        return redirect(url_for('job.job_list'))
    
    if request.method == 'POST':
        # Handle form submission
        job_title = request.form.get('job_title')
        company_name = request.form.get('company_name')
        job_type = request.form.get('job_type')
        experience_level = request.form.get('experience_level')
        location = request.form.get('location')
        salary_min = request.form.get('salary_min')
        salary_max = request.form.get('salary_max')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        benefits = request.form.get('benefits')
        contact_email = request.form.get('contact_email')
        deadline = request.form.get('deadline')
        
        # Create new job object (you may need to update your Job model)
        job = Job(
            title=job_title,
            company=company_name,
            description=description,
            job_type=job_type,
            experience_level=experience_level,
            location=location,
            salary_min=salary_min if salary_min else None,
            salary_max=salary_max if salary_max else None,
            requirements=requirements,
            benefits=benefits,
            contact_email=contact_email,
            deadline=datetime.strptime(deadline, '%Y-%m-%d') if deadline else None
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('job.job_detail', job_id=job.id))
    
    # GET request - show the form
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('jobOffer/jobAdd.html', today_date=today_date)