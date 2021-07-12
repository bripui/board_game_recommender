import pandas as pd
import numpy as np

boardgames = pd.read_csv('./data/boardgames_extend.csv', index_col='id')

ratings = pd.read_csv('./data/ratings_cleaned.csv')

users = pd.read_csv('./data/users.csv')


def lookup_boardgame(ids):    
    '''
    converts boardgame ids into boardgame names
    '''
    return boardgames.loc[ids, 'name'].tolist()

def lookup_user_id(user_name):
    '''
    returns the user id of a user
    '''
    user_id = users[users['user_name']==user_name]['user_id'].tolist()[0]
    return user_id

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
    '''
    returns a dataframe with rated boardgames for a specified user
    '''
    user_id = lookup_user_id(user_name)
    user = ratings[ratings['user_id']==user_id]
    return user

def values_to_list(df, column_name):
    categories = []
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
    user_boardgames = boardgames.loc[user_ratings.index]
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