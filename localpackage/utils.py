import math
from datetime import datetime
from dateutil.parser import parse
from localpackage.errorLogging import errors

sexes=['Male','Female']
regions=['UK','EW','EN','SC','WA','NI','GB']
years=[2008, 2018]
wordPoints=['TRIAL', 'LIFE', 'RETIREMENT', 'INJURY']
plusMinus=['+','-']
fr=['Y','M','W','D','A']
discountOptions=['A','M','I','C','D']

defaultdiscountRate=-0.25/100
defaultSwiftCarpenterDiscountRate=5/100
defaultOgden=8
Ogden=[7,8]
ContDetailsdefault={'employed':True,'qualification':'D','disabled':False} #default
Ogden7={'year':2008,'region':'UK','yrAttainedIn':2011}
Ogden8={'year':2018,'region':'UK','yrAttainedIn':2022}


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def returnFreq(freq,fromAge=None, toAge=None):
    #where freq is a string '<3Y' meaning every 3 years starting at the first date
    #returns tuple of timedelta and whether < or >
    if len(freq)<1:
        errors.add("Nil length freq")
        return False, False, 1, None
    st=False
    en=False
    if freq[0]=='<': st=True
    if freq[-1]=='>': en=True
    if st and en: st=en=False #if both True turn them False
    f=freq.strip('<').strip('>') #remove arrows
    p=f[-1] #get main period Y,M,W,D
    if len(f)>1:
        if isfloat(f[:-1]):
            n=float(f[:-1])
        else:
            n=1
    else:
        n=1

    factor=1.0

    if p=='Y':
        tinterval=n #in years
        factor=1.0/n
    elif p=='M':
        tinterval=(n*1/12) #in years
        factor=12.0/n
    elif p=='W':
        tinterval=(n*1/52) #in years
        factor=52.0/n
    elif p=='D':
        tinterval=(n*1/365.25) #in years
        factor=365.25/n
    elif p=='A':
        tinterval=n
        if (not toAge==None and not fromAge==None):
            factor=1.0
        else:
            print("toAge and fromAge need to be specified for 'A' in returnFreq")
            errors.add("toAge and fromAge need to be specified for 'A' in returnFreq")
            factor=1.0/n
    else:
        #Error wrong period passed
        print('Wrong period passed to returnFreq')
        errors.add("Wrong period passed to returnFreq")
        return st, en, 1, None

    return st, en, factor, tinterval


def discountFactor(yrs,discountRate):
    #returns the discountFactor after yrs with discountRate
    if discountRate==-1:
        errors.add('Discount rate is -1')
        return None
    if yrs<0: return 1
    factor=1/(1+discountRate)
    return factor**yrs

def termCertain(yrs,discountRate):
    if discountRate==-1:
        errors.add('Discount rate is -1')
        return None
    if yrs==0:
        return 0
    factor=1/(1+discountRate)
    if factor==1:
        return 1+yrs
    else:
        return ((factor**yrs)/(math.log(factor)))-(1/math.log(factor))

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
    parts = text.split('/')
    d = int(parts[0])
    m = int(parts[1])
    y = int(parts[2])
    return datetime(y, m, d)
