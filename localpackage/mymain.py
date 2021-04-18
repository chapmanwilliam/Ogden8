from dataSet import dataSet
from person import person
from game import game
from datetime import datetime
from errorLogging import errors


from pymaybe import maybe

from receiver import receiver
import numpy as np
import pandas as pd
import json
from utils import Ogden7,Ogden8
from TablesAD import TablesAD
from SAR import SAR
import requests



#t=TablesAD(8)
#print(t.getCont(sex='F',employed=False,qualification=1,disabled=True,age=33))


game1={'discountRate':-0.25/100, 'Ogden':7}
contDetails={'employed':True,'disabled':False,'qualification': 1 }

c1={"name":"Jonnie","cont":1,"dob":'27/2/2005', 'liveto':75, "sex":"Male", 'dod':'13/4/2021','fatal':False,"dataSet":Ogden8, "contDetails":contDetails}
c2={"name":"Priya","cont":1,"dob":"7/10/1972", 'deltaLE':-5, "sex":"Female", "dataSet":Ogden8, 'dependenton':'',"contDetails":contDetails}
claimant = {'name':'Christopher', 'age': 111, 'aai': 25, 'sex': 'Male', 'dataSet': Ogden8, 'deltaLE': -5, 'retirement':67, 'cont':0.75}
dependent1 = {'name': 'John1', 'age': 20, 'sex': 'Male', 'dataSet': Ogden8, 'dependenton':'Christopher1', 'retirement':57}
dependent2 = {'name': 'John2', 'age': 20, 'sex': 'Male', 'dataSet': Ogden8, 'dependenton':'Christopher2', 'retirement':57}

claimantdeceased = {'name': 'John', 'age': 55, 'aai': 25, 'aad':30, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLE': -15, 'retirement':67}


row={'name': 'PRIYA','fromAge':58.36, 'toAge':125, 'freq': 'Y', 'options':'MI'}
rows=[row for a in range(1,2)]
eg={"rows": rows, 'game': {"trialDate":datetime(2023,3,31),"projection":True,"autoYrAttained": False, "discountRate": -0.25/100, "Ogden": 8, "claimants": [c1,c2]}}


eg2='{"rows":[{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"MI"},{"name":"JANE","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"JOHN","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"JOHN","fromAge":40,"toAge":60,"freq":"Y","options":"AMID"},{"name":"CHRISTOPHER","fromAge":"trial-3Y","toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"},{"name":"","fromAge":"","toAge":"","freq":"","options":""},{"name":"NAME","fromAge":"From Age","toAge":"To Age","freq":"FREQ","options":"OPTIONS"},{"name":"CHRISTOPHER","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"trial-3Y","toAge":60,"freq":"Y","options":"AMID"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"MI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"}],"game":{"discountRate":-0.005,"Ogden":7,"claimants":[{"name":"Christopher","cont":1,"age":58.362765229295,"sex":"Male","dataSet":{"year":2018,"region":"UK","yrAttainedIn":2022},"deltaLE":-5,"dependenton":"","retirement":67},{"name":"Jane","cont":1,"age":36.94455852156057,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLE":0,"aad":"","dependenton":"","retirement":67},{"name":"John","cont":1,"age":25.1088295687885,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLE":0,"aad":"","dependenton":"Christopher","retirement":67}]}}'

eg4={"rows":[],'game':{"discountRate":-0.0025,"Ogden":8,"trialDate":"29/03/2021","autoYrAttained":False,"projection":True,"claimants":[{"fatal":True,"name":"Jonnie","dob":"29/03/1972","cont":1,"sex":"Male","dataSet":{"year":2018,"region":"UK","yrAttainedIn":2022},"deltaLE":0,"dependenton":"","retirement":65,"contDetails":{"employed":True,"qualification":3,"disabled":True},"dod":"24/01/2021"},{"fatal":False,"name":"WilliamC","dob":"28/03/1974","cont":0.75,"sex":"Male","dataSet":{"year":2018,"region":"UK","yrAttainedIn":2022},"deltaLE":-2,"dependenton":"","retirement":65,"contDetails":{"employed":True,"qualification":3,"disabled":True}}]}}

eg5={"rows":[{"name":"Zaki","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"}],"game":{"discountRate":-0.01,"trialDate":"31/03/2023","projection":True,"Ogden":8,"claimants":[{"fatal":False,"dependenton":"","dob":"27/02/2005","sex":"Male","qualification":"3","disabled":False,"cont":0.67,"name":"Zaki","targetLE_":30,"dataSet":{"year":2018,"region":"UK","yrAttainedIn":2022},"retirement":100,"region":"UK","liveto_":75,"deltaLE":0,"deltaLEcounter":0,"employed":False,"dod":"13/04/2021","contDetails":{"qualification":"3","employed":False,"disabled":False},"deltaLE_":0}],"autoYrAttained":False}}
eg6={"rows":[{"name":"Zaki","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"}],"game":{"claimants":[{"fatal":False,"sex":"Male","livetoN":75,"yrsleftN":98,"cont":0.67,"employed":False,"disabled":False,"dob":"27/02/2005","dependenton":"","dod":"13/04/2021","targetLE":75,"qualification":"3","retirement":100,"dataSet":{"year":2018,"yrAttainedIn":2022,"region":"UK"},"deltaLEcounter":1,"contDetails":{"disabled":False,"employed":True,"qualification":"3"},"region":"UK","deltaLEN":0,"name":"Zaki"}],"autoYrAttained":False,"Ogden":8,"discountRate":-0.0025,"projection":True,"trialDate":"31/03/2023"}}
g=game(eg6)
#print(g.processRows())
print(g.getClaimant('Zaki').M('TRIAL','LIFE', freq='A',options='AMI'))
print(errors.getLog())
#print(g.getClaimant('Zaki').getAutoCont())
#print(g.getClaimant('Jonnie').getStateRetirementAge())
#print(g.process())
#print(g.getClaimant('Jonnie').M('TRIAL',125, freq='Y',options='AMI'))
#print(g.getClaimant('Jonnie').getAutoCont())
#print(g.getClaimant('Jonnie').isFatal())
#print(g.getClaimant('JOHN2').M(20,125, freq='Y',options='D'))
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



