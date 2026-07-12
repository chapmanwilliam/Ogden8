from localpackage.game import game
from fastapi import FastAPI

import json
import math

# NOTE (F60): the FastAPI app/decorators below are dead scaffolding — the untyped `request`
# parameter cannot be served as a real ASGI route (every POST 422s). In production Google Cloud
# Functions invokes these handler functions directly with a flask-style request, which is the
# path they are written for. Left in place pending confirmation of the deployment config;
# recommend removing the FastAPI wrapper (and the fastapi dependency) if ASGI is not used.
app = FastAPI()

# CORS headers for the actual request and for the preflight (OPTIONS) request.
CORS_HEADERS = {'Access-Control-Allow-Origin': '*'}
PREFLIGHT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
}


def _sanitize(obj):
    # json.dumps emits NaN/Infinity, which Apps Script's JSON.parse rejects. Replace any
    # non-finite float with null so the Sheet always receives valid JSON. (F57)
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, (list, tuple)):
        return [_sanitize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    return obj


def _attributes(request):
    request_json = request.get_json()  # dict, or a JSON string that needs loading
    if isinstance(request_json, dict):
        return request_json
    return json.loads(request_json)


def _handle(request, compute):
    # Shared handler: CORS preflight, JSON parse, compute, and a single try/except so a
    # malformed payload or an internal error returns a parseable JSON error WITH CORS headers
    # instead of a bare 500 with no body. (F58)
    if request.method == 'OPTIONS':
        return ('', 204, PREFLIGHT_HEADERS)
    try:
        attributes = _attributes(request)
        result = compute(attributes)
        return (json.dumps(_sanitize(result)), 200, CORS_HEADERS)
    except Exception as e:
        return (json.dumps({'error': str(e)}), 400, CORS_HEADERS)


@app.post("/Multiplier/")
def Multiplier(request):
    # returns an array of (past, interest, future, total) tuples, one per input row
    return _handle(request, lambda a: game(attributes=a).processRows())


@app.post("/InterestHouse/")
def InterestHouse(request):
    return _handle(request, lambda a: game(attributes=a).processRowsInterestHouse())


@app.post("/Reversion/")
def Reversion(request):
    return _handle(request, lambda a: game(attributes=a).processRowsReversion())


@app.post("/Cont/")
def Cont(request):
    def compute(attributes):
        g = game(attributes=attributes)
        name = attributes.get('name')  # was attributes['name'] -> KeyError if absent (F58)
        claimant = g.getClaimant(name)
        if claimant is None:  # unknown name: other endpoints degrade; /Cont/ used to crash (F58)
            raise ValueError("Unknown or missing claimant name: " + str(name))
        return claimant.getAutoCont()

    return _handle(request, compute)


@app.post("/Process/")
def Process(request):
    # returns per-row tuples plus per-claimant summary statistics
    return _handle(request, lambda a: game(attributes=a).process())
