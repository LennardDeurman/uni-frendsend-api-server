'''

These are the objects used as overriden classes or extensions, so that it can be used in multiple database entities without redefining. 

'''
from app.provider import db
from datetime import datetime
import simplejson as json

class ObjectWithDefaultProps:
    server_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    date_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class ObjectWithLocation:
    zip_code = db.Column(db.String(6), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False) 

class ObjectWithContactDetails:
    phone = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


class DBModel(db.Model):

    __abstract__ = True

    @classmethod
    def editable_columns(cls):
        return cls.__table__.columns.keys()

    @property
    def fields(self):
        fields = self.__json__() if hasattr(self, '__json__') else dir(self)
        return [f for f in fields if not f.startswith("_") and f not in [
            'metadata',
            'query',
            'query_class',
            'editable_columns',
            'binary_notification_fields',
            'as_dict',
            'fields'
        ]]
    
    def as_dict(self, ignored_columns = []):
        fields = self.fields
        dictionary = {}
        current_class = type(self).__name__
        for field in fields:

            ignore_field = False
            for ignored_column in ignored_columns:
                ignored_field = ignored_column.key
                ignored_field_class = ignored_column.parent.entity.__name__
                if ignored_field == field and ignored_field_class == current_class:
                    ignore_field = True
                    break

            if not ignore_field:
                value = getattr(self, field)
                if isinstance(value, list):
                    dictionary_objs = []
                    for obj in value:
                        if isinstance(obj, DBModel):
                            dictionary_objs.append(obj.as_dict(ignored_columns=ignored_columns))
                        else:
                            dictionary_objs.append(obj)
                    dictionary[field] = dictionary_objs
                elif isinstance(value, datetime):
                    epoch = datetime(1970, 1, 1)
                    time_stamp = (value - epoch).total_seconds()
                    dictionary[field] = int(time_stamp)
                elif isinstance(value, DBModel):
                    dictionary[field] = value.as_dict(ignored_columns=ignored_columns)
                else:
                    try:
                        json.dumps(value)
                        dictionary[field] = value
                    except:
                        pass
            else:
                dictionary[field] = None

        return dictionary