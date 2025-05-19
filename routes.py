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
from sqlalchemy import func, case,  desc
from wordcloud import WordCloud
from matplotlib import pyplot as plt
from io import BytesIO
import base64





# Load model and tokenizer
sentiment_pipeline = pipeline("sentiment-analysis", model="./ai_model/fine_tuned_twitter_xlm-roberta_model_bv2.3")


# text preprocess remove all unecesary before process ... .  
def preprocess_text(text):
    text = text.lower()
    text = emoji.replace_emoji(text, replace='')
    text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', text)
    text = " ".join(text.split())
    text = re.sub(r'\d+', '', text).strip()  
    return text



def predict_sentiment(text):
    """
    Predict sentiment using predefined mappings or the sentiment model.
    """
    # Check for predefined sentiment
    predefined_sentiment = get_predefined_sentiment(text)
    if predefined_sentiment is not None:
        return predefined_sentiment

    # Default: use the sentiment pipeline
    preprocessed_text = preprocess_text(text)
    inputs = sentiment_pipeline.tokenizer(
        preprocessed_text, return_tensors='pt', truncation=True, padding=True, max_length=512
    )
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
        comment.category = sentiment,
        comment.ai_old_result = sentiment 
    db.session.commit()

    flash('Sentiment analysis completed successfully.', 'success')
    return redirect(url_for('analys'))
    

@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if 'username' not in session:
        return redirect(url_for('loading_screen', target=url_for('login')))

    sentiment = None
    comment = None

    # Get semester from args or cookie
    selected_semester = request.args.get('ay_id') or request.cookies.get('selectedSemester')

    # Default to latest semester if none selected
    if not selected_semester:
        latest_semester = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).first()
        selected_semester = latest_semester.ay_id if latest_semester else None

    selected_semester_name = AY_SEM.query.filter_by(ay_id=selected_semester).first().ay_name if selected_semester else "N/A"

    if request.method == 'POST':
        comment = request.form.get('comment')
        if comment: 
            predicted_class = predict_sentiment(comment)
            sentiment = ['Negative', 'Neutral', 'Positive'][predicted_class]

    # Filter comments by semester
    base_query = Comment.query.filter(Comment.category != 3)
    if selected_semester:
        base_query = base_query.filter(Comment.ay_id == selected_semester)

    total_comments = base_query.count()
    total_revisions = base_query.filter(Comment.edit_status == 0).count()
    improvement_percentage = (total_revisions / total_comments) * 100 if total_comments > 0 else 0

    # Latest revision timestamp
    latest_revision = base_query.order_by(desc(Comment.updated_at)).first()
    latest_updated_at = latest_revision.updated_at.strftime('%B %d, %Y %I:%M %p') if latest_revision and latest_revision.updated_at else "No data"

    return render_template(
        'evaluate.html',
        username=session['username'],
        sentiment=sentiment,
        comment=comment,
        total_revisions=total_revisions,
        improvement_percentage=round(improvement_percentage, 2),
        latest_updated_at=latest_updated_at,
        selected_semester=selected_semester,
        selected_semester_name=selected_semester_name,
        all_semesters=AY_SEM.query.all()
    )







def get_predefined_sentiment(text):
    # Clean and normalize the input text
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)  
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    # Predefined sentiments with expanded common phrases
    specific_sentiments = {
        # Positive comments
        "thanks": 2,
        "thank you": 2,
        "thankyou": 2,
        "i appreciate it": 2,
        "good job": 2,
        "well done": 2,
        "salamat": 2,
        "i love you": 2,
        "mahal kita": 2,
        "ayos ka": 2,
        "galing mo": 2,
        "galing": 2,
        "very good": 2,
        "very good sir": 2,
        "very good maam": 2,
        "i like you": 2,
        "i like you maam": 2,
        "i like you sir": 2,
        
        # Neutral comments
        "ayos lang": 1,
        "okay lang": 1,
        "fine": 1,
        "noted": 1,
        "sure": 1,
        "sige": 1,
        "ok": 1,
        "wala lang": 1,
        
        # Negative comments
        "tanga": 0,
        "yawa ka": 0,
        "yawa ka maam": 0,
        "bobo ka": 0,
        "bugo ka": 0,
        "pangit ka": 0,
        "i hate you": 0,
        "walang kwenta": 0,
        "basura ka": 0,
        "walang kwenta ka": 0,
        "inutil ka": 0,
        "mahina ka": 0,
    }

    # Check if the cleaned text matches predefined sentiments
    sentiment = specific_sentiments.get(cleaned_text.lower(), None)
    if sentiment is not None:
        return sentiment

    # Additional feature: Check length and positive words
    positive_words = ["very good", "nice","good job" , "excellent", "awesome"]
    # Check if the text length is 15 and contains any of the positive words
    if len(cleaned_text) <= 10 and any(word in cleaned_text.lower() for word in positive_words):
        return 2  # Positive sentiment
    
    return None  # Default to None if no match



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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']  
        password = request.form['password']
    
        user = Users.query.filter_by(email=email).first()
        
        if user:
            if user.status == 1:  # Check if user is active
                if check_password_hash(user.password, password):  # Compare hashed password
                    session['username'] = user.lname + " " + user.fname
                    session['user_id'] = user.id
                    return redirect(url_for("loading_screen", target=url_for("dashboard")))
                else:
                    flash("Invalid password!", "error")
            else:
                flash("Account is not authorized to access the admin page.ssh Access is restricted to staff and admin only. Please contact support if you need assistance.", "error")
        else:
            flash("Email not found!", "error")

        return redirect(url_for("login"))

    return render_template('Auth/login.html')


#Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        lname = request.form['lname']  # Last Name
        fname = request.form['fname']  # First Name
        password = request.form['password']
        confpassword = request.form['confpassword']
        status = 1

        if password != confpassword:  
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))

        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Email address already exists!", "error")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new user with first name and last name
        new_user = Users(lname=lname, fname=fname, email=email, password=hashed_password, status=status)
        
        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.fname
        session['user_id'] = new_user.id

        flash("Registration successful!", "success")
        return redirect(url_for('dashboard'))  # Redirect to dashboard

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

        if not selected_ay_id:
            last_semester = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).first()
            if last_semester:
                selected_ay_id = last_semester.ay_id  

        # Call the function to generate the word cloud image, passing the selected filters
        wordcloud_data = generate_wordcloud(selected_ay_id, selected_college_id, selected_department_id)

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
            .group_by(AY_SEM.ay_id, AY_SEM.ay_name) 
            .order_by(AY_SEM.ay_id.desc())   
            .limit(5)           
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
            selected_semester_name=selected_semester_name 
           # Pass the semester name to the template
           
        )

    return redirect(url_for('login'))


def generate_wordcloud(selected_ay_id=None, selected_college_id=None, selected_department_id=None):

    query = db.session.query(Comment).filter(Comment.category != 3)  

    if selected_ay_id:
        query = query.filter(Comment.ay_id == selected_ay_id)

    if selected_college_id:
        query = query.join(Faculty).join(Department).join(College).filter(College.college_id == selected_college_id)

    if selected_department_id:
        query = query.filter(Department.department_id == selected_department_id)

    comments = query.all()

    text = " ".join([comment.comment for comment in comments])
    text = text.replace("Ma'am", "").replace("Sir", "")  

    if not text.strip():
        return "No Data"  

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

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
    semesters = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).limit(6).all()

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

#model Perforamance







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





@app.route('/comments', methods=['GET'])
def comments():
    if 'username' not in session:
        return redirect(url_for('loading_screen', target=url_for('comments')))

    username = session['username']
    page = request.args.get('page', 1, type=int)
    per_page = 6

    selected_semester = request.args.get('ay_id') or request.cookies.get('selectedSemester')
    selected_college = request.args.get('college_id')
    selected_department = request.args.get('department_id')
    selected_origin = request.args.get('origin')  # 'revision' or 'ai'

    if not selected_semester:
        latest_semester = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).first()
        selected_semester = latest_semester.ay_id if latest_semester else None

    selected_semester_name = AY_SEM.query.filter_by(ay_id=selected_semester).first().ay_name if selected_semester else "N/A"

    # Base query
    query = db.session.query(Comment, Faculty, AY_SEM, Department, College) \
        .join(Faculty, Comment.faculty_id == Faculty.faculty_id) \
        .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id) \
        .join(Department, Faculty.department_id == Department.department_id) \
        .join(College, Department.college_id == College.college_id) \
        .filter(Comment.category != 3)

    # Filters
    if selected_semester:
        query = query.filter(Comment.ay_id == selected_semester)
    if selected_college:
        query = query.filter(Department.college_id == selected_college)
    if selected_department:
        query = query.filter(Faculty.department_id == selected_department)

    # 💡 New logic using edit_status
    if selected_origin == "revision":
        query = query.filter(Comment.edit_status == 0)
    elif selected_origin == "ai":
        query = query.filter(Comment.edit_status == 1)

    comments_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    start_page = max(1, comments_pagination.page - 4)
    end_page = min(comments_pagination.pages, comments_pagination.page + 5)

    colleges = College.query.all()
    selected_departments = Department.query.filter_by(college_id=selected_college).all() if selected_college else []
    revision_count = query.filter(Comment.edit_status == 0).count()
    ai_count = query.filter(Comment.edit_status == 1).count()
    return render_template(
        'comments.html',
        username=username,
        comments=comments_pagination.items,
        comments_pagination=comments_pagination,
        start_page=start_page,
        end_page=end_page,
        max_pages_to_show=10,
        selected_semester=selected_semester,
        selected_semester_name=selected_semester_name,
        all_semesters=AY_SEM.query.all(),
        colleges=colleges,
        selected_college=selected_college,
        selected_department=selected_department,
        selected_departments=selected_departments,
        selected_origin=selected_origin,
        revision_count=revision_count,
        ai_count=ai_count,

    )


#   Routes for comments with loading screen
@app.route('/loading_comments')
def loading_comments():
    return redirect(url_for("loading_screen", target=url_for("comments")))



@app.route('/comments/edit/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    if 'username' in session:
        comment = Comment.query.get_or_404(comment_id)

        if request.method == 'POST':
            new_result = request.form.get('edit_result')

            if new_result is not None:
                new_result = int(new_result)

                # Save current category to ai_old_result only on first edit
                if comment.edit_status == 1:
                    comment.ai_old_result = comment.category

                # Always update category to new selection
                comment.category = new_result

                # If same as AI result, it's like no change
                if new_result == comment.ai_old_result:
                    comment.edit_status = 1  # not changed
                else:
                    comment.edit_status = 0  # changed by staff

                db.session.commit()
                flash('Comment result updated successfully!', 'success')
                return redirect(url_for('comments'))

        return render_template('Crud/edit_category.html', comment=comment)

    return redirect(url_for('loading_screen', target=url_for('comments')))




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

        college = faculty_member.department.college
        department = faculty_member.department

        all_semesters = AY_SEM.query.order_by(AY_SEM.ay_id.desc()).all()

        selected_semester = (
            request.args.get('semester') or 
            request.cookies.get('selectedSemester') or 
            (all_semesters[0].ay_id if all_semesters else None)
        )
        default_semester_obj = AY_SEM.query.filter_by(ay_id=selected_semester).first()

        # Pagination Setup
        page = request.args.get('page', 1, type=int)
        per_page = 15

        comments_query = (
            db.session.query(Comment, AY_SEM, Subject)
            .filter(Comment.faculty_id == faculty_id)
            .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id)
            .join(Subject, Comment.subject_id == Subject.subject_id)
            .filter(Comment.category != 3)
            .filter(Comment.ay_id == selected_semester)
        )

        # Apply Pagination
        paginated_comments = comments_query.paginate(page=page, per_page=per_page, error_out=False)

        comments = [
            {"comment": comment, "ay_sem": ay_sem, "subject": subject}
            for comment, ay_sem, subject in paginated_comments.items
        ]

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

        total_comments = comments_query.count()
        positive_count = comments_query.filter(Comment.category == 2).count()
        neutral_count = comments_query.filter(Comment.category == 1).count()
        negative_count = comments_query.filter(Comment.category == 0).count()

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

        return render_template(
            'print/faculty_comments.html',
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
            semester_sentiment_counts=semester_sentiment_counts,
            paginated_comments=paginated_comments  # Pass pagination object
        )

    return redirect(url_for('loading_screen', target=url_for('login')))



# Profile 

@app.route('/loading_profile')
def loading_profile():
    return redirect(url_for("loading_screen", target=url_for("profile")))

@app.route('/profile')
def profile():
    if 'username' in session:
       
        user_id = session['user_id']
        
        # Fetch user data based on the user_id
        user = Users.query.get(user_id)
        
        # Pass the available data to the template
        return render_template('staff/profile.html', 
                               lname=user.lname,
                               fname=user.fname,
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
            user.lname = request.form['lname']
            user.fname = request.form['fname']
            user.email = request.form['email']
            
            
            # Save changes to the database
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile'))

        return render_template('staff/edit_profile.html', 
                               lname=user.lname, 
                               fname=user.fname, 
                               email=user.email, 
        )
    return redirect(url_for('loading_screen', target=url_for('login')))



#   FQS
@app.route('/FQS')
def FQS():
    if 'username' in session:
        username = session['username']
        return render_template('staff/FQS.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('FQS')))

# Settings
@app.route('/Setting')
def Setting():
    if 'username' in session:
        username = session['username']
        return render_template('staff/Data_manupulate/settings.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('FQS')))




@app.route('/new_comment_count', methods=['GET'])
def new_comment_count():
   
    count = db.session.query(Comment).filter(Comment.category == 3).count()
    return str(count)







