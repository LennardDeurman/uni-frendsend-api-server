import unittest

class TestObjectCreation(unittest.TestCase):

    def test_user_create(self):
        new_user = User(
            **dictionary 
        )
        db.session.add(new_user)