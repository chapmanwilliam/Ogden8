from dataSet import dataSet
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

c1={"name":"Christopher","cont":1,"age":58.362765229295,'deltaLE':100,"sex":"Male","dataSet":{"year":2018,"region":"UK","yrAttainedIn":2022}}
claimant = {'name':'Christopher', 'age': 58.36, 'aai': 25, 'sex': 'Male', 'dataSet': Ogden8, 'deltaLE': -5, 'retirement':67, 'cont':0.75}
dependent = {'name': 'John', 'age': 40, 'sex': 'Male', 'dataSet': Ogden7, 'dependenton':'Christopher', 'retirement':57}

claimantdeceased = {'name': 'John', 'age': 55, 'aai': 25, 'aad':30, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLE': -15, 'retirement':67}


row={'name': 'CHRISTOPHER','fromAge':58.36, 'toAge':125, 'freq': 'Y', 'options':'MI'}
rows=[row for a in range(1,2)]
eg={"rows": rows, 'game': {"discountRate": -0.005, "Ogden": 7, "claimants": [c1]}}


eg2='{"rows":[{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"MI"},{"name":"JANE","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"JOHN","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"JOHN","fromAge":40,"toAge":60,"freq":"Y","options":"AMID"},{"name":"CHRISTOPHER","fromAge":"trial-3Y","toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"},{"name":"","fromAge":"","toAge":"","freq":"","options":""},{"name":"NAME","fromAge":"From Age","toAge":"To Age","freq":"FREQ","options":"OPTIONS"},{"name":"CHRISTOPHER","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"trial-3Y","toAge":60,"freq":"Y","options":"AMID"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"MI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"}],"game":{"discountRate":-0.005,"Ogden":7,"claimants":[{"name":"Christopher","cont":1,"age":58.362765229295,"sex":"Male","dataSet":{"year":2018,"region":"UK","yrAttainedIn":2022},"deltaLE":-5,"dependenton":"","retirement":67},{"name":"Jane","cont":1,"age":36.94455852156057,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLE":0,"aad":"","dependenton":"","retirement":67},{"name":"John","cont":1,"age":25.1088295687885,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLE":0,"aad":"","dependenton":"Christopher","retirement":67}]}}'


g=game(eg)
#print(g.processRows())
print(g.getClaimant('CHRISTOPHER').M('TRIAL','LIFE', freq='Y',options='MI'))
#print(g.getClaimant('JOHN').M(55, 125, freq='Y',options='AMID'))
#print(g.getClaimant('CHRISTOPHER').M(55, 125, status='Injured', freq='Y',options='AMI'))
#print(g.claimants['JOHN'].MB(55,70, freq='<Y',options='AMI'))
#print(g.dependents['JOHN'].MJ(40,60, freq='<Y',options='AMI'))
#print(g.dependents['JOHN'].M(40,60, freq='<Y',options='AMI'))
#eg={"rows":[{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"},{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"}],"discountRate":-0.005,"Ogden":7,"claimants":[{"age":55,"aai":24.999315537303218,"sex":"Female","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLEB":-15,"deltaLEA":-15}],"dependents":[{"age":40,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011}}]}

#print(json.dumps(eg))

#print(receiver().receive(gamejs=json.dumps(eg)))

url="https://europe-west2-ogden8.cloudfunctions.net/ogden"
#js=json.dumps(eg)
#print(js)
#r=requests.post(url,json=eg2)
#print(r.text)



