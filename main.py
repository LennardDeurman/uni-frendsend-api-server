from app.provider import flask_app, db
from flask import request, g
from managers.identity import IdentityManager
from managers.object_manager import ObjectManager
from database.entities import User, Category, Advertisement, Message
from result_message import ResultMessage
from server_util import ServerUtil
from datetime import datetime
from geopy.geocoders import Nominatim
from werkzeug.utils import secure_filename

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

class ChatManager (ObjectManager):

    def __init__(self, identity_manager, user_id):
        self.identity_manager = identity_manager
        self.user_id = user_id
        super().__init__(Message)
    
    def get_conversation(self):
        return db.session.query(
            Message
        ).options(
            db.noload(
                Message.receiver
            ),
            db.noload(
                Message.sender
            )
        ).filter(
            db.or_(
                Message.receiver_id == self.identity_manager.user.server_id,
                Message.receiver_id == self.user_id
            ),
            db.or_(
                Message.sender_id == self.identity_manager.user.server_id,
                Message.sender_id == self.user_id
            )
        ).order_by(
            Message.date_added
        ).all()
    
    def update_or_create(self, dictionary, auto_commit=True):
        dictionary[Message.sender_id.key] = self.identity_manager.user.server_id
        dictionary[Message.receiver_id.key] = self.user_id        
        return super().update_or_create(dictionary, auto_commit=auto_commit)

class AdvertisementsManager (ObjectManager):

    def __init__(self, identity_manager):
        super().__init__(Advertisement)
        self.location_resolver = LocationResolver()
        self.identity_manager = identity_manager
    
    def append_categories(self, dictionary, db_object):
        category_ids = dictionary.get("categories")

        objects = db.session.query(Category).all()

        for obj in objects:
            db_object.categories.append(
                obj
            )
        

    def create(self, dictionary):
        db_object = super().create(dictionary)
        self.append_categories(dictionary, db_object)
        return db_object
    
    def update_existing_object(self, db_object, dictionary):
        db_object = super().update_existing_object(db_object, dictionary)
        self.append_categories(dictionary, db_object)
        return db_object

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

@flask_app.route("/user/<int:user_id>/chat")
def get_chat(user_id):
    g.identity_manager.validate()
    return ResultMessage.ok_with_object(
        dictionaries_from_objects(
            ChatManager(
                g.identity_manager,
                user_id
            ).get_conversation()
        )
    )

@flask_app.route("/user/<int:user_id>/chat", methods=["POST"])
def update_chat(user_id):
    g.identity_manager.validate()
    chat_manager = ChatManager(
        g.identity_manager,
        user_id
    )
    return ResultMessage.ok_with_object(
        chat_manager.update_or_create(
            request.json
        ).as_dict(
            ignored_columns=[
                User.advertisements
            ]
        )
    )


@flask_app.route("/advertisement", methods=["POST"])
def update_advertisement():
    g.identity_manager.validate()
    advertisement = AdvertisementsManager(g.identity_manager).update_or_create(request.json)
    return ResultMessage.ok_with_object(advertisement.as_dict(
        ignored_columns=[
            Advertisement.author
        ]
    ))

@flask_app.route("/advertisement/all", methods=["GET"])
def get_advertisements():
    g.identity_manager.validate()

    max_distance_km = int(request.args.get('max_km', default=10))
    search = request.args.get('search', default="")
    cat_ids = list(map(int, request.args.get('cats', default="").split(",")))
    offset = int(request.args.get('offset', default=0))
    limit = int(request.args.get('limit', default=20))
    order = int(request.args.get('order', default=0))
    show_deleted = bool(request.args.get('show_deleted', default=False))
    my_coord = g.identity_manager.user.coordinates

    query = db.session.query(
        Advertisement,
        Advertisement.distance(my_coord)
    ).filter(
        Advertisement.distance(my_coord) < max_distance_km
    )

    if not show_deleted:
        query = query.filter(
            Advertisement.deleted == False
        )

    if (len(search) > 0):
        search_query = "%{0}%".format(search)
        query = query.filter(
            db.or_(
                Advertisement.details.ilike(
                    search_query
                ),
                Advertisement.title.ilike(
                    search_query
                )
            )
            
        )
    
    if len(cat_ids) > 0:
        query = query.filter(
            Advertisement.categories.any(
                Category.server_id.in_(cat_ids)
            )
        )
    

    if (order == 0):
        query = query.order_by(
            Advertisement.distance(my_coord)
        )
    elif (order == 1):
        query = query.order_by(
            Advertisement.date_modified
        )
    elif (order == 2):
        query = query.order_by(
            Advertisement.date_added
        )
    
    query = query.offset(
        offset
    ).limit(
        limit
    )

    items = query.all()
    dictionaries = []
    for item in items:
        advertisement_dict = item[0].as_dict(
            ignored_columns=[
                User.advertisements
            ]
        )
        distance = item[1]
        advertisement_dict["distance"] = distance
        dictionaries.append(advertisement_dict)

    return ResultMessage.ok_with_object(
        dictionaries
    )

@flask_app.route("/category/all", methods=["GET"])
def get_categories():
    return ResultMessage.ok_with_object(dictionaries_from_objects(CategoriesManager().get_all()))

@flask_app.route("/upload", methods=["POST"]) #TODO: out of scope for now, implement a good file uploading structure
def upload():
    g.identity_manager.validate()
    f = request.files['file']
    file_name = "data/" + secure_filename(f.filename)
    f.save(file_name)
    return ResultMessage.ok_with_object(file_name)



#TODO: Users get_all 

if __name__ == '__main__':
	flask_app.run(debug=is_debug, port=5001)  


