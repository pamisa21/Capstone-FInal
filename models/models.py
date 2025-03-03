# model.py
from datetime import datetime
from models.extensions import db  # Import the db instance from extensions

# Create Model
class Users(db.Model):
    __tablename__ = 'users'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    lname = db.Column(db.String(200), nullable=False)
    fname=db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, lname, email, password, status, fname):
        self.lname = lname
        self.email = email
        self.password = password
        self.status = status
        self.fname= fname
    def __repr__(self):  
        return '<Name %r>' % self.lname
