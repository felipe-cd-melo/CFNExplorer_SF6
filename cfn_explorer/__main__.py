import database
from cfnscraper import Logger
from cfnrequests import CFNAPI

import json
import logging
import asyncio
import aiohttp
import aiosqlite
import time
from os.path import exists
from jproperties import Properties
from datetime import datetime

#paths
TOKEN_HOME      = "./data/token.txt"
DB_HOME         = "./data/sf6Players.db"
PROPERTIES_HOME = "./app.properties"

#json_objects
PROPS          = "props"
PAGE_PROPS     = "pageProps"
LEAGUE_RANKING = "league_point_ranking"
FIGHTER_BANNER = "fighter_banner_info"
PERSONAL_INFO  = "personal_info"
MAX_CONTENT    = "max_content_play_time"

is_url_json = True

configs: Properties = Properties()

async def main():
    if not exists(DB_HOME):
        conn = database.create_connection(DB_HOME)

        database.initialize_db(conn)
        conn.close()

    with open(PROPERTIES_HOME, "rb") as config_file:
        configs.load(config_file)
        config_file.close()
    
    token = get_token()

    service = CFNAPI(token)
    initial_data = league_ranking_todata(service.get_lp_paginated(1, json_url= is_url_json))

    max_pages = initial_data.get("total_page")
    min_page = 2
    steps = 40

    insert_list = []

    insert_list.append(normalize_player_data(initial_data.get("ranking_fighter_list")))

    for pmin in range(min_page, max_pages + 1, steps):
        time_check = time.time()

        if pmin + steps > max_pages:
            pmax = max_pages
        else:
            pmax = pmin + steps - 1

        logging.info(f"Fetching pages: {pmin} to {pmax}")

        response_list = await collect_league_ranking(service, pmin, pmax)

        for response in response_list:
            resp = league_ranking_todata(response)
            play_data = normalize_player_data(resp.get("ranking_fighter_list"))
            insert_list.append(play_data)

        await insert_league_ranking(insert_list)

        insert_list = []

        #if time.time() - time_check < 30:
        time.sleep(30)

def get_token():
    """validade if there is a valid token. If not, log on capcom website to retrive one and save for future use.

    :return: valid token for the REST calls
    """
    
    token_ok = False

    if exists(TOKEN_HOME):
        with open(TOKEN_HOME, "r") as file:
            new_token = file.readline()
            file.close()

        try:
            CFNAPI(new_token).get_lp_paginated(1, json_url=is_url_json)
            token_ok = True
            logging.info("Valid token found")
        except Exception as e:
            logging.info("Token is not valid anymore")

    if not token_ok:
        logging.info("updating token....")
        logger = Logger(configs.get("login.email").data, configs.get("login.secret").data)
        new_token = logger.cfn_login()

    with open(TOKEN_HOME, "w") as file:
            file.writelines(new_token)
            file.close()
    
    return new_token

def insert_players(players_characters: dict):
    """save the players and their characters infromation on the db

    :args:
    - players_characters: a dict containg both "players" and "characters" lists"""

    conn = database.create_connection(DB_HOME)

    database.insert_many(conn, "players"   , players_characters.get("players"))
    database.insert_many(conn, "playerchar", players_characters.get("characters"))

    conn.commit()
    conn.close()

async def insert_league_ranking(data_list: list):
    async with aiosqlite.connect(DB_HOME) as conn:
        tasks = []

        for data in data_list:
            task_p = asyncio.ensure_future(database.aio_insert_many(conn, "players", data.get("players")))
            task_c = asyncio.ensure_future(database.aio_insert_many(conn, "playerchar", data.get("characters")))

            tasks.append(task_p)
            tasks.append(task_c)

        await asyncio.gather(*tasks)
        
        await conn.commit()

def normalize_player_data(players_data: dict):
    """normalize the players and their characters infromation for manipulation

    :args:
    - players_data: a dict containg the ranking_fighter_list object from de request json"""
    players = []
    characters = []

    for player_data in players_data:
        p_id         = player_data.get(FIGHTER_BANNER).get(PERSONAL_INFO).get("short_id")
        p_name       = player_data.get(FIGHTER_BANNER).get(PERSONAL_INFO).get("fighter_id")
        p_platform   = player_data.get(FIGHTER_BANNER).get(PERSONAL_INFO).get("platform_id")
        p_home       = player_data.get(FIGHTER_BANNER).get("home_id")
        p_crossplay  = player_data.get(FIGHTER_BANNER).get("allow_cross_play")
        p_favcontent = player_data.get(FIGHTER_BANNER).get(MAX_CONTENT).get("content_type")
        p_playtime   = player_data.get(FIGHTER_BANNER).get(MAX_CONTENT).get("play_time")
        p_lastplayed = player_data.get(FIGHTER_BANNER).get("last_play_at")

        p = (p_id, p_name, p_platform, p_home, p_crossplay, p_favcontent, p_playtime, p_lastplayed)
        
        pc_id      = player_data.get("character_id")
        pc_control = player_data.get(FIGHTER_BANNER).get("battle_input_type")
        pc_league  = player_data.get("league_rank")
        pc_lp      = player_data.get("league_point")
        pc_mr      = player_data.get("master_rating")

        c = (p_id, pc_id, pc_control, pc_league, pc_lp, pc_mr)

        players.append(p)
        characters.append(c)
    
    return {"players":players, "characters": characters}

async def collect_league_ranking(service: CFNAPI, start, stop):
        async with aiohttp.ClientSession() as session:
            tasks = []

            for i in range(start, (stop + 1)):
                task = service.aio_get_lp_paginated(session, i, json_url= is_url_json)
                tasks.append(asyncio.ensure_future(task))
            
            return await asyncio.gather(*tasks)

def league_ranking_todata(response: str):
    data = json.loads(response)
    if is_url_json:
        return data.get(PAGE_PROPS).get(LEAGUE_RANKING)
    else:
        return data.get(PROPS).get(PAGE_PROPS).get(LEAGUE_RANKING)

if __name__ == '__main__':
    logging.basicConfig(level= logging.INFO, format= "%(asctime)s:%(levelname)s:%(message)s")

    asyncio.run(main())

    conn = database.create_connection(DB_HOME)
    data = database.get_tabe_data(conn, "playerchar")
    print(len(data))


    
