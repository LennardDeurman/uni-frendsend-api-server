from datetime import datetime

def dictionaries_from_objects(db_objects):
    dictionaries = []
    for db_object in db_objects:
        dictionaries.append(db_object.as_dict())
    return dictionaries

def timestamp_dict_value_to_date(dictionary, key):
    value = dictionary.get(key)
    if (value != None):
        dtn = datetime.fromtimestamp(value)
        dictionary[key] = dtn

