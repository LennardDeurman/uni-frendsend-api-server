from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

flask_app = Flask(__name__)
flask_app.debug = True
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(flask_app)

class ObjectWithDefaultProps:
    server_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class ObjectWithLocation:
    zip_code = db.Column(db.String(6), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False) 

class ObjectWithContactDetails:
    phone = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class PreferenceMode(Enum):
    OFFERING = 1
    SEEKING = 2

class User(db.Model, ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails):
    email = db.Column(db.String(100), unique=True, nullable=False)
    firebase_uid = db.Column(db.String(100), unique=True, nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    profile_image_url = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    bio = db.Column(db.String(300))
    phone = db.Column(db.String(10), unique=True, nullable=False)
    main_preference_mode = db.Column(db.Integer, nullable=False)

class Advertisement(db.Model, ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails):
    title = db.Column(db.String(20), nullable=False)
    details = db.Column(db.String(300), nullable=False)
    deadline = db.Column(db.DateTime)
    finished = db.Column(db.Boolean, nullable=False, default=False)

class Category(db.Model, ObjectWithDefaultProps):
    name = db.Column(db.String(10), unique=True, nullable=False)
    color = db.Column(db.String(6), unique=True, nullable=False)

class Message(db.Model, ObjectWithDefaultProps):
    body = db.Column(db.String, nullable=False)

flask_app.run()

