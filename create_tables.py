from server import db, app  # Import db and app from your Flask application

# Create a database and tables
with app.app_context():
    db.create_all()  # This will create all tables defined in your models
    print("Database tables created successfully.")
