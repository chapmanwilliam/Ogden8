from localpackage.game import game
from localpackage import sartable, pidrtable

import json
import math

# CORS headers for the actual request and for the preflight (OPTIONS) request.
CORS_HEADERS = {'Access-Control-Allow-Origin': '*'}
PREFLIGHT_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST',
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


# These handlers are invoked directly by the Google Cloud (Cloud Run) Functions runtime with a
# flask-style `request`; the deployed entry point is `Process`. (A former FastAPI wrapper here was
# dead scaffolding — F60 — and was removed because its pinned starlette blocked the build.)
def Multiplier(request):
    # returns an array of (past, interest, future, total) tuples, one per input row
    return _handle(request, lambda a: game(attributes=a).processRows())


def InterestHouse(request):
    return _handle(request, lambda a: game(attributes=a).processRowsInterestHouse())


def Reversion(request):
    return _handle(request, lambda a: game(attributes=a).processRowsReversion())


def Cont(request):
    def compute(attributes):
        g = game(attributes=attributes)
        name = attributes.get('name')  # was attributes['name'] -> KeyError if absent (F58)
        claimant = g.getClaimant(name)
        if claimant is None:  # unknown name: other endpoints degrade; /Cont/ used to crash (F58)
            raise ValueError("Unknown or missing claimant name: " + str(name))
        return claimant.getAutoCont()

    return _handle(request, compute)


def _is_sar_request(request):
    # GET .../ogden-2/sar (or ?sar) returns the Special Account Rate table. Every other
    # request is the JSON POST the clients have always sent.
    if request.method != 'GET':
        return False
    path = (request.path or '').rstrip('/')
    return path.endswith('/sar') or path == 'sar' or 'sar' in request.args


def Sar(request):
    # The canonical Special Account Rate table, so clients can read it live and sar-watch
    # can confirm a deploy landed. Cached for an hour at most: a rate change is announced
    # weeks ahead of its effective date, so an hour's staleness never changes an answer.
    try:
        body = json.dumps(sartable.table())
        return (body, 200, {**CORS_HEADERS, 'Content-Type': 'application/json',
                            'Cache-Control': 'public, max-age=3600'})
    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, CORS_HEADERS)


def _is_pidr_request(request):
    # GET .../ogden-2/pidr (or ?pidr) returns the Personal Injury Discount Rate table.
    if request.method != 'GET':
        return False
    path = (request.path or '').rstrip('/')
    return path.endswith('/pidr') or path == 'pidr' or 'pidr' in request.args


def Pidr(request):
    # The canonical discount rate table, so the web page can pick its default rate live and
    # sar-watch can confirm a deploy landed. Cached for an hour at most, as /sar is; a new
    # rate is announced weeks ahead of its effective date, so an hour's staleness is harmless.
    try:
        body = json.dumps(pidrtable.table())
        return (body, 200, {**CORS_HEADERS, 'Content-Type': 'application/json',
                            'Cache-Control': 'public, max-age=3600'})
    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, CORS_HEADERS)


def Process(request):
    # returns per-row tuples plus per-claimant summary statistics
    if _is_sar_request(request):
        return Sar(request)
    if _is_pidr_request(request):
        return Pidr(request)
    return _handle(request, lambda a: game(attributes=a).process())


def Explain(request):
    # EXPLAIN: returns, per MULTIPLIER row, {result, explanation} — a structured audit trail of how
    # the multiplier was computed. Forces explain on; pass explainTable:true for the per-age table.
    # Additive endpoint; does not affect the others. (EXPLAIN)
    def compute(a):
        a = dict(a)
        a['explain'] = True
        a.setdefault('function', 'MULTIPLIER')
        return game(attributes=a).processRows()

    return _handle(request, compute)
