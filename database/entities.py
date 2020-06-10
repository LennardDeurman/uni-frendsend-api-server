'''

These are the database entities itself, which may possible inherit properties from the extension classes

'''

from database.extensions import ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails
from app.provider import db
from datetime import datetime

class User(db.Model, ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails):
    email = db.Column(db.String(100), unique=True, nullable=False)
    firebase_uid = db.Column(db.String(100), unique=True, nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    profile_image_url = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    bio = db.Column(db.String(300))
    phone = db.Column(db.String(10), unique=True, nullable=False)
    main_preference_mode = db.Column(db.Integer, nullable=False) #This is an int; in the manager class we need to check if it conforms to our enum PreferenceMode 



class Advertisement(db.Model, ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails):
    title = db.Column(db.String(20), nullable=False)
    details = db.Column(db.String(300), nullable=False)
    deadline = db.Column(db.DateTime)
    finished = db.Column(db.Boolean, nullable=False, default=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.server_id"))
    author = db.relationship("User", foreign_keys=author_id, lazy="joined")
    

class Category(db.Model, ObjectWithDefaultProps):
    name = db.Column(db.String(10), unique=True, nullable=False)
    color = db.Column(db.String(6), unique=True, nullable=False)

class Message(db.Model, ObjectWithDefaultProps):
    body = db.Column(db.String, nullable=False)

    receiver_id = db.Column(db.Integer, db.ForeignKey("user.server_id"))
    sender_id = db.Column(db.Integer, db.ForeignKey("user.server_id"))

    receiver = db.relationship("User", foreign_keys=receiver_id, lazy="joined")
    sender = db.relationship("User", foreign_keys=sender_id, lazy="joined")