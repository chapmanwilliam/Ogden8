from localpackage.game import game
import json



def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    row = {'fromAge': 35, 'toAge': 60, 'freq': 'Y', 'name': 'Uninjured', 'cont': 1, 'options': 'AMI'}
    rows = [row for a in range(1, 20)]
    eg = {"rows": rows, "discountRate": -0.005, "Ogden": 7, "claimants": [
        {"age": 55, "aai": 24.999315537303218, "sex": "Female",
         "dataSet": {"year": 2008, "region": "UK", "yrAttainedIn": 2011}, "deltaLEB": -15, "deltaLEA": -15}],
          "dependents": [{"age": 40, "sex": "Male", "dataSet": {"year": 2008, "region": "UK", "yrAttainedIn": 2011}}]}

    gamejs = json.dumps(eg)

#    attributes = json.loads(gamejs)
    g = game(attributes=eg)
#    rows = attributes['rows']

    request_json = request.get_json()
#    x=json.loads(request_json)
#    g = game(attributes=x)
#    rows = x['rows']

    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'