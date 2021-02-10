from localpackage.game import game
from fastapi import FastAPI
from pymaybe import maybe

import json

app=FastAPI()

@app.post("/Multiplier/")
def Multiplier(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    request_json = request.get_json() #gets json string from request

    if isinstance(request_json,dict):
        attributes=request_json #it is already a dictionary
    else:
        attributes=json.loads(request_json) #takes a json string and loads it into python dictionary

    g = game(attributes=attributes)
    rows = attributes['rows']
    a = [maybe(g.claimants[row['name']]).M(row['fromAge'], row['toAge'], status=row['status'],freq=row['freq'], options=row['options']) for row in rows]

#    a=[]
#    for row in rows:
#        if g.getClaimant(row['name']):
#            a.append(g.getClaimant(row['name']).M(row['fromAge'], row['toAge'], status=row['status'],freq=row['freq'], options=row['options']))
#        else:
#            a.append([None,None,None,None])

#    print(g.getClaimant('CHRISTOPHER').M(55, 125, status='Injured', freq='Y', options='AMIC'))

    return json.dumps(a)

