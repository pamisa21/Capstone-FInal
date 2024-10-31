from datetime import datetime
from models.extensions import db  

class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    school_year = db.Column(db.String(20), nullable=False)  
    semester_number = db.Column(db.Integer, nullable=False)  
  
    

    def __repr__(self):
        return f'<Semester {self.school_year} - {self.semester_number}>'
