import mysql.connector
import env as e
# env (enviorment) is the env.py file where all of the
# variables are stored for the database access create
# your own file with all the needed variables (see below)


def openDBConnection():
    db = mysql.connector.connect(
        host=e.db_host,
        user=e.db_username,
        passwd=e.db_password,
        database=e.db_database
    )
    return db
