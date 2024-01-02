"""Provides an interface for a SQlite database that suports the SF6 data collection"""
import sqlite3
from sqlite3 import Connection
from aiosqlite import Connection as aioConnection
import logging
import json

VERSION = 10001

INITIAL_VALUES = "./data/values.json"

#data base tables
TABLE_PLAYERS   = """players (
                Id          INT PRIMARY KEY,
                Name        TEXT,
                HomeId      INT,
                LastPlayed  INT,
                ContentType INT,
                PlayTime    INT,
                Plataform   INT,
                Crossplay   INT
                )"""

TABLE_PXC       = """playerchar (
                PlayerId    INT,
                CharacterID INT,
                InputType   INT,
                LeagueRank  INT,
                LP          INT,
                MR          INT,
                CONSTRAINT PK_PlayChar PRIMARY KEY (PlayerId, CharacterID)
                )""" 

TABLE_CHARS     = """characters (
                Id   INT PRIMARY KEY,
                Name TEXT,
                ToolName TEXT
                )"""

TABLE_LEAGUES   = """leagues(
                Id   INT PRIMARY KEY,
                Name TEXT
                )"""

TABLE_HOMES     = """homes(
                Id   INT PRIMARY KEY,
                Name TEXT
                )"""

TABLE_PLATFORMS = """platforms(
                Id   INT PRIMARY KEY,
                Name TEXT
                )"""

TABLE_VERSION  = """version(
                K0 INT,
                DBVer INT
                )"""


def initialize_db(conn: Connection):
    tables = [TABLE_PLAYERS, TABLE_PXC, TABLE_CHARS, TABLE_LEAGUES, TABLE_HOMES, TABLE_PLATFORMS, TABLE_VERSION]

    for table in tables:
        __create_table(conn, table)

    with open(INITIAL_VALUES, "r") as file:
            values = json.loads(file.read())
            file.close()

    chars = values.get("character_values")
    leagues = values.get("League_values")
    homes = values.get("Home_values")
    
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO version VALUES ( 0, {} )""".format(VERSION))
        conn.commit()

        c.executemany("""INSERT OR IGNORE INTO characters VALUES ( :value, :name, :tool_name ) """, chars)
        conn.commit()

        c.executemany("""INSERT OR IGNORE INTO leagues VALUES ( :value, :label ) """, leagues)
        conn.commit()

        c.executemany("""INSERT OR IGNORE INTO homes VALUES ( :value, :label ) """, homes)
        conn.commit()

    except Exception as e:
        logging.error("cannot initiate database, erro: {}".format(e))
    finally:
        c.close()

def create_connection(db_path: str) -> Connection:
    """get a connection to the sqlite database

    :args:
    - db_path: database path
    :return: connection"""
    conn = None

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        logging.error("cannot connect to database, erro: {}".format(e))

    return conn

def __create_table(conn: Connection, createtable_sql: str):
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE IF NOT EXISTS {}".format(createtable_sql) )
        c.close()
        conn.commit()
    except Exception as e:
        logging.error("Could not create table, error: {}".format(e))
    finally:
        c.close()

def get_size(conn: Connection, table: str):
    c = conn.cursor()

    try:
        c.execute("SELECT COUNT(*) FROM {}".format(table))
        size: int = c.fetchone()[0]
    except Exception as e:
        logging.error("Could not get table size, error: {}".format(e))
    finally:
        c.close()

    return size

def insert_many(conn: Connection, table: str, data: list):
    """"Insert a list of data where each data is a row on the table. 
    Each Data must have the same number of intens as the number of columns on the table

    :args:
    - conn: connection to db
    - table: table where the data will be inserted
    - data: a list of tuples where the tuples have data for all the columns on the table"""
    c = conn.cursor()

    query = __insert_many_query(table, data)

    c.executemany(query, data)
    c.close()

async def aio_insert_many(conn: aioConnection, table: str, data: list):
    """"asynchronously Insert a list of data where each data is a row on the table. 
    Each Data must have the same number of intens as the number of columns on the table

    :args:
    - conn: iosqlite connection to db
    - table: table where the data will be inserted
    - data: list of tuples where the tuples have data for all the columns on the table"""
    query = __insert_many_query(table, data)
    try:
        await conn.executemany(query, data)
    except Exception as e:
        logging.warn(f"aio_insert_many:({query}\n{*data,})\n{e}")

def __insert_many_query(table: str, data: list):
    values = ""
    insert_size = len(data[0])

    for i in range(insert_size):
        values = values + "?"
        if i < (insert_size - 1):
            values = values + ", "
    
    query = "INSERT OR IGNORE INTO {} VALUES ( {} )".format(table, values)
    return query

def get_tabe_data(conn: Connection, table: str):
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM {}".format(table))
        data = c.fetchall()
    except Exception as e:
        logging.error("Could not get table data, error: {}".format(e))
    finally:
        c.close()

    return data