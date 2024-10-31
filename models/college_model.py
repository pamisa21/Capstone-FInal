from models.extensions import db  # Import the db instance from extensions

class College(db.Model):
    __tablename__ = 'colleges'
    college_id = db.Column(db.String(20), primary_key=True)  # Changed to String with length 20
    college_name = db.Column(db.String(255), nullable=False, unique=True)

    # Relationship with Faculty
  
    departments = db.relationship('Department', backref='college', lazy=True)
    
    def __repr__(self):
        return f'<College {self.college_id} - {self.college_name}>'
