import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)

app.config['SECRET_KEY'] = 'smart-portal-production-key-9988'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_job_portal_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Setup
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== DATABASE MODELS (Matching Flowchart) ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False) # 'JOB_SEEKER', 'JOB_PROVIDER', 'ADMIN'
    is_verified = db.Column(db.Boolean, default=True)

    # Profiles (1-to-1)
    seeker_profile = db.relationship('SeekerProfile', backref='user', uselist=False, cascade="all, delete")
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade="all, delete")

class SeekerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    key_skills = db.Column(db.Text)
    languages = db.Column(db.String(200))
    # Employment
    experience_years = db.Column(db.String(50))
    current_company = db.Column(db.String(100))
    # Education
    course_degree = db.Column(db.String(100))
    institute = db.Column(db.String(100))
    # Project
    project_title = db.Column(db.String(100))
    project_detail = db.Column(db.Text)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100))
    location = db.Column(db.String(100))
    size = db.Column(db.String(50))
    industry = db.Column(db.String(100))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(100))
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Technology')
    location = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False) # Full-Time / Part-Time
    pay = db.Column(db.String(50))
    benefits = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=True) # Admin Approval Flow
    job_posted_at = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    seeker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resume_file = db.Column(db.String(255), nullable=False)
    screening_answer = db.Column(db.Text)
    # Flowchart statuses: ACTIVE -> REVIEWED -> HIRED / REJECTED
    status = db.Column(db.String(30), default='ACTIVE') 
    interview_date = db.Column(db.String(100), nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship('Job', backref=db.backref('applications', cascade="all, delete"))
    seeker = db.relationship('User', backref=db.backref('applications', cascade="all, delete"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ROUTES & CONTROLLERS ====================

@app.route('/')
def home():
    category = request.args.get('category')
    location = request.args.get('location')
    job_type = request.args.get('job_type')

    query = Job.query.filter_by(is_approved=True)

    if category:
        query = query.filter(Job.category.ilike(f'%{category}%'))
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter_by(job_type=job_type)

    jobs = query.order_by(Job.job_posted_at.desc()).all()
    return render_template('index.html', jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        if User.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('register'))

        user = User(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=email,
            password=request.form.get('password'),
            user_type=request.form.get('user_type')
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            if not user.is_verified:
                flash('Your account has been suspended by Admin.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile/build', methods=['GET', 'POST'])
@login_required
def build_profile():
    if current_user.user_type != 'JOB_SEEKER':
        return redirect(url_for('dashboard'))

    profile = SeekerProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        if not profile:
            profile = SeekerProfile(user_id=current_user.id)
            db.session.add(profile)

        profile.key_skills = request.form.get('key_skills')
        profile.languages = request.form.get('languages')
        profile.experience_years = request.form.get('experience_years')
        profile.current_company = request.form.get('current_company')
        profile.course_degree = request.form.get('course_degree')
        profile.institute = request.form.get('institute')
        profile.project_title = request.form.get('project_title')
        profile.project_detail = request.form.get('project_detail')

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('dashboard'))

    return render_template('build_profile.html', profile=profile)

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.user_type != 'JOB_PROVIDER':
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        job = Job(
            provider_id=current_user.id,
            company_name=request.form.get('company_name'),
            job_title=request.form.get('job_title'),
            job_description=request.form.get('job_description'),
            category=request.form.get('category'),
            location=request.form.get('location'),
            job_type=request.form.get('job_type'),
            pay=request.form.get('pay'),
            benefits=request.form.get('benefits'),
            is_approved=True
        )
        db.session.add(job)
        db.session.commit()
        flash('Job post created successfully!')
        return redirect(url_for('dashboard'))

    return render_template('post_job.html')

@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_job(job_id):
    if current_user.user_type != 'JOB_SEEKER':
        flash('Only Job Seekers can apply.')
        return redirect(url_for('home'))

    existing = Application.query.filter_by(job_id=job_id, seeker_id=current_user.id).first()
    if existing:
        flash('You have already applied for this job!')
        return redirect(url_for('dashboard'))

    if 'resume' not in request.files:
        flash('No file uploaded.')
        return redirect(url_for('home'))

    file = request.files['resume']
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        app_entry = Application(
            job_id=job_id,
            seeker_id=current_user.id,
            resume_file=filename,
            screening_answer=request.form.get('screening_answer'),
            status='ACTIVE'
        )
        db.session.add(app_entry)
        db.session.commit()
        flash('Application submitted successfully!')
    else:
        flash('Invalid file type! Upload PDF or DOCX.')

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'ADMIN':
        return redirect(url_for('admin_panel'))

    if current_user.user_type == 'JOB_PROVIDER':
        applications = Application.query.join(Job).filter(Job.provider_id == current_user.id).all()
        my_jobs = Job.query.filter_by(provider_id=current_user.id).all()
        return render_template('dashboard.html', applications=applications, my_jobs=my_jobs)
    else:
        applications = Application.query.filter_by(seeker_id=current_user.id).all()
        profile = SeekerProfile.query.filter_by(user_id=current_user.id).first()
        return render_template('dashboard.html', applications=applications, profile=profile)

@app.route('/uploads/<filename>')
@login_required
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/update-status/<int:app_id>', methods=['POST'])
@login_required
def update_status(app_id):
    if current_user.user_type == 'JOB_PROVIDER':
        app_item = Application.query.get_or_404(app_id)
        status = request.form.get('status')
        interview_date = request.form.get('interview_date')

        app_item.status = status
        if interview_date:
            app_item.interview_date = interview_date

        db.session.commit()
        flash('Candidate status updated!')
    return redirect(url_for('dashboard'))

# ==================== ADMIN LAYER ====================

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.user_type != 'ADMIN':
        flash('Access Denied: Admins Only!')
        return redirect(url_for('dashboard'))

    users = User.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()

    # System Reports logic
    reports = {
        'total_users': len(users),
        'total_jobs': len(jobs),
        'total_applications': len(applications),
        'total_hired': Application.query.filter_by(status='HIRED').count()
    }

    return render_template('admin.html', users=users, jobs=jobs, reports=reports)

@app.route('/admin/toggle-user/<int:user_id>')
@login_required
def toggle_user(user_id):
    if current_user.user_type == 'ADMIN':
        u = User.query.get_or_404(user_id)
        u.is_verified = not u.is_verified
        db.session.commit()
        flash('User status changed!')
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-job/<int:job_id>')
@login_required
def delete_job(job_id):
    if current_user.user_type == 'ADMIN':
        j = Job.query.get_or_404(job_id)
        db.session.delete(j)
        db.session.commit()
        flash('Job post removed!')
    return redirect(url_for('admin_panel'))

# Create Admin & Seed Database
def init_db():
    with app.app_context():
        db.create_all()
        # Create default System Admin
        if not User.query.filter_by(email='admin@smartjob.com').first():
            admin = User(
                first_name='System',
                last_name='Admin',
                email='admin@smartjob.com',
                password='adminpassword',
                user_type='ADMIN'
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)