'''
This script edits the file 'ratings.csv'.
It provides user ids to each user, writes a user table 
and removes users with less a defined number of ratings 
from ratings table.
'''


from numpy.core.fromnumeric import sort
import pandas as pd

def create_users(ratings):
    '''
    returns a user table and creates user ids
    '''
    users = pd.DataFrame(ratings.value_counts('user_name'), columns=['num_ratings'])
    user_ids = list(range(0,len(users)))
    users['user_id'] = user_ids
    users.to_csv('../data/users.csv')
    return users

def apply_userids(ratings, users):
    '''
    returns a merged dataframe of ratings and users
    adds user_id and num_ratings to ratings table
    '''
    ratings = pd.merge(ratings, users, on='user_name')
    return ratings

def clean_dataframe(ratings, n_ratings):
    '''
    returns a cleaned ratings table containing boardgame_ids, user_ids and ratings
    removes users with less than n ratings
    '''
    users = create_users(ratings)
    ratings = apply_userids(ratings, users)
    #print(ratings.columns)
    ratings = ratings[ratings['num_ratings']>=n_ratings]
    ratings = ratings.drop(columns=['user_name','num_ratings'])
    return ratings



if __name__ == "__main__":

    #ratings = pd.read_csv('../data/ratings_small.csv')
    ratings = pd.read_csv('../data/ratings.csv', 
                           usecols=[0,1,2], 
                           names=['boardgame_id', 'user_name', 'ratings', 'comments']
                           )

    ratings_cleaned = clean_dataframe(ratings, 5)

    ratings_cleaned.to_csv('../data/ratings_cleaned.csv', index=False)


