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

spreadsheet_id_generated = '1MADead62q5c8M0-O1Xuf-30aYy93FgfrrMM4vFKkmzw' #for my google sheet
spreadsheet_id_Ogden8published = '1EoXK2lAKS8KJ5ULLQYxt6lYgJv0VVvnElYa-KqApBWc'
service_file_path = "/Users/William/Dropbox (Personal)/Python/Code/pyCharm/Ogden8/pro-tracker-360811-236cce02c285.json" #for credentials

def joint_lives_table(start_age, end_age, sexes):
    yrs = end_age - start_age
    dataJLE = {}
    dataJLM = {}
    dataLE={}
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
    for h in range(start_age, end_age+1):  # column
        husband = {'name': "husband", 'age': h, 'sex': first_sex, 'dependenton': 'wife', 'dataSet': Ogden8,
                   'retirement': 78}  # create husband of age h
        colJLE = []
        colJLM = []
        colLE=[]
        for w in range(start_age, end_age+1):  # row
            count+=1
            print (f"{count/total:.0%}")
            wife = {'name': "wife", 'age': w, 'sex': second_sex, 'dataSet': Ogden8, 'dependenton': 'husband',
                    'retirement': 78}  # create wife of age h
            eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                       "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [wife, husband]}}
            g = game(eg)
            husbandLE = g.getClaimant('husband').LE()[3]
            wifeLE = g.getClaimant('wife').LE()[3]
            LE=min(husbandLE,wifeLE)
            colLE.append(LE)
            colJLE.append(g.getClaimant('husband').JLE()[3])
            colJLM.append(g.getClaimant('husband').JLM()[3])
        dataJLE[h] = colJLE
        dataJLM[h] = colJLM
        dataLE[h]=colLE
    dfJLE = pd.DataFrame(dataJLE, index=[*range(start_age, end_age)])
    dfJLM = pd.DataFrame(dataJLM, index=[*range(start_age, end_age)])
    dfLE = pd.DataFrame(dataLE,index=[*range(start_age,end_age)])
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

    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'JLE ' + sexes, dfJLE, titleJLE, colTitle, rowTitle)
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'JLM ' + sexes, dfJLM, titleJLM, colTitle, rowTitle)
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'LE ' + sexes, dfLE, "Shortest life expectancy", "", "")


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
    # formatting - data cells
    model_cell = pygsheets.Cell("B3")
    if not 'discount factor' in title:
        model_cell.set_number_format(
            format_type=pygsheets.FormatType.NUMBER,
            pattern="0.00"
        )
    else:
        model_cell.set_number_format(
            format_type=pygsheets.FormatType.NUMBER,
            pattern="0.0000"
        )

    left_corner_cell = (3, 2)
    right_corner_cell = [sum(x) for x in zip(left_corner_cell, data_df.shape, (-1, -1))]
    pygsheets.DataRange(left_corner_cell, right_corner_cell, worksheet=wks_write).apply_format(model_cell)
    # formatting - top row if Table
    if 'Table' in title:
        model_cell = pygsheets.Cell("B2")
        model_cell.set_number_format(
            format_type=pygsheets.FormatType.PERCENT,
            pattern="0.00%"
        )
        left_corner_cell = (2, 2)
        right_corner_cell = (2,15)
        pygsheets.DataRange(left_corner_cell, right_corner_cell, worksheet=wks_write).apply_format(model_cell)
    #conditional formatting
#    wks_write.add_conditional_formatting(left_corner_cell,right_corner_cell,"CUSTOM_FORMULA")

def create_joint_lives_tables(start_age,end_age):
    joint_lives_table(start_age, end_age, 'MM')
    joint_lives_table(start_age, end_age, 'MF')
    joint_lives_table(start_age, end_age, 'FF')

def createTableE():
    yrstotrial=[*range(1,11)]
    agedeath=[*range(40,95,5)]
    print(agedeath)
    dataMale={}
    dataFemale={}
    for c in yrstotrial:
        colMale = []
        colFemale = []
        for r in agedeath:
            male = {'name': "male", 'age': r, 'sex': "M", 'dataSet': Ogden8,
                       'retirement': 78}  # create male of age ageatdeath
            female = {'name': "female", 'age': r, 'sex': "F", 'dataSet': Ogden8,
                       'retirement': 78}  # create female of age ageatdeath
            eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                       "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [male, female]}}
            g=game(eg)
            colMale.append(g.getClaimant('male').M('TRIAL','TRIAL+' + str(c) + "Y",'Y','M')[3]/c)
            colFemale.append(g.getClaimant('female').M('TRIAL','TRIAL+' + str(c) + "Y",'Y','M')[3]/c)
        dataMale[c]=colMale
        dataFemale[c]=colFemale
    dfMale = pd.DataFrame(dataMale, index=agedeath)
    dfFemale = pd.DataFrame(dataFemale, index=agedeath)
    print(dfMale)
    print(dfFemale)
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table E (male)', dfMale, "Table E (male)", "Yrs to trial", "Age at death")
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table E (female)', dfFemale, "Table E (female)", "Yrs to trial", "Age at death")

def createTableF():
    yrstotrial=[*range(1,11)]
    agedeath=[*range(40,95,5)]
    print(agedeath)
    dataMale={}
    dataFemale={}
    for c in yrstotrial:
        colMale = []
        colFemale = []
        for r in agedeath:
            male = {'name': "male", 'age': r, 'sex': "M", 'dataSet': Ogden8,
                       'retirement': 78}  # create male of age ageatdeath
            female = {'name': "female", 'age': r, 'sex': "F", 'dataSet': Ogden8,
                       'retirement': 78}  # create female of age ageatdeath
            eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                       "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [male, female]}}
            g=game(eg)
            colMale.append(g.getClaimant('male').M('TRIAL+' + str(c) + "Y",None,'Y','M')[3])
            colFemale.append(g.getClaimant('female').M('TRIAL+' + str(c) + "Y",None,'Y','M')[3])
        dataMale[c]=colMale
        dataFemale[c]=colFemale
    dfMale = pd.DataFrame(dataMale, index=agedeath)
    dfFemale = pd.DataFrame(dataFemale, index=agedeath)
    print(dfMale)
    print(dfFemale)
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table F (male)', dfMale, "Table F (male)", "Yrs to trial", "Age at death")
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table F (female)', dfFemale, "Table F (female)", "Yrs to trial", "Age at death")

def createTables1to34():
    drs=[-0.02,-0.0175,-0.015,-0.01,-0.0075,-0.005,-0.0025,0,0.005,0.01,0.015,0.02, 0.025,0.03]
    upto=['LIFE',50,55,60,65,68,70,75,80]
    fr=[50,55,60,65,68,70,75,80]
    dataMaleUP={}
    dataFemaleUP={}
    dataMaleFR={}
    dataFemaleFR={}
    tableCountUP=1
    tableCountFR=19
    for up in upto:
        for dr in drs:
            colMaleUP = []
            colFemaleUP = []
            colMaleFR = []
            colFemaleFR = []
            if tableCountUP<=2:
                ages=[*range(0,101)]
            elif tableCountUP>2 and tableCountUP<=18:
                ages = [*range(16, up)]
            for age in ages:
                male = {'name': "male", 'age': age, 'sex': "M", 'dataSet': Ogden8,
                        'retirement': 78}  # create male of age age
                female = {'name': "female", 'age': age, 'sex': "F", 'dataSet': Ogden8,
                          'retirement': 78}  # create female of age age
                eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                           "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [male, female]}}
                g=game(eg)
                colMaleUP.append(g.getClaimant('male').M("TRIAL",up,discountRate=dr)[3])
                colFemaleUP.append(g.getClaimant('female').M("TRIAL",up,discountRate=dr)[3])
            if tableCountUP>2:
                agesFR=[*range(0,up+1)]
                for age in agesFR:
                    male = {'name': "male", 'age': age, 'sex': "M", 'dataSet': Ogden8,
                            'retirement': 78}  # create male of age age
                    female = {'name': "female", 'age': age, 'sex': "F", 'dataSet': Ogden8,
                              'retirement': 78}  # create female of age age
                    eg = {"rows": [],
                          'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                   "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [male, female]}}
                    g = game(eg)
                    colMaleFR.append(g.getClaimant('male').M(up,'LIFE', discountRate=dr)[3])
                    colFemaleFR.append(g.getClaimant('female').M(up,'LIFE', discountRate=dr)[3])
            dataMaleUP[dr]=colMaleUP
            dataFemaleUP[dr]=colFemaleUP
            if tableCountUP>2:
                dataMaleFR[dr] = colMaleFR
                dataFemaleFR[dr] = colFemaleFR
        dfMaleUP = pd.DataFrame(dataMaleUP, index=ages)
        dfFemaleUP = pd.DataFrame(dataFemaleUP, index=ages)
        if tableCountUP>2:
            dfMaleFR = pd.DataFrame(dataMaleFR, index=agesFR)
            dfFemaleFR = pd.DataFrame(dataFemaleFR, index=agesFR)
        print(dfMaleUP)
        print(dfFemaleUP)
        if tableCountUP>2:
            print(dfMaleFR)
            print(dfFemaleFR)
        if tableCountUP>2:
            write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table ' + str(tableCountFR), dfMaleFR, 'Table ' + str(tableCountFR) + ": multiplier from " + str(up), "Discount rate", "Age")
            tableCountFR+=1
            write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table ' + str(tableCountFR), dfFemaleFR, 'Table ' + str(tableCountFR) + ": multiplier from " + str(up), "Discount rate", "Age")
            tableCountFR += 1
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table ' + str(tableCountUP), dfMaleUP, 'Table ' + str(tableCountUP) + ": multiplier to " + str(up), "Discount rate", "Age")
        tableCountUP+=1
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table ' + str(tableCountUP), dfFemaleUP, 'Table ' + str(tableCountUP) + ": multiplier to " + str(up), "Discount rate", "Age")
        tableCountUP+=1

def createDFTables35to36():
    drs=[-0.02,-0.0175,-0.015,-0.01,-0.0075,-0.005,-0.0025,0,0.005,0.01,0.015,0.02, 0.025,0.03]
    yrs=[*range(1,81)]
    dataDF={}
    dataTC={}
    male = {'name': "male", 'age': 10, 'sex': "M", 'dataSet': Ogden8,
            'retirement': 78}  # create male of age age
    eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                               "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [male]}}
    g = game(eg)

    for dr in drs:
        colDF = []
        colTC = []
        for yr in yrs:
            colDF.append(g.getClaimant('male').M("TRIAL + " + str(yr) + "Y",options="A",discountRate=dr)[3])
            colTC.append(g.getClaimant('male').M("TRIAL","TRIAL + " + str(yr) + "Y", options="A", discountRate=dr)[3])
        dataDF[dr]=colDF
        dataTC[dr]=colTC
    dfDF = pd.DataFrame(dataDF, index=yrs)
    dfTC = pd.DataFrame(dataTC, index=yrs)
    print(dfDF)
    print(dfTC)
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table 35', dfDF, 'Table 35: discount factor', "Discount rate", "Years")
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table 36', dfTC, 'Table 36: term certain', "Discount rate", "Years")

def additionalTables():
    drs=[-0.015,-0.0075,-0.0025,0] #discount rates
    tos=[*range(1,126)] #cols
    frs=[*range(0,116)] #rows
    dataM={}
    dataF={}
    for dr in drs:
        for to in tos:
            colM=[]
            colF=[]
            for fr in frs:
                print(fr,to)
                if(fr<to):
                    male = {'name': "male", 'age': fr, 'sex': "M", 'dataSet': Ogden8,
                            'retirement': 78}  # create male of age fr
                    female = {'name': "female", 'age': fr, 'sex': "F", 'dataSet': Ogden8,
                            'retirement': 78}  # create female of age fr
                    eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                               "discountRate": dr, "Ogden": 8, "claimants": [male, female]}}
                    g = game(eg)
                    colM.append(g.getClaimant('male').M(fr,to)[3])
                    colF.append(g.getClaimant('female').M(fr,to)[3])
                else:
                    colM.append("")
                    colF.append("")
            dataM[to]=colM
            dataF[to]=colF
        dfM=pd.DataFrame(dataM,index=frs)
        dfF=pd.DataFrame(dataF,index=frs)
        print(dfM)
        print(dfF)
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Males ' + f'{dr:0.2%}', dfM, 'Males ' + f'{dr:0.2%}', "Discount rate", "Age at trial")
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Females ' + f'{dr:0.2%}', dfM, 'Females ' + f'{dr:0.2%}', "Discount rate", "Age at trial")

def copypasteOgden8publishedTables(spreadsheet_id):
    #test
    rows=[100,100,34,34,39,39,44,44,49,49,52,52,54,54,59,59,65,65,50,50,55,55,60,60,65,65,68,68,70,70,75,75,80,80,80,80]
    cols=14
    tables=[*range(1,37)]
    gc = pygsheets.authorize(service_file=service_file_path)
    shPublished = gc.open_by_key(spreadsheet_id)
    shGenerated = gc.open_by_key(spreadsheet_id_generated)
    for table in tables:
        sheet_name="Table " + str(table)
        wks_published = shPublished.worksheet_by_title(sheet_name)
        wks_generated = shGenerated.worksheet_by_title(sheet_name)
        print(rows[table-1]+3)
        x=wks_published.get_values((4,2),(rows[table-1]+3,cols))

        wks_generated.update_values((rows[table-1]+4, 2),x, extend=True)
        # formatting - data cells
        model_cell = pygsheets.Cell((rows[table-1]+4, 2))
        model_cell.set_number_format(
            format_type=pygsheets.FormatType.NUMBER,
            pattern="0.00"
        )
        pygsheets.DataRange((rows[table-1]+4, 2), (2*rows[table-1]+4,cols), worksheet=wks_generated).apply_format(model_cell)


def createOgdenTables():
    #createTableF()
    #createTableE()
    createTables1to34()
    createDFTables35to36()
    additionalTables()
    copypasteOgden8publishedTables(spreadsheet_id_Ogden8published)
    #create_joint_lives_tables(0,100)


# print(g.processRows())
# print(g.getClaimant('Gadsden').getSummaryStats())
# print(errors.getLog())
# print(g.getClaimant('Jonnie').getStateRetirementAge())
# print(g.process())
# print(g.getClaimant('Hicken').M(60,'LIFE', freq='Y',options='M'))


print(g.getClaimant('Norman').M('TRIAL', 'LIFE', freq='Y',discountRate=0))
print(g.getClaimant('Norman').M('TRIAL', 'LIFE', freq='Y'))
#print(g.getClaimant('Norman').getdiscountFactor(90, -0.0025))
#print(g.getClaimant('Norman').gettermCertain(76, 86, discountRate=-0.0075))
#print(json.dumps(g.getClaimant('Norman').getEDD().isoformat()))
#print(g.getClaimant('Norman').getAAT())

#print(g.getClaimant('Norman').LM())

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
