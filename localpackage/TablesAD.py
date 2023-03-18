from localpackage.utils import Ogden
import pandas as pd
import math
import os

Sex=['M','F']
Tables=['A','B','C','D']
Qual7=['D','G','O']
Qual8=['1','2','3']
Employment=['Employed','Unemployed']
header7 = pd.MultiIndex.from_product([Employment, Qual7], names=['Employment', 'Qualification'])
header8 = pd.MultiIndex.from_product([Employment, Qual8], names=['Employment', 'Qualification'])


class TablesAD():
    def __init__(self, Ogden):
        self.Ogden=Ogden
        self.OgdenTables={}
        self.loadOgdenCSV()

    def getCont(self,sex,employed,qualification,disabled,age):
        sex=sex[0]
        if self.Ogden==8: qualification = str(qualification)
        if sex not in Sex:
            print('Sex must be ""M"" or ""F""')
            return None
        if self.Ogden==7 and qualification not in Qual7:
            print('Wrong qualification label (Ogden 7)')
            return None
        if self.Ogden==8 and qualification not in Qual8:
            print('Wrong qualification label (Ogden 8)')
            return None
        Table=None
        if sex=='M' and not disabled:
            Table=self.getTable('A')
        if sex=='M' and disabled:
            Table=self.getTable('B')
        if sex=='F' and not disabled:
            Table=self.getTable('C')
        if sex=='F' and disabled:
            Table=self.getTable('D')
        if int(age) > Table.iloc[-1].name: return None  # too old for table
        rows=Table[Table.index<=int(age)]
        if len(rows.index)>0:
            emp=Employment[0] if employed else Employment[1]
            if math.isnan(rows.iloc[-1][emp][qualification]): return None #not defined in the Table
            return rows.iloc[-1][emp][qualification]
        return None #too young for table


    def getTable(self,Table):
        return self.OgdenTables[self.Ogden][Table]

    def loadOgdenCSV(self):
        for O in Ogden:
            Tabs={}
            for Table in Tables:
                path = os.path.dirname(os.path.abspath(__file__))+"/Data/" + str(O)+"Table"+Table+".csv"
                Tabs[Table]=pd.read_csv(path, index_col=0,header=[0,1])
                def spl(x):
                    return int(x.split('-')[0])
                Tabs[Table].index=Tabs[Table].index.map(spl)
            self.OgdenTables[O]=Tabs


    def createCSV(self):
        self.loadOgden()
        for O in Ogden:
            for Table in Tables:
                path = os.path.dirname(os.path.abspath(__file__))+"/Data/" + str(O)+"Table"+Table+".csv"
                self.OgdenTables[O][Table].to_csv(path, index=True)

    def loadOgden(self):
        for O in Ogden:
            file = 'Ogden ' + str(O) + ' Tables A-D.xlsx'
            if O==7: header=header7
            if O==8: header=header8
            Tabs={}
            for Table in Tables:
                Tabs[Table]=pd.read_excel(file, Table, index_col=0, header=0)
                Tabs[Table].columns=header
            self.OgdenTables[O]=Tabs


