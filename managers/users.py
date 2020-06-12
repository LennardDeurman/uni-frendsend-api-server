import dictionary_util
from location_resolver import LocationResolver
from database.entities import User
from managers.object_manager import ObjectManager
from app.provider import db

class UsersManager (ObjectManager):


    def __init__(self, identity_manager):
        super().__init__(User)
        self.location_resolver = LocationResolver()
        self.identity_manager = identity_manager


    def update_or_create(self, dictionary, auto_commit=True):
        dictionary[User.firebase_uid.key] = self.identity_manager.firebase_user.uid #This is to ensure only the object of the own user is edited 
        if (dictionary.get(User.email.key) == None):
            dictionary[User.email.key] = self.identity_manager.firebase_user.email
        
        dictionary_util.timestamp_dict_value_to_date(dictionary, User.date_of_birth.key)
        self.location_resolver.apply_coordinates_info_to_dict(dictionary)
        
        return super().update_or_create(dictionary, auto_commit=auto_commit)