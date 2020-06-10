from app.provider import flask_app, db
from database.entities import Category

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