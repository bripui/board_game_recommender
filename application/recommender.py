import pandas as pd
import numpy as np
import random
import pickle
from sklearn.neighbors import NearestNeighbors
from application.utils import boardgames, ratings, create_user_vector, lookup_boardgame, create_user_ratings

with open('./models/knn_model_cosine.pickle', 'rb') as file:
    model = pickle.load(file)

with open('./models/nmf_50.pickle', 'rb') as file:
    nmf = pickle.load(file)

with open('./models/P_50', 'rb') as file:
    P = np.load(file)    

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
    #create neigbors of user
    distances, neighbor_ids = model.kneighbors([user_vector], n_neighbors=10)
    print(neighbor_ids)
    print(distances)
    neighbor_filter = ratings['user_id'].isin(neighbor_ids[0][1:])
    #create mean retings of games, rated by the neighbors
    neighbor_ratings = ratings[neighbor_filter].groupby('boardgame_id').mean()
    #sort rated games by mean rating
    neighbor_top = neighbor_ratings['ratings'].sort_values(ascending=False)
    #remove games which user rated already
    played_filter = ~neighbor_top.index.isin(user_ratings['boardgame_id'])
    recommend_ids = neighbor_top[played_filter].index
    return boardgames.loc[recommend_ids]['name'].tolist()[:10]

def knn_nmf_recommender(user_name):
    user_vector = create_user_vector(user_name)
    knn = NearestNeighbors(metric='cosine')
    knn.fit(P)
    vector_transformed = nmf.transform([user_vector])
    vector_transformed = vector_transformed.T.reshape(50,)
    distances, neighbor_ids = knn.kneighbors([vector_transformed], n_neighbors=20)
    user_ratings = create_user_ratings(user_name)
    played_by_user = user_ratings['boardgame_id']
    neighbor_ratings = ratings[ratings['user_id'].isin(neighbor_ids[0][1:])]
    neighbor_ratings = neighbor_ratings[~neighbor_ratings['boardgame_id'].isin(played_by_user)]
    value_counts = pd.DataFrame(neighbor_ratings['boardgame_id'].value_counts())
    value_counts.columns = ['count']
    frequently_played = value_counts[value_counts['count']>=5].index
    recommendations = neighbor_ratings[neighbor_ratings['boardgame_id'].isin(frequently_played)].groupby('boardgame_id').mean().sort_values('ratings', ascending=False).head(15).index
    return boardgames.loc[recommendations]['name'].tolist()
