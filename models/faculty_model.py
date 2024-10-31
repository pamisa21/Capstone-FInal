from models.extensions import db  # Import the db instance from extensions

class Faculty(db.Model):
    __tablename__ = 'faculty'
    faculty_id = db.Column(db.String(20), primary_key=True)
    lname = db.Column(db.String(100), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    mi = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.String(20), db.ForeignKey('department.department_id'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    department = db.relationship('Department', back_populates='faculties')

    def __repr__(self):
        return f'<Faculty {self.lname} {self.fname}>'