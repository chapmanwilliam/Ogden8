from localpackage.utils import Ogden
from localpackage.errorLogging import errors
import pandas as pd
import math
import os

Sex=['M','F']
Tables=['A','B','C','D']
Qual7=['D','G','O']
Qual8=['1','2','3']
# Education-level label equivalence between Ogden 7 (D=Degree, G=GCSE-A-level, O=Other/below)
# and Ogden 8 (Level 3 / 2 / 1). Lets a claimant configured with either label set work under
# either edition. (F26/F38/F51)
#
# D maps to 3, NOT to 1. This was the other way round and inverted the education axis: a
# degree-educated claimant carrying the Ogden 7 label was priced on the Ogden 8 "below GCSE"
# column. On Table D (disabled female, employed) that returned 0.22 against a correct 0.60.
#
# The tables settle it without needing to rely on how the levels are named. Reading the two
# CSVs column by column, 7TableA D/G/O = 0.92/0.92/0.87 at 20-24 against 8TableA 3/2/1 =
# 0.91/0.91/0.87: the columns correspond in file order. And the 16-19 band is blank in the
# D column of every Ogden 7 table and in the 3 column of every Ogden 8 table - nobody holds a
# degree at 16 - which pins D to 3 independently of the values.
Qual7to8={'D':'3','G':'2','O':'1'}
Qual8to7={'3':'D','2':'G','1':'O'}
FALLBACK_CONT=0.9  # VBA Claimant.getCont returns 0.9 when the table value is <=0 / NaN / absent
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
        qualification=str(qualification)
        # Accept either edition's label set by mapping to the active edition's labels. (F26/F38/F51)
        if self.Ogden==8 and qualification in Qual7:
            qualification=Qual7to8[qualification]
        if self.Ogden==7 and qualification in Qual8:
            qualification=Qual8to7[qualification]
        if sex not in Sex:
            errors.add('Sex must be "M" or "F"')
            return FALLBACK_CONT
        if (self.Ogden==7 and qualification not in Qual7) or (self.Ogden==8 and qualification not in Qual8):
            errors.add('Unrecognised contingency qualification label: ' + qualification)
            return FALLBACK_CONT
        Table=None
        if sex=='M' and not disabled:
            Table=self.getTable('A')
        if sex=='M' and disabled:
            Table=self.getTable('B')
        if sex=='F' and not disabled:
            Table=self.getTable('C')
        if sex=='F' and disabled:
            Table=self.getTable('D')
        # Clamp the age to the table's band range instead of returning None (the VBA clamps
        # over-age to the last band and under-age to the first band). (F36)
        firstBand=int(Table.index[0])
        lastBand=int(Table.iloc[-1].name)
        a=min(max(int(age), firstBand), lastBand)
        rows=Table[Table.index<=a]
        emp=Employment[0] if employed else Employment[1]
        value=rows.iloc[-1][emp][qualification]
        if math.isnan(value):
            return FALLBACK_CONT  # NaN cell -> VBA 0.9 fallback (F36)
        return value


    def getTable(self,Table):
        return self.OgdenTables[self.Ogden][Table]

    def loadOgdenCSV(self):
        for O in Ogden:
            OgdenTableVersion=int(O)
            Tabs={}
            for Table in Tables:
                path = os.path.dirname(os.path.abspath(__file__))+"/Data/" + str(OgdenTableVersion)+"Table"+Table+".csv"
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


