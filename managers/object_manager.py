from app.provider import db

class ObjectManager:

    class Keys:
        SERVER_ID = "server_id"

    def __init__(self, cls_type):
        self.cls_type = cls_type

    def commit_if_required(self, should_commit=True):
        if should_commit:
            db.session.commit()

    def create(self, dictionary):
        new_object = self.cls_type(**dictionary)
        db.session.add(new_object)
        return new_object
    
    def get_single(self, server_id):
        return db.session.query(
            self.cls_type
        ).filter(
            self.cls_type.server_id == server_id
        ).first()

    def update_existing_object(self, db_object, dictionary):
        keys = dictionary.keys()
        for key in keys:
            setattr(db_object, key, dictionary.get(key))
        return db_object

    def update_or_create(self, dictionary, auto_commit=True):
        server_id = dictionary.get(ObjectManager.Keys.SERVER_ID)

        #TODO: out of scope for now, prevent updating of unwanted values

        if server_id != None:
            db_object = self.get_single(server_id)
            db_object = self.update_existing_object(db_object, dictionary)
        else:
            db_object = self.create(dictionary)

        self.commit_if_required(should_commit=auto_commit)
        return db_object

    def update_or_create_multi(self, dictionaries, auto_commit=True):
        objects = []
        for dictionary in dictionaries:
            obj = self.update_or_create(dictionary)
            objects.append(obj)
        self.commit_if_required(should_commit=should_commit)
        return objects