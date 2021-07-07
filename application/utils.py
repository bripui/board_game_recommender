import pandas as pd

boardgames = pd.read_csv('../data/boardgames.csv')

#ratings_small has the correct header! ratings won't
ratings = pd.read_csv('../data/ratings_small.csv')

users = pd.DataFrame(ratings.value_counts('user_name'), columns=['ratings'])
user_ids = list(range(0,len(users)))
users['user_id'] = user_ids
users = users.set_index('user_name')

def select_users(n_ratings):
    '''
    returns only users witch more than the defined number of ratings
    '''
    users[users['ratings'] > n_ratings]
    return users['user_id']



