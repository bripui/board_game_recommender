import pandas as pd
import numpy as np
import random
import pickle
import logging
from sklearn.neighbors import NearestNeighbors
from application.utils import create_user_vector, create_user_ratings, list_to_query

logging.basicConfig(filename='debug.log', 
                    level=logging.WARNING)

MODELPATH='./models/nmf_50.pickle'

#with open('./models/knn_model_cosine.pickle', 'rb') as file:
#    model = pickle.load(file)

with open(MODELPATH, 'rb') as file:
    nmf = pickle.load(file)
    logging.debug('model path: ' + MODELPATH)

#with open('./models/P_50', 'rb') as file:
#    P = np.load(file)    


def random_recommender(N, engine):
    '''
    returns a list of N random boardgames
    '''
    query = '''
            SELECT boardgameid, boardgamename FROM boardgames
            '''
    boardgames = pd.read_sql(query, engine)
    boardgames = boardgames.set_index('boardgameid')
    print(boardgames.head())
    rec_names = []
    for n in range(0,N):
        rec_id = random.choice(boardgames.index)
        logging.debug(rec_id)
        rec_name = boardgames.loc[rec_id, 'boardgamename']
        rec_names.append(rec_name)
    return rec_names


#multiple sql queries, not cleaned yet!
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

#multiple sql queries, not cleaned yet! modelname is P and not model
def knn_nmf_recommender_sql(user_name):
    '''
    returns recommendations for a user based on a combined knn and nmf model
    '''
    user_vector = create_user_vector(user_name)
    knn = NearestNeighbors(metric='cosine')
    knn.fit(P)
    vector_transformed = nmf.transform([user_vector])
    vector_transformed = vector_transformed.T.reshape(50,)
    distances, neighbor_ids = knn.kneighbors([vector_transformed], n_neighbors=20)
    print(neighbor_ids)
    neighbor_ids = list_to_query(neighbor_ids[0])
    user_ratings = create_user_ratings(user_name)
    boardgame_ids, boardgame_names, ratings = user_rated_boardgames(user_name)
    boardgame_ids = list_to_query(boardgame_ids)
    query = f'''
            SELECT COUNT(ratings.boardgameid), boardgames.boardgamename, AVG(ratings.rating) FROM ratings 
            JOIN boardgames ON boardgames.boardgameid = ratings.boardgameid
            WHERE ratings.userid IN({neighbor_ids}) AND ratings.boardgameid NOT IN ({boardgame_ids}) 
            GROUP BY boardgames.boardgamename
            HAVING count(*)>4
            ORDER BY avg DESC
            LIMIT 15
            '''
    return pd.read_sql(query, engine)['boardgamename'].tolist()


def nmf_recommender(user, max_id, engine):
    '''
    takes user dataframe containing 'boardgameid', 'rating', 'categories', 'machanics'
    this dataframe can be created with get_user_boardgame_ratings() from utils
    takes the highest boardgame id (max_id) which can be created with create_max_id() from utils
    returns recommendations
    '''
    logging.debug('start nmf recommender')
    logging.debug('start task: create user vector')
    user_vector = np.repeat(0, max_id+1)
    user_vector[user['boardgameid']] = user['rating']
    logging.debug('task finished')

    logging.debug('start task: transform user vector')
    P = nmf.transform([user_vector])
    Q = nmf.components_
    predictions = np.dot(P, Q)   
    logging.debug('task finished') 

    logging.debug('start task: get recommendation ids')
    #prediction include ids from 0 to length of user_vector
    #pseudo ids for constructing a dataframe
    pseudo_ids = list(range(0,len(user_vector)))
    df = pd.DataFrame(predictions, columns=pseudo_ids)
    #sort values: existing ids will be first, non-existing ids last (due to 0 value)
    recommendations_all = df.T.sort_values(0, ascending=False)
    recommendations_all = recommendations_all.reset_index()
    recommendations_all.columns = ['pseudo_id', 'pred_rating']
    boardgame_ids = user['boardgameid']
    #filter already played ids from recommendations_all
    recommendations_all = recommendations_all[~recommendations_all['pseudo_id'].isin(boardgame_ids)]
    recommendation_ids = recommendations_all.head(15)['pseudo_id']
    recommendation_ids = list_to_query(recommendation_ids)
    logging.debug('task finished')

    logging.debug('start task: get recommendation boardgames from aws')
    query = f'''
            SELECT boardgameid, boardgamename FROM boardgames
            WHERE boardgameid IN({recommendation_ids})
            '''
    recommendations = pd.read_sql(query, engine)
    logging.debug('task finished')
    logging.debug('nmf recommender finished')

    return recommendations['boardgamename'].tolist()