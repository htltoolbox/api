import mysql.connector
import env as e
# env (enviorment) is the env.py file where all of the
# variables are stored for the database access create
# your own file with all the needed variables (see below)


def openDBConnection():
    db = mysql.connector.connect(
        host=e.host,
        user=e.username,
        passwd=e.password,
        database=e.database
    )
    return db
