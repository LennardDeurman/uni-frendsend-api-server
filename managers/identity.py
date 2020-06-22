from database.entities import User
from firebase_admin import auth
from app.provider import db

class UserInfoMissingException(Exception):
    pass

class FirebaseInfoMissingException(Exception):
    pass

class UnauthorizedAccessException(Exception):
    pass

class IdentityManager:

    class Headers:
        ID_TOKEN = "X-Id-Token"

    class Keys:
        UID = "uid"

    def __init__ (self, request):
        id_token = request.headers.get(IdentityManager.Headers.ID_TOKEN)
        self.firebase_user = self.fetch_firebase_user(id_token)
        if self.firebase_user != None:
            self.user = db.session.query(User).filter(
                User.firebase_uid == self.firebase_user.uid
            ).first()
        else:
            self.user = None

    def fetch_firebase_user(self, id_token):
        if (id_token != None and id_token != ""):
            try:
                response = auth.verify_id_token(id_token)
                uid = response[IdentityManager.Keys.UID]
                return auth.get_user(uid)
            except:
                return None
        return None
    
    def validate(self):
        if self.user == None:
            raise UserInfoMissingException("There is no user info filled for this account")
    
    def validate_fir(self):
        if self.firebase_user == None:
            raise FirebaseInfoMissingException("Firebase user not active")