import pandas as pd
import random
import pickle
from application.utils import create_user_vector, lookup_boardgame, create_user_ratings, user_rated_boardgames, list_to_query
from application.utils import engine

with open('./models/knn_model_cosine.pickle', 'rb') as file:
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
    distances, neighbor_ids = model.kneighbors([user_vector], n_neighbors=10)
    neighbor_ids = list_to_query(neighbor_ids[0])
    boardgame_ids, boardgame_names, ratings = user_rated_boardgames(user_name)
    boardgame_ids = list_to_query(boardgame_ids)
    query = f'''
        SELECT boardgames.boardgamename, AVG(ratings.rating) FROM ratings 
        JOIN boardgames ON boardgames.boardgameid = ratings.boardgameid
        WHERE ratings.userid IN({neighbor_ids}) AND ratings.boardgameid NOT IN ({boardgame_ids})
        GROUP BY boardgames.boardgamename
        ORDER BY avg DESC
        LIMIT 20;
        '''
    return pd.read_sql(query, engine)['boardgamename'].tolist()
