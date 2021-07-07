import pandas as pd
import random
from utils import boardgames

def lookup_boardgame(ids):    
    '''
    converts boardgame ids into boardgame names
    '''
    return boardgames.loc[ids, 'name'].tolist()

def random_recommender(N):
    '''
    returns a list of N random boardgames
    '''
    rec_ids = []
    for n in range(0,N):
        rec_ids.append(random.choice(boardgames.index))
        recommendations = lookup_boardgame(rec_ids)
    return recommendations