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

    posts = db.relationship('Advertisement', backref='author', lazy=True)
    #responds relationship necessary?
    sends = db.relationship('Message', backref='sender', lazy=True)
    receives = db.relationship('Message', backref='receiver', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.firstName}', '{self.lastName}', '{self.profileImgUrl}', '{self.dateOfBirth}', '{self.bio}','{self.zip}', '{self.phone}', '{self.isVolunteer}')" #no firebaseUid and coordinates

#helper table for categories relationship in advertisement
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
    
    #categories 'attribute' as many-to-many relationship
    categories = db.relationship('Category', secondary=categories, lazy='subquery', backref=db.backref('advertisements', lazy=True))
    
    def __repr__(self):
        return f"Advertisement('{self.title}', '{self.details}', '{self.deadline}', '{self.zip}', '{self.phone}', '{self.isChecked})" #no coordinates


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    color = db.Column(db.String(6), unique=True, nullable=False)

    def __repr__(self):
        return f"Category('{self.name}', '{self.color}')"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(30), nullable=False)
    sendDate = db.Column(db.DateTime, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@flask_app.route("/test")
def get_test():
    return "test2!"

flask_app.run()

