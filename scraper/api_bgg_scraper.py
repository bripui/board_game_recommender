import pandas as pd
import requests
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

logging.basicConfig(filename='api_scraper.log', 
                    level=logging.INFO)

boardgames =pd.read_csv('../data/boardgames.csv', index_col='id')
boardgames['categories'] = None
boardgames['mechanics'] = None
boardgames['family'] = None
boardgames['expansions'] = None
boardgames['integrations'] = None
boardgames['designers'] = None
boardgames['publishers'] = None

sleep_default = 2

for ID in boardgames.index:
    logging.info(f'movie id: {ID}')
    
    user_ratings = []
    users = []
    comments = []
    ratings = pd.DataFrame()
    page = 1
    
    # request page 1 of game overview with user ratings and comments
    api_adress = f"https://www.boardgamegeek.com/xmlapi2/thing?id={ID}&ratingcomments=1&page={page}"
    response = requests.get(api_adress)  
    logging.info(f'status {response.status_code} for {api_adress}')    
    
    xml = response.text
    soup = BeautifulSoup(xml, 'xml')
    
    # get the number of pages of ratings
    total_items = soup.find('comments').get('totalitems')
    logging.info(f'total items: {total_items}')
    pagecount = calculate_pagecount(total_items)
    logging.info(f'pagecount: {pagecount}')
    logging.info(f'start scraping page {page} of {pagecount}')

    
    # extend boardgames dataframe 
    categories = [link.get('value') for link in soup.find_all('link', attrs={'type':'boardgamecategory'})]
    boardgames.loc[ID,'categories'] = ', '.join(categories)
    mechanics = [link.get('value') for link in soup.find_all('link', attrs={'type':'boardgamemechanic'})]
    boardgames.loc[ID,'mechanics'] = ', '.join(mechanics)
    family = [link.get('value') for link in soup.find_all('link', attrs={'type':'boardgamefamily'})]
    boardgames.loc[ID,'family'] = ', '.join(family)
    expansions = [link.get('value') for link in soup.find_all('link', attrs={'type':'boardgameexpansion'})]
    boardgames.loc[ID,'expansions'] = ', '.join(expansions)
    integrations = [link.get('value') for link in soup.find_all('link', attrs={'type':'boardgameintegration'})]
    boardgames.loc[ID,'integrations'] = ', '.join(integrations)
    designers = [link.get('value') for link in soup.find_all('link', attrs={'type':'boardgamedesigner'})]
    boardgames.loc[ID,'designers'] = ', '.join(designers)
    publishers = [link.get('value') for link in soup.find_all('link', attrs={'type':'boardgamepublisher'})]
    boardgames.loc[ID,'publishers'] = ', '.join(publishers)
    
    # update number of voters
    boardgames.loc[ID, 'num_voters'] = total_items
    
    boardgames.to_csv('../data/boardgames_extend.csv', index=False)
    
    #get user ratings from page 1
    for comment in soup.find_all('comment'):
        user_ratings.append(comment.get('rating'))
        users.append(comment.get('username'))
        comments.append(comment.get('value')) 
        
    boardgame_id = [ID] * len(user_ratings)

    ratings = pd.DataFrame({
        'id':boardgame_id,
        'user':users,
        'rating':user_ratings,
        'comment':comments
    })
        
    ratings.to_csv('../data/ratings.csv', index=False, header=None, mode='a')
    
    # if more than one page of comments send request for each page
    if pagecount > page:
        page = page + 1

        while page <= pagecount:
            logging.info(f'start scraping page {page} of {pagecount}')
            user_ratings = []
            users = []
            comments = []
            ratings = pd.DataFrame()
            
            api_adress = f"https://www.boardgamegeek.com/xmlapi2/thing?id={ID}&ratingcomments=1&page={page}"
            response = requests.get(api_adress)
            logging.info(f'status {response.status_code} for {api_adress}')
            
            if response.status_code != 200:
                logging.warning(f'STATUS {response.status_code}, increase sleep time and try again')
                time.sleep(10)
                sleep_default = 5
                
            else:
            
                xml = response.text
                soup = BeautifulSoup(xml, 'xml')

                for comment in soup.find_all('comment'):
                    user_ratings.append(comment.get('rating'))
                    users.append(comment.get('username'))
                    comments.append(comment.get('value'))

                boardgame_id = [ID] * len(user_ratings)

                ratings = pd.DataFrame({
                    'id':boardgame_id,
                    'user':users,
                    'rating':user_ratings,
                    'comment':comments
                })

                ratings.to_csv('../data/ratings.csv', index=False, header=False, mode='a')

                page = page + 1
                time.sleep(sleep_default+random.random())

