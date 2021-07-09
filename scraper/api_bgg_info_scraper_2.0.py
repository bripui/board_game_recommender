import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import random
import time
import logging


retry_strategy = Retry(
    total=10, 
    backoff_factor=1,
    respect_retry_after_header=True,
    status_forcelist=[429, 413, 502, 500],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)
# use the session object to make requests
#response = session.get(url)

logging.basicConfig(filename='api_info_scraper_2.0.log', 
                    level=logging.INFO)

boardgames = pd.read_csv('../data/boardgames.csv', index_col='id')
boardgames['categories'] = None
boardgames['mechanics'] = None
boardgames['family'] = None
boardgames['expansions'] = None
boardgames['integrations'] = None
boardgames['designers'] = None
boardgames['publishers'] = None

restart = False
#restart_page = 40
#restart_id = 463

step_width = 100
start_id = 30549 #Pandemic
start_index = boardgames.index.tolist().index(start_id)
end_index = start_index + step_width
boardgame_list = []

while start_index < len(boardgames.index):

    boardgame_list = boardgames.index[start_index:end_index].astype('str').tolist()
    ID = ','.join(boardgame_list)
    logging.info(f'movie id: {ID}')
    
    page = 1

    # request page 1 of game overview with user ratings and comments
    api_adress = f"https://www.boardgamegeek.com/xmlapi2/thing?id={ID}&ratingcomments=1&page={page}"
    response = session.get(api_adress)  
    logging.info(f'status {response.status_code} for {api_adress}')    
    
    xml = response.text
    soup = BeautifulSoup(xml, 'xml')

    maxitems = 0
    for item in soup.find_all('item'):

        boardgame_id = int(item.get('id'))
        ratings_page = int(item.find('comments').get('page'))
        logging.info(f'boardgame id: {boardgame_id}, page: {ratings_page}')

        if restart == False:
            categories = [link.get('value') for link in item.find_all('link', attrs={'type':'boardgamecategory'})]
            boardgames.loc[boardgame_id,'categories'] = ', '.join(categories)
            mechanics = [link.get('value') for link in item.find_all('link', attrs={'type':'boardgamemechanic'})]
            boardgames.loc[boardgame_id,'mechanics'] = ', '.join(mechanics)
            family = [link.get('value') for link in item.find_all('link', attrs={'type':'boardgamefamily'})]
            boardgames.loc[boardgame_id,'family'] = ', '.join(family)
            expansions = [link.get('value') for link in item.find_all('link', attrs={'type':'boardgameexpansion'})]
            boardgames.loc[boardgame_id,'expansions'] = ', '.join(expansions)
            integrations = [link.get('value') for link in item.find_all('link', attrs={'type':'boardgameintegration'})]
            boardgames.loc[boardgame_id,'integrations'] = ', '.join(integrations)
            designers = [link.get('value') for link in item.find_all('link', attrs={'type':'boardgamedesigner'})]
            boardgames.loc[boardgame_id,'designers'] = ', '.join(designers)
            publishers = [link.get('value') for link in item.find_all('link', attrs={'type':'boardgamepublisher'})]
            boardgames.loc[boardgame_id,'publishers'] = ', '.join(publishers)
            # update number of voters
            #boardgames.loc[boardgame_id, 'num_voters'] = total_items

            boardgames.to_csv('../data/boardgames_extend.csv')


    time.sleep(5)

    start_index = end_index
    end_index = start_index + step_width
    restart = False
