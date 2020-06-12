from app.provider import flask_app, db
from database.entities import *


'''

Use this file to recreate the database. What it does:

1. Drops all the existing data
2. Recreates based on the structure in entities

To use this call it inside your virtualenv in command prompt in the root dir server 
python reset_database.py 


'''


db.drop_all()
db.create_all()
print("db reset")