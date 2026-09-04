# 💼 Smart Job Portal & Recruitment System

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-06B6D4.svg)

A modern, full-stack web application designed to bridge the gap between **Job Seekers** and **Employers**. Built with **Python Flask**, **SQLite**, and **Tailwind CSS**, this platform streamlines job searches, resume submissions, and real-time recruitment tracking.

---

## 🌟 Key Features

### 👤 Role-Based Authentication
* **Dual Roles:** User accounts are categorized as **Job Seeker** or **Employer**.
* **Session Management:** Route-level dynamic access control powered by **Flask-Login**.

### 🏢 Employer Dashboard
* **Job Management:** Create and publish dynamic job listings complete with category, location, salary, and benefits details.
* **Applicant Review:** Review applications, inspect screening responses, and download submitted resumes (PDF/Docs).
* **Live Status Updates:** Update applicant status (Pending Review, Shortlisted, Hired, Rejected) and set interview schedules.

### 🧑‍💻 Job Seeker Experience
* **Interactive Job Board:** Search available positions filtered by location, category, and job types.
* **One-Click Application:** Apply directly to positions with uploaded resumes and screening answers.
* **Application Tracking:** Live dashboard to monitor real-time recruitment progress and interview schedules.

---

## 🛠️ Technology Stack

| Domain | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3.x, Flask 3.x |
| **Database & ORM** | SQLite 3, Flask-SQLAlchemy |
| **Authentication & Security** | Flask-Login, Werkzeug |
| **Frontend UI** | HTML5, Jinja2 Templating, Tailwind CSS |
| **Version Control** | Git & GitHub |

---

## 📁 Directory Structure

smart_job_portal/
├── app.py                   # Flask Application Core & Routing Logic
├── instance/
│   └── smart_job_portal.db  # SQLite Database File
├── static/
│   └── css/
│       └── style.css        # Stylesheet & Tailwind CSS Configurations
├── templates/
│   ├── base.html            # Core HTML Layout
│   ├── index.html           # Public Job Board / Search Interface
│   ├── login.html           # Authentication Interface
│   ├── register.html        # Registration Interface
│   ├── dashboard.html       # Dynamic Dashboard (Seeker / Employer)
│   ├── post_job.html        # Circular Posting Form
│   └── admin.html           # System Management Interface
└── uploads/                 # Storage for Candidate Resumes & Docs


🚀 Getting Started
Prerequisites
Ensure Python 3.x is installed on your system:
-----

Bash
python --version
1. Clone Repository
   
Bash
git clone [https://github.com/mursalin-decen/Smart-Job-Portal---Recruitment-System.git](https://github.com/mursalin-decen/Smart-Job-Portal---Recruitment-System.git)
cd Smart-Job-Portal---Recruitment-System
3. Virtual Environment Setup
Bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Bash
pip install flask flask-sqlalchemy flask-login werkzeug
4. Run Application
Bash
python app.py
Access the portal on your browser at: http://127.0.0.1:5000/

🔄 End-to-End Workflow Demonstration
Employer Workflow: Register as an Employer → Navigate to Post New Job → Publish job circulars with benefits and qualifications.

Job Seeker Workflow: Register as a Job Seeker → Browse available jobs → Submit screening answers and attach resume → Apply.

Recruitment Pipeline: Switch back to Employer account → Manage Applicants → Review resume → Change status to HIRED or SHORTLISTED and schedule interview.

Verification: Log back as Job Seeker to view instant real-time status updates on the dashboard.

👤 Author & Acknowledgment
Md Mursalin Ahmmed Zamzam

Department of Computer Science and Engineering

Northern University of Business and Technology Khulna

Student ID: 11240321817
