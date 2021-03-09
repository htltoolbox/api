from models import user
from assets.database import datasource
from typing import Optional
from models.app import App

ds = datasource()
ds.connect()


def getApp(ID: Optional[int] = None, NAME: Optional[str] = None, API_KEY: Optional[str] = None):
    global SQL, PARAM
    if ID is not None:
        SQL = "SELECT * FROM toolbox.APPS WHERE ID = %s"
        PARAM = (ID,)
    elif NAME is not None:
        SQL = "SELECT * FROM toolbox.APPS WHERE NAME = %s"
        PARAM = (NAME,)
    elif API_KEY is not None:
        SQL = "SELECT * FROM toolbox.APPS WHERE API_KEY = %s"
        PARAM = (API_KEY,)
    ds.execute(SQL, PARAM)
    data = ds.fetch_dict()
    return App(**data)

