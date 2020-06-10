from flask import Flask
from flask_sqlalchemy import SQLAlchemy

flask_app = Flask(__name__)
flask_app.debug = True
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(flask_app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    firebaseUid = db.Column(db.String(100), unique=True, nullable=False)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    profileImgUrl = db.Column(db.String(100), nullable=False) #add default?
    dateOfBirth = db.Column(db.DateTime, nullable=False)
    bio = db.Column(db.String(300))
    zip = db.Column(db.String(6), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False) #unique?
    phone = db.Column(db.String(10), unique=True, nullable=False)
    isVolunteer = db.Column(db.Boolean, nullable=False, default=False)


categories = db.Table('categories',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('advertisement_id', db.Integer, db.ForeignKey('advertisement.id'), primary_key=True)
)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    details = db.Column(db.String(300), nullable=False)
    deadline = db.Column(db.DateTime)
    zip = db.Column(db.String(6), nullable=False) #default user.zip?
    coordinates = db.Column(db.String(100), nullable=False) #default user?
    phone = db.Column(db.String(10), unique=True, nullable=False) #default user?
    isChecked = db.Column(db.Boolean, nullable=False, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    color = db.Column(db.String(6), unique=True, nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(30), nullable=False)
    sendDate = db.Column(db.DateTime, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

flask_app.run()

