import dictionary_util
from managers.object_manager import ObjectManager
from managers.identity import UnauthorizedAccessException
from location_resolver import LocationResolver
from database.entities import Category, Advertisement
from app.provider import db

class AdvertisementsManager (ObjectManager):

    class Keys:
        CATEGORIES = "categories"

    def __init__(self, identity_manager):
        super().__init__(Advertisement)
        self.location_resolver = LocationResolver()
        self.identity_manager = identity_manager
    
    #Create the many to many relation
    def append_categories(self, dictionary, db_object):
        category_ids = dictionary.get(AdvertisementsManager.Keys.CATEGORIES, [])
        db_object.categories.clear()
        if len(category_ids) > 0:
            objects = db.session.query(Category).filter(
                Category.server_id.in_(
                    category_ids
                )
            ).all()

            for obj in objects:
                db_object.categories.append(
                    obj
                )
        

    def create(self, dictionary):
        db_object = super().create(dictionary)
        self.append_categories(dictionary, db_object)
        return db_object
    
    def update_existing_object(self, db_object, dictionary):
        if (db_object.author_id != g.identity_manager.user.server_id):
            raise UnauthorizedAccessException("You don't have access to this object, you're not the owner")
        db_object = super().update_existing_object(db_object, dictionary)
        self.append_categories(dictionary, db_object)
        return db_object

    def update_or_create(self, dictionary, auto_commit=True):
        dictionary_util.timestamp_dict_value_to_date(dictionary, Advertisement.deadline.key)
        self.location_resolver.apply_coordinates_info_to_dict(dictionary)
        dictionary[Advertisement.author_id.key] = self.identity_manager.user.server_id
        return super().update_or_create(dictionary, auto_commit=auto_commit)