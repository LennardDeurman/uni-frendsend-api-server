'''

These are the database entities itself, which may possible inherit properties from the extension classes

'''

from database.extensions import ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails, DBModel
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.sql.expression import cast
from app.provider import db
from datetime import datetime 
import sqlalchemy
import math

class User(DBModel, ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails):
    email = db.Column(db.String(100), unique=True, nullable=False)
    firebase_uid = db.Column(db.String(100), unique=True, nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    profile_image_url = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    bio = db.Column(db.String(300))
    phone = db.Column(db.String(10), unique=True, nullable=False)
    main_preference_mode = db.Column(db.Integer, nullable=False) #This is an int; in the manager class we need to check (not implemented for now) if it conforms to our enum PreferenceMode 

category_association_table = db.Table(
    'category_association_table', db.metadata,
    db.Column(
        'category_id',
        db.Integer,
        db.ForeignKey(
            'category.server_id'
        )
    ),
    db.Column(
        'advertisement_id',
        db.Integer,
        db.ForeignKey(
            'advertisement.server_id'
        )
    )
)



class Advertisement(DBModel, ObjectWithDefaultProps, ObjectWithLocation, ObjectWithContactDetails):
    title = db.Column(db.String(20), nullable=False)
    details = db.Column(db.String(300), nullable=False)
    deadline = db.Column(db.DateTime)
    finished = db.Column(db.Boolean, nullable=False, default=False)

    author_id = db.Column(db.Integer, db.ForeignKey("user.server_id"))
    author = db.relationship("User", foreign_keys=author_id, lazy="joined", backref="advertisements")

    categories = db.relationship(
        "Category",
        secondary=category_association_table
    )

    @hybrid_method
    def distance(self, my_coordinates):
        lon1 = db.func.substr(self.coordinates, db.func.instr(self.coordinates, ',') + 1)
        lat1 = db.func.substr(self.coordinates, 0, db.func.instr(self.coordinates, ','))
        lat2 = db.func.substr(my_coordinates, 0, db.func.instr(my_coordinates, ','))
        lon2 = db.func.substr(my_coordinates, db.func.instr(my_coordinates, ',') + 1)

        earth_radius_km = 6371.009
        
        lon1 = cast(lon1, sqlalchemy.Float)
        lon2 = cast(lon2, sqlalchemy.Float)
        lat1 = cast(lat1, sqlalchemy.Float)
        lat2 = cast(lat2, sqlalchemy.Float)

        km_per_deg_lat = db.literal(2 * math.pi * earth_radius_km / 360.0)

        km_per_deg_lon = km_per_deg_lat * db.func.cos(
            db.func.radians(
                lat1
            )
        )

        lat_calc_col = db.func.power(km_per_deg_lat * (lat1 - lat2), 2)
        lon_calc_col = db.func.power(km_per_deg_lon * (lon1 - lon2), 2)
        calc_col = lat_calc_col + lon_calc_col

        return db.func.round(db.func.sqrt(calc_col), 2)
    

class Category(DBModel, ObjectWithDefaultProps):
    name = db.Column(db.String(20), unique=True, nullable=False)
    color = db.Column(db.String(20), unique=True, nullable=False)

class Message(DBModel, ObjectWithDefaultProps):
    body = db.Column(db.String(250), nullable=False)

    receiver_id = db.Column(db.Integer, db.ForeignKey("user.server_id"))
    sender_id = db.Column(db.Integer, db.ForeignKey("user.server_id"))

    receiver = db.relationship("User", foreign_keys=receiver_id, lazy="joined")
    sender = db.relationship("User", foreign_keys=sender_id, lazy="joined")