from typing import Optional

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
        database=e.db_database,
        autocommit=True,
        connect_timeout=900
    )
    return db


class datasource:
    db_conn: mysql.connector.MySQLConnection
    cursor: mysql.connector.MySQLConnection.cursor

    def connect(self):
        self.db_conn = openDBConnection()
        self.cursor = self.db_conn.cursor()

    def execute(self, SQL: str, PARAM: Optional[tuple] = None):
        if PARAM is not None:
            self.cursor.execute(SQL, PARAM)
        else:
            self.cursor.execute(SQL)

    def fetch_row(self):
        return self.cursor.fetchone()

    def fetch_all(self):
        return self.cursor.fetchall()

    def fetch_dict(self):
        return dict(zip(self.cursor.column_names, self.cursor.fetchone()))

    def commit(self):
        self.db_conn.commit()

    def close(self):
        self.cursor.close()
        self.db_conn.close()
