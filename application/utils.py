import pandas as pd
import numpy as np

boardgames = pd.read_csv('../data/boardgames.csv', index_col='id')

#ratings_small has the correct header! ratings won't
ratings = pd.read_csv('../data/ratings_cleaned.csv')

def lookup_boardgame(ids):    
    '''
    converts boardgame ids into boardgame names
    '''
    return boardgames.loc[ids, 'name'].tolist()

def create_user_vector(user_name):
    '''
    returns a 1d array of the ratings of one user
    unrated boardgames = 0
    '''
    user = create_user_ratings(user_name)
    vector_length = ratings['boardgame_id'].max()
    vector = np.repeat(0, vector_length+1)
    vector[user['boardgame_id']] = user['ratings']
    return vector

def create_user_ratings(user_name):
    user = ratings[ratings['user_name']==user_name]
    return user




