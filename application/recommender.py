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
    distances, neighbor_ids = model.kneighbors([user_vector], n_neighbors=20)
    neighbor_filter = (ratings['user_id'].isin(neighbor_ids[0][1:]))
    user_played_filter = (~ratings['boardgame_id'].isin(user_ratings['boardgame_id']))
    #create df only with neighboars and unplayed boardgames
    neighbor_ratings = ratings[neighbor_filter&user_played_filter]
    #filter for boardgames which have been played by more than 5 neighbors, groupby boardgames and order by the mean of ratings
    value_counts = pd.DataFrame(neighbor_ratings['boardgame_id'].value_counts())
    value_counts.columns = ['count']
    frequently_played = value_counts[value_counts['count']>5].index
    frequently_played_filter = (neighbor_ratings['boardgame_id'].isin(frequently_played))
    neighbor_taste = neighbor_ratings[frequently_played_filter].groupby('boardgame_id').mean().sort_values('ratings', ascending=False)
    recommend_ids = neighbor_taste.index
    return boardgames.loc[recommend_ids]['name'].tolist()[:10]

def nmf_recommender(user_name):
    user_vector = create_user_vector(user_name)
    user_ratings = create_user_ratings(user_name)
    P = nmf.transform([user_vector])
    Q = nmf.components_
    predictions = np.dot(P, Q)
    #prediction include ids from 0 to length of user_vector
    #pseudo ids for constructing a dataframe
    pseudo_ids = list(range(0,len(user_vector)))
    df = pd.DataFrame(predictions, columns=pseudo_ids)
    recommendations_all = df.T.sort_values(0, ascending=False)
    recommendations_all = recommendations_all.reset_index()
    recommendations_all.columns = ['pseudo_id', 'pred_rating']
    #merging with boardgames dataframe keeps only existing boardgameids
    boardgames_merge = boardgames[['name']].reset_index()
    prediction_df = pd.merge(boardgames_merge[['id','name']], recommendations_all, left_on='id', right_on='pseudo_id', how='left')
    prediction_df = prediction_df.set_index('id')
    played_by_user = user_ratings['boardgame_id']
    played_filter = ~prediction_df.index.isin(played_by_user)
    return prediction_df.loc[played_filter].sort_values('pred_rating', ascending=False).head(15)['name'].tolist()


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
