import requests
import logging
from bs4 import BeautifulSoup
from aiohttp import ClientSession


class CFNAPI:

    BASE_URL        = "https://www.streetfighter.com/"
    RANK_LP_URL_OLD = "6/buckler/ranking/league"
    RANK_LP_URL     = "6/buckler/_next/data/7R1j0S8w9k0X3T3Db5_0h/en/ranking/league.json"

    def __init__(self, token):
        self.token = token

    def get_lp_paginated (self, page, league_rank=0, char= 1, platform= 1, json_url=True):
        """"Get the players data for a set page on the SF6 League points Ranking

        :Args:
        - page: the page desired
        - new_url: use the updated url that return an json directly, if using the old url the object 'pageProps' will be inside 'props' 
        - league_rank: filter for diferent league ranks  
        - char: filter to select the main char of the player
        - platform: filter for diferent gaming platforms

        :return: a Json file containing all data related to league Points
        """

        params  = CFNAPIUtils.params_lp_paginated(page, char, league_rank, platform )
        headers = CFNAPIUtils.general_header(self.token)
        url     = self.BASE_URL + (self.RANK_LP_URL if json_url else self.RANK_LP_URL_OLD)
       
        response = requests.request("GET", url, params= params, headers= headers)

        if response.status_code == 200:
            if json_url:
                return response.text
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                script = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"}).text

                return script
        else:
            raise Exception(f"status: {response.status_code}")
        
    async def aio_get_lp_paginated(self, session: ClientSession, page: int, league_rank=0, char= 1, platform= 1, json_url= True):
        """"the player's data for a selected page on the SF6 League points Ranking

        :Args:
        - session: instance of aiohttp.ClientSession()
        - page: the page desired
        - league_rank: filter for diferent league ranks  
        - char: filter to select the main char of the player
        - platform: filter for diferent gaming platforms

        :return: a Json file containing all data related to league Points
        """
        logging.debug(f"aio_get_lp_paginated({page}, {league_rank}, {char}, {platform},{json_url})")
        
        params  = CFNAPIUtils.params_lp_paginated(page, char, league_rank, platform )
        headers = CFNAPIUtils.general_header(self.token)
        url     = self.BASE_URL + (self.RANK_LP_URL if json_url else self.RANK_LP_URL_OLD)

        async with session.get(url,params= params, headers= headers) as response:
            if  response.status == 200:
                if json_url:
                    return await response.text()
                else:
                    soup = BeautifulSoup( await response.text(), "html.parser")
                    script = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"}).text

                    return script
            else:
                raise Exception(f"status: {response.status}, page:{page}")

class CFNAPIUtils:

    @staticmethod
    def general_header(token):
        headers = {
            "accept-language": "en-US",
            "user-agent"     : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Cookie"         : "buckler_id=" + token
        }
        return headers

    @staticmethod
    def params_lp_paginated(page= 1, char= 1, league_rank= 0, platform= 1):
        params = {
                "character_filter": char,
                "character_id"    : "luke",
                "platform"        : platform,
                "user_status"     : 1,
                "home_filter"     : 1,
                "home_category_id": 0,
                "home_id"         : 1,
                "league_rank"     : league_rank,
                "page"            : page
            }
        return params