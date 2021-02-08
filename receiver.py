import json
import numpy as np
from game import game


class receiver():

    def receive(self,gamejs,rowsjs):
        #takes json for game and rows
        #sets up entire game
        #returns vector of answers
        g=game(attributes=json.loads(gamejs))
        rows=json.loads(rowsjs)
        a=np.array([g.claimants[0].MB(row['fromAge'], row['toAge'], freq=row['freq'], cont=row['cont'], options=row['options']) for row in rows])
        return a




