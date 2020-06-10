import unittest
from geopy.geocoders import Nominatim
class TestGeoPy(unittest.TestCase):

    def test_location_decode(self):
        geolocator = Nominatim(user_agent="frendsend")
        location = geolocator.geocode("3971CX")
        print(location.latitude)
        print(location.longtitude) 
        pass