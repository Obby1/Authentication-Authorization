from app import app
from models import db, User, Feedback

db.drop_all()
db.create_all()

u1 = User(
    username = "obbydel",
    password="123",
    email="obby@obby.com",
    first_name = "obby",
    last_name = "del"
)

db.session.add(u1)
db.session.commit()


f1 = Feedback(
    title = "testtitle",
    content = "testcontent",
    username = "obbydel",
)

db.session.add(f1)
db.session.commit()

# class Feedback(db.Model):
#     __tablename__ = 'feedback'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     username = db.Column(db.String(50), ForeignKey('users.username'), nullable=False)
#     # user = relationship('User', back_populates='feedback')
#     user = db.relationship('User', backref = "feedback")
