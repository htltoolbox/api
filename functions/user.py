from assets.database import openDBConnection
from models.sessionkey import SessionKey
from models.user import User


def get_user(ID=None, EMAIL=None, SESSION_KEY=None):
    db = openDBConnection()
    cursor = db.cursor()

    if ID is not None:
        cursor.execute("SELECT * FROM USERDATA WHERE ID = %s", (ID,))
        return fetch_data(cursor)
    if EMAIL is not None:
        cursor.execute("SELECT * FROM USERDATA WHERE ID = %s", (EMAIL,))
        return fetch_data(cursor)
    if SESSION_KEY is not None:
        cursor.execute("SELECT * FROM USERDATA WHERE ID = %s", (SESSION_KEY,))
        return fetch_data(cursor)
    else:
        raise ValueError('USER not Valid')


def fetch_data(cursor):
    data = cursor.fetchone()
    return User(
        ID=data[0],
        EMAIL=data[1],
        PASSWORD_HASH=data[2],
        NAME=data[3],
        LASTNAME=data[4],
        CLASS=data[5],
        PERMISSION_LEVEL=data[6],
        LAST_IP=data[7],
        ACTIVE=data[8],
        SESSION_KEY=SessionKey(key=data[9])
    )
