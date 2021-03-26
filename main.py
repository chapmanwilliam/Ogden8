from localpackage.game import game
from fastapi import FastAPI

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
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    request_json = request.get_json() #gets json string from request

    if isinstance(request_json,dict):
        attributes=request_json #it is already a dictionary
    else:
        attributes=json.loads(request_json) #takes a json string and loads it into python dictionary

    #returns an array of tuples (past,interest,future,total), one for each row

    return (json.dumps(game(attributes=attributes).processRows()), 200, headers)

@app.post("/Cont/")
def Cont(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    request_json = request.get_json() #gets json string from request

    if isinstance(request_json,dict):
        attributes=request_json #it is already a dictionary
    else:
        attributes=json.loads(request_json) #takes a json string and loads it into python dictionary

    #returns an array of tuples (past,interest,future,total), one for each row

    g=game(attributes=attributes);


    return (json.dumps(game(attributes=attributes).processRows()), 200, headers)
