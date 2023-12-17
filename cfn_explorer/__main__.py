import database
from cfnbrowser import Logger
from cfnrequests import CFNRequest

import json
import logging
from os.path import exists
from jproperties import Properties

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
    
if __name__ == '__main__':
    main()



    
