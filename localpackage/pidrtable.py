"""The Personal Injury Discount Rate table as the engine serves it: GET /pidr.

The CSV in localpackage/Data is the canonical table for every Ogden product
(see README): one row per change, for each of the three jurisdictions that
set their own rate. The web page reads it live to choose its default discount
rate, and the engine's own default (utils.defaultDiscountRate) comes from it.

  Jurisdiction  EW  England and Wales   set by the Lord Chancellor
                SC  Scotland            set by the Government Actuary
                NI  Northern Ireland    set by the Government Actuary
  Dt            dd/mm/yyyy, the day the rate took effect
  Rate          percent per annum; negative rates are written with a minus

Rows are in date order (then jurisdiction). The table starts at the first
rate each product has ever needed; earlier history is not held.
"""
import csv
import os
from datetime import date, datetime

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'PIDR.csv')
SOURCE = 'https://www.gov.uk/guidance/personal-injury-discount-rate'
JURISDICTIONS = {'EW': 'England and Wales', 'SC': 'Scotland', 'NI': 'Northern Ireland'}


def load_rows(path=CSV_PATH):
    """[{'jurisdiction': 'EW', 'date': 'YYYY-MM-DD', 'ratePct': 0.5}, ...] in date order."""
    rows = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        if [h.strip() for h in header[:3]] != ['Jurisdiction', 'Dt', 'Rate']:
            raise ValueError('PIDR.csv: expected header Jurisdiction,Dt,Rate, got %r' % header)
        for line in reader:
            if not line or not line[0].strip():
                continue
            j = line[0].strip()
            if j not in JURISDICTIONS:
                raise ValueError('PIDR.csv: unknown jurisdiction %r' % j)
            d = datetime.strptime(line[1].strip(), '%d/%m/%Y').date()
            rows.append({'jurisdiction': j, 'date': d.isoformat(), 'ratePct': float(line[2])})
    rows.sort(key=lambda r: (r['date'], r['jurisdiction']))
    for j in JURISDICTIONS:
        if not any(r['jurisdiction'] == j for r in rows):
            raise ValueError('PIDR.csv: no rows for %s' % j)
    return rows


def current(rows, jurisdiction, on=None):
    """The row in force in `jurisdiction` on the date `on` (today by default):
    the latest row for it dated on or before that day."""
    on = (on or date.today()).isoformat()
    hits = [r for r in rows if r['jurisdiction'] == jurisdiction and r['date'] <= on]
    if not hits:
        raise ValueError('PIDR.csv: no %s rate in force on %s' % (jurisdiction, on))
    return hits[-1]


def current_rate(jurisdiction='EW', on=None):
    """The rate in force, as a percentage."""
    return current(load_rows(), jurisdiction, on)['ratePct']


def table():
    rows = load_rows()
    return {
        'name': 'Personal Injury Discount Rate',
        'source': SOURCE,
        'unit': 'percent per annum, in force in each jurisdiction from each date until the next',
        'jurisdictions': JURISDICTIONS,
        'count': len(rows),
        'current': {j: current(rows, j) for j in JURISDICTIONS},
        'rates': rows,
    }
