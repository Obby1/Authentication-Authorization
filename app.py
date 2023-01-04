from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
# new
# from flask_login import login_manager
# from forms import UserForm, TweetForm 
# to catch error, need to import it
# from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_ex_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# def create_app():
#     app = Flask(__name__)
#     ...
#     login_manager = LoginManager()
#     login_manager.init_app(app)
#     ...
#     return app


toolbar = DebugToolbarExtension(app)

##### connect & initialize DB ####
connect_db(app)


with app.app_context():
    db.create_all()
####################################
# new


@app.route('/')
def homepage():
    if "user_id" not in session:
        flash('Please login first!', 'danger')
        return redirect('/register')
    user_id = session['user_id']    
    user = User.query.get_or_404(user_id)
    username = user.username
    return redirect(f'/users/{username}')


@app.route('/register', methods = ["GET", "POST"])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        # if username is taken it may fail, would need error handling for that
        # would probably want to re-render the sign up form with flashed error msg username taken
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            # good to specify error like if checking if duplicate email etc
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('register.html', form = form)
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', 'success')
        # return redirect('/secret')
        return redirect(f'/users/{new_user.username}')
    
    return render_template('register.html', form = form)

# @app.route('/secret', methods = ["GET"])
# def secret():
#     if "user_id" not in session:
#         flash('Please login first!', 'danger')
#         return redirect ('/')
#     return render_template('secret.html')




@app.route('/login', methods=["GET", "POST"])
def login():
    # may want different forms if you want to collec diff info from log in user vs register user
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            # errors html logic already in form 
            form.username.errors = ['Invalid username/password.']
    return render_template('login.html', form=form)

# add error handling for logging out route if already logged out 
@app.route('/logout', methods = ["POST"])
def logout_user():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    username = user.username
    session.pop('user_id')
    session.pop('username')
    flash(f'Goodbye {username}!', 'info')
    return redirect('/')

@app.route('/users/<username>', methods = ["GET"])
def user_page(username):
    if "user_id" not in session:
        flash('Please login first!', 'danger')
        return redirect ('/login')
    user_id = session['user_id']    
    user = User.query.get_or_404(user_id)
    form = DeleteForm()
    # feedbacks = User.feedback.query.all()
    # above not working, may need to do a join query later to optimize below
    feedbacks = Feedback.query.all()
    return render_template('userpage.html', user=user, form=form)

@app.route('/profile')
def profile():
    user_id = session['user_id']    
    user = User.query.get_or_404(user_id)
    username = user.username
    return redirect(f'/users/{username}')


# class Feedback(db.Model):
#     __tablename__ = 'feedback'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     username = db.Column(db.String(50), ForeignKey('users.username'), nullable=False)
#     # user = relationship('User', back_populates='feedback')
#     user = db.relationship('User', backref = "feedback")


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def feedback_from(username):
    if "user_id" not in session:
        flash('Please login first!', 'danger')
        return redirect ('/login')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title = title, content = content, 
        username = session['username'])
        db.session.add(new_feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(f'/users/{username}')
    return render_template('feedback.html', form = form)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("update.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")

@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user and redirect to login."""
    # test Unauthorized 
    if "username" not in session or username != session['username']:
        raise Unauthorized()
    # user = User.query.get(username)
    user_id = session['user_id']    
    user = User.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    session.pop('user_id')
    flash(f'Goodbye {username}!', 'info')

    return redirect("/login")



# # add edit button that brings user to here
# @app.route('/users/<int:feedbackid>/update', methods = ["GET", "PATCH"])
# def update_feedback(feedbackid):
#     if "user_id" not in session:
#         flash('Please login first!', 'danger')
#         return redirect ('/login')
#     username = session['username']
#     form = FeedbackForm()
#     if form.validate_on_submit():
#         id = feedbackid
#         title = form.title.data
#         content = form.content.data
#         old_feedback = Feedback(id = id, title = title, content = content, 
#         username = session['username'])
#         db.session.patch(old_feedback)
#         db.session.commit()
#         return redirect(f'/users/{username}')
#     return render_template('update.html', form = form)


# todo:
# study how to add profile page to nav bar using modern flask syntax
# <nav>
#   <ul>
#     <li><a href="{{ url_for('home') }}">Home</a></li>
#     <li><a href="{{ url_for('user_profile', username=current_user.username) }}">Profile</a></li>
#   </ul>
# </nav>
# from flask_login import login_manager
# ...
# login_manager.init_app(app)
# the way you're doing it now seems hacky
