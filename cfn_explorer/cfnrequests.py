import requests
from bs4 import BeautifulSoup


class CFNRequest:

    base_url        = "https://www.streetfighter.com/"
    rank_lp_url_old = "6/buckler/ranking/league"
    rank_lp_url     = "6/buckler/_next/data/0g-OtaI_DSAQVV_p9TUej/en/ranking/league.json"

    def __init__(self, token):
        self.token = token

    def get_lp_paginated (self, page, new_url=True,  league_rank=0, char= 1, platform= 1):
        """"Get the players data for a set page on the SF6 League points Ranking

        :Args:
        - page: the page desired
        - new_url: use the updated url that return an json directly, if using the old url the object 'pageProps' will be inside 'props' 
        - league_rank: filter for diferent league ranks  
        - char: filter to select the main char of the player
        - platform: filter for diferent gaming platforms

        :return: a Json file containing all data related to league Points
        """

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

        headers = {
            "accept-language": "en-US",
            "user-agent"     : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Cookie"         : "buckler_id=" + self.token
        }

        request_url = self.base_url + (self.rank_lp_url if new_url else self.rank_lp_url_old)
       
        response = requests.request("GET", request_url, params= params, headers= headers)

        if response.status_code == 200:
            if new_url:
                return response.text
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                script = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"}).text

                return script
        else:
            raise Exception("status: {}".format(response.status_code))
        
    
    
