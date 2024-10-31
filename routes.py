# Import
from flask import render_template, session, request, redirect, url_for, flash
from server import app,db
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from server import Users,Faculty,Comment,Semester,SentimentComment,Department,College,Subject,AY_SEM,Student
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd  # import for excel uploading 
import os # for uplading exxel file

# Load model and tokenizer
model_path = "./ai_model/twitter_xlm_roberta_fine_tuned_sentiment"
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()
tokenizer = AutoTokenizer.from_pretrained(model_path)



# Function to predict sentiment
def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    predicted_class = logits.argmax().item() 
    return predicted_class  


@app.route('/start_sentiment', methods=['POST'])
def start_sentiment():
    if 'username' not in session:
        return redirect(url_for('loading_screen', target=url_for('login')))

    # Fetch all comments
    comments = Comment.query.all()
    
    for comment in comments:
        # Predict sentiment for each comment
        sentiment = predict_sentiment(comment.comment)
        # Update the category based on the predicted sentiment
        comment.category = sentiment
    
    # Commit the changes to the database
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']  # Email is used as the username
        password = request.form['password']
    
        user = Users.query.filter_by(email=email).first()
        
        if user:
            if user.status == 1:  # Check if user is active
                if user.password == password:
                    session['username'] = user.name 
                    session['user_id'] = user.id  
                    return redirect(url_for("loading_screen", target=url_for("dashboard")))
                else:
                    flash("Invalid password!", "error")
            else:
               flash("Account is not authorized to access the admin page. Access is restricted to staff and admin only. Please contact support if you need assistance.", "error")

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

        # Assuming the Users model includes a 'status' field
        new_user = Users(name=username, email=email, password=password, status=status)
        
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('Auth/register.html')


@app.route('/register_page')
def register_page():
    return render_template('Auth/register.html')



#   Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('loading_screen', target=url_for('main')))



#   admin Page //  Staff Page


# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']

        total_comments = db.session.query(SentimentComment).join(Comment).count()
        positive_count = db.session.query(SentimentComment).join(Comment).filter(SentimentComment.category == 2).count()
        neutral_count = db.session.query(SentimentComment).join(Comment).filter(SentimentComment.category == 1).count()
        negative_count = db.session.query(SentimentComment).join(Comment).filter(SentimentComment.category == 0).count()
        colleges = College.query.all()
        semesters = AY_SEM.query.all()

        # Serialize departments by college
        departments_by_college = {
            college.college_id: [
                {'department_id': dept.department_id, 'department_name': dept.department_name}
                for dept in college.departments
            ]
            for college in colleges
        }

        # Fetch faculties grouped by department
        faculties_by_department = {
            department.department_id: [
                {'faculty_id': faculty.faculty_id, 'faculty_name': f'{faculty.lname} {faculty.fname}'}
                for faculty in department.faculties
            ]
            for college in colleges for department in college.departments
        }

        return render_template(
            'dashboard.html',
            username=username,
            total_comments=total_comments,
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            colleges=colleges,
            departments_by_college=departments_by_college,
            faculties_by_department=faculties_by_department,
            semesters=semesters
        )

    return redirect(url_for('loading_screen', target=url_for('login')))



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
        per_page = 5

        query = db.session.query(Comment, Faculty, AY_SEM)\
            .join(Faculty, Comment.faculty_id == Faculty.faculty_id)\
            .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id)\
            .filter(Comment.category == 4) 

        if search_query:
            query = query.filter(
                (Faculty.name.ilike(f'%{search_query}%')) | 
                (Comment.comment.ilike(f'%{search_query}%'))
            )

        # Apply pagination
        comments_pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return render_template('analys.html', 
                               username=username, 
                               comments=comments_pagination,  # Change here
                               pagination=comments_pagination)  # Add pagination
    return redirect(url_for('loading_screen', target=url_for('analys')))



# View Comments 
@app.route('/view_comment/<int:comment_id>', methods=['GET'])
def view_comment(comment_id):
    if 'username' in session:
        username = session['username']  # Capture username for future use if needed
        
        # Query for the specific comment and associated faculty name
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
@app.route('/add_comment', methods=['GET', 'POST'])
def add_comment():
    if request.method == 'POST':
        user_id = session.get('user_id')  
        
        if user_id is None:
            flash('User is not logged in!', 'error')
            return redirect(url_for('login')) 


        content = request.form.get('content')
        faculty_id = request.form.get('faculty_id')


        if not content or not faculty_id:
            flash('All fields are required!', 'error')
            return render_template('Crud/add_comment.html', content=content, faculty_id=faculty_id, faculties=get_faculties())


        current_semester = Semester.query.first()  
        if current_semester is None:
            flash('No current semester found. Please set the semester first.', 'error')
            return redirect(url_for('add_comment'))

        semester_number = current_semester.semester_number
        school_year = current_semester.school_year


        new_comment = Comment(
            user_id=user_id, 
            content=content,
            faculty_id=faculty_id,
            semester_number=semester_number,  
            school_year=school_year  
        )
        try:
            db.session.add(new_comment)  
            db.session.commit()  
            flash('Comment added successfully!', 'success')
            return redirect(url_for('analys'))  
        except Exception as e:
            db.session.rollback()  
            flash('An error occurred while adding the comment. Please try again.', 'error')
            return render_template('Crud/add_comment.html', content=content, faculty_id=faculty_id, faculties=get_faculties())
    return render_template('Crud/add_comment.html', faculties=get_faculties())




#  Upload Commnets usign excel file 

@app.route('/upload_comments', methods=['POST'])
def upload_comments():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('analys'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('analys'))

    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename) 
        file.save(file_path)


        df = pd.read_excel(file_path)

        # Process each row and add to the database
        for _, row in df.iterrows():
            new_comment = Comment(
                user_id=row['user_id'], 
                content=row['content'],  
                faculty_id=row['faculty_id'],  
                semester_number=row['semester_number'],  # Add these as per your Excel structure
                school_year=row['school_year']
            )
            db.session.add(new_comment)

        try:
            db.session.commit()
            flash('Comments added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the comments.', 'error')

        return redirect(url_for('analys'))

    flash('Invalid file format. Please upload an Excel (.xlsx) file.', 'error')
    return redirect(url_for('analys'))


# History 

@app.route('/history')
def history():
    if 'username' in session:
        username = session['username']

        history_data = (db.session.query(Comment.semester_number, Comment.school_year,
                                         db.func.count(SentimentComment.id).label('total_comments'),
                                         db.func.sum(db.case((SentimentComment.category == 2, 1), else_=0)).label('positive'),
                                         db.func.sum(db.case((SentimentComment.category == 0, 1), else_=0)).label('negative'),
                                         db.func.sum(db.case((SentimentComment.category == 1, 1), else_=0)).label('neutral'))
                        .join(SentimentComment, SentimentComment.comment_id == Comment.comment_id)
                        .join(Faculty, Faculty.faculty_id == Comment.faculty_id)  
                        .filter(Comment.status == 1)
                        .group_by(Comment.semester_number, Comment.school_year) 
                        
                        .order_by(Comment.semester_number.desc()))
                        

        return render_template('history.html', username=username, history_data=history_data)

    return redirect(url_for('loading_screen', target=url_for('login')))

#   Loading  History 
@app.route('/loading_history')
def loading_history():
    return redirect(url_for("loading_screen", target=url_for("history")))


# View Coments Sentiment Resutls Routes s
@app.route('/semester_comments/<int:semester>/<string:year>')
def semester_comments(semester, year):
    if 'username' in session:
        username = session['username']
        page = request.args.get('page', 1, type=int)
        filter_category = request.args.get('category')
        filter_faculty = request.args.get('faculty')
        filter_college = request.args.get('college')

        faculties_with_comments = (
            db.session.query(Faculty)
            .join(Comment, Comment.faculty_id == Faculty.faculty_id)
            .filter(Comment.semester_number == semester, Comment.school_year == year, Comment.status == 1)
            .group_by(Faculty.faculty.faculty_id)
            .all()
        )

        # Base query for comments
        query = (
            db.session.query(Comment, SentimentComment, Faculty.name.label('faculty_name'))
            .join(SentimentComment, SentimentComment.comment_id == Comment.comment_id)
            .join(Faculty, Comment.faculty_id == Faculty.faculty_id)
            .filter(Comment.semester_number == semester, Comment.school_year == year, Comment.status == 1)
        )

        # Apply category filter based on selected value
        if filter_category:
            if filter_category == "Positive":
                query = query.filter(SentimentComment.category == 2)
            elif filter_category == "Negative":
                query = query.filter(SentimentComment.category == 0)
            elif filter_category == "Neutral":
                query = query.filter(SentimentComment.category == 1)

        # Apply faculty name filter if provided
        if filter_faculty:
            query = query.filter(Faculty.name == filter_faculty)
        if filter_college:
            query = query.filter(Faculty.college == filter_college)

        # Paginate the query
        comments_data = query.paginate(page=page, per_page=5, error_out=False)

        return render_template(
            'Crud/semester_comments.html',
            username=username,
            comments_data=comments_data,
            semester=semester,
            year=year,
            filter_category=filter_category,
            filter_faculty=filter_faculty,
            filter_college=filter_college,
            all_faculty=faculties_with_comments
        )

    return redirect(url_for('loading_screen', target=url_for('login')))

#   Comments  || Sentiment Process
@app.route('/comments', methods=['GET'])
def comments():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 5

        
        query = db.session.query(Comment, Faculty, AY_SEM).join(Faculty, Comment.faculty_id == Faculty.faculty_id)\
        .join(AY_SEM, Comment.ay_id == AY_SEM.ay_id)\
        .filter(Comment.category != 0)

       
        if search_query:
            query = query.filter(
                (Faculty.name.ilike(f'%{search_query}%')) | 
                (Comment.comment.ilike(f'%{search_query}%'))
            )

       
        comments_pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        
        return render_template('comments.html', 
                        username=username, 
                        comments=comments_pagination.items,  
                        comments_pagination=comments_pagination,
                        search_query=search_query,  
                        filter_category=request.args.get('category', ''), 
                        filter_faculty=request.args.get('faculty', ''))

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




#  Faculty 
@app.route('/faculty', methods=['GET'])
def faculty():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')  
        page = request.args.get('page', '1')  

      
        if page.isdigit():
            page = int(page) 
        else:
            page = 1  
        query = Faculty.query

        if search_query:
            query = query.filter(
                (Faculty.name.ilike(f'%{search_query}%')) |
                (Faculty.email.ilike(f'%{search_query}%'))
            )
        faculty_members = query.paginate(page=page, per_page=5, error_out=False)

        return render_template('faculty.html', username=username, faculty_members=faculty_members)

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


# View Faculty Comments
@app.route('/faculty/comments/<faculty_id>', methods=['GET'])  
def faculty_comments(faculty_id):
    if 'username' in session:
        username = session['username']
        
        faculty_member = Faculty.query.get(faculty_id)  
        if faculty_member is None:
            flash('Faculty member not found!', 'error')
            return redirect(url_for('faculty'))

        page = request.args.get('page', 1, type=int)

        comments_query = (
            db.session.query(Comment, SentimentComment)
            .join(SentimentComment, Comment.comment_id == SentimentComment.comment_id)
            .filter(Comment.faculty_id == faculty_id)
        )
        
        sentiment_comments = comments_query.paginate(page=page, per_page=5)

        total_comments = sentiment_comments.total
        positive_comments = sum(1 for _, sentiment in sentiment_comments.items if sentiment.category == 2)
        negative_comments = sum(1 for _, sentiment in sentiment_comments.items if sentiment.category == 0)
        neutral_comments = sum(1 for _, sentiment in sentiment_comments.items if sentiment.category == 1)

        return render_template(
            'Crud/faculty_comments.html',
            username=username,
            faculty=faculty_member,
            comments=sentiment_comments.items,
            total_comments=total_comments,
            positive_comments=positive_comments,
            negative_comments=negative_comments,
            neutral_comments=neutral_comments,
            sentiment_comments=sentiment_comments
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
        return render_template('Users/profile.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('login')))

@app.route('/loading_edit_profile')
def loading_edit_profile():
    return redirect(url_for("loading_screen", target=url_for("edit_profile")))


#   Edit Profile
@app.route('/edit_profile')
def edit_profile():
    if 'username' in session:
        username = session['username']
        return render_template('Users/edit_profile.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('login')))

#   FQS
@app.route('/FQS')
def FQS():
    if 'username' in session:
        username = session['username']
        return render_template('FQS.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('FQS')))
