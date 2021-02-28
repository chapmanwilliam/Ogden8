import math
from datetime import datetime
from dateutil.parser import parse
sexes=['Male','Female']
regions=['UK','EW','EN','SC','WA','NI','GB']
years=[2008,2018]
wordPoints=['TRIAL', 'LIFE', 'RETIREMENT']
plusMinus=['+','-']
fr=['Y','M','W','D']
discountOptions=['A','M','I','C','D']

defaultdiscountRate=-0.5/100
defaultOgden=8
Ogden=[7,8]
ContDetailsdefault={'employed':True,'qualification':'D','disabled':False} #default
Ogden7={'year':2008,'region':'UK','yrAttainedIn':2011}
Ogden8={'year':2018,'region':'UK','yrAttainedIn':2022}


def returnFreq(freq):
    #where freq is a string '<3Y' meaning every 3 years starting at the first date
    #returns tuple of timedelta and whether < or >
    st=False
    en=False
    if freq[0]=='<': st=True
    if freq[-1]=='>': en=True
    if st and en: st=en=False #if both True turn them False
    f=freq.strip('<').strip('>') #remove arrows
    p=f[-1] #get main period Y,M,W,D
    if len(f)>1:
        if f[:-1].isnumeric():
            n=float(f[:-1])
        else:
            n=1
    else:
        n=1

    factor=1

    if p=='Y':
        tinterval=n #in years
        factor=1/n
    elif p=='M':
        tinterval=(n*1/12) #in years
        factor=12.0/n
    elif p=='W':
        tinterval=(n*1/52) #in years
        factor=52/n
    elif p=='D':
        tinterval=(n*1/365.25) #in years
        factor=365.25/n
    elif p=='A':
        pass
    else:
        #Error wrong period passed
        print('Wrong period passed to returnFreq')
        return st, en, 1, 1

    return st, en, factor, tinterval


def discountFactor(yrs,discountRate):
    #returns the discountFactor after yrs with discountRate
    if discountRate==-1: return None
    if yrs<0: return 1
    factor=1/(1+discountRate)
    return factor**yrs

def termCertain(yrs,discountRate):
    if discountRate==-1: return None
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
