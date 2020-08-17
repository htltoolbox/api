import mysql.connector
from env import *
# env (enviorment) is the env.py file where all of the
# variables are stored for the database access create
# your own file with all the needed variables (see below)


def openDBConnection():
    db = mysql.connector.connect(
        host=host,
        user=username,
        passwd=password,
        database=database
    )
    return db
