from database.entities import Category
from managers.object_manager import ObjectManager
from app.provider import db

class CategoriesManager (ObjectManager):

    def __init__(self):
        super().__init__(Category)

    def get_all(self):
        return db.session.query(Category).all()