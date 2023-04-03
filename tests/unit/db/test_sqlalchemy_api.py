import unittest
from db.sqlalchemy.api import create_room


class SqlalchemyApiTestCase(unittest.TestCase):

    def test_create_room(self):
        self.assertRaises(create_room('room'), ValueError)

