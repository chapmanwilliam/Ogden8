"""The Special Account Rate table as the engine serves it: GET /sar.

The CSV in localpackage/Data is the canonical table for every Ogden product
(see README). Serving it lets the clients read the live table instead of
carrying copies, and lets sar-watch confirm a deploy took.
"""
import csv
import os
from datetime import datetime

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data', 'SAR.csv')
SOURCE = 'https://www.gov.uk/search/news-and-communications?keywords=court+funds+office+interest+rate&organisations[]=ministry-of-justice'


def load_rows(path=CSV_PATH):
    """[{'date': 'YYYY-MM-DD', 'ratePct': 3.75}, ...] in date order."""
    rows = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        if [h.strip() for h in header[:2]] != ['Dt', 'Rate']:
            raise ValueError('SAR.csv: expected header Dt,Rate, got %r' % header)
        for line in reader:
            if not line or not line[0].strip():
                continue
            d = datetime.strptime(line[0].strip(), '%d/%m/%Y').date()
            rows.append({'date': d.isoformat(), 'ratePct': float(line[1])})
    rows.sort(key=lambda r: r['date'])
    return rows


def table():
    rows = load_rows()
    return {
        'name': 'Court Funds Office Special Account Rate',
        'source': SOURCE,
        'unit': 'percent per annum, simple, in force from each date until the next',
        'count': len(rows),
        'last': rows[-1],
        'rates': rows,
    }
