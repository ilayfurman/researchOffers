from flask import Flask, render_template, request, redirect, url_for, session
from models import db, find_or_create_user, get_filtered_jobs, Departments # import the User classes 
import os


app = Flask(__name__, template_folder='pages')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', default=os.urandom(16).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://researchoffers_4hhf_user:J4LjE1VPo7DLbZLJAG34mBdKYezVxRC4@dpg-cjrrvetv2qks73b45ss0-a.oregon-postgres.render.com/researchoffers_4hhf'


db.init_app(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST','GET'])
def login():
    alert = None
    username = request.form['username']
    password = request.form['password']  # should encrypt the password
    position = request.form['position']
    
    user, status = find_or_create_user(username, password, position)
    
    if user:
        session['username'] = username
        session['position'] = position.lower()
        return redirect(url_for(f'{position.lower()}_home'))
    else:
        alert = status

    return render_template('login.html', password_error=alert)

@app.route('/student_home')
def student_home():
    prof = request.args.get('prof', '').strip()
    keyword = request.args.get('keyword', '').strip()
    dept = request.args.get('dept', 'All').strip()
    classYear = request.args.get('classYear', 'All').strip()

    jobs = get_filtered_jobs(prof, keyword, dept, classYear)
    departments_query = Departments.query.all()
    departments = [department.title for department in departments_query]

    if jobs:
        return render_template('student-search.html', jobs=jobs, professor=prof, keyword=keyword, dept=dept, classYear=classYear, departments=departments)
    else:
        return render_template('error.html', error="No jobs found")

@app.route('/prof_home')
def prof_home():
    if 'username' in session and session['position'] == 'professor':
        return 'Welcome Professor!'
    else:
        return redirect(url_for('index'))