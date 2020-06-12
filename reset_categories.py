from app.provider import flask_app, db
from database.entities import Category

'''

Use this file to create the categories. What it does:

1. First it deletes all the existing categories
2. Then it creates the categories that are defined by the add functions

To use this call it inside your virtualenv in command prompt in the root dir server 
python reset_categories.py 


'''


db.session.query(Category).delete()
db.session.add(
    Category(
        name="Boodschappen",
        color="blue"
    )
)
db.session.add(
    Category(
        name="Oppas",
        color="orange"
    )
)
db.session.commit()
print("recreated categories")