from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, PasswordField
from wtforms.validators import InputRequired
from sqlalchemy.orm import relationship


db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)
    app.app_context().push()





class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(50), unique = True, nullable = False)
    first_name = db.Column(db.String(30), nullable= False)
    last_name = db.Column(db.String(30), nullable = False)
    # need to reload models for below to work 
    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        # return instance of User w/username and hashed pwd
        # using cls since it's a class method, but you are in fact making a new User
        # just like self is passed into an instance method, cls passed into a Class method
        return cls(username=username, password=hashed_utf8, email=email, first_name = first_name, last_name = last_name)
    # end_register
    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.
        Return user if valid; else return False.
        """
        # .first() is best since if it returns none it doesn't break the app like .one() would
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance if u is True and checkpwd is True 
            return u
        else:
            return False
    # end_authenticate        


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(50), ForeignKey('users.username'), nullable=False)
    # user = relationship('User', back_populates='feedback')
    # user = db.relationship('User', backref = "feedback")


