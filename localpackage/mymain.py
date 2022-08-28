from dataSet import dataSet
from person import person
from game import game
from datetime import datetime
from errorLogging import errors
import json
from json import JSONEncoder
import numpy as np
from pymaybe import maybe

from receiver import receiver
import numpy as np
import math
import pandas as pd
import json
import pygsheets
from utils import Ogden7, Ogden8
from TablesAD import TablesAD
from SAR import SAR
import requests

# t=TablesAD(8)
# print(t.getCont(sex='F',employed=False,qualification=1,disabled=True,age=33))


game1 = {'discountRate': -0.25 / 100, 'Ogden': 7}
contDetails = {'employed': True, 'disabled': False, 'qualification': 1}

c1 = {"name": "Gadsden", "cont": 1, "dob": '12/8/1975', "sex": "Male", 'dod': '13/4/2021', 'fatal': False,
      "dataSet": Ogden8, "contDetails": contDetails}
c2 = {"name": "Priya", "cont": 1, "dob": "7/10/1972", 'deltaLE': -5, "sex": "Female", "dataSet": Ogden8,
      'dependenton': '', "contDetails": contDetails}
c3 = {"name": "Mason", "cont": 1, "dob": '7/10/1972', 'deltaLE': 0, "sex": "Male", 'fatal': False, "dataSet": Ogden8,
      "contDetails": contDetails}
c4 = {"name": "Jennifer", "cont": 1, "dob": '12/3/1949', 'dod': '23/2/2020', 'deltaLE': 0, "sex": "Female",
      'fatal': True, "dataSet": Ogden8, "contDetails": contDetails}
c5 = {"name": "Gerald", "cont": 1, "dob": '6/4/1943', 'deltaLE': 0, "sex": "Male", 'fatal': False, "dataSet": Ogden8,
      'dependenton': 'Jennifer', "contDetails": contDetails}
claimant = {'name': "Jacqueline", 'dob': '25/8/1946', 'dod': '31/7/2017', 'fatal': True, 'sex': 'Female',
            'dataSet': Ogden8, 'deltaLE': 0, 'retirement': 78, 'cont': 0.75}
dependent1 = {'name': "Norman", 'dob': '31/07/2017', 'sex': 'Male', 'dataSet': Ogden8, 'dependenton': 'John',
              'retirement': 78}
dependent2 = {'name': "John", 'dob': '31/07/2017', 'sex': 'Male', 'dataSet': Ogden8, 'dependenton': 'Norman',
              'retirement': 79}
nondependent3 = {'name': "Brian", 'dob': '25/8/1990', 'sex': 'Male', 'dataSet': Ogden8, 'retirement': 79}

claimantdeceased = {'name': 'John', 'age': 55, 'aai': 25, 'aad': 30, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLE': -15,
                    'retirement': 67}

row = {'name': 'Jacqueline', 'fromAge': 76, 'toAge': 'LIFE', 'freq': 'Y', 'options': None}
rows = [row for a in range(1, 2)]
eg = {"rows": [], 'game': {"trialDate": datetime(2017, 7, 31), "DOI": datetime(2017,7,31), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [claimant, dependent1, dependent2]}}

eg2 = '{"rows":[{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"MI"},{"name":"JANE","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"JOHN","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"JOHN","fromAge":40,"toAge":60,"freq":"Y","options":"AMID"},{"name":"CHRISTOPHER","fromAge":"trial-3Y","toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"},{"name":"","fromAge":"","toAge":"","freq":"","options":""},{"name":"NAME","fromAge":"From Age","toAge":"To Age","freq":"FREQ","options":"OPTIONS"},{"name":"CHRISTOPHER","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":55,"toAge":125,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":40,"toAge":60,"freq":"Y","options":"AMI"},{"name":"CHRISTOPHER","fromAge":"trial-3Y","toAge":60,"freq":"Y","options":"AMID"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"MI"},{"name":"CHRISTOPHER","fromAge":"TRIAL","toAge":"LIFE","freq":"Y","options":"AMI"}],"game":{"discountRate":-0.005,"Ogden":7,"claimants":[{"name":"Christopher","cont":1,"age":58.362765229295,"sex":"Male","dataSet":{"year":2018,"region":"UK","yrAttainedIn":2022},"deltaLE":-5,"dependenton":"","retirement":67},{"name":"Jane","cont":1,"age":36.94455852156057,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLE":0,"aad":"","dependenton":"","retirement":67},{"name":"John","cont":1,"age":25.1088295687885,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLE":0,"aad":"","dependenton":"Christopher","retirement":67}]}}'

eg4 = {"rows": [], 'game': {"discountRate": -0.0025, "Ogden": 8, "trialDate": "29/03/2021", "autoYrAttained": False,
                            "projection": True, "claimants": [
        {"fatal": True, "name": "Jonnie", "dob": "29/03/1972", "cont": 1, "sex": "Male",
         "dataSet": {"year": 2018, "region": "UK", "yrAttainedIn": 2022}, "deltaLE": 0, "dependenton": "",
         "retirement": 65, "contDetails": {"employed": True, "qualification": 3, "disabled": True},
         "dod": "24/01/2021"}, {"fatal": False, "name": "WilliamC", "dob": "28/03/1974", "cont": 0.75, "sex": "Male",
                                "dataSet": {"year": 2018, "region": "UK", "yrAttainedIn": 2022}, "deltaLE": -2,
                                "dependenton": "", "retirement": 65,
                                "contDetails": {"employed": True, "qualification": 3, "disabled": True}}]}}

eg5 = {"rows": [{"name": "Zaki", "fromAge": "TRIAL", "toAge": "LIFE", "freq": "Y", "options": "AMI"}],
       "game": {"discountRate": -0.01, "trialDate": "31/03/2023", "projection": True, "Ogden": 8, "claimants": [
           {"fatal": False, "dependenton": "", "dob": "27/02/2005", "sex": "Male", "qualification": "3",
            "disabled": False, "cont": 0.67, "name": "Zaki", "targetLE_": 30,
            "dataSet": {"year": 2018, "region": "UK", "yrAttainedIn": 2022}, "retirement": 100, "region": "UK",
            "liveto_": 75, "deltaLE": 0, "deltaLEcounter": 0, "employed": False, "dod": "13/04/2021",
            "contDetails": {"qualification": "3", "employed": False, "disabled": False}, "deltaLE_": 0}],
                "autoYrAttained": False}}
eg6 = {"rows": [{"name": "Zaki", "fromAge": "TRIAL", "toAge": "LIFE", "freq": "Y", "options": "AMI"}],
       "game": {"DOI": "29/3/2012", "claimants": [
           {"fatal": False, "sex": "Male", "livetoN": 75, "yrsleftN": 98, "cont": 0.67, "employed": False,
            "disabled": False, "dob": "2/9/2002", "dependenton": "", "dod": "13/04/2021", "qualification": "1",
            "retirement": 100, "dataSet": {"year": 2018, "yrAttainedIn": 2022, "region": "UK"}, "deltaLEcounter": 1,
            "contDetails": {"disabled": False, "employed": True, "qualification": "2"}, "region": "UK", "deltaLEN": 0,
            "name": "Zaki"}], "autoYrAttained": False, "Ogden": 8, "discountRate": -0.0025, "projection": True,
                "trialDate": "27/4/2021"}}
g = game(eg)

spreadsheet_id = '1MADead62q5c8M0-O1Xuf-30aYy93FgfrrMM4vFKkmzw' #for my google sheet
service_file_path = "/Users/William/Dropbox (Personal)/Python/Code/pyCharm/Ogden8/pro-tracker-360811-236cce02c285.json" #for credentials

def joint_lives_table(start_age, end_age, sexes):
    yrs = end_age - start_age
    dataJLE = {}
    dataJLM = {}
    first_sex = ""
    second_sex = ""
    count = 0
    total = (end_age - start_age) * (end_age - start_age)
    if sexes[0] == 'M':
        first_sex = 'Male'
    else:
        first_sex = 'Female'
    if sexes[1] == "F":
        second_sex = "Female"
    else:
        second_sex = "Male"
    for h in range(start_age, end_age):  # column
        husband = {'name': "husband", 'age': h, 'sex': first_sex, 'dependenton': 'wife', 'dataSet': Ogden8,
                   'retirement': 78}  # create husband of age h
        colJLE = []
        colJLM = []
        for w in range(start_age, end_age):  # row
            print('{0:.0f%}'.format(count / total))
            wife = {'name': "wife", 'age': w, 'sex': second_sex, 'dataSet': Ogden8, 'dependenton': 'husband',
                    'retirement': 78}  # create wife of age h
            eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                       "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [wife, husband]}}
            g = game(eg)
            colJLE.append(g.getClaimant('husband').JLE()[3])
            colJLM.append(g.getClaimant('husband').JLM()[3])
        dataJLE[h] = colJLE
        dataJLM[h] = colJLM
    dfJLE = pd.DataFrame(dataJLE, index=[*range(start_age, end_age)])
    dfJLM = pd.DataFrame(dataJLM, index=[*range(start_age, end_age)])
    print(dfJLE)
    print(dfJLM)
    titleJLM = ""
    titleJLE = ""
    rowTitle = ""
    colTitle = ""
    if sexes[0] == sexes[1] and sexes[0] == 'M':
        titleJLM = "Joint Life Multiplier of two men"
        titleJLE = "Joint Life Expectancy of two men"
        rowTitle = "Age man"
        colTitle = "Age man"
    elif sexes[0] == sexes[1] and sexes[0] == 'F':
        titleJLM = "Joint Life Multiplier of two women"
        titleJLE = "Joint Life Expectancy of two women"
        rowTitle = 'Age woman'
        colTitle = 'Age woman'
    elif not sexes[0] == sexes[1]:
        titleJLM = "Joint Life Multiplier of man and woman"
        titleJLE = "Joint Life Expectancy of man and woman"
        if sexes[0] == 'M':
            colTitle = 'Age man'
            rowTitle = 'Age woman'
        else:
            colTitle = 'Age woman'
            rowTitle = 'Age man'

    write_to_gsheet(service_file_path, spreadsheet_id, 'JLE ' + sexes, dfJLE, titleJLE, colTitle, rowTitle)
    write_to_gsheet(service_file_path, spreadsheet_id, 'JLM ' + sexes, dfJLM, titleJLM, colTitle, rowTitle)


def write_to_gsheet(service_file_path, spreadsheet_id, sheet_name, data_df, title, colTitle, rowTitle):
    """
        this function takes data_df and writes it under spreadsheet_id
        and sheet_name using your credentials under service_file_path
        """
    gc = pygsheets.authorize(service_file=service_file_path)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        sh.add_worksheet(sheet_name)
    except:
        pass
    wks_write = sh.worksheet_by_title(sheet_name)
    # write data
    wks_write.clear('A1', None, '*')
    wks_write.cell((1, 1)).wrap_strategy = "WRAP"
    wks_write.set_dataframe(data_df, (2, 1), copy_index=True, encoding='utf-8', fit=False)
    # write titles
    wks_write.cell((1, 1)).value = title
    wks_write.cell((2, 1)).value = rowTitle
    wks_write.cell((1, 2)).value = colTitle
    wks_write.frozen_rows = 2
    wks_write.frozen_cols = 1
    # formatting
    model_cell = pygsheets.Cell("B3")
    model_cell.set_number_format(
        format_type=pygsheets.FormatType.NUMBER,
        pattern="0.00"
    )
    left_corner_cell = (3, 2)
    right_corner_cell = [sum(x) for x in zip(left_corner_cell, data_df.shape, (-1, -1))]
    pygsheets.DataRange(left_corner_cell, right_corner_cell, worksheet=wks_write).apply_format(model_cell)

def create_joint_lives_tables(start_age,end_age):
    joint_lives_table(start_age, end_age, 'MM')
    joint_lives_table(start_age, end_age, 'MF')
    joint_lives_table(start_age, end_age, 'FF')


# print(g.processRows())
# print(g.getClaimant('Gadsden').getSummaryStats())
# print(errors.getLog())
# print(g.getClaimant('Jonnie').getStateRetirementAge())
# print(g.process())
# print(g.getClaimant('Hicken').M(60,'LIFE', freq='Y',options='M'))

#create_joint_lives_tables(0,100)

print(g.getClaimant('Norman').M('INJURY', 'LIFE', freq='Y'))
#print(g.getClaimant('Norman').getdiscountFactor(90, -0.0025))
#print(g.getClaimant('Norman').gettermCertain(76, 86, discountRate=-0.0075))
#print(json.dumps(g.getClaimant('Norman').getEDD().isoformat()))
print(g.getClaimant('Norman').getAAT())

print(g.getClaimant('Norman').LM())

# print(g.getClaimant('Mason').getAAT())
# print(g.getClaimant('Mason').LE()[3])
# print(g.getClaimant('Mason').getEAD())
# print(g.getClaimant('Jonnie').getAutoCont())
# print(g.getClaimant('Jonnie').isFatal())
# print(g.getClaimant('JOHN2').M(20,125, freq='Y',options='D'))
# print(g.getClaimant('JOHN').M(55, 125, freq='Y',options='AMID'))
# print(g.getClaimant('CHRISTOPHER').M(55, 125, status='Injured', freq='Y',options='AMI'))
# print(g.claimants['JOHN'].MB(55,70, freq='<Y',options='AMI'))
# print(g.dependents['JOHN'].MJ(40,60, freq='<Y',options='AMI'))
# print(g.dependents['JOHN'].M(40,60, freq='<Y',options='AMI'))
# eg={"rows":[{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"},{"fromAge":35,"toAge":60,"freq":"Y","name":"Uninjured","cont":1,"options":"AMI"}],"discountRate":-0.005,"Ogden":7,"claimants":[{"age":55,"aai":24.999315537303218,"sex":"Female","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011},"deltaLEB":-15,"deltaLEA":-15}],"dependents":[{"age":40,"sex":"Male","dataSet":{"year":2008,"region":"UK","yrAttainedIn":2011}}]}

# print(json.dumps(eg))

# print(receiver().receive(gamejs=json.dumps(eg)))

url = "https://europe-west2-ogden8.cloudfunctions.net/ogden"
# js=json.dumps(eg)
# print(js)
# r=requests.post(url,json=eg2)
# print(r.text)
