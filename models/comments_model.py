from datetime import datetime
from models.extensions import db  

class Comment(db.Model):
    __tablename__ = 'comments' 
    comment_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    faculty_id = db.Column(db.String(20), db.ForeignKey('faculty.faculty_id'), nullable=False)
    subject_id = db.Column(db.String(20), db.ForeignKey('subjects.subject_id'), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    ay_id = db.Column(db.String(20), db.ForeignKey('AY_SEM.ay_id'), nullable=False)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=True)  
    category = db.Column(db.Integer, default=3, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True, default=None, onupdate=datetime.utcnow)

    edit_status = db.Column(db.Integer, default=1)
    ai_old_result = db.Column(db.Integer, nullable=True)

    # Relationships
    student = db.relationship('Student', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.comment_id}>'
