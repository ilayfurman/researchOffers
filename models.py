from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, BINARY, PickleType, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError


db = SQLAlchemy()

class Departments(db.Model):
    __tablename__ = 'departments'
    dept_id = Column(Integer, primary_key=True)
    title = Column(String(225))
    students = relationship("Students", back_populates="department")
    professors = relationship("Professors", back_populates="department")
    jobs = relationship("Jobs", back_populates="departments", secondary="jobsdepartment")

class Jobs(db.Model):
    __tablename__ = 'jobs'
    job_id = Column(Integer, primary_key=True)
    title = Column(String(127))
    description = Column(String(225))
    class_year = Column(String(100))
    dept = Column(String(100))
    professor_id = Column(Integer, ForeignKey('professors.professor_id', ondelete='CASCADE'))
    dynamic_app = relationship("DynamicApps", back_populates="job", uselist=False)
    departments = relationship("Departments", back_populates="jobs", secondary="jobsdepartment")
    professor = relationship("Professors", back_populates="jobs", uselist=False)

class Professors(db.Model):
    __tablename__ = 'professors'
    professor_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='SET NULL'))
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    department = relationship('Departments')
    professor_photo = relationship("ProfessorsPhoto", back_populates="professor", uselist=False)
    jobs = relationship("Jobs", back_populates="professor")

class ProfessorsBio(db.Model):
    __tablename__ = 'professorsbio'
    professor_id = Column(Integer, ForeignKey('professors.professor_id', ondelete='CASCADE'),  primary_key=True)
    biography = Column(String(500))
    professor = relationship('Professors', backref='bio')

class Students(db.Model):
    __tablename__ = 'students'
    student_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    year = Column(String(10))
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete='SET NULL'))
    email = Column(String(50))
    department = relationship('Departments', back_populates="students")
    student_resume = relationship("StudentsResume", back_populates="student", uselist=False)
    student_photo = relationship("StudentsPhoto", back_populates="student", uselist=False)

class StudentsBio(db.Model):
    __tablename__ = 'studentsbio'
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), primary_key=True)
    biography = Column(String(500))
    student = relationship('Students', backref='bio')

class StudentSkills(db.Model):
    __tablename__ = 'studentskills'
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), primary_key=True)
    skills = Column(PickleType)
    student = relationship('Students', backref='skills')

class StudentsResume(db.Model):
    __tablename__ = 'studentsresume'
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), primary_key=True)
    resume = Column(BINARY)
    student = relationship("Students", back_populates="student_resume", uselist=False)

class StudentsPhoto(db.Model):
    __tablename__ = 'studentsphoto'
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete='CASCADE'), primary_key=True)
    photo = Column(BINARY)
    student = relationship("Students", back_populates="student_photo", uselist=False)

class ProfessorsPhoto(db.Model):
    __tablename__ = 'professorsphoto'
    professor_id = Column(Integer, ForeignKey('professors.professor_id', ondelete='CASCADE'), primary_key=True)
    photo = Column(BINARY)
    professor = relationship("Professors", back_populates="professor_photo", uselist=False)

class Applications(db.Model):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete="CASCADE"))
    status = Column(String(10))
    response = Column(PickleType)
    student_id = Column(Integer, ForeignKey('students.student_id', ondelete="CASCADE"))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    job = relationship("Jobs", backref="applications")
    student = relationship("Students", backref="applications")
    UniqueConstraint(job_id, student_id, name="uni_app")

class DynamicApps(db.Model):
    __tablename__ = 'dynamicapps'
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete="CASCADE"), primary_key=True)
    questions = Column(PickleType)
    job = relationship("Jobs", back_populates="dynamic_app", uselist=False)

class JobsDepartment(db.Model):
    __tablename__ = 'jobsdepartment'
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete="CASCADE"), primary_key=True)
    dept_id = Column(Integer, ForeignKey('departments.dept_id', ondelete="CASCADE"), primary_key=True)



def find_or_create_user(username, password, position):
    user = None
    if position == 'Student':
        user = Students.query.filter_by(username=username).first()
    elif position == 'Professor':
        user = Professors.query.filter_by(username=username).first()

    try:
        if user:
            if user.password == password:
                db.session.commit()
                return user, 'Logged in'
            else:
                db.session.rollback()
                return None, 'Password incorrect for existing username'
    
        else:
            if position == 'Student':
                new_user = Students(username=username, name=username, password=password)
            elif position == 'Professor':
                new_user = Professors(username=username, name=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return new_user, 'New user created'
        
    except SQLAlchemyError as e:
        db.session.rollback()
        print("Error occurred:", e)
        return None, 'Database error occurred'
    

def get_filtered_jobs(prof='', keyword='', dept='All', classYear='All'):
    query = Jobs.query
    if prof:
        query = query.filter(Jobs.professor_id == prof)
    if keyword:
        query = query.filter(Jobs.description.contains(keyword))
    if dept != 'All':
        query = query.join(JobsDepartment).filter(JobsDepartment.dept_id == dept)  # Make sure to import JobsDepartment if you have such a table
    if classYear != 'All':
        query = query.filter(Jobs.class_year == classYear)
    return query.all()