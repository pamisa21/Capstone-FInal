from datetime import datetime
from models.extensions import db  # Import the db instance from extensions

class SentimentComment(db.Model):
    __tablename__ = 'sentiment_comments'

    id = db.Column(db.Integer, primary_key=True)  # Sentiment_Comments_id
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.comment_id'), nullable=False)  # Foreign key from Comment
    comment_content = db.relationship('Comment', backref='sentiment_comments', lazy=True)  # Relationship to access comment content
    category = db.Column(db.Integer, default=0, nullable=False)  # category, default 0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # created_at, default current timestamp
    publish = db.Column(db.Integer, default=0, nullable=False)  # publish, default 0

    def __repr__(self):
        return f'<SentimentComment {self.id} linked to Comment {self.comment_id}>'
