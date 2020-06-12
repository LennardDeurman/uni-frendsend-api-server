from app.provider import db
from managers.object_manager import ObjectManager
from managers.identity import UnauthorizedAccessException
from database.entities import Message

class ChatManager (ObjectManager):

    def __init__(self, identity_manager, user_id):
        self.identity_manager = identity_manager
        self.user_id = user_id
        super().__init__(Message)
    
    #We prevent the loading of the receiver, and sender as this is not necessary
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

    def update_existing_object(self, db_object, dictionary):
        if (db_object.sender_id != g.identity_manager.user.server_id):
            raise UnauthorizedAccessException("You don't have access to this object, you're not the owner")
        return super().update_existing_object(db_object, dictionary)
    
    def update_or_create(self, dictionary, auto_commit=True):
        dictionary[Message.sender_id.key] = self.identity_manager.user.server_id
        dictionary[Message.receiver_id.key] = self.user_id        
        return super().update_or_create(dictionary, auto_commit=auto_commit)