import dictionary_util
import populate_database
from app.provider import flask_app, db
from flask import request, g
from managers.identity import IdentityManager, UnauthorizedAccessException, UserInfoMissingException, FirebaseInfoMissingException
from managers.users import UsersManager
from managers.categories import CategoriesManager
from managers.chat import ChatManager
from managers.upload import GoogleStorageManager
from managers.advertisements import AdvertisementsManager
from database.entities import User, Advertisement
from result_message import ResultMessage
from server_util import ServerUtil
from werkzeug.utils import secure_filename
from overviews.advertisements import AdvertisementsOverview
from overviews.users import UsersOverview

ServerUtil.initialize_app(flask_app)
is_debug = ServerUtil.is_debug()

app = flask_app #required by the GCE

@app.before_request
def before_request():
    g.identity_manager = IdentityManager(request)

@app.errorhandler(UserInfoMissingException)
def invalid_exception_handler(error):
    return ResultMessage.fail_with_object(ResultMessage.StatusCodes.BAD_REQUEST, error)

@app.errorhandler(UnauthorizedAccessException)
def access_exception_handler(error):
    return ResultMessage.fail_with_object(ResultMessage.StatusCodes.NO_ACCESS, error)

@app.errorhandler(FirebaseInfoMissingException)
def access_exception_handler(error):
    return ResultMessage.fail_with_object(ResultMessage.StatusCodes.NO_ACCESS, error)


@app.route("/admin/reset/db")
def reset_db():
    populate_database.reset_database()
    return ResultMessage.ok()

@app.route("/admin/reset/cats")
def reset_cats():
    populate_database.reset_categories()
    return ResultMessage.ok()    

#Gets a dummy token for testing purposes
@app.route("/idtoken")
def get_id_token():
    if (is_debug):
        return ResultMessage.ok_with_object({
          ServerUtil.Keys.TOKEN: ServerUtil.get_id_token(ServerUtil.DEMO_UID)  
        })
    return None

#Get teh current user info
@app.route("/user", methods=["GET"])
def get_my_user():
    g.identity_manager.validate_fir()
    if (g.identity_manager.user != None):
        return ResultMessage.ok_with_object(g.identity_manager.user.as_dict(
            ignored_columns=[
                Advertisement.author #authors are excluded, because all the same
            ]
        ))
    else:
        return ResultMessage.ok_with_object(None)

#Post current user info
@app.route("/user", methods=["POST"])
def update_user():
    g.identity_manager.validate_fir()
    updated_user = UsersManager(g.identity_manager).update_or_create(request.json)
    return ResultMessage.ok_with_object(updated_user.as_dict(
        ignored_columns=[
            Advertisement.author #authors are excluded, because all the same
        ]
    ))

#Get a specific user (advertisements relations included)
@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    g.identity_manager.validate_fir()
    user = UsersManager(g.identity_manager).get_single(user_id)
    return ResultMessage.ok_with_object(user.as_dict(
        ignored_columns=[
            Advertisement.author #authors are excluded, because all the same
        ]
    ))

@app.route("/user/all", methods=["GET"])
def get_users():
    g.identity_manager.validate()
    return ResultMessage.ok_with_object(
        UsersOverview(
            g.identity_manager,
            request
        ).build()
    )
    



@app.route("/user/<int:user_id>/chat")
def get_chat(user_id):
    g.identity_manager.validate()
    return ResultMessage.ok_with_object(
        dictionary_util.dictionaries_from_objects(
            ChatManager(
                g.identity_manager,
                user_id
            ).get_conversation()
        )
    )

@app.route("/user/<int:user_id>/chat", methods=["POST"])
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


@app.route("/advertisement", methods=["POST"])
def update_advertisement():
    g.identity_manager.validate()
    advertisement = AdvertisementsManager(g.identity_manager).update_or_create(request.json)
    return ResultMessage.ok_with_object(advertisement.as_dict(
        ignored_columns=[
            Advertisement.author
        ]
    ))

@app.route("/advertisement/all", methods=["GET"])
def get_advertisements():
    g.identity_manager.validate()
    
    return ResultMessage.ok_with_object(
        AdvertisementsOverview(
            g.identity_manager,
            request
        ).build()
    )


@app.route("/category/all", methods=["GET"])
def get_categories():
    return ResultMessage.ok_with_object(dictionary_util.dictionaries_from_objects(CategoriesManager().get_all()))

#TO BE Improved: Create a better upload endpoint via a third party service, and handle photos properly (resizing)
@app.route("/upload", methods=["POST"])
def upload():
    g.identity_manager.validate()
    f = request.files['file']
    file_name = secure_filename(f.filename)
    result = GoogleStorageManager().upload_file(f, file_name)
    return ResultMessage.ok_with_object(result)

if __name__ == '__main__':
	app.run(debug=is_debug, port=5001)  


