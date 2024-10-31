from models.extensions import db  

class Subject(db.Model):
    __tablename__ = 'subjects'
    subject_id = db.Column(db.String(20), primary_key=True) 
    subject_name = db.Column(db.String(255), nullable=False, unique=True)  

    def __repr__(self):
        return f'<Subject {self.subject_id} - {self.subject_name}>'
