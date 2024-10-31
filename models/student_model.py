from models.extensions import db  # Import the db instance from extensions

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.String(20), primary_key=True)
    lname = db.Column(db.String(100), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    mi = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.String(20), db.ForeignKey('department.department_id'), nullable=False)  # ForeignKey to Department
    email = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)  # Default set to True (active)

    # Relationships
    department = db.relationship('Department', back_populates='students')

    def __repr__(self):
        return f'<Student {self.fname} {self.lname}>'
