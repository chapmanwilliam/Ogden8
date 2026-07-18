import math
from datetime import datetime
from dateutil.parser import parse
from localpackage.errorLogging import errors

sexes = ['Male', 'Female']
regions = ['UK', 'EW', 'EN', 'SC', 'WA', 'NI', 'GB']
years = [2008, 2018]
wordPoints = ['TRIAL', 'LIFE', 'RETIREMENT', 'INJURY']
plusMinus = ['+', '-']
fr = ['Y', 'M', 'W', 'D', 'A']
discountOptions = ['A', 'M', 'I', 'C', 'D']
DRMethods = ['BLENDED', 'SWITCHED', 'SINGLE', 'STEPPED']  # STEPPED is dispatched in getdiscountRate (F55)
overrides = ['DRMETHOD', 'SHORTRATE', 'LONGRATE', 'SINGLERATE', 'SWITCH', 'SEX', 'AGE', 'DEPENDENTON', 'REGION']

defaultdiscountRate = 0.5 / 100
defaultSwiftCarpenterDiscountRate = 5 / 100
defaultOgden = 8
Ogden = [7, 8]
ContDetailsdefault = {'employed': True, 'qualification': 'D', 'disabled': False}  # default
Ogden7 = {'year': 2008, 'region': 'UK', 'yrAttainedIn': 2011}
Ogden8 = {'year': 2018, 'region': 'UK', 'yrAttainedIn': 2022}
Ogden8_1 = {'year': 2020, 'region': 'UK', 'yrAttainedIn': 2024}
defaultMultipleRates = [{'rate': -0.015, 'switch': 15}, {'rate': 0.015, 'switch': 125}]


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def explainDiscountsText(options):
    # Human-readable description of the discount/option letters (mirrors VBA ExplainDiscounts). (EXPLAIN)
    o = (options or '').upper()
    parts = []
    if 'M' in o: parts.append('mortality')
    if 'A' in o: parts.append('accelerated receipt')
    if 'D' in o: parts.append('mortality of a deceased dependant')
    if 'C' in o: parts.append('contingencies other than mortality')
    s = ('discounted for ' + ', '.join(parts[:-1]) + (' and ' if len(parts) > 1 else '') + parts[-1]) if parts else 'no discounts'
    if 'I' in o:
        s += ', with interest on past losses'
    return s


def explainFrequencyText(freq):
    # Human-readable description of the frequency code (mirrors VBA ExplainFrequency). (EXPLAIN)
    f = (freq or 'Y').upper()
    start = f.startswith('<')
    end = f.endswith('>')
    core = f.strip('<').strip('>')
    unit = core[-1] if core else 'Y'
    num = core[:-1] if len(core) > 1 else '1'
    units = {'Y': 'year', 'M': 'month', 'W': 'week', 'D': 'day', 'A': 'period (averaged)'}
    base = 'continuous' if unit == 'Y' and num == '1' and not start and not end else ('every ' + num + ' ' + units.get(unit, unit))
    if unit == 'Y' and num == '1' and not start and not end:
        return 'continuous (annual, mid-year convention)'
    timing = ' in advance' if start else (' in arrears' if end else '')
    return base + timing


def returnFreq(freq, fromAge=None, toAge=None):
    # where freq is a string '<3Y' meaning every 3 years starting at the first date
    # returns tuple of timedelta and whether < or >
    if len(freq) < 1:
        errors.add("Nil length freq")
        return False, False, 1, None
    st = False
    en = False
    if freq[0] == '<': st = True
    if freq[-1] == '>': en = True
    if st and en: st = en = False  # if both True turn them False
    f = freq.strip('<').strip('>')  # remove arrows
    if len(f) < 1:  # e.g. a bare '<' or '>' -> nothing left to index. (F49)
        errors.add("'Frequency' invalid")
        return st, en, 1, None
    p = f[-1]  # get main period Y,M,W,D
    if len(f) > 1:
        if isfloat(f[:-1]):
            n = float(f[:-1])
        else:
            n = 1
    else:
        n = 1

    if n <= 0:  # a zero/negative count would ZeroDivisionError (factor = 1.0/n) or invert. (F34/F49)
        errors.add("'Frequency' invalid")
        return st, en, 1, None

    factor = 1.0

    if p == 'Y':
        tinterval = n  # in years
        factor = 1.0 / n
    elif p == 'M':
        tinterval = (n * 1 / 12)  # in years
        factor = 12.0 / n
    elif p == 'W':
        tinterval = (n * 1 / 52)  # in years
        factor = 52.0 / n
    elif p == 'D':
        tinterval = (n * 1 / 365.25)  # in years
        factor = 365.25 / n
    elif p == 'A':
        tinterval = n
        if (not toAge == None and not fromAge == None):
            factor = 1.0
        else:
            print("toAge and fromAge need to be specified for 'A' in returnFreq")
            errors.add("toAge and fromAge need to be specified for 'A' in returnFreq")
            factor = 1.0 / n
    else:
        # Error wrong period passed
        print('Wrong period passed to returnFreq')
        errors.add("Wrong period passed to returnFreq")
        return st, en, 1, None

    return st, en, factor, tinterval


def discountFactor(yrs, discountRate):
    # returns the discountFactor after yrs with discountRate
    if discountRate == -1:
        errors.add('Discount rate is -1')
        return None
    if yrs < 0: return 1
    factor = 1 / (1 + discountRate)
    return factor ** yrs


def termCertain(yrs, discountRate):
    if discountRate == -1:
        errors.add('Discount rate is -1')
        return None
    if yrs == 0:
        return 0
    factor = 1 / (1 + discountRate)
    if factor == 1:
        return yrs
    else:
        return ((factor ** yrs) / (math.log(factor))) - (1 / math.log(factor))


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def parsedate(text):
    return parse(text, dayfirst=True)


def parsedateString(text):
    # text is of format d/m/y
    try:
        parts = str(text).split('/')
        if len(parts) != 3:
            errors.add("Date not in d/m/y format: " + str(text))
            return None
        d = int(parts[0])
        m = int(parts[1])
        y = int(parts[2])
    except (ValueError, TypeError):
        errors.add("Invalid date: " + str(text))
        return None
    if y < 100:
        # Pivot 2-digit years (Excel convention: <30 -> 20xx, else 19xx) so '27/2/85' is 1985,
        # not the year 85 AD. (F50) — flagged: pivot window is a convention choice.
        y += 2000 if y < 30 else 1900
    return datetime(y, m, d)


def parseOverrides(text):
    # text is like this:
    # {DRMethod: BLENDED, ShortRate: -3%, LongRate: 3%, SingleRate: 2%, Sex: MALE, Age: 20, DependentOn: Norman, Region: UK }
    result = {}
    text = text.replace("{", "").replace("}", "")  # remove braces
    textSplit = text.split(',')  # split at the commas
    for x in textSplit:  # iterate through each split
        y = x.split(":", 1)  # split at the FIRST colon only
        if len(y) < 2:  # segment without a colon (typo / trailing comma) -> skip, don't IndexError (F22/F48)
            if x.strip():
                errors.add("Override segment without a colon ignored: " + x.strip())
            continue
        f = y[0].strip().upper()  # the key (upper-cased for matching)
        p = y[1].strip()  # the value — kept verbatim so mixed-case names (DependentOn) survive (F30/F48)
        if f in overrides:  # if a valid function
            result[f] = p
        #else: unrecognised override key — silently ignored (as before)
    return result
