import sqlite3
import bcrypt

from backend.models.user import User
from backend.models.groceries import Groceries

class DatabaseHelper:
    _instance = None

    def __init__(self):
        raise RuntimeError("Use DatabaseHelper.instance() instead")

    def _init_db(self):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(""" CREATE TABLE IF NOT EXISTS users(
                                id integer PRIMARY KEY,
                                name text,
                                hashed_password text
                               ); """)

        cursor.execute(""" CREATE TABLE IF NOT EXISTS storage(
                                id integer PRIMARY KEY,
                                name text,
                                user_id integer
                               ); """)
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def get_conn(self):
        return sqlite3.connect("users.db")

    def add_user(self, username: str, hashed_password: str) -> int:
        '''

        '''

        try:
            conn = self.get_conn()
            with conn:
                cursor = conn.cursor()
                data = cursor.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()

                if data is None:
                    cursor.execute(""" INSERT INTO users
                                       (name, hashed_password)
                                       VALUES (?, ?); """, (username, hashed_password))
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


    def get_user(self, username: str) -> User:
        '''
        
        '''
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                user_id = cursor.execute('SELECT id FROM users WHERE name = ?', (username,)).fetchone()[0]

                if user_id is None:
                    raise ValueError(f"no user found with name: '{username}'")
                
                cursor.execute('SELECT name FROM storage WHERE user_id = ?', (user_id))
                rows = cursor.fetchall()
                groceries_names = [row[0] for row in rows]

            user = User(name=username, groceries=groceries_names)
            return user
        
        except sqlite3.Error as error:
            print("Failed to return user from db:", error)

        finally:
            cursor.close()
            conn.close()

    def delete_user(self, user: User) -> int:
        pass

    def insert_groceries_for_user(self, groceries: Groceries) -> int:
        pass

    def valid_password(self, username: str, password: str) -> bool:
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                hashed_password = cursor.execute('SELECT hashed_password FROM users WHERE name = ?', (username)).fetchone()[0]

                if hashed_password is None:
                    raise ValueError(f"no user registred with name: '{username}'")
                
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        
        except sqlite3.Error as error:
            print("Failed to return hashed_password from db:", error)

        finally:
            cursor.close()
            conn.close()