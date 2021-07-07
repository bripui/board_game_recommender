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
    users = pd.DataFrame(ratings.value_counts('user_name'), columns=['ratings'])
    user_ids = list(range(0,len(users)))
    users['user_id'] = user_ids
    users.to_csv('../data/users.csv')
    return users

def sort_out_users(ratings, users, n_ratings):
    '''
    returns ratings of users who have rated more than n boardgames
    '''
    remaining_users = users[users['ratings']>n_ratings]
    user_filter = ratings['user_name'].isin(remaining_users.index)
    remaining_ratings = ratings[user_filter]
    return remaining_ratings

def apply_userids(ratings, users):
    ratings['user_id'] = None
    for row in ratings.iterrows():
        username = row[1]['user_name']
        user_id = users.loc[username][1]
        ratings.loc[row[0], 'user_id'] = user_id
        ratings.drop(columns=['user_name'])
        print(username, user_id)
    return ratings

if __name__ == "__main__":

    ratings = pd.read_csv('../data/ratings_small.csv')
    #ratings = pd.read_csv('../data/ratings.csv', 
    #                       names=['boardgame_id, 'user_name', 'ratings', 'comments']
    #                       )

    users = create_users(ratings)
    ratings_cleaned = sort_out_users(ratings, users, 1)
    apply_userids(ratings_cleaned, users)

    ratings_cleaned.to_csv('../data/ratings_cleaned.csv', index=False)


