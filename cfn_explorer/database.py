import sqlite3
import logging
from os.path import exists

initial_version = 10000

table_player   = """players (
                Id         INT PRIMARY KEY,
                Name       TEXT,
                HomeId     INT,
                LastPlayed INT,
                PlayTime   INT,
                Plataform  INT,
                Crossplay  INT,
                )"""

table_pxc      = """playchar (
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
        __setup_table(conn, table)
    
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO version VALUES ( 0, {} )""".format(initial_version))
        conn.commit()


    except Exception as e:
        logging.error("cannot initiate database, erro: {}".format(e))
    finally:
        c.close()


def create_connection(db_path):
    conn = None

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        logging.error("cannot connect to database, erro: {}".format(e))

    return conn

def __setup_table(conn, createtable_sql):
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



if __name__ == '__main__':
    db_ready = exists("./data/sf6Players.db")

    conn = create_connection("./data/sf6Players.db")

    if not db_ready:
        initialize_db(conn)

    c = conn.cursor()
    c.execute("SELECT * FROM version")

    print(c.fetchall())

    c.close()
    conn.close()

