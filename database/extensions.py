'''

These are the objects used as overriden classes or extensions, so that it can be used in multiple database entities without redefining. 

'''
from app.provider import db
from datetime import datetime

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
