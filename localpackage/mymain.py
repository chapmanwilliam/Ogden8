from dataClass import dataSet
from person import person
from game import game
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
dependent = {'age': 40, 'sex': 'Male', 'dataSet': Ogden7}
dependents=[dependent for a in range(1,3)]
claimant = {'age': 55, 'aai': 25, 'aad': 45, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLEB': 0, 'deltaLEA': -15}
claimants=[claimant for a in range(1,1)]
claimantdeceased = {'age': 55, 'aai': 25, 'aad':30, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLEB': -15, 'deltaLEA': -15}


row={'fromAge':55, 'toAge':70, 'freq': 'Y', 'name': 'Uninjured', 'cont':1, 'options':'AMI'}
rows=[row for a in range(1,200)]
eg={"rows": rows, 'game': {"discountRate": -0.005, "Ogden": 7, "claimants": [claimant], "dependents": [dependent]}}

g=game(eg)
print(g.claimants[0].MB('TRIAL', freq='<Y',options='AMI'))
print(g.claimants[0].MA(55,70, freq='<Y',options='AMI'))
print(g.dependents[0].MJ(40,60, freq='<Y',options='AMI'))
print(g.dependents[0].M(40,60, freq='<Y',options='AMI'))
#eg={"rows":[{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"},{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"}],"discountRate":-0.005,"Ogden":7,"claimants":[{"age":55,"aai":24.999315537303218,"sex":"Female","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLEB":-15,"deltaLEA":-15}],"dependents":[{"age":40,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011}}]}

#print(json.dumps(eg))

#print(receiver().receive(gamejs=json.dumps(eg)))

url="https://europe-west2-ogden8.cloudfunctions.net/ogden"
js=json.dumps(eg)
#print(js)
r=requests.post(url,json=js)
print(r.text)



