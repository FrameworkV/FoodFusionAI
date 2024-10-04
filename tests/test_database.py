import unittest

from backend.models.user import User
from backend.models.groceries import Grocery
from backend.database.database_setup import create_db_and_tables, get_session


class TestDatabase(unittest.TestCase):
    def setUp(self):
        create_db_and_tables()

    def test_hello_world(self):
        user = User(username="Kai", hashed_password="hashed_pass")

        grocery1 = Grocery(name="Apples", user=user, quantity=3)
        grocery2 = Grocery(name="Bananas", user=user, quantity=3)
        # Add user and groceries to session
        with next(get_session()) as session:
            session.add(user)
            session.add(grocery1)
            session.add(grocery2)
            session.commit()
            session.close()


if __name__ == "__main__":
    unittest.main()
