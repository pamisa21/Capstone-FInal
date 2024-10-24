from flask import Flask, render_template, session, request, redirect, url_for, flash, g
from models.models import Users
from models.faculty_model import Faculty
from models.comments_model import Comment
from models.semester_model import Semester
from models.sentement_model import SentimentComment

from models.extensions import db
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/ComFES'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

@app.context_processor
def inject_default_semester():
    """Inject the default semester and school year into all templates."""
    default_semester = Semester.query.first()  # Fetch the default semester
    return {
        'default_semester': default_semester
    }

# Import the routes from routes.py
with app.app_context():
    from routes import *
    db.create_all()  # Create tables after importing routes

if __name__ == '__main__':
    app.run(debug=True)
