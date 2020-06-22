from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, event
from server_util import ServerUtil
import os
import math

flask_app = Flask(__name__)

GAE_VERSION = os.environ.get("GAE_VERSION")

if GAE_VERSION != None:
    CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME' '')
    CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER', 'root')
    CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD', '')
    CLOUDSQL_DATABASE = os.environ.get('CLOUDSQL_DATABASE', '')
    LIVE_SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://{nam}:{pas}@localhost/{dbn}?unix_socket=/cloudsql/{con}').format (
        nam=CLOUDSQL_USER,
        pas=CLOUDSQL_PASSWORD,
        dbn=CLOUDSQL_DATABASE,
        con=CLOUDSQL_CONNECTION_NAME,
    )
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = LIVE_SQLALCHEMY_DATABASE_URI

else:
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///development_database.sqlite"


flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}



db = SQLAlchemy(flask_app, metadata=MetaData(naming_convention=naming_convention))



'''
@event.listens_for(db.engine, 'connect')
def create_functions(dbapi_connection, connection_record):
    dbapi_connection.create_function('sqrt', 1, math.sqrt)
    dbapi_connection.create_function('radians', 1, math.radians)
    dbapi_connection.create_function('cos', 1, math.cos)
    dbapi_connection.create_function('to_float', 1, to_float)
    dbapi_connection.create_function('round', 2, round)
    dbapi_connection.create_function('pow', 2, math.pow)
'''