from typing import Optional, List

import mysql
from pydantic import PositiveInt

import env as e
from assets.database import datasource
from models.clickboard import Clickboard, TempClickboard


def get_clickboard(ID: PositiveInt):
    ds = datasource()
    ds.connect()

    if ID is not None:
        ds.execute("""
            SELECT CLICKBOARDS.*, USERDATA.NAME, USERDATA.LASTNAME FROM CLICKBOARDS JOIN USERDATA
            ON CLICKBOARDS.AUTHOR = USERDATA.ID
            WHERE CLICKBOARDS.ID = %s
            """, (ID,))

    data = ds.fetch_row()
    ds.close()

    if data is not None:
        return Clickboard(**data)
    else:
        return ValueError('No clickboard found')


def fetch_data(data):
    return Clickboard(
        ID=data[0],
        NAME=data[1],
        AUTHOR_ID=data[2],
        AUTHOR=str(data[9])+" "+str(data[10]),
        SHORT_DESCRIPTION=data[3],
        IMG_URL=data[4],
        DOK_URL=data[5],
        SCH_URL=data[6],
        BRD_URL=data[7],
        STP_URL=data[8]
    )


def push_data(c: Clickboard):
    ds = datasource()
    ds.connect()

    SQL = """
    UPDATE CLICKBOARDS SET
    NAME = %s,
    AUTHOR = %s,
    SHORT_DESCRIPTION = %s,
    IMG_URL = %s,
    DOK_URL = %s,
    SCH_URL = %s,
    BRD_URL = %s,
    STP_URL = %s
    WHERE ID = %s
    """

    PARAM = (
        c.NAME,
        c.AUTHOR,
        c.SHORT_DESCRIPTION,
        c.IMG_URL,
        c.DOK_URL,
        c.SCH_URL,
        c.BRD_URL,
        c.STP_URL
    )

    ds.execute(SQL, PARAM)
    ds.commit()
    ds.close()


def create_clickboard(c: TempClickboard):
    ds = datasource()
    ds.connect()

    SQL = """
    INSERT INTO CLICKBOARDS (NAME, AUTHOR, SHORT_DESCRIPTION, IMG_URL, DOK_URL, SCH_URL, BRD_URL, STP_URL) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    PARAM = (
        c.NAME,
        c.AUTHOR_ID,
        c.SHORT_DESCRIPTION,
        c.IMG_URL,
        c.DOK_URL,
        c.SCH_URL,
        c.BRD_URL,
        c.STP_URL
    )

    ds.execute(SQL, PARAM)
    ds.commit()
    ds.close()


def get_all_clickboards():
    ds = datasource()
    ds.connect()

    ds.execute("SELECT CLICKBOARDS.*, USERDATA.NAME, USERDATA.LASTNAME FROM CLICKBOARDS JOIN USERDATA ON CLICKBOARDS.AUTHOR = USERDATA.ID")

    allClickboards = list()

    data = ds.fetch_all()
    ds.close()

    for x in data:
        allClickboards.append(fetch_data(x))

    return allClickboards
