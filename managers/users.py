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

        current_user = self.identity_manager.user
        if current_user == None:
            current_user = self.create(
                dictionary
            )
        else:
            current_user = self.update_existing_object(current_user, dictionary)

        self.commit_if_required(should_commit=auto_commit)
        return current_user
