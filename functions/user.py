from fastapi import Depends

from assets.database import openDBConnection
from models.sessionkey import SessionKey
from models.user import User


def get_user(ID=None, EMAIL=None):
    db = openDBConnection()
    cursor = db.cursor()

    if ID is not None:
        cursor.execute("SELECT * FROM USERDATA WHERE ID = %s", (ID,))
        return fetch_data(cursor.get_row())
    if EMAIL is not None:
        cursor.execute("SELECT * FROM USERDATA WHERE EMAIL = %s", (EMAIL,))
        return fetch_data(cursor.get_row())
    else:
        raise ValueError('USER not Valid')


def push_data(u: User):
    db = openDBConnection()
    cursor = db.cursor()

    SQL = """
    UPDATE USERDATA SET 
    EMAIL = %s,
    PASSWORD_HASH = %s,
    NAME = %s,
    LASTNAME = %s,
    CLASS = %s,
    PERMISSION_LEVEL = %s,
    LAST_IP = %s,
    ACTIVE = %s
    WHERE ID = %s
    """

    PARAM = (
        u.EMAIL,
        u.PASSWORD_HASH,
        u.NAME,
        u.LASTNAME,
        u.CLASS,
        u.PERMISSION_LEVEL,
        str(u.LAST_IP),
        u.ACTIVE,
        u.ID
    )

    cursor.execute(SQL, PARAM)
    db.commit()
    cursor.close()
    db.close()


def create_user(u: User):
    db = openDBConnection()
    cursor = db.cursor()

    SQL = """
    INSERT INTO USERDATA (EMAIL, PASSWORD_HASH, NAME, LASTNAME, CLASS, PERMISSION_LEVEL, LAST_IP, ACTIVE) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    PARAM = (
        u.EMAIL,
        u.PASSWORD_HASH,
        u.NAME,
        u.LASTNAME,
        u.CLASS,
        u.PERMISSION_LEVEL,
        str(u.LAST_IP),
        u.ACTIVE
    )

    cursor.execute(SQL, PARAM)
    db.commit()
    cursor.close()
    db.close()


def fetch_data(data):
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
    )


def is_teacher(EMAIL: str):
    db = openDBConnection()
    cursor = db.cursor()

    cursor.execute("SELECT EMAIL FROM GLOBAL_TEACHERS WHERE EMAIL = %s", (EMAIL,))

    data: str = cursor.fetchone()

    if data is not None:
        if data[0].casefold() == EMAIL.casefold():
            return True
        return False
    return False


def get_all_users():
    db = openDBConnection()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM USERDATA")

    allUsers = dict()

    data = cursor.fetchall()

    for x in data:
        allUsers[x[0]] = fetch_data(x)

    return remove_passwordhash(allUsers)


def remove_passwordhash(users: dict):
    for x in users:
        users[x].PASSWORD_HASH = None
    return users


def remove_passwordhash_obj(users: User):
    users.PASSWORD_HASH = None
    return users
