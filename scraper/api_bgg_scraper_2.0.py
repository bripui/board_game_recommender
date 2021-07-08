import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import random
import time
import logging

def calculate_pagecount(total_items):
    if int(total_items)%100 ==0:
        pages = int(total_items)//100
    else:
        pages = (int(total_items)//100)+1
    return pages

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

logging.basicConfig(filename='api_scraper_2.0.log', 
                    level=logging.INFO)

boardgames_raw = pd.read_csv('../data/boardgames.csv')
boardgames = pd.read_csv('../data/boardgames_extend.csv')
boardgames['id'] = boardgames_raw['id']
boardgames = boardgames.set_index('id')
#boardgames['categories'] = None
#boardgames['mechanics'] = None
#boardgames['family'] = None
#boardgames['expansions'] = None
#boardgames['integrations'] = None
#boardgames['designers'] = None
#boardgames['publishers'] = None

restart = True
restart_page = 40
#restart_id = 463

step_width = 100
start_id = 245934
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
        total_items = int(item.find('comments').get('totalitems'))
        if total_items > maxitems:
            maxitems = total_items

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
            boardgames.loc[boardgame_id, 'num_voters'] = total_items

            boardgames.to_csv('../data/boardgames_extend.csv', index=False)

            #initialize lists and dataframe
            boardgame_ids = []
            user_ratings = []
            users = []
            user_comments = []
            ratings = pd.DataFrame()

            for comment in item.find_all('comment'):
                boardgame_ids.append(boardgame_id)
                user_ratings.append(comment.get('rating'))
                users.append(comment.get('username'))
                user_comments.append(comment.get('value')) 

            ratings = pd.DataFrame({
                            'boardgame_id':boardgame_ids,
                            'user_name': users,
                            'rating': user_ratings,
                            'comment': user_comments
                            })

            ratings.to_csv('../data/ratings.csv', index=False, header=None, mode='a')

    max_pagecount = calculate_pagecount(maxitems)

    if restart == False:
        nextpage = 2
    else: 
        nextpage = restart_page
    for page in range(nextpage,max_pagecount+1):

        api_adress = f"https://www.boardgamegeek.com/xmlapi2/thing?id={ID}&ratingcomments=1&page={page}"
        response = session.get(api_adress)  
        logging.info(f'status {response.status_code} for {api_adress}')    
    
        xml = response.text
        soup = BeautifulSoup(xml, 'xml')

        for item in soup.find_all('item'):
            boardgame_id = item.get('id')
            ratings_page = int(item.find('comments').get('page'))
            logging.info(f'boardgame id: {boardgame_id}, page: {ratings_page}')

            boardgame_ids = []
            user_ratings = []
            users = []
            user_comments = []
            ratings = pd.DataFrame() 

            for comment in item.find_all('comment'):
                boardgame_ids.append(boardgame_id)
                user_ratings.append(comment.get('rating'))
                users.append(comment.get('username'))
                user_comments.append(comment.get('value')) 

            ratings = pd.DataFrame({
                    'boardgame_id':boardgame_ids,
                    'user_name': users,
                    'rating': user_ratings,
                    'comment': user_comments
                    })

            ratings.to_csv('../data/ratings.csv', index=False, header=None, mode='a')

        time.sleep(10)

    start_index = end_index
    end_index = start_index + step_width
    restart = False
