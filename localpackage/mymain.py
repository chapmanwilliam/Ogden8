from dataSet import dataSet
from person import person
from game import game
from datetime import datetime
from functools import reduce
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
claimant = {'name': "Jacqueline", 'age': 20, 'fatal': False, 'sex': 'Female','dependenton': 'Norman',
            'dataSet': Ogden8, 'deltaLE': 0, 'retirement': 78, 'cont': 0.75}
dependent1 = {'name': "Norman", 'age': 60, 'aad':50, 'sex': 'Male', 'fatal' :True, 'dataSet': Ogden8,
              'retirement': 78}
dependent2 = {'name': "John", 'dob': '31/07/2017', 'sex': 'Male', 'dataSet': Ogden8, 'dependenton': 'Jacqueline',
              'retirement': 79}
nondependent3 = {'name': "Brian", 'dob': '25/8/1990', 'sex': 'Male', 'dataSet': Ogden8, 'retirement': 79}

claimantdeceased = {'name': 'John', 'age': 55, 'aai': 25, 'aad': 30, 'sex': 'Female', 'dataSet': Ogden7, 'deltaLE': -15,
                    'retirement': 67}

row = {'name': 'Jacqueline', 'fromAge': 76, 'toAge': 'LIFE', 'freq': 'Y', 'options': None}
rows = [row for a in range(1, 2)]
eg = {"rows": [], 'game': {"trialDate": datetime(2022, 7, 31), "DOI": datetime(2012,7,31), "useMultipleRates": True, 'DRMethod': 'BLENDED', "projection": True, 'useTablesEF': True, "autoYrAttained": False,
                           "discountRate": -1.5 / 100, "Ogden": 8, "multipleRates":[{'rate':-0.015,'switch':15},{'rate':0.015,'switch':125}], "claimants": [claimant, dependent1]}}

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
spreadsheet_id_Ogden8published = '1EoXK2lAKS8KJ5ULLQYxt6lYgJv0VVvnElYa-KqApBWc' #for published Ogden data
spreadsheet_DigitalGoods="1LtswwaUEeF1uNCVwzYHuqpymKGMDDCnOUoSJ15msjJw" #for digital goods
service_file_path = "/Users/William/Dropbox (Personal)/Python/Code/pyCharm/Ogden8/pro-tracker-360811-236cce02c285.json" #for credentials

def write_to_gsheet(service_file_path, spreadsheet_id, sheet_name, data_df, title, colTitle, rowTitle, start_cell=(2,1)):
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
    #wks_write.clear('A1', None, '*')
    wks_write.cell((1, 1)).wrap_strategy = "WRAP"
    wks_write.set_dataframe(data_df, start_cell, copy_index=True, encoding='utf-8', fit=False, extend=True)
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
    if 'Discount' in colTitle:
        model_cell = pygsheets.Cell("B2")
        model_cell.set_number_format(
            format_type=pygsheets.FormatType.PERCENT,
            pattern="0.00%"
        )
    else:
        model_cell = pygsheets.Cell("B2")
        model_cell.set_number_format(
            format_type=pygsheets.FormatType.PERCENT,
            pattern="0"
        )

    left_corner_cell = (2, 2)
    right_corner_cell = (2,15)
    pygsheets.DataRange(left_corner_cell, right_corner_cell, worksheet=wks_write).apply_format(model_cell)
    #conditional formatting
#    wks_write.add_conditional_formatting(left_corner_cell,right_corner_cell,"CUSTOM_FORMULA")

def joint_lives_tablev2(start_age,end_age,sexes):
    print("Creating joint lives tables....")
    ages=[*range(0,101)]
    men=[{'name': "man " + str(age) + " " + str(dage), 'age': age, 'sex': sexes[1], 'dataSet': Ogden8, 'dependenton': 'woman ' +str(dage)} for age in ages for dage in ages] # create women of age age
    women=[{'name': "woman " + str(age), 'age': age, 'sex': sexes[0], 'dataSet': Ogden8} for age in ages]  # create men of age age

    claimants=men+women

    eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False, "discountRate": -0.25/100, "Ogden": 8, "claimants":  claimants}}
    g=game(eg)
    dataJLE=[[g.getClaimant('man ' + str(age) + ' ' + str(dage)).JLE()[3] for age in ages] for dage in ages]
    dataJLM=[[g.getClaimant('man ' + str(age) + ' ' + str(dage)).JLM()[3] for age in ages] for dage in ages]

    mLE=[g.getClaimant('man ' + str(age) + ' 0').LE()[3] for age in ages]
    wLE=[g.getClaimant('woman ' + str(age)).LE()[3] for age in ages]
    dataLE=[[min(mLE[age], wLE[dage]) for dage in ages] for age in ages]

    dfJLE=pd.DataFrame(dataJLE, index=ages).set_axis(ages,'columns')
    dfJLM=pd.DataFrame(dataJLM, index=ages).set_axis(ages,'columns')
    dfLE=pd.DataFrame(dataLE, index=ages).set_axis(ages,'columns')

    print(dfJLE)
    print(dfJLM)
    print(dfLE)

    print('Writing joint lives tables...')
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
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'LE ' + sexes, dfLE, "Shortest life expectancy", "", "",(len(ages)+3,1))

    print('Finished joint lives tables.')

def joint_lives_table(start_age, end_age, sexes):
    print('Creating joint lives tables....')
    yrs = end_age - start_age
    dataJLE = {}
    dataJLM = {}
    dataLE={}
    dataLM={}
    count = 0
    total = (end_age - start_age) * (end_age - start_age)
    for h in range(start_age, end_age+1):  # column
        husband = {'name': "husband", 'age': h, 'sex': sexes[0], 'dependenton': 'wife', 'dataSet': Ogden8,
                   'retirement': 78}  # create husband of age h
        colJLE = []
        colJLM = []
        colLE=[]
        colLM=[]
        for w in range(start_age, end_age+1):  # row
            count+=1
            print (f"{count/total:.0%}")
            wife = {'name': "wife", 'age': w, 'sex': sexes[1], 'dataSet': Ogden8, 'dependenton': 'husband',
                    'retirement': 78}  # create wife of age h
            eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                                       "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [wife, husband]}}
            g = game(eg)
            husbandLE = g.getClaimant('husband').LE()[3]
            wifeLE = g.getClaimant('wife').LE()[3]
            LE=min(husbandLE,wifeLE)
            colLE.append(LE)
            husbandLM = g.getClaimant('husband').LM()[3]
            wifeLM = g.getClaimant('wife').LM()[3]
            LM=min(husbandLM,wifeLM)
            colLM.append(LM)
            colJLE.append(g.getClaimant('husband').JLE()[3])
            colJLM.append(g.getClaimant('husband').JLM()[3])
        dataJLE[h] = colJLE
        dataJLM[h] = colJLM
        dataLE[h]=colLE
        dataLM[h]=colLM
    dfJLE = pd.DataFrame(dataJLE, index=[*range(start_age, end_age+1)])
    dfJLM = pd.DataFrame(dataJLM, index=[*range(start_age, end_age+1)])
    dfLE = pd.DataFrame(dataLE,index=[*range(start_age,end_age+1)])
    dfLM = pd.DataFrame(dataLM,index=[*range(start_age,end_age+1)])
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
    print('Writing joint lives tables...')
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'JLE ' + sexes, dfJLE, titleJLE, colTitle, rowTitle)
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'JLM ' + sexes, dfJLM, titleJLM, colTitle, rowTitle)
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'LE ' + sexes, dfLE, "Shortest life expectancy", "", "")
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'LM ' + sexes, dfLM, "Shortest life multiplier", "", "")
    print('Finished joint lives tables.')

def create_joint_lives_tables(start_age,end_age):
    print('Creating joint lives tables....')
    joint_lives_table(start_age, end_age, 'MM')
    joint_lives_table(start_age, end_age, 'MF')
    joint_lives_table(start_age, end_age, 'FF')
    print('Finished joint lives tables.')

def createTableE():
    print('Creating Table E....')
    yrstotrial=[*range(1,11)]
    agedeath=[*range(40,95,5)]
    men=[{'name': "male " + str(age), 'age': age, 'sex': "M", 'dataSet': Ogden8} for age in agedeath]  # create women of age age
    women=[{'name': "female " + str(age), 'age': age, 'sex': "F", 'dataSet': Ogden8} for age in agedeath]  # create men of age age
    egMen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": men}}
    egWomen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": women}}
    gMen=game(egMen)
    gWomen=game(egWomen)

    dataMale=[[gMen.getClaimant(man).M('TRIAL','TRIAL+' + str(c) + "Y",options='M')[3]/c for c in yrstotrial] for man in gMen.getClaimants()]
    dataFemale=[[gWomen.getClaimant(woman).M('TRIAL','TRIAL+' + str(c) + "Y",options='M')[3]/c for c in yrstotrial] for woman in gWomen.getClaimants()]
    dfMale = pd.DataFrame(dataMale, index=agedeath).set_axis(yrstotrial,'columns')
    dfFemale = pd.DataFrame(dataFemale, index=agedeath).set_axis(yrstotrial,'columns')
    print('Writing tables...')
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table E (male)', dfMale, "Table E (male)", "Yrs to trial", "Age at death")
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table E (female)', dfFemale, "Table E (female)", "Yrs to trial", "Age at death")
    print('Finished Table E.')

def createTableF():
    print('Creating Table F....')
    yrstotrial=[*range(1,11)]
    agedeath=[*range(40,95,5)]
    men=[{'name': "male " + str(age), 'age': age, 'sex': "M", 'dataSet': Ogden8} for age in agedeath]  # create women of age age
    women=[{'name': "female " + str(age), 'age': age, 'sex': "F", 'dataSet': Ogden8} for age in agedeath]  # create men of age age
    egMen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": men}}
    egWomen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": women}}
    gMen=game(egMen)
    gWomen=game(egWomen)

    dataMale=[[gMen.getClaimant(man).M('TRIAL+' + str(c) + "Y",options='M')[3] for c in yrstotrial] for man in gMen.getClaimants()]
    dataFemale=[[gWomen.getClaimant(woman).M('TRIAL+' + str(c) + "Y",options='M')[3] for c in yrstotrial] for woman in gWomen.getClaimants()]
    dfMale = pd.DataFrame(dataMale, index=agedeath).set_axis(yrstotrial,'columns')
    dfFemale = pd.DataFrame(dataFemale, index=agedeath).set_axis(yrstotrial,'columns')
    print('Writing tables...')
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table F (male)', dfMale, "Table F (male)", "Yrs to trial", "Age at death")
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table F (female)', dfFemale, "Table F (female)", "Yrs to trial", "Age at death")
    print('Finished Table F.')

def createTables1to34():
    print('Generating Tables 1 to 34....')
    drs=[-0.02,-0.0175,-0.015,-0.01,-0.0075,-0.005,-0.0025,0,0.005,0.01,0.015,0.02, 0.025,0.03]
    tables=[['TRIAL','LIFE',[0,100]],['TRIAL',50,[16,49]],['TRIAL',55,[16,54]],['TRIAL',60,[16,59]],['TRIAL',65,[16,64]],['TRIAL',68,[16,67]],['TRIAL',70,[16,69]],['TRIAL',75,[16,74]],['TRIAL',80,[16,79]],[50,'LIFE',[0,50]],[55,'LIFE',[0,55]],[60,'LIFE',[0,60]],[65,'LIFE',[0,65]],[68,'LIFE',[0,68]],[70,'LIFE',[0,70]],[75,'LIFE',[0,75]],[80,'LIFE',[0,80]]]
    ages=[*range(0,101)]
    men=[{'name': "male " + str(age), 'age': age, 'sex': "M", 'dataSet': Ogden8} for age in ages]  # create women of age age
    women=[{'name': "female " + str(age), 'age': age, 'sex': "M", 'dataSet': Ogden8} for age in ages]  # create men of age age
    egMen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": men}}
    egWomen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": women}}
    gMen=game(egMen)
    gWomen=game(egWomen)
    dataMen=[[[gMen.getClaimant(c).M(table[0],table[1],discountRate=dr)[3] for dr in drs] for c in gMen.claimants if gMen.getClaimant(c).getAge()>=table[2][0] and gMen.getClaimant(c).getAge()<=table[2][1]] for table in tables]
    dataWomen=[[[gWomen.getClaimant(c).M(table[0],table[1],discountRate=dr)[3] for dr in drs] for c in gWomen.claimants if gWomen.getClaimant(c).getAge()>=table[2][0] and gWomen.getClaimant(c).getAge()<=table[2][1]] for table in tables]
    dataFramesMen=[pd.DataFrame(d, index=[*range(tables[dataMen.index(d)][2][0],tables[dataMen.index(d)][2][1]+1)]).set_axis(drs,'columns') for d in dataMen]
    dataFramesWomen=[pd.DataFrame(d, index=[*range(tables[dataWomen.index(d)][2][0],tables[dataWomen.index(d)][2][1]+1)]).set_axis(drs,'columns') for d in dataMen]

    print("Writing men's tables...")
    #Write men
    tableCount=1
    tCount=0
    for dataFrame in dataFramesMen:
        if tableCount<=18:
            tabletitle='Table ' + str(tableCount) + ": multiplier to " + str(tables[tCount][1])
        else:
            'Table ' + str(tableCount) + ": multiplier from " + str(tables[tCount][0])
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table ' + str(tableCount), dataFrame,
                        tabletitle, "Discount rate", "Age")
        tableCount+=2
        tCount+=1

    print("Writing women's tables...")
    #Write women
    tableCount=1
    tCount=0
    for dataFrame in dataFramesWomen:
        if tableCount<=18:
            tabletitle='Table ' + str(tableCount) + ": multiplier to " + str(tables[tCount][1])
        else:
            'Table ' + str(tableCount) + ": multiplier from " + str(tables[tCount][0])
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table ' + str(tableCount), dataFrame,
                        tabletitle, "Discount rate", "Age")
        tableCount+=2
        tCount+=1
    print('Finished generating Tables 1 to 34.')

def createDFTables35to36():
    print('Generating Tables 35 to 36...')
    drs=[-0.02,-0.0175,-0.015,-0.01,-0.0075,-0.005,-0.0025,0,0.005,0.01,0.015,0.02, 0.025,0.03]
    yrs=[*range(1,81)]
    male = {'name': "male", 'age': 10, 'sex': "M", 'dataSet': Ogden8}  # create male of age age
    eg = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                               "discountRate": -0.25 / 100, "Ogden": 8, "claimants": [male]}}
    g = game(eg)
    dataDF = [[g.getClaimant('male').M("TRIAL + " + str(yr) + "Y",options="A",discountRate=dr)[3] for dr in drs] for yr in yrs]
    dataTC = [[g.getClaimant('male').M("TRIAL","TRIAL + " + str(yr) + "Y", options="A", discountRate=dr)[3] for dr in drs] for yr in yrs]
    dfDF = pd.DataFrame(dataDF, index=yrs).set_axis(drs,'columns')
    dfTC = pd.DataFrame(dataTC, index=yrs).set_axis(drs,'columns')
    print('Writing tables...')
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table 35', dfDF, 'Table 35: discount factor', "Discount rate", "Years")
    write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Table 36', dfTC, 'Table 36: term certain', "Discount rate", "Years")
    print('Finished Tables 35 to 36.')

def additionalTables():
    print('Generating additional tables....')
    drs=[-0.015,-0.0075,-0.0025,0] #discount rates
    tos=[*range(1,126)] #cols
    ages=[*range(0,116)] #rows
    men=[{'name': "male " + str(age), 'age': age, 'sex': "M", 'dataSet': Ogden8} for age in ages]  # create women of age age
    women=[{'name': "female " + str(age), 'age': age, 'sex': "F", 'dataSet': Ogden8} for age in ages]  # create men of age age
    egMen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": men}}
    egWomen = {"rows": [], 'game': {"trialDate": datetime(2022, 8, 25), "projection": True, "autoYrAttained": False,
                           "discountRate": -0.25/100, "Ogden": 8, "claimants": women}}
    gMen=game(egMen)
    gWomen=game(egWomen)
    dfM={}
    dfW={}
    for dr in drs: #for each discount rate
        dfM[dr]=pd.DataFrame([[gMen.getClaimant(c).M('TRIAL',to,discountRate=dr)[3] for to in tos] for c in gMen.claimants],index=ages).set_axis(tos,axis='columns').replace("'To' date must be after 'From' date","")
        dfW[dr]=pd.DataFrame([[gWomen.getClaimant(c).M('TRIAL',to, discountRate=dr)[3] for to in tos] for c in gWomen.claimants],index=ages).set_axis(tos,axis='columns').replace("'To' date must be after 'From' date","")
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Males ' + f'{dr:0.2%}', dfM[dr], 'Males ' + f'{dr:0.2%}',
                        "Age until", "Age at trial")
        write_to_gsheet(service_file_path, spreadsheet_id_generated, 'Females ' + f'{dr:0.2%}', dfW[dr],
                    'Females ' + f'{dr:0.2%}', "Age until", "Age at trial")
    print('Finished generating additional tables.')

def copypasteOgden8publishedTables(spreadsheet_id):
    #test
    rows=[101,101,34,34,39,39,44,44,49,49,52,52,54,54,59,59,64,64,51,51,56,56,61,61,66,66,69,69,71,71,76,76,81,81,80,80]
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
        x=wks_published.get_values((4,2),(rows[table-1]+3,cols+1))

        wks_generated.update_values((rows[table-1]+4, 2),x, extend=True)
        # formatting - data cells
        model_cell = pygsheets.Cell((rows[table-1]+4, 2))
        model_cell.set_number_format(
            format_type=pygsheets.FormatType.NUMBER,
            pattern="0.00"
        )
        pygsheets.DataRange((rows[table-1]+4, 2), (2*rows[table-1]+4,cols+1), worksheet=wks_generated).apply_format(model_cell)

def createOgdenTables():
    x=0
    #createTableE()
    #createTableF()
    #createTables1to34()
    #createDFTables35to36()
    #additionalTables()
    #copypasteOgden8publishedTables(spreadsheet_id_Ogden8published)
    #create_joint_lives_tables(0,100)









createOgdenTables()

def check_in_list(unique_code):
    #returns true if unique code in list
    #get list
    gc = pygsheets.authorize(service_file=service_file_path)
    shDigitalGoods = gc.open_by_key(spreadsheet_DigitalGoods)
    wks=shDigitalGoods.worksheet_by_title('Codes')
    codes = [wks.get_col(2,include_tailing_empty=False),wks.get_col(4,include_tailing_empty=False),wks.get_col(6,include_tailing_empty=False)] #the three codes
    col=1
    for code in codes:
        col+=2
        if unique_code in code:
            ro=code.index(unique_code)
            dt=wks.get_value((ro+1,col))
            if dt=="":
                #unactivated - so add date
                wks.update_value((ro+1,col),datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
                return True
            else : #check if expired
                n=datetime.today()
                a=datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
                e=add_years(a,1)
                if n<=e:
                    return True
    return False

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (datetime(d.year + years, 1, 1) - datetime(d.year, 1, 1))



# print(g.processRows())
# print(g.getClaimant('Gadsden').getSummaryStats())
# print(errors.getLog())
# print(g.getClaimant('Jonnie').getStateRetirementAge())
# print(g.process())
# print(g.getClaimant('Hicken').M(60,'LIFE', freq='Y',options='M'))


#print(g.getClaimant('Norman').JLE())
#print(g.getClaimant('Norman').JLM())
print(g.getClaimant('Jacqueline').M('TRIAL',40,'Y','A'))
print(g.getClaimant('Jacqueline').M('TRIAL',40,"Y","AM"))
#print(g.getClaimant('Norman').M('TRIAL','LIFE',freq='Y'))
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
