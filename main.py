from app.provider import flask_app, db
from flask import request, g
from managers.identity import IdentityManager
from managers.object_manager import ObjectManager
from database.entities import User, Category, Advertisement
from result_message import ResultMessage
from server_util import ServerUtil
from datetime import datetime
from geopy.geocoders import Nominatim

ServerUtil.initialize_app(flask_app)
is_debug = ServerUtil.is_debug()

def dictionaries_from_objects(db_objects):
    dictionaries = []
    for db_object in db_objects:
        dictionaries.append(db_object.as_dict())
    return dictionaries

def timestamp_dict_value_to_date(dictionary, key):
    value = dictionary.get(key)
    if (value != None):
        dictionary[key] = datetime.fromtimestamp(value)

def apply_coordinates_info_to_dict(dictionary, resolver):
    zip_code = dictionary.get("zip_code")
    if (zip_code != None):
        location = resolver.resolve(
            zip_code
        )
        coordinates = resolver.coordinates_as_string(
            location
        )
        dictionary["coordinates"] = coordinates

@flask_app.before_request
def before_request():
    g.identity_manager = IdentityManager(request)

class LocationResolver:

    def __init__(self):
        self.geolocator = Nominatim(user_agent="frendsend")
    
    def resolve(self, location_name):
        return self.geolocator.geocode(location_name)

    def coordinates_as_string(self, location):
        return "{0},{1}".format(
            location.latitude,
            location.longitude
        )

class UsersManager (ObjectManager):


    class Keys:
        FIREBASE_UID = "firebase_uid"
        EMAIL = "email"

    def __init__(self, identity_manager):
        super().__init__(User)
        self.location_resolver = LocationResolver()
        self.identity_manager = identity_manager


    def update_or_create(self, dictionary, auto_commit=True):
        dictionary[UsersManager.Keys.FIREBASE_UID] = self.identity_manager.firebase_user.uid
        if (dictionary.get(UsersManager.Keys.EMAIL) == None):
            dictionary[UsersManager.Keys.EMAIL] = self.identity_manager.firebase_user.email
        
        timestamp_dict_value_to_date(dictionary, User.date_of_birth.key)
        apply_coordinates_info_to_dict(dictionary, self.location_resolver)
        
        return super().update_or_create(dictionary, auto_commit=auto_commit)
 
class CategoriesManager (ObjectManager):

    def __init__(self):
        super().__init__(Category)

    def get_all(self):
        return db.session.query(Category).all()

class AdvertisementsManager (ObjectManager):

    def __init__(self, identity_manager):
        super().__init__(Advertisement)
        self.location_resolver = LocationResolver()
        self.identity_manager = identity_manager
    
    def update_or_create(self, dictionary, auto_commit=True):
        timestamp_dict_value_to_date(dictionary, Advertisement.deadline.key)
        apply_coordinates_info_to_dict(dictionary, self.location_resolver)
        dictionary[Advertisement.author_id.key] = self.identity_manager.user.server_id
        return super().update_or_create(dictionary, auto_commit=auto_commit)


@flask_app.route("/idtoken")
def get_id_token():
    if (is_debug):
        return ResultMessage.ok_with_object({
          ServerUtil.Keys.TOKEN: ServerUtil.get_id_token(ServerUtil.DEMO_UID)  
        })
    return None

@flask_app.route("/user", methods=["GET"])
def get_my_user():
    g.identity_manager.validate_fir()
    if (g.identity_manager.user != None):
        return ResultMessage.ok_with_object(g.identity_manager.user.as_dict())
    else:
        return ResultMessage.ok_with_object(None)

@flask_app.route("/user", methods=["POST"])
def update_user():
    g.identity_manager.validate_fir()
    updated_user = UsersManager(g.identity_manager).update_or_create(request.json)
    return ResultMessage.ok_with_object(updated_user.as_dict())

@flask_app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    g.identity_manager.validate_fir()
    user = UsersManager(g.identity_manager).get_single(user_id)
    return ResultMessage.ok_with_object(user.as_dict(
        ignored_columns=[
            Advertisement.author #authors are excluded, because all the same
        ]
    ))

@flask_app.route("/advertisement", methods=["POST"])
def update_advertisement():
    g.identity_manager.validate()
    advertisement = AdvertisementsManager(g.identity_manager).update_or_create(request.json)
    return ResultMessage.ok_with_object(advertisement.as_dict(
        ignored_columns=[
            Advertisement.author
        ]
    ))


@flask_app.route("/category/all", methods=["GET"])
def get_categories():
    return ResultMessage.ok_with_object(dictionaries_from_objects(CategoriesManager().get_all()))

if __name__ == '__main__':
	flask_app.run(debug=is_debug, port=5001)  


