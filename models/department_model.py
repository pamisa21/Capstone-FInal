from models.extensions import db  # Import the db instance from extensions

class Department(db.Model):
    __tablename__ = 'department'
    department_id = db.Column(db.String(20), primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.String(20), db.ForeignKey('colleges.college_id'), nullable=False)

 
    faculties = db.relationship('Faculty', back_populates='department')
    students = db.relationship('Student', back_populates='department')

    def __repr__(self):
        return f'<Department {self.department_name}>'
