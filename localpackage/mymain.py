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
from main import hello_world
import requests



#t=TablesAD(8)
#print(t.getCont(sex='F',employed=False,qualification=1,disabled=True,age=33))


game1={ 'discountRate':-0.5/100, 'Ogden':7}
dependent = {'age': 40, 'sex': 'Male', 'dataSet': Ogden7}
dependents=[dependent for a in range(1,3)]
claimant = {'age': 55, 'aai': 25, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLEB': -15, 'deltaLEA': -15}
claimants=[claimant for a in range(1,1)]
claimantdeceased = {'age': 55, 'aai': 25, 'aad':30, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLEB': -15, 'deltaLEA': -15}


row={'fromAge':35, 'toAge':60, 'freq': 'Y', 'name': 'Uninjured', 'cont':1, 'options':'AMI'}
rows=[row for a in range(1,20)]
eg={"rows": rows, "discountRate": -0.005, "Ogden": 7, "claimants": [{"age": 55, "aai": 24.999315537303218, "sex": "Female", "dataSet": {"year": 2008, "region": "UK", "yrAttainedIn": 2011}, "deltaLEB": -15, "deltaLEA": -15}], "dependents": [{"age": 40, "sex": "Male", "dataSet": {"year": 2008, "region": "UK", "yrAttainedIn": 2011}}]}

print(json.dumps(eg))

print(receiver().receive(gamejs=json.dumps(eg)))
url="https://europe-west2-ogden8.cloudfunctions.net/ogden"
js=json.dumps(eg)
r=requests.post(url,json=js)
print(r.text)



#print(hello_world(json.dumps({"message":"William"})))

