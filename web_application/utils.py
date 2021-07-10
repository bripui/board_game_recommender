import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
#from dotenv import load_dotenv

#boardgames = pd.read_csv('../data/boardgames.csv', index_col='id')
#boardgames_ext = pd.read_csv('../data/boardgames_extend_backup.csv', index_col='id')

#ratings = pd.read_csv('../data/ratings_cleaned.csv')

#users = pd.read_csv('../data/users.csv')
#load_env()
uri = os.environ['CONNECT_AWS_POSTGRES_BOARDGAMEGEEKS']
engine = create_engine(uri, echo=False)#

def list_to_query(ids):
    ids_str = [str(i) for i in ids]
    ids_str = ','.join(ids_str)
    return ids_str

def lookup_boardgame(ids):    
    '''
    converts boardgame ids into boardgame names
    '''    
    ids_str = list_to_query(ids)
    query = f'SELECT boardgamename FROM boardgames WHERE boardgameid IN ({ids_str});'
    request = pd.read_sql(query, engine)
    return request['boardgamename'].tolist()

def lookup_user_id(user_name):
    '''
    returns the user id of a user
    '''
    query = f'''SELECT userid FROM users WHERE username = '{user_name}';'''
    user_id = pd.read_sql(query, engine )['userid'][0]
    return user_id

def create_user_ratings(user_name):
    '''
    returns a dataframe with rated boardgames for a specified user
    '''
    user_id = lookup_user_id(user_name)
    query = f'''SELECT boardgameid,rating, userid FROM ratings WHERE userid = {user_id};'''
    user = pd.read_sql(query, engine)
    return user

def create_user_vector(user_name):
    '''
    returns a 1d array of the ratings of one user
    unrated boardgames = 0
    '''
    user = create_user_ratings(user_name)
    query = '''SELECT MAX(boardgameid) FROM boardgames;'''
    vector_length = pd.read_sql(query, engine)['max'][0]
    vector = np.repeat(0, vector_length+1)
    vector[user['boardgameid']] = user['rating']
    return vector

def values_to_list(df, column_name):
    categories = []
    query = f'''SELECT {column_name} FROM boardgames;'''
    df = pd.read_sql(query, engine)
    for i in df[df[column_name].notna()].iterrows():
        categories = categories + i[1][column_name].split(', ')
    categories = list(dict.fromkeys(categories))
    categories.sort()
    return categories


def ohe_user_boardgames(user_name, column, weight=False):
    '''
    returns a one-hot-encoded matrix of parameters in column of games played by user
    if weight = True, the encoding gets weighted by the rating
    '''
    games_ohe={}
    user_id = users[users['user_name']==user_name]['user_id'].tolist()[0]
    user_ratings = ratings[ratings['user_id']==user_id].set_index('boardgame_id')
    user_boardgames = boardgames_ext.loc[user_ratings.index]
    user_boardgames = user_boardgames[user_boardgames[column].notna()]
    user_categories = values_to_list(user_boardgames, column)    
    for i in user_boardgames.iterrows():
        game_vector = [0]*len(user_categories)
        for c in i[1][column].split(', '):
            index = user_categories.index(c)
            if weight == True:
                game_vector[index]=1 * user_ratings.loc[i[0]]['ratings']
            else: 
                game_vector[index]=1
        games_ohe[i[0]] = game_vector
    df = pd.DataFrame(games_ohe)
    df = df.transpose()
    df.columns = user_categories
    return df

def user_rated_boardgames(user_name):
    '''
    returns lists of boardgame_id, boardgame_name and rating of users votes
    '''
    query = f'''
        SELECT boardgames.boardgameid, boardgames.boardgamename, ratings.rating FROM boardgames
        JOIN ratings ON ratings.boardgameid = boardgames.boardgameid
        JOIN users ON users.userid = ratings.userid
        WHERE users.username = '{user_name}'
        ORDER BY ratings.rating DESC;
        '''
    df = pd.read_sql(query, engine)
    return df['boardgameid'].tolist(), df['boardgamename'].tolist(), df['rating'].tolist()
