from datetime import datetime
from models.extensions import db  # Import the db instance from extensions

# Create Model
class Comment(db.Model):
    __tablename__ = 'comments'  # Specify the table name
    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(255))
    faculty_id = db.Column(db.Integer, nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    semester_number = db.Column(db.Integer)
    school_year = db.Column(db.String(255))
    status = db.Column(db.Integer, default=0)  # Add status column with default value of 1
    def __repr__(self):
        return f'<Comment {self.comment_id}>'  # Use comment_id for representation
