import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from fuzzywuzzy import process
import os
#from dotenv import load_dotenv

#boardgames = pd.read_csv('../data/boardgames.csv', index_col='id')
#boardgames_ext = pd.read_csv('../data/boardgames_extend_backup.csv', index_col='id')

#ratings = pd.read_csv('../data/ratings_cleaned.csv')

#users = pd.read_csv('../data/users.csv')
#load_env()
##uri = os.environ['CONNECT_AWS_POSTGRES_BOARDGAMEGEEKS']
#engine = create_engine(uri, echo=False)#
def create_max_id(engine):
    max_id = pd.read_sql('SELECT MAX(boardgameid) FROM boardgames', engine).loc[0].values[0]
    return max_id

def get_boardgame_names(engine):    
    boardgame_names = pd.read_sql('SELECT boardgamename FROM boardgames', engine)['boardgamename']
    return boardgame_names

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
    for i in df[df[column_name].notna()].iterrows():
        categories = categories + i[1][column_name].split(', ')
    categories = list(dict.fromkeys(categories))
    categories.sort()
    return categories


def ohe_user_boardgames(user, column, weight=False):
    '''
    returns a one-hot-encoded matrix of parameters in column of games played by user
    if weight = True, the encoding gets weighted by the rating
    '''
    print(f'start ohe of {column}')
    games_ohe={}
    print('start task: create ohe dataframe')
    df_column = user[[column,'rating']]
    df_column = df_column[df_column[column].notna()]
    user_categories = values_to_list(df_column, column)  
    for i in df_column.iterrows():
        game_vector = [0]*len(user_categories)
        for c in i[1][column].split(', '):
            index = user_categories.index(c)
            if weight == True:
                game_vector[index]=1 * i[1]['rating']
            else: 
                game_vector[index]=1
        games_ohe[i[0]] = game_vector
    df = pd.DataFrame(games_ohe)
    df = df.transpose()
    df.columns = user_categories
    print('task finished')
    print('start task: clean column names if required')
    if 'Deck' in user_categories:
        df['Deck, Bag and Pool Building'] = df['Deck']
        df.drop(columns=['Deck', 'Bag', 'and Pool Building'], inplace=True)
    if 'I Cut' in user_categories:
        df['I Cut, You Choose'] = df['I Cut']
        df.drop(columns=['I Cut', 'You Choose'], inplace=True)
    print('task finfihed')
    print(f'one hot encoding of {column}')
    return df

def rank_ohe_categories(df):
    return df.sum().sort_values(ascending=False).index.tolist()[:5]


def get_user_boardgame_ratings(user_name, engine):
    '''
    returns a user dataframe with 'boardgameid', 'rating', 'categories', 'machanics'
    '''
    print('start task: get user data from aws')
    query = f'''
    SELECT boardgames.boardgameid, boardgames.categories, boardgames.machanics,
    ratings.rating FROM ratings
    JOIN users ON users.userid = ratings.userid
    JOIN boardgames ON boardgames.boardgameid = ratings.boardgameid
    WHERE users.username = '{user_name}'
    '''
    user = pd.read_sql(query, engine)
    print('task completed')
    return user

def create_new_user(new_user, engine):
    boardgamenames = '\',\''.join(new_user['boardgames'])
    query = f'''
    SELECT boardgameid, categories, machanics FROM boardgames
    WHERE boardgamename IN('{boardgamenames}');
    '''
    user = pd.read_sql(query, engine)
    user['rating'] = new_user['ratings']
    return user

def lookup_boardgamenames(search_queries, titles):
    """
    given a search query, uses fuzzy string matching to search for similar
    strings in a pandas series of movie titles

    returns a list of search results. Each result is a tuple that contains
    the title, the matching score and the movieId.
    """
    matches =[]
    for q in search_queries:
        match = process.extractOne(q, titles)
        print(f'for {q} I looked up {match}')
        matches.append(match[0])
    # [(title, score, movieId), ...]
    return matches