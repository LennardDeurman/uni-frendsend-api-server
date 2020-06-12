

from geopy.geocoders import Nominatim
class LocationResolver:

    class Keys:
        USER_AGENT = "frendsend"
        ZIP_CODE = "zip_code"
        COORDINATES = "coordinates"

    def __init__(self):
        self.geolocator = Nominatim(user_agent="frendsend")
    
    def resolve(self, location_name):
        return self.geolocator.geocode(location_name)

    def coordinates_as_string(self, location):
        return "{0},{1}".format(
            location.latitude,
            location.longitude
        )
    
    def apply_coordinates_info_to_dict(self, dictionary):
        zip_code = dictionary.get(LocationResolver.Keys.ZIP_CODE)
        if (zip_code != None):
            location = self.resolve(
                zip_code
            )
            coordinates = self.coordinates_as_string(
                location
            )
            dictionary[LocationResolver.Keys.COORDINATES] = coordinates