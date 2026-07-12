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
# and Ogden 8 (1/2/3). Lets a claimant configured with either label set work under either
# edition, and in particular lets the historical default qualification 'D' resolve under the
# default Ogden 8 (to '1'=Degree, preserving the default's original meaning). (F26/F38/F51)
# NOTE: this D/G/O <-> 1/2/3 mapping is a domain assumption (flagged in the review).
Qual7to8={'D':'1','G':'2','O':'3'}
Qual8to7={'1':'D','2':'G','3':'O'}
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


