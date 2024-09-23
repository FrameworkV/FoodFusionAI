import sqlite3

from src.backend.models.user import User
from src.backend.models.groceries import Groceries

class DatabaseHelper:
    _instance = None

    def __init__(self):
        raise RuntimeError("Use DatabaseHelper.instance() instead")

    def _init_db(self):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(""" CREATE TABLE IF NOT EXISTS users (
                                id integer PRIMARY KEY,
                                name text
                               ); """)

        cursor.execute(""" CREATE TABLE IF NOT EXISTS storage(
                                id integer PRIMARY KEY,
                                name text,
                                user_id integer,
                               ); """)
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def get_conn(self):
        return sqlite3.connect("users.db")

    def insert_user(self, user: User) -> int:
        '''

        '''

        try:
            conn = self.get_conn()
            with conn:
                cursor = conn.cursor()
                name = user.get_name()
                data = cursor.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchone()

                if data is None:
                    cursor.execute(""" INSERT INTO users
                                       (name)
                                       VALUES (?); """, (name,))
                    user_id = cursor.lastrowid
                    return user_id
                else:
                    user_id = data[0]
                    return user_id

        except sqlite3.Error as error:
            print("Failed to insert program into db:", error)

        finally:
            cursor.close()
            conn.close()

    def get_user(self,) -> User:
        pass

    def delete_user(self, user: User) -> int:
        pass

    def insert_groceries_for_user(self, groceries: Groceries) -> int:
        pass


