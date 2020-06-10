from app.provider import flask_app, db
from database.entities import *
db.drop_all()
db.create_all()
print("db reset")