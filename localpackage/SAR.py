import numpy as np
import pandas as pd


class SAR():
    def __init__(self, parent):
        self.parent=parent
        self.loadSAR()
        self.dirty=True
        self.refresh()

    def setDirty(self,value=True):
        self.dirty=True

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def getDOB(self):
        return self.parent.getDOB()

    def isFatal(self):
        return self.parent.isFatal()

    def getAge(self):
        if self.isFatal(): #i.e. if this is a fatal case, use age at death
            return self.parent.getAAD()
        return self.parent.getAge()

    def calcs(self):
        self._Lx, self.Rng=self.getLxLd()

    def getLxLd(self):
        #add extra row if necessary
        if self.dfSAR.iloc[-1].name<self.gettrialDate():
            a=pd.Series({'Rate':0.2},name=self.gettrialDate()) #arbitrary rate
            self.dfSAR=self.dfSAR.append(a)
        self.dfSAR['Rate']=self.dfSAR['Rate'].shift(+1)
        self.dfSAR['tvalue'] = self.dfSAR.index

        self.dfSAR=self.dfSAR.iloc[::-1] #reverse rows

        self.dfSAR['days'] = (self.dfSAR['tvalue'].shift() - self.dfSAR['tvalue']).dt.days
        self.dfSAR.iat[0,2]=0 #days

        self.dfSAR['dailyRate'] = self.dfSAR['Rate'].apply(lambda x: x  / (365.25*100))
        self.dfSAR['aggInt'] = self.dfSAR['dailyRate'].shift(1) * self.dfSAR['days']
        self.dfSAR.iat[0, 4] = 0  # aggInt


        self.dfSAR['cumaggInt']=self.dfSAR['aggInt'].cumsum()
        self.dfSAR['Lx']=self.dfSAR['cumaggInt']+1
        self.dfSAR['age']=self.dfSAR['tvalue'].apply(lambda x: (x-self.getDOB()).days/365.25) #age of person

        days=np.array(self.dfSAR['days'])
        self._pastDays=np.cumsum(days)
        self.dfSAR=self.dfSAR.iloc[::-1] #reverse rows

        #The Rng
        Rng = np.array(self.dfSAR['age'])
        #Interest
        Lx=np.array(self.dfSAR['Lx'])

        self.dirty=False

        return Lx, Rng

    def refresh(self):
        if self.dirty: self.calcs()

    def loadSAR(self):
        file= 'localpackage/Data/SAR.csv'

        try:
            self.dfSAR = pd.read_csv(file, index_col=0, header=0, parse_dates=True, dayfirst=True)
        except:
            return False

        return True
