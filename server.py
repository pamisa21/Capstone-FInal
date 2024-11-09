from flask import Flask, render_template, session, request, redirect, url_for, flash, g
from models.models import Users
from models.faculty_model import Faculty
from models.department_model import Department
from models.faculty_model import Faculty
from models.comments_model import Comment
from models.college_model import College
from models.sentement_model import SentimentComment
from models.semester_model import Semester
from models.student_model import Student
from models.ay_model import AY_SEM
from models.subject_model import Subject
from models.extensions import db
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/ComFES'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FES_LOGO_PATH'] = '/static/img/feslogo.png'
app.config['LOADING_GIF'] = '/static/img/Orange and Purple Vibrant Colorful Geometric Website Logo.gif'

# Initialize SQLAlchemy with the app
db.init_app(app)

# server.py

@app.context_processor
def inject_default_semester():
    """Inject all academic years and semesters into all templates."""
    # Fetch all records from AY_SEM table
    all_semesters = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).all()
    latest_semester = all_semesters[0] if all_semesters else None

    # Set the latest semester as the default if no semester is in localStorage or passed in URL
    default_semester = latest_semester.ay_id if latest_semester else None
    
    return dict(all_semesters=all_semesters, default_semester=default_semester)


with app.app_context():
    from routes import *
    db.create_all()  

if __name__ == '__main__':
    app.run(debug=True)
