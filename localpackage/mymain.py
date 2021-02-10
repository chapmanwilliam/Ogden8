from dataClass import dataSet
from person import person
from game import game
from pymaybe import maybe

from receiver import receiver
import numpy as np
import pandas as pd
import json
from utils import parsedateString, Ogden7,Ogden8
from TablesAD import TablesAD
from SAR import SAR
import requests



#t=TablesAD(8)
#print(t.getCont(sex='F',employed=False,qualification=1,disabled=True,age=33))


game1={ 'discountRate':-0.5/100, 'Ogden':7}
dependent = {'name': 'John', 'age': 40, 'sex': 'Male', 'dataSet': Ogden7, 'dependenton':'Christopher', 'retirementA':57, 'retirementB':57}

claimant = {'name':'Christopher', 'age': 55, 'aai': 25, 'sex': 'Male', 'dataSet': Ogden7, 'deltaLEB': 0, 'deltaLEA': 0, 'retirementA':67, 'retirementB': 67, 'contB':0.75, 'contA':0.75}

claimantdeceased = {'name': 'John', 'age': 55, 'aai': 25, 'aad':30, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLEB': -15, 'deltaLEA': -15, 'retirementA':67, 'retirementB':67}


row={'name': 'CHRISTOPHER','fromAge':55, 'toAge':125, 'freq': 'Y', 'status': 'Injured', 'options':'AMIC'}
rows=[row for a in range(1,2)]
eg={"rows": rows, 'game': {"discountRate": -0.005, "Ogden": 7, "claimants": [dependent,claimant]}}

g=game(eg)
print(g.processRows())
print(g.getClaimant('JOHN').M('1/10/2010', 125, status='Injured', freq='Y',options='AMICD'))
print(g.getClaimant('JOHN').M(55, 125, status='Injured', freq='Y',options='AMID'))
#print(g.getClaimant('CHRISTOPHER').M(55, 125, status='Injured', freq='Y',options='AMI'))
#print(g.claimants['JOHN'].MB(55,70, freq='<Y',options='AMI'))
#print(g.dependents['JOHN'].MJ(40,60, freq='<Y',options='AMI'))
#print(g.dependents['JOHN'].M(40,60, freq='<Y',options='AMI'))
#eg={"rows":[{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"},{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"}],"discountRate":-0.005,"Ogden":7,"claimants":[{"age":55,"aai":24.999315537303218,"sex":"Female","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLEB":-15,"deltaLEA":-15}],"dependents":[{"age":40,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011}}]}

#print(json.dumps(eg))

#print(receiver().receive(gamejs=json.dumps(eg)))

url="https://europe-west2-ogden8.cloudfunctions.net/ogden"
js=json.dumps(eg)
print(js)
r=requests.post(url,json=js)
print(r.text)



