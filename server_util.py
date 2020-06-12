import os
from firebase_admin import auth
import firebase_admin
import json
import urllib.request

#Connection with the Google Apis (Login)

class ServerUtil:

    VERSION_BETA = "beta"
    VERSION_PROD = "prod"
    GOOGLE_CREDENTIALS_KEY = "GOOGLE_APPLICATION_CREDENTIALS"
    GOOGLE_CREDENTIALS_FILE = "service_account_key.json"
    API_KEY = "AIzaSyBtQiG6ZHKZ-UroaXXDG97HiPlrI96sUPQ"
    DEMO_UID = "8dryBOqYduMSTLMBCztp78wRXaY2"

    class Keys:
        APP_ENGINE_VERSION = "app_engine_version"
        IS_APP_ENGINE = "is_app_engine"
        IS_DEBUG = "is_debug"
        TOKEN = "token"

    @staticmethod
    def is_app_engine():
        return ServerUtil.get_app_version() != None

    @staticmethod
    def get_app_version():
        return os.environ.get("GAE_VERSION")
    
    @staticmethod
    def is_debug():
        app_version = ServerUtil.get_app_version()
        if (app_version == ServerUtil.VERSION_PROD):
            return False
        return True
    
    @staticmethod
    def initialize_app(app):
        os.environ[ServerUtil.GOOGLE_CREDENTIALS_KEY] = ServerUtil.GOOGLE_CREDENTIALS_FILE
        firebase_admin.initialize_app()

    @staticmethod
    def get_id_token(uid):
        token = auth.create_custom_token(uid)
        url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key={}".format(ServerUtil.API_KEY)
        body = {
            "token": token.decode("utf-8"), 
            "returnSecureToken": True
        }
        jsondata = json.dumps(body).encode()
        req = urllib.request.Request(url, data=jsondata,
                                    headers={'content-type': 'application/json'})
        response = urllib.request.urlopen(req)
        json_resp = json.loads(response.read().decode("utf-8"))
        return json_resp["idToken"]
        