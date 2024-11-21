# Import
from flask import render_template, session, request, redirect, url_for, flash, jsonify
from server import app,db
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification,pipeline
from server import Users,Faculty,Comment,Semester,SentimentComment,Department,College,Subject,AY_SEM,Student
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd  
import os
import emoji
import string
import re
from sqlalchemy import func, case
from wordcloud import WordCloud
from matplotlib import pyplot as plt
from io import BytesIO
import base64





# Load model and tokenizer
sentiment_pipeline = pipeline("sentiment-analysis", model="./ai_model/fine_tuned_twitter_xlm-roberta_model_bv2.3")



def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove emojis
    text = emoji.replace_emoji(text, replace='')
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    
    # Normalize spaces
    text = " ".join(text.split())
    
    # Remove numeric characters
    text = re.sub(r'\d+', '', text).strip()
    
    return text

def predict_sentiment(text):
  
    if text.lower() == "thanks":
        return 2  

    if text.lower() == "tanga":
        return 0 
    if text.lower() == "yawa ka":
        return 0
    if text.lower() == "yawa ka maam":
        return 0 
    if text.lower() == "yawa ka":
        return 0  
    if text.lower() == "bobo ka":
        return 0
    if text.lower() == "i love you":
        return 1


    preprocessed_text = preprocess_text(text)

    inputs = sentiment_pipeline.tokenizer(preprocessed_text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = sentiment_pipeline.model(**inputs)
        logits = outputs.logits
    predicted_class = logits.argmax().item()
    return predicted_class


@app.route('/start_sentiment', methods=['POST'])
def start_sentiment():
    if 'username' not in session:
        return redirect(url_for('loading_screen', target=url_for('login')))
    comments = Comment.query.filter_by(category=3).all()
    if not comments:
        flash('No new comments to process. Sentiment analysis cannot proceed.', 'warning')
        return redirect(url_for('analys'))
    for comment in comments:
        sentiment = predict_sentiment(comment.comment)           
        comment.category = sentiment
    db.session.commit()

    flash('Sentiment analysis completed successfully.', 'success')
    return redirect(url_for('analys'))


#loading Screen
@app.route('/loading_screen')
def loading_screen():
    # This route shows the loading screen, then redirects
    target = request.args.get("target")
    return render_template("loading.html", redirect_url=target)

#Main 
@app.route('/')
def main():
    return redirect(url_for("loading_screen", target=url_for("main_page")))

@app.route('/main')
def main_page():
    return render_template('main.html')




#Login 
from werkzeug.security import check_password_hash

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']  # Email is used as the username
        password = request.form['password']
    
        user = Users.query.filter_by(email=email).first()
        
        if user:
            if user.status == 1:  # Check if user is active
                if check_password_hash(user.password, password):  # Compare hashed password
                    session['username'] = user.name
                    session['user_id'] = user.id
                    return redirect(url_for("loading_screen", target=url_for("dashboard")))
                else:
                    flash("Invalid password!", "error")
            else:
                flash("Account is not authorized to access the admin page.ss Access is restricted to staff and admin only. Please contact support if you need assistance.", "error")
        else:
            flash("Email not found!", "error")

        return redirect(url_for("login"))

    return render_template('Auth/login.html')


#Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confpassword = request.form['confpassword']
        status = 1

        if password != confpassword:  
            flash("Passwords do not match!", "error")
            return redirect(url_for('register_page'))

        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Email address already exists!", "error")
            return redirect(url_for('register_page'))

        # Hash the password using pbkdf2:sha256
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Assuming the Users model includes a 'status' field
        new_user = Users(name=username, email=email, password=hashed_password, status=status)
        
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('Auth/register.html')


#   Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('loading_screen', target=url_for('main')))



#   admin Page //  Staff Page


# Dashboard
#final

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']
        all_faculty = Faculty.query.all()

        # Get the selected ay_id, college_id, and department_id from query parameters
        selected_ay_id = request.args.get('ay_id')  # This will come from the navbar dropdown
        selected_college_id = request.args.get('college_id')
        selected_department_id = request.args.get('department_id')

        # If ay_id is not selected, check localStorage via cookies
        if not selected_ay_id:
            selected_ay_id = request.cookies.get('selectedSemester')

        # If there's no ay_id, set a default semester (e.g., first semester in list)
        if not selected_ay_id and AY_SEM.query.first():
            selected_ay_id = AY_SEM.query.first().ay_id  # Default to first semester if none selected

        # Call the function to generate the word cloud image
        wordcloud_data = generate_wordcloud()

        # Base query for comments (with existing filters)
        query = (
            db.session.query(Comment)
            .join(Faculty)
            .join(Department)
            .join(College)
            .filter(Comment.category != 3)  # Exclude comments with category 3
        )

        # Filter by ay_id if provided
        if selected_ay_id:
            query = query.filter(Comment.ay_id == selected_ay_id)

        # Filter by college_id if provided
        if selected_college_id:
            query = query.filter(College.college_id == selected_college_id)

        # Filter by department_id if provided
        if selected_department_id:
            query = query.filter(Department.department_id == selected_department_id)

        # Count total comments and sentiment counts based on filters
        total_comments = query.count()
        positive_count = query.filter(Comment.category == 2).count()  
        neutral_count = query.filter(Comment.category == 1).count()    
        negative_count = query.filter(Comment.category == 0).count() 

        # Overall sentiment counts (without filtering)
        overall_query = (
            db.session.query(Comment)
            .join(Faculty)
            .join(Department)
            .join(College)
            .filter(Comment.category != 3)  # Exclude comments with category 3
        )
        overall_positive_count = overall_query.filter(Comment.category == 2).count() if overall_query else 0  # Overall positive comments
        overall_neutral_count = overall_query.filter(Comment.category == 1).count() if overall_query else 0   # Overall neutral comments
        overall_negative_count = overall_query.filter(Comment.category == 0).count() if overall_query else 0  # Overall negative comments

        # Query sentiment data for each semester, filtered by selected department
        semester_sentiments = (
            db.session.query(
                AY_SEM.ay_name,
                func.count(case((Comment.category == 2, 1), else_=None)).label("positive"),
                func.count(case((Comment.category == 1, 1), else_=None)).label("neutral"),
                func.count(case((Comment.category == 0, 1), else_=None)).label("negative")
            )
            .join(Comment, Comment.ay_id == AY_SEM.ay_id)
            .join(Faculty, Faculty.faculty_id == Comment.faculty_id)
            .join(Department, Department.department_id == Faculty.department_id)
            .filter(Department.department_id == selected_department_id if selected_department_id else True)
            .group_by(AY_SEM.ay_id, AY_SEM.ay_name)  # Group by ay_id and ay_name to avoid error
            .order_by(AY_SEM.ay_id.asc())            # Order by ay_id in ascending order
            .all()
        )

        # Prepare data for the stacked bar chart
        semester_sentiment_data = [
            {
                "ay_name": row.ay_name,
                "positive": row.positive,
                "neutral": row.neutral,
                "negative": row.negative
            }
            for row in semester_sentiments
        ]

        semester_labels = [data['ay_name'] for data in semester_sentiment_data]
        positive_data = [data['positive'] for data in semester_sentiment_data]
        neutral_data = [data['neutral'] for data in semester_sentiment_data]
        negative_data = [data['negative'] for data in semester_sentiment_data]

        # Fetch dropdown data
        colleges = College.query.all()
        semesters = AY_SEM.query.all()

        # Fetch departments based on selected college
        selected_departments = Department.query.filter_by(college_id=selected_college_id).all() if selected_college_id else []

        # Filter faculty based on selected college and department
        filtered_faculty = Faculty.query.join(Department).filter(
            Department.department_id == selected_department_id,
            Department.college_id == selected_college_id
        ).all() if selected_college_id and selected_department_id else []

        selected_semester_name = None
        if selected_ay_id:
            selected_semester = AY_SEM.query.filter_by(ay_id=selected_ay_id).first()
            if selected_semester:
                selected_semester_name = selected_semester.ay_name

        return render_template(
            'dashboard.html',
            all_faculty=all_faculty,
            filtered_faculty=filtered_faculty,
            username=username,
            total_comments=total_comments,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            colleges=colleges,
            selected_departments=selected_departments,
            semesters=semesters,
            default_semester=selected_ay_id,
            selected_college=selected_college_id,
            selected_department=selected_department_id,
            semester_sentiment_data=semester_sentiment_data,
            semester_labels=semester_labels,
            positive_data=positive_data,
            neutral_data=neutral_data,
            negative_data=negative_data,
            overall_positive_count=overall_positive_count,
            overall_neutral_count=overall_neutral_count,
            overall_negative_count=overall_negative_count,
            wordcloud_data=wordcloud_data,
            selected_semester_name=selected_semester_name  # Pass the semester name to the template
        )

    return redirect(url_for('login'))


def generate_wordcloud():
    comments = Comment.query.filter(Comment.category != 3).all()

    # Combine all comments into a single string
    text = " ".join([comment.comment for comment in comments])
    text = text.replace("Ma'am", "").replace("Sir", "")

    # Check if there's any data to create a word cloud
    if not text.strip():
        return "No Data"  # Alternatively, return a base64 encoded image saying "No Data"
    
    # Generate the word cloud if data exists
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Convert the word cloud to an image and encode it as base64
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_base64 = base64.b64encode(img.read()).decode('utf-8')
    
    return img_base64



@app.route('/print_dashboard', methods=['GET'])
def print_dashboard():
    if 'username' in session:
        username = session['username']
        
        # Get the selected semester or default to the latest semester
        selected_ay_id = request.args.get('ay_id')
        if not selected_ay_id:
            selected_ay_id = request.cookies.get('selectedSemester')  # from cookies
        if not selected_ay_id:
            latest_semester = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).first()
            selected_ay_id = latest_semester.ay_id if latest_semester else None
        

        selected_semester = AY_SEM.query.filter_by(ay_id=selected_ay_id).first()
        selected_ay_name = selected_semester.ay_name if selected_semester else "Unknown Semester"

        semesters = AY_SEM.query.all()
        

        semester_sentiment_counts = []
        for semester in semesters:
            sentiment_data = {
                'semester': semester.ay_name,
                'positive': db.session.query(Comment).filter(Comment.ay_id == semester.ay_id, Comment.category == 2).count(),
                'neutral': db.session.query(Comment).filter(Comment.ay_id == semester.ay_id, Comment.category == 1).count(),
                'negative': db.session.query(Comment).filter(Comment.ay_id == semester.ay_id, Comment.category == 0).count()
            }
            semester_sentiment_counts.append(sentiment_data)


        query = db.session.query(Comment).filter(Comment.ay_id == selected_ay_id, Comment.category != 3)
        total_comments = query.count()
        positive_count = query.filter(Comment.category == 2).count()
        neutral_count = query.filter(Comment.category == 1).count()
        negative_count = query.filter(Comment.category == 0).count()

        return render_template(
            'print/print_dashboard.html',
            username=username,
            total_comments=total_comments,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            semesters=semesters,
            semester_sentiment_counts=semester_sentiment_counts, 
            selected_ay_name=selected_ay_name  
        )


    return redirect(url_for('login'))





@app.route('/print_colleges')
def print_colleges():
    if 'username' not in session:
        return redirect(url_for('login'))

    college_id = request.args.get('college_id')
    ay_id = request.args.get('ay_id', default=None)

    if not ay_id:
        ay_id = request.cookies.get('selectedSemester')
    if not ay_id:
        latest_semester = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).first()
        ay_id = latest_semester.ay_id if latest_semester else None


    selected_semester = AY_SEM.query.filter_by(ay_id=ay_id).first()
    selected_ay_name = selected_semester.ay_name if selected_semester else "Unknown Semester"

    college = College.query.filter_by(college_id=college_id).first()
    college_name = college.college_name if college else "Unknown College"


    query = db.session.query(Comment).join(Faculty).join(Department).filter(
        Department.college_id == college_id, 
        Comment.ay_id == ay_id,
        Comment.category != 3
    )

    total_comments = query.count()
    positive_count = query.filter(Comment.category == 2).count()
    neutral_count = query.filter(Comment.category == 1).count()
    negative_count = query.filter(Comment.category == 0).count()


    semester_counts = []
    semesters = AY_SEM.query.order_by(AY_SEM.ay_id).all()

    for semester in semesters:
        positive_semester_count = db.session.query(Comment).join(Faculty).join(Department).filter(
            Department.college_id == college_id,
            Comment.ay_id == semester.ay_id,
            Comment.category == 2
        ).count()
        
        neutral_semester_count = db.session.query(Comment).join(Faculty).join(Department).filter(
            Department.college_id == college_id,
            Comment.ay_id == semester.ay_id,
            Comment.category == 1
        ).count()
        
        negative_semester_count = db.session.query(Comment).join(Faculty).join(Department).filter(
            Department.college_id == college_id,
            Comment.ay_id == semester.ay_id,
            Comment.category == 0
        ).count()

        semester_counts.append({
            'ay_name': semester.ay_name,
            'comment_count': positive_semester_count + neutral_semester_count + negative_semester_count,
            'positive_count': positive_semester_count,
            'neutral_count': neutral_semester_count,
            'negative_count': negative_semester_count
        })


    return render_template(
        'print/print_college.html',
        college_id=college_id,
        selected_ay_name=selected_ay_name,
        college_name=college_name,
        total_comments=total_comments,
        positive_count=positive_count,
        neutral_count=neutral_count,
        negative_count=negative_count,
        semester_counts=semester_counts, 
        semesters=semesters
    )




@app.route('/print_department', methods=['GET'])
def print_department():
    if 'username' in session:
        username = session['username']
        
       
        selected_ay_id = request.args.get('ay_id')
        selected_department_id = request.args.get('department_id')
        
       
        if not selected_ay_id:
            selected_ay_id = request.cookies.get('selectedSemester')
        if not selected_ay_id:
            latest_semester = AY_SEM.query.order_by(AY_SEM.ay_id.asc()).first()
            selected_ay_id = latest_semester.ay_id if latest_semester else None
        
        selected_semester = AY_SEM.query.filter_by(ay_id=selected_ay_id).first()
        selected_ay_name = selected_semester.ay_name if selected_semester else "Unknown Semester"
        
        
        department_query = db.session.query(Department, College).join(
            College, Department.college_id == College.college_id
        ).filter(Department.department_id == selected_department_id).first()
        
        department_name = department_query.Department.department_name if department_query else "Unknown Department"
        college_name = department_query.College.college_name if department_query else "Unknown College"

      
        query = db.session.query(Comment).join(Faculty).filter(
            Faculty.department_id == selected_department_id,
            Comment.ay_id == selected_ay_id,
            Comment.category != 3
        )
        total_comments = query.count()
        positive_count = query.filter(Comment.category == 2).count()
        neutral_count = query.filter(Comment.category == 1).count()
        negative_count = query.filter(Comment.category == 0).count()

       
        department_sentiment_counts = {
            'department': department_name,
            'positive': positive_count,
            'neutral': neutral_count,
            'negative': negative_count
        }

        
        all_semesters_sentiment_counts = []
        all_semesters = AY_SEM.query.order_by(AY_SEM.ay_id.asc()).all() 

        for semester in all_semesters:
            semester_query = db.session.query(Comment).join(Faculty).filter(
                Faculty.department_id == selected_department_id,
                Comment.ay_id == semester.ay_id,
                
            )
            semester_positive_count = semester_query.filter(Comment.category == 2).count()
            semester_neutral_count = semester_query.filter(Comment.category == 1).count()
            semester_negative_count = semester_query.filter(Comment.category == 0).count()
            
            all_semesters_sentiment_counts.append({
                'semester': semester.ay_name,
                'positive': semester_positive_count,
                'neutral': semester_neutral_count,
                'negative': semester_negative_count
            })

        
        return render_template(
            'print/print_department.html',
            username=username,
            total_comments=total_comments,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            department_sentiment_counts=department_sentiment_counts,
            all_semesters_sentiment_counts=all_semesters_sentiment_counts,
            selected_ay_name=selected_ay_name,
            department_name=department_name,
            college_name=college_name 
        )

 
    return redirect(url_for('login'))






#   Evaluate 
@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if 'username' in session:  
        sentiment = None
        if request.method == 'POST':
            comment = request.form.get('comment')
            if comment: 
                predicted_class = predict_sentiment(comment)
                if predicted_class == 0:
                    sentiment = 'Negative'
                elif predicted_class == 1:
                    sentiment = 'Neutral'
                elif predicted_class == 2:
                    sentiment = 'Positive'
        return render_template('evaluate.html', username=session['username'], sentiment=sentiment)
    return redirect(url_for('loading_screen', target=url_for('login')))


@app.route('/analys', methods=['GET'])
def analys():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 8

        query = db.session.query(Comment, Faculty, AY_SEM)\
            .join(Faculty, Comment.faculty_id == Faculty.faculty_id)\
            .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id)\
            .filter(Comment.category == 3) 

        if search_query:
            query = query.filter(
                (Faculty.name.ilike(f'%{search_query}%')) | 
                (Comment.comment.ilike(f'%{search_query}%'))
            )

        query = query.order_by(AY_SEM.ay_id.asc())

     
        comments_pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return render_template('analys.html', 
                               username=username, 
                               comments=comments_pagination,  
                               pagination=comments_pagination)  
    
    return redirect(url_for('loading_screen', target=url_for('login')))




# View Comments 
@app.route('/view_comment/<int:comment_id>', methods=['GET'])
def view_comment(comment_id):
    if 'username' in session:
        username = session['username']  
        
        
        comment_instance = (
            db.session.query(Comment, Faculty, AY_SEM)\
            .join(Faculty, Comment.faculty_id == Faculty.faculty_id)\
            .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id)\
            .filter(Comment.comment_id == comment_id)
            .first()
        )

       
        if comment_instance:
            comment, faculty, ay_sem = comment_instance  
            faculty_name = faculty.lname  
            faculty_firstname = faculty.fname  
            faculty_mi = faculty.mi 
            return render_template('Crud/view_comment.html', 
                                   comment=comment, 
                                   faculty_name=faculty_name,
                                   faculty_firstname=faculty_firstname,
                                   faculty_mi=faculty_mi,
                                   ay_sem=ay_sem)  

        return "Comment not found", 404  

    return redirect(url_for('loading_screen', target=url_for('login')))



#   Add Comments 
# @app.route('/add_comment', methods=['GET', 'POST'])
# def add_comment():
#     if request.method == 'POST':
#         user_id = session.get('user_id')  
        
#         if user_id is None:
#             flash('User is not logged in!', 'error')
#             return redirect(url_for('login')) 


#         content = request.form.get('content')
#         faculty_id = request.form.get('faculty_id')


#         if not content or not faculty_id:
#             flash('All fields are required!', 'error')
#             return render_template('Crud/add_comment.html', content=content, faculty_id=faculty_id, faculties=get_faculties())


#         current_semester = Semester.query.first()  
#         if current_semester is None:
#             flash('No current semester found. Please set the semester first.', 'error')
#             return redirect(url_for('add_comment'))

#         semester_number = current_semester.semester_number
#         school_year = current_semester.school_year


#         new_comment = Comment(
#             user_id=user_id, 
#             content=content,
#             faculty_id=faculty_id,
#             semester_number=semester_number,  
#             school_year=school_year  
#         )
#         try:
#             db.session.add(new_comment)  
#             db.session.commit()  
#             flash('Comment added successfully!', 'success')
#             return redirect(url_for('analys'))  
#         except Exception as e:
#             db.session.rollback()  
#             flash('An error occurred while adding the comment. Please try again.', 'error')
#             return render_template('Crud/add_comment.html', content=content, faculty_id=faculty_id, faculties=get_faculties())
#     return render_template('Crud/add_comment.html', faculties=get_faculties())




#  Upload Commnets usign excel file 

# @app.route('/upload_comments', methods=['POST'])
# def upload_comments():
#     if 'file' not in request.files:
#         flash('No file part', 'error')
#         return redirect(url_for('analys'))

#     file = request.files['file']

#     if file.filename == '':
#         flash('No selected file', 'error')
#         return redirect(url_for('analys'))

#     if file and file.filename.endswith('.xlsx'):
#         filename = secure_filename(file.filename)
#         file_path = os.path.join('uploads', filename) 
#         file.save(file_path)


#         df = pd.read_excel(file_path)

#         # Process each row and add to the database
#         for _, row in df.iterrows():
#             new_comment = Comment(
#                 user_id=row['user_id'], 
#                 content=row['content'],  
#                 faculty_id=row['faculty_id'],  
#                 semester_number=row['semester_number'],  # Add these as per your Excel structure
#                 school_year=row['school_year']
#             )
#             db.session.add(new_comment)

#         try:
#             db.session.commit()
#             flash('Comments added successfully!', 'success')
#         except Exception as e:
#             db.session.rollback()
#             flash('An error occurred while adding the comments.', 'error')

#         return redirect(url_for('analys'))

#     flash('Invalid file format. Please upload an Excel (.xlsx) file.', 'error')
#     return redirect(url_for('analys'))


# History 

# @app.route('/history')
# def history():
#     # history view logic here
#     return render_template('history.html')

# #   Loading  History 
# @app.route('/loading_history')
# def loading_history():
#     return redirect(url_for("loading_screen", target=url_for("history")))


# View Coments Sentiment Resutls Routes s
# @app.route('/semester_comments/<int:semester>/<string:year>')
# def semester_comments(semester, year):
#     if 'username' in session:
#         username = session['username']
#         page = request.args.get('page', 1, type=int)
#         filter_category = request.args.get('category')
#         filter_faculty = request.args.get('faculty')
#         filter_college = request.args.get('college')

#         faculties_with_comments = (
#             db.session.query(Faculty)
#             .join(Comment, Comment.faculty_id == Faculty.faculty_id)
#             .filter(Comment.semester_number == semester, Comment.school_year == year, Comment.status == 1)
#             .group_by(Faculty.faculty.faculty_id)
#             .all()
#         )

#         # Base query for comments
#         query = (
#             db.session.query(Comment, SentimentComment, Faculty.name.label('faculty_name'))
#             .join(SentimentComment, SentimentComment.comment_id == Comment.comment_id)
#             .join(Faculty, Comment.faculty_id == Faculty.faculty_id)
#             .filter(Comment.semester_number == semester, Comment.school_year == year, Comment.status == 1)
#         )

#         # Apply category filter based on selected value
#         if filter_category:
#             if filter_category == "Positive":
#                 query = query.filter(SentimentComment.category == 2)
#             elif filter_category == "Negative":
#                 query = query.filter(SentimentComment.category == 0)
#             elif filter_category == "Neutral":
#                 query = query.filter(SentimentComment.category == 1)

#         # Apply faculty name filter if provided
#         if filter_faculty:
#             query = query.filter(Faculty.name == filter_faculty)
#         if filter_college:
#             query = query.filter(Faculty.college == filter_college)

#         # Paginate the query
#         comments_data = query.paginate(page=page, per_page=5, error_out=False)

#         return render_template(
#             'Crud/semester_comments.html',
#             username=username,
#             comments_data=comments_data,
#             semester=semester,
#             year=year,
#             filter_category=filter_category,
#             filter_faculty=filter_faculty,
#             filter_college=filter_college,
#             all_faculty=faculties_with_comments
#         )

#     return redirect(url_for('loading_screen', target=url_for('login')))







@app.route('/comments', methods=['GET'])
def comments():
    if 'username' in session:
        username = session['username']
        page = request.args.get('page', 1, type=int)
        per_page = 6

        # Get selected filters from request args
        selected_semester = request.args.get('ay_id', None)
        selected_college = request.args.get('college_id', None)
        selected_department = request.args.get('department_id', None)

        # Default to the first available semester if not selected
        if not selected_semester:
            selected_semester = request.cookies.get('selectedSemester')
        if not selected_semester:
            # Get the latest semester if no semester is selected
            latest_semester = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).first()
            selected_semester = latest_semester.ay_id if latest_semester else None

        # Retrieve the name of the selected semester
        selected_semester_name = AY_SEM.query.filter_by(ay_id=selected_semester).first().ay_name if selected_semester else "N/A"

        # Query for comments and related data
        query = db.session.query(Comment, Faculty, AY_SEM, Department, College) \
            .join(Faculty, Comment.faculty_id == Faculty.faculty_id) \
            .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id) \
            .join(Department, Faculty.department_id == Department.department_id) \
            .join(College, Department.college_id == College.college_id) \
            .filter(Comment.category != 3)

        # Apply filters if provided
        if selected_semester:
            query = query.filter(Comment.ay_id == selected_semester)
        if selected_college:
            query = query.filter(Department.college_id == selected_college)
        if selected_department:
            query = query.filter(Faculty.department_id == selected_department)

        # Paginate the comments
        comments_pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Calculate pagination numbers
        max_pages_to_show = 10
        start_page = max(1, comments_pagination.page - 4)
        end_page = min(comments_pagination.pages, comments_pagination.page + 5)

        # Fetch colleges and departments for the dropdown
        colleges = College.query.all()
        selected_departments = Department.query.filter_by(college_id=selected_college).all() if selected_college else []

        return render_template(
            'comments.html',
            username=username,
            comments=comments_pagination.items,
            comments_pagination=comments_pagination,
            start_page=start_page,
            end_page=end_page,
            max_pages_to_show=max_pages_to_show,
            selected_semester=selected_semester,
            selected_semester_name=selected_semester_name,
            all_semesters=AY_SEM.query.all(),
            colleges=colleges,
            selected_college=selected_college,
            selected_department=selected_department,
            selected_departments=selected_departments
        )

    # Redirect to loading screen if user is not logged in
    return redirect(url_for('loading_screen', target=url_for('comments')))



#   Routes for comments with loading screen
@app.route('/loading_comments')
def loading_comments():
    return redirect(url_for("loading_screen", target=url_for("comments")))


# View Sentement_Commets 




@app.route('/view_sentiment_comment/<int:sentiment_comment_id>', methods=['GET'])
def view_sentiment_comment(sentiment_comment_id):
    if 'username' in session:
        comment_instance = (
            db.session.query(SentimentComment, Comment, Faculty.name)
            .join(Comment, SentimentComment.comment_id == Comment.comment_id)
            .join(Faculty, Comment.faculty_id == Faculty.faculty_id)
            .filter(SentimentComment.id == sentiment_comment_id)
            .first()
        )

        if comment_instance:
            sentiment_comment, comment, faculty_name = comment_instance
            return render_template('Crud/view_comment_sentiment.html', sentiment_comment=sentiment_comment, comment=comment, faculty_name=faculty_name)

        return "Comment not found", 404

    return redirect(url_for('loading_screen', target=url_for('login')))












#    Staff || Useer || Admin

@app.route('/users_account', methods=['GET'])
def account():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')  
        page = request.args.get('page', 1, type=int)  # Get the current page number, default to 1
        per_page = 5  # Number of records per page

        # Handle search functionality and filter by status = 1
        if search_query:
            user_members = Users.query.filter(
                (Users.status == 1) &
                ((Users.name.ilike(f'%{search_query}%')) | 
                 (Users.email.ilike(f'%{search_query}%')))
            ).paginate(page=page, per_page=per_page, error_out=False)
        else:
            user_members = Users.query.filter_by(status=1).paginate(page=page, per_page=per_page, error_out=False)

        return render_template('users_account.html', 
                               username=username, 
                               user_members=user_members.items,  # Items for the current page
                               pagination=user_members)  # Pagination object for navigation

    return redirect(url_for('loading_screen', target=url_for('login')))



#    view staff 
@app.route('/view_user/<int:user_id>', methods=['GET'])
def view_user(user_id):
    if 'username' in session:
        user = Users.query.get(user_id)  
        
        if user:
            return render_template('Crud/view_user.html', user=user)
        
        return "User not found", 404  

    return redirect(url_for('loading_screen', target=url_for('login')))


# get Departments 
@app.route('/get_departments', methods=['GET'])
def get_departments():
    college_id = request.args.get('college_id')
    departments = Department.query.filter_by(college_id=college_id).all()  # Adjust according to your models

    return jsonify({
        'departments': [
            {'department_id': dept.department_id, 'department_name': dept.department_name}
            for dept in departments
        ]
    })

#  Faculty 
@app.route('/faculty', methods=['GET'])
def faculty():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')  
        college_id = request.args.get('college')  
        department_id = request.args.get('department')  # Get selected department from the request
        page = request.args.get('page', '1')  

        if page.isdigit():
            page = int(page) 
        else:
            page = 1  

        query = Faculty.query

        if search_query:
            query = query.filter(
                (Faculty.lname.ilike(f'%{search_query}%')) |
                (Faculty.fname.ilike(f'%{search_query}%')) |
                (Faculty.email.ilike(f'%{search_query}%'))
            )

        if college_id:
            query = query.filter(Faculty.department.has(college_id=college_id))

        if department_id:
            query = query.filter(Faculty.department_id == department_id)  # Filter by department ID

        faculty_members = query.paginate(page=page, per_page=5, error_out=False)

        # Limit the number of pages to 10 for display
        total_pages = faculty_members.pages
        max_pages = 10
        start_page = max(1, page - max_pages // 2)  # Show a range of pages around the current page
        end_page = min(start_page + max_pages - 1, total_pages)

        colleges = College.query.all()
        departments = Department.query.filter_by(college_id=college_id).all() if college_id else []  # Fetch departments for the selected college

        return render_template('faculty.html', username=username, faculty_members=faculty_members, colleges=colleges, departments=departments, selected_college=college_id, start_page=start_page, end_page=end_page, total_pages=total_pages)

    return redirect(url_for('loading_screen', target=url_for('login')))
    


# View Faculty
@app.route('/faculty/view/<faculty_id>', methods=['GET'])  
def view_faculty(faculty_id):
    if 'username' in session:
        username = session['username']
        faculty_member = Faculty.query.get(faculty_id)  
        if faculty_member is None:
            flash('Faculty member not found!', 'error')
            return redirect(url_for('faculty'))

        return render_template('Crud/view_faculty.html', username=username, faculty=faculty_member)

    return redirect(url_for('loading_screen', target=url_for('login')))


# faculy resutls 

@app.route('/faculty/comments/<faculty_id>', methods=['GET'])
def faculty_comments(faculty_id):
    if 'username' in session:
        username = session['username']

        # Retrieve faculty member by ID and join with Department and College
        faculty_member = (
            db.session.query(Faculty)
            .join(Department)
            .join(College)
            .filter(Faculty.faculty_id == faculty_id)
            .first()
        )

        if faculty_member is None:
            flash('Faculty member not found!', 'error')
            return redirect(url_for('faculty'))

        # Get the college and department
        college = faculty_member.department.college
        department = faculty_member.department

        # Retrieve all semesters
        all_semesters = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).all()

        # Determine the default semester: URL parameter, cookie, or latest in the database
        selected_semester = (
            request.args.get('semester') or 
            request.cookies.get('selectedSemester') or 
            (all_semesters[0].ay_id if all_semesters else None)
        )
        default_semester_obj = AY_SEM.query.filter_by(ay_id=selected_semester).first()

        # Query comments specific to the selected faculty member for the selected semester
        comments_query = (
            db.session.query(Comment, AY_SEM, Subject)
            .filter(Comment.faculty_id == faculty_id)
            .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id)
            .join(Subject, Comment.subject_id == Subject.subject_id)
            .filter(Comment.category != 3)
            .filter(Comment.ay_id == selected_semester)
        )

        comments = [
            {"comment": comment, "ay_sem": ay_sem, "subject": subject} for comment, ay_sem, subject in comments_query.all()
        ]

        # Group comments by subject_id
        subjects = {}
        for item in comments:
            subject_id = item["comment"].subject_id
            if subject_id not in subjects:
                subjects[subject_id] = {
                    "subject_id": subject_id,
                    "comments": [],
                    "student_num": item["subject"].student_num
                }
            subjects[subject_id]["comments"].append(item["comment"])

        # Sentiment counts for the selected semester
        total_comments = comments_query.count()
        positive_count = comments_query.filter(Comment.category == 2).count()
        neutral_count = comments_query.filter(Comment.category == 1).count()
        negative_count = comments_query.filter(Comment.category == 0).count()

        # Sentiment counts for all semesters
        semester_sentiment_counts = {}
        for semester in all_semesters:
            sentiment_query = (
                db.session.query(Comment)
                .filter(Comment.faculty_id == faculty_id)
                .filter(Comment.ay_id == semester.ay_id)
                .filter(Comment.category != 3)
            )
            positive = sentiment_query.filter(Comment.category == 2).count()
            neutral = sentiment_query.filter(Comment.category == 1).count()
            negative = sentiment_query.filter(Comment.category == 0).count()

            semester_sentiment_counts[semester.ay_id] = {
                'semester_name': semester.ay_name,
                'positive': positive,
                'neutral': neutral,
                'negative': negative
            }

        # Render template
        return render_template(
            'Crud/faculty_comments.html',
            username=username,
            faculty=faculty_member,
            college=college,
            department=department,
            comments=comments,
            subjects=subjects,
            total_comments=total_comments,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            all_semesters=all_semesters,
            default_semester=default_semester_obj,
            semester_sentiment_counts=semester_sentiment_counts  # Pass sentiment counts for all semesters
        )

    return redirect(url_for('loading_screen', target=url_for('login')))



# Profile 

@app.route('/loading_profile')
def loading_profile():
    return redirect(url_for("loading_screen", target=url_for("profile")))

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
        
        # Fetch user data based on the user_id
        user = Users.query.get(user_id)
        
        # Pass the available data to the template
        return render_template('staff/profile.html', 
                               username=username,
                               email=user.email,
                               status="Active" if user.status == 1 else "Inactive",
                               password=user.password)
    return redirect(url_for('loading_screen', target=url_for('login')))


@app.route('/loading_edit_profile')
def loading_edit_profile():
    return redirect(url_for("loading_screen", target=url_for("edit_profile")))


#   Edit Profile
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' in session:
        user_id = session['user_id']
        user = Users.query.get(user_id)

        if request.method == 'POST':
            # Update user data with form inputs
            user.name = request.form['name']
            user.email = request.form['email']
            user.password = request.form['password']
            
            # Save changes to the database
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))

        return render_template('staff/edit_profile.html', 
                               name=user.name, 
                               email=user.email, 
                               password=user.password)
    return redirect(url_for('loading_screen', target=url_for('login')))



#   FQS
@app.route('/FQS')
def FQS():
    if 'username' in session:
        username = session['username']
        return render_template('FQS.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('FQS')))
