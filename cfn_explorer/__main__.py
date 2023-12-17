import database
from cfnbrowser import Logger
from cfnrequests import CFNRequest

import json
import logging
from os.path import exists
from jproperties import Properties
from datetime import datetime

token_home = "./data/token.txt"
db_home = "./data/sf6Players.db"
configs= Properties()

def main():
    if not exists(db_home):
        conn = database.create_connection(db_home)

        database.initialize_db(conn)
        conn.close()


    with open("./app.properties", "rb") as config_file:
        configs.load(config_file)
        config_file.close
    
    token = get_token()

    request = CFNRequest(token)
    data = json.loads(request.get_lp_paginated(1)).get("pageProps").get("league_point_ranking")

    max_pages = data.get("total_page")
    players_data = data.get("ranking_fighter_list")

    insert_players(players_data)


    
def get_token():
    """validade if there is a valid token. If not, log on capcom website to retrive one and save for future use.
    :return: valid token for the REST calls
    """
    token_ok = False

    if exists(token_home):
        with open(token_home, "r") as file:
            new_token = file.readline()
            file.close()

        try:
            CFNRequest(new_token).get_lp_paginated(1)
            token_ok = True
        except Exception as e:
            logging.info("Token is not valid anymore")

    if not token_ok:
        logging.info("updating token....")
        logger = Logger(configs.get("login.email").data, configs.get("login.secret").data)
        new_token = logger.cfn_login()

    with open(token_home, "w") as file:
            file.writelines(new_token)
            file.close()
    
    return new_token

def insert_players(players_data):
    """Organize and save the players and their characters on the db
    :args:
    - players_data: a list of ranking_fhighters objects"""
    players = []
    characters = []

    for player_data in players_data:
        p_id         = player_data.get("fighter_banner_info").get("personal_info").get("short_id")
        p_name       = player_data.get("fighter_banner_info").get("personal_info").get("fighter_id")
        p_platform   = player_data.get("fighter_banner_info").get("personal_info").get("platform_id")
        p_home       = player_data.get("fighter_banner_info").get("home_id")
        p_crossplay  = player_data.get("fighter_banner_info").get("allow_cross_play")
        p_favcontent = player_data.get("fighter_banner_info").get("max_content_play_time").get("content_type")
        p_playtime   = player_data.get("fighter_banner_info").get("max_content_play_time").get("play_time")
        p_lastplayed = player_data.get("fighter_banner_info").get("last_play_at")

        p = (p_id, p_name, p_platform, p_home, p_crossplay, p_favcontent, p_playtime, p_lastplayed)
        
        pc_id     = player_data.get("character_id")
        pc_league = player_data.get("league_rank")
        pc_lp     = player_data.get("league_point")
        pc_mr     = player_data.get("master_rating")

        c = (p_id, pc_id, pc_league, pc_lp, pc_mr)

        players.append(p)
        characters.append(c)

    conn = database.create_connection(db_home)

    database.insert_many(conn, "players", players)
    database.insert_many(conn, "playerchar", characters)

    conn.close()



    
if __name__ == '__main__':
    main()



    
