from fastapi import Depends

from assets.database import openDBConnection
from assets.database import datasource
from models.sessionkey import SessionKey
from models.user import User

from typing import Optional

import env as e


def get_user(ID: Optional[str] = None, EMAIL: Optional[str] = None, TEMPHASH: Optional[str] = None):
    ds = datasource()
    ds.connect()

    if ID is not None:
        if e.DEBUG:
            print(ID)
        ds.execute("SELECT * FROM USERDATA WHERE ID = %s", (ID,))
    elif EMAIL is not None:
        if e.DEBUG:
            print(EMAIL)
        ds.execute("SELECT * FROM USERDATA WHERE EMAIL = %s", (EMAIL,))
    elif TEMPHASH is not None:
        if e.DEBUG:
            print(TEMPHASH)
        ds.execute("SELECT * FROM USERDATA WHERE TEMPHASH = %s", (TEMPHASH,))
    else:
        raise ValueError('USER not Valid')
    data = ds.fetch_row()
    if data is not None:
        return fetch_data(data)
    else:
        raise ValueError('No user found')


def push_data(u: User):
    ds = datasource()
    ds.connect()

    SQL = """
    UPDATE USERDATA SET 
    EMAIL = %s,
    PASSWORD_HASH = %s,
    NAME = %s,
    LASTNAME = %s,
    CLASS = %s,
    PERMISSION_LEVEL = %s,
    LAST_IP = %s,
    ACTIVE = %s,
    TEMPHASH = %s
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
        u.TEMPHASH,
        u.ID
    )

    ds.execute(SQL, PARAM)
    ds.commit()
    ds.close()


def create_user(u: User):
    ds = datasource()
    ds.connect()

    SQL = """
    INSERT INTO USERDATA (EMAIL, PASSWORD_HASH, NAME, LASTNAME, CLASS, PERMISSION_LEVEL, LAST_IP, ACTIVE, TEMPHASH) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        u.TEMPHASH
    )

    ds.execute(SQL, PARAM)
    ds.commit()
    ds.close()


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
        TEMPHASH=data[9],
    )


def is_teacher(EMAIL: str):
    ds = datasource()
    ds.connect()

    ds.execute("SELECT EMAIL FROM GLOBAL_TEACHERS WHERE EMAIL = %s", (EMAIL,))

    data: str = ds.fetch_row()

    if data is not None:
        if data[0].casefold() == EMAIL.casefold():
            return True
        return False
    return False


def get_all_users():
    ds = datasource()
    ds.connect()

    ds.execute("SELECT * FROM USERDATA")

    allUsers = dict()

    data = ds.fetch_all()

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
