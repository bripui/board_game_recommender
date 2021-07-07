import pandas as pd
import random
import pickle
from utils import boardgames, ratings, create_user_vector, lookup_boardgame, create_user_ratings

with open('../models/small_model.pickle', 'rb') as file:
    model = pickle.load(file)

def random_recommender(N):
    '''
    returns a list of N random boardgames
    '''
    rec_ids = []
    for n in range(0,N):
        rec_ids.append(random.choice(boardgames.index))
        recommendations = lookup_boardgame(rec_ids)
    return recommendations

def neighbor_recommender(user_name):
    '''
    returns a list of boardgame recommendations
    '''
    user_ratings = create_user_ratings(user_name)
    user_vector = create_user_vector(user_name)
    distances, neighbor_ids = model.kneighbors([user_vector], n_neighbors=20)
    neighbor_filter = ratings['user_id'].isin(neighbor_ids[0][1:])
    neighbor_ratings = ratings[neighbor_filter].groupby('boardgame_id').mean()
    neighbor_top = neighbor_ratings['ratings'].sort_values(ascending=False)
    played_filter = ~neighbor_top.index.isin(user_ratings['boardgame_id'])
    recommend_ids = neighbor_top[played_filter].index
    return boardgames.loc[recommend_ids]['name'].tolist()