"""Provides an interface for a SQlite database that suports the SF6 data collection"""
import sqlite3
import logging
import json

initial_version = 10000
initial_values = "./data/values.json"

table_player   = """players (
                Id          INT PRIMARY KEY,
                Name        TEXT,
                HomeId      INT,
                LastPlayed  INT,
                ContentType INT,
                PlayTime    INT,
                Plataform   INT,
                Crossplay   INT
                )"""

table_pxc      = """playerchar (
                PlayerId    INT,
                CharacterID INT,
                LeagueRank  INT,
                LP          INT,
                MR          INT,
                CONSTRAINT PK_PlayChar PRIMARY KEY (PlayerId, CharacterID)
                )""" 

table_char     = """characters (
                Id   INT PRIMARY KEY,
                Name TEXT,
                ToolName TEXT
                )"""

table_league   = """leagues(
                Id   INT PRIMARY KEY,
                Name TEXT
                )"""

table_home     = """homes(
                Id   INT PRIMARY KEY,
                Name TEXT
                )"""

table_platform = """platforms(
                Id   INT PRIMARY KEY,
                Name TEXT
                )"""

table_version  = """version(
                K0 INT,
                DBVer INT
                )"""


def initialize_db(conn):
    tables = [table_player, table_pxc, table_char, table_league, table_home, table_platform, table_version]

    for table in tables:
        __create_table(conn, table)

    with open(initial_values, "r") as file:
            values = json.loads(file.read())
            file.close()

    chars = values.get("character_values")
    leagues = values.get("League_values")
    homes = values.get("Home_values")
    
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO version VALUES ( 0, {} )""".format(initial_version))
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


def create_connection(db_path):
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

def __create_table(conn, createtable_sql):
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE IF NOT EXISTS {}".format(createtable_sql) )
        c.close()
        conn.commit()
    except Exception as e:
        logging.error("Could not create table, error: {}".format(e))
    finally:
        c.close()

def get_size(conn, table):
    c = conn.cursor()

    try:
        c.execute("SELECT COUNT(*) FROM {}".format(table))
        size = c.fetchone()[0]
    except Exception as e:
        logging.error("Could not get table size, error: {}".format(e))
    finally:
        c.close()

    return size

def insert_many(conn, table, data):
    """"Insert a list of data where each data is a row on the table. 
    Each Data must have the same number of intens as the number of columns on the table
    :args:
    - conn: connection to db
    - table: table where the data will be inserted
    - data: a list of tuples where the tuples have data for all the columns on the table"""
    c =conn.cursor()
    
    values = ""
    insert_size = len(data[0])

    for i in range(insert_size):
        values = values + "?"
        if i < (insert_size - 1):
            values = values + ", "
    
    query = "INSERT OR IGNORE INTO {} VALUES ( {} ) \n".format(table, values)

    c.executemany(query, data)
    conn.commit()
    c.close()

