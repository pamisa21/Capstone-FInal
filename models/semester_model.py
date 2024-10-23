from datetime import datetime
from models.extensions import db  # Import the db instance from extensions




class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    school_year = db.Column(db.String(20), nullable=False)  # E.g., "2024-2025"
    semester_number = db.Column(db.Integer, nullable=False)  # Numeric representation of the semester

    def __repr__(self):
        return f'<Semester {self.school_year} - {self.semester_number}>'
