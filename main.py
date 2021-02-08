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

    request_json = request.get_json()

    return request_json

    attributes=json.loads(request_json)
    g = game(attributes=attributes)
    rows = attributes['rows']
    a = [g.claimants[0].MB(row['fromAge'], row['toAge'], freq=row['freq'], cont=row['cont'], options=row['options']) for row in rows]

    return json.dumps(a)
