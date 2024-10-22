from flask import render_template, session, request, redirect, url_for, flash
from server import app,db
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from server import Users,Faculty,Comment,Semester  # Make sure to import the Users model
from werkzeug.security import generate_password_hash, check_password_hash


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
    sentiment_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    return sentiment_map.get(predicted_class, "Unknown")


@app.route('/loading_screen')
def loading_screen():
    # This route shows the loading screen, then redirects
    target = request.args.get("target")
    return render_template("loading.html", redirect_url=target)


@app.route('/')
def main():
    return redirect(url_for("loading_screen", target=url_for("main_page")))

@app.route('/main')
def main_page():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']  # Email is used as the username
        password = request.form['password']
        
        # Check if the user exists in the database
        user = Users.query.filter_by(email=email).first()
        if user:
            # Check if the password matches
            if user.password == password:  # Direct comparison
                session['username'] = user.name  # Store username in session
                return redirect(url_for("loading_screen", target=url_for("dashboard")))
            else:
                flash("Invalid password!", "error")  # Password is incorrect
        else:
            flash("Email not found!", "error")  # Email is not registered

        return redirect(url_for("login"))  # Redirect back to login

    return render_template('Auth/login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('loading_screen', target=url_for('login')))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confpassword = request.form['confpassword']
        
        # Check if passwords match
        if password != confpassword:  
            flash("Passwords do not match!", "error")
            return redirect(url_for('register_page'))

        # Check if the user already exists
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Email address already exists!", "error")
            return redirect(url_for('register_page'))

        # Create a new user without hashing the password
        new_user = Users(name=username, email=email, password=password)
        
        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('Auth/register.html')






@app.route('/register_page')
def register_page():
    return render_template('Auth/register.html')

# Other routes similarly wrapped with the loading screen
@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if 'username' in session:
        sentiment = None
        if request.method == 'POST':
            comment = request.form.get('comment')
            if comment:
                sentiment = predict_sentiment(comment)
        return render_template('evaluate.html', username=session['username'], sentiment=sentiment)
    return redirect(url_for('loading_screen', target=url_for('login')))


@app.route('/loading_dashboard')
def loading_dashboard():
    return redirect(url_for("loading_screen", target=url_for("dashboard")))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('login')))


# Routes for history with loading screen
@app.route('/loading_history')
def loading_history():
    return redirect(url_for("loading_screen", target=url_for("history")))

@app.route('/history')
def history():
    if 'username' in session:
        username = session['username']
        return render_template('history.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('login')))


# Routes for comments with loading screen
@app.route('/loading_comments')
def loading_comments():
    return redirect(url_for("loading_screen", target=url_for("comments")))

@app.route('/comments')
def comments():
    if 'username' in session:
        username = session['username']
        return render_template('comments.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('login')))


# Routes for user account with loading screen
@app.route('/loading_users_account')
def loading_users_account():
    return redirect(url_for("loading_screen", target=url_for("account")))


# Routes for profile with loading screen
@app.route('/loading_profile')
def loading_profile():
    return redirect(url_for("loading_screen", target=url_for("profile")))

@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        return render_template('Users/profile.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('login')))


# Routes for edit profile with loading screen
@app.route('/loading_edit_profile')
def loading_edit_profile():
    return redirect(url_for("loading_screen", target=url_for("edit_profile")))

@app.route('/edit_profile')
def edit_profile():
    if 'username' in session:
        username = session['username']
        return render_template('Users/edit_profile.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('login')))


@app.route('/FQS')
def FQS():
    if 'username' in session:
        username = session['username']
        return render_template('FQS.html', username=username)
    return redirect(url_for('loading_screen', target=url_for('FQS')))


@app.route('/analys', methods=['GET'])
def analys():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')

        if search_query:
            comments = db.session.query(Comment, Faculty).join(Faculty, Comment.faculty_id == Faculty.id)\
                .filter(
                    (Faculty.name.ilike(f'%{search_query}%')) | 
                    (Comment.content.ilike(f'%{search_query}%'))
                ).all()  # Search by faculty name or comment content
        else:
            comments = db.session.query(Comment, Faculty).join(Faculty, Comment.faculty_id == Faculty.id).all()  # Get all comments

        return render_template('analys.html', username=username, comments=comments)

    return redirect(url_for('loading_screen', target=url_for('analys')))




@app.route('/users_account', methods=['GET'])
def account():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')  
        if search_query:
                user_members = Users.query.filter(
                    (Users.name.ilike(f'%{search_query}%')) | 
                    (Users.email.ilike(f'%{search_query}%'))
                ).all()     
        else:
                user_members = Users.query.all()  # Get all faculty members if no search query

        return render_template('users_account.html', username=username, user_members=user_members)

    return redirect(url_for('loading_screen', target=url_for('login')))




@app.route('/faculty', methods=['GET'])
def faculty():
    if 'username' in session:
        username = session['username']
        search_query = request.args.get('search', '')  # Get the search query from the URL

        # Fetch faculty members based on the search query
        if search_query:
            faculty_members = Faculty.query.filter(
                (Faculty.name.ilike(f'%{search_query}%')) | 
                (Faculty.email.ilike(f'%{search_query}%'))
            ).all()
        else:
            faculty_members = Faculty.query.all()  # Get all faculty members if no search query

        return render_template('faculty.html', username=username, faculty_members=faculty_members)

    return redirect(url_for('loading_screen', target=url_for('login')))


# Crud Faculty 

@app.route('/faculty/add', methods=['GET', 'POST'])
def add_faculty():
    if 'username' in session:
        username = session['username']
        
        if request.method == 'POST':
            name = request.form['name']
            department = request.form['department']
            college = request.form['college']
            gender = request.form['gender']
            birthdate = request.form['birthdate']  # Optional, can be None
            email = request.form['email']
            password = request.form['password']
            confpassword = request.form['confpassword']
            
            # Check if passwords match
            if password != confpassword:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('add_faculty'))

            # Create a new Faculty instance
            new_faculty = Faculty(
                name=name, 
                department=department, 
                college=college, 
                gender=gender, 
                birthdate=birthdate,  # This can be None if not provided
                email=email, 
                password=password
            )
            
            # Add the new faculty member to the database
            db.session.add(new_faculty)
            db.session.commit()
            
            return redirect(url_for('faculty'))  # Redirect to the faculty page after adding
        
        return render_template('Crud/add_faculty.html', username=username)  

    return redirect(url_for('loading_screen', target=url_for('login')))

@app.route('/faculty/view/<int:id>', methods=['GET'])
def view_faculty(id):
    if 'username' in session:
        username = session['username']
        
        # Fetch the faculty member from the database
        faculty_member = Faculty.query.get(id)
        
        if faculty_member is None:
            flash('Faculty member not found!', 'error')
            return redirect(url_for('faculty'))

        return render_template('Crud/view_faculty.html', username=username, faculty=faculty_member)

    return redirect(url_for('loading_screen', target=url_for('login')))

@app.route('/faculty/update/<int:id>', methods=['GET', 'POST'])
def update_faculty(id):
    if 'username' in session:
        username = session['username']
        faculty_member = Faculty.query.get(id)

        if faculty_member is None:
            flash('Faculty member not found!', 'error')
            return redirect(url_for('faculty'))

        if request.method == 'POST':
            faculty_member.name = request.form['name']
            faculty_member.department = request.form['department']
            faculty_member.college = request.form['college']
            faculty_member.gender = request.form['gender']
            faculty_member.birthdate = request.form['birthdate']  # Optional
            faculty_member.email = request.form['email']
            password = request.form['password']
            confpassword = request.form['confpassword']

            # Check if passwords match
            if password != confpassword:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('update_faculty', id=id))

            # Update the password if it's provided
            if password:
                faculty_member.password = password
            
            db.session.commit()
            return redirect(url_for('faculty'))  # Redirect to the faculty page after updating

        return render_template('Crud/update_faculty.html', username=username, faculty=faculty_member)

    return redirect(url_for('loading_screen', target=url_for('login')))


# delete Faculty 

@app.route('/faculty/delete/<int:id>', methods=['POST'])
def delete_faculty(id):
    if 'username' in session:
        faculty_member = Faculty.query.get(id)  # Get the faculty member by ID
        if faculty_member:
            db.session.delete(faculty_member)  # Delete the faculty member
            db.session.commit()  # Commit the changes
            flash('Faculty member deleted successfully.', 'success')  # Flash a success message
        else:
            flash('Faculty member not found.', 'error')  # Flash an error message if not found
        return redirect(url_for('faculty'))  # Redirect to the faculty page

    return redirect(url_for('loading_screen', target=url_for('login')))



# view users 


@app.route('/view_user/<int:user_id>', methods=['GET'])
def view_user(user_id):
    if 'username' in session:
        user = Users.query.get(user_id)  # Get user by ID
        
        if user:
            return render_template('Crud/view_user.html', user=user)
        
        return "User not found", 404  # Handle case where user doesn't exist

    return redirect(url_for('loading_screen', target=url_for('login')))


# Delete Users account 

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' in session:
        user = Users.query.get(user_id)  # Get the user by ID
        
        if user:
            db.session.delete(user)  # Delete the user
            db.session.commit()  # Commit the changes
            flash('User deleted successfully!', 'success')
        else:
            flash('User not found.', 'error')
        
        return redirect(url_for('account'))

    return redirect(url_for('loading_screen', target=url_for('login')))

# Route to update a user
@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if 'username' in session:
        user = Users.query.get(user_id)  # Get user by ID
        
        if request.method == 'POST':
            # Update user details
            user.name = request.form['name']
            user.email = request.form['email']
            # You may want to handle the password and other fields accordingly
            # user.password = request.form['password']  # Uncomment if you allow password change

            db.session.commit()  # Save changes
            return redirect(url_for('account'))  # Redirect to the user accounts page
        
        if user:
            return render_template('Crud/update_user.html', user=user)  # Render form for updating user
        
        return "User not found", 404  # Handle case where user doesn't exist

    return redirect(url_for('loading_screen', target=url_for('login')))


# view Comments Details 
@app.route('/view_comment/<int:comment_id>', methods=['GET'])
def view_comment(comment_id):
    if 'username' in session:
        # Perform an inner join between Comment and Faculty
        comment_instance = (
            db.session.query(Comment, Faculty.name)
            .join(Faculty, Comment.faculty_id == Faculty.id)
            .filter(Comment.comment_id == comment_id)
            .first()
        )

        if comment_instance:
            comment, faculty_name = comment_instance
            return render_template('Crud/view_comment.html', comment=comment, faculty_name=faculty_name)

        return "Comment not found", 404  # Handle case where the comment doesn't exist

    return redirect(url_for('loading_screen', target=url_for('login')))




# Semester 
# Route to view the default semester
@app.route('/semester')
def semester():
    if 'username' in session:
        username = session['username']
        
        # Fetch the default semester from the database
        default_semester = Semester.query.first()  # Adjust this query as needed
        
        return render_template('semester.html', username=username, default_semester=default_semester)
    
    return redirect(url_for('loading_screen', target=url_for('semester')))

# Route to edit the default semester
@app.route('/edit_semester', methods=['GET', 'POST'])
def edit_semester():
    if 'username' in session:
        username = session['username']
        
        # Fetch the current default semester
        default_semester = Semester.query.first()  # Adjust the query as needed
        
        if request.method == 'POST':
            # Handle the form submission to edit the semester
            semester_number = request.form.get('semester_number')
            school_year = request.form.get('school_year')
            
            # Update the semester details
            default_semester.semester_number = semester_number
            default_semester.school_year = school_year
            
            # Commit changes to the database
            db.session.commit()
            
            # Redirect back to the semester page
            return redirect(url_for('semester'))
        
        # Render the edit semester page with the current default semester details
        return render_template('Crud/edit_semester.html', username=username, default_semester=default_semester)
    
    return redirect(url_for('loading_screen', target=url_for('edit_semester')))
