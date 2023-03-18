import numpy as np
import pandas as pd
import os


class SAR():
    def __init__(self, parent):
        self.parent=parent
        self.loadSAR()
        self.dirty=True
        self.refresh()
        self.dfSAR
        self.Rng
        self._Lx

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
        self.loadSAR()
        self._Lx, self.Rng=self.getLx()

    def transformLx(self,newRng,shift=0):
        #Takes a newRng and returns a corresponding Lx
        newLx=np.array([np.interp(age-shift, self.Rng, self._Lx, left=1,right=0) for age in newRng])
        return newLx


    def getLx(self):
        #add extra row if necessary
        self.dfSAR=self.dfSAR[:self.gettrialDate()]
        if self.dfSAR.iloc[-1].name<self.gettrialDate():
            a=pd.Series({'Rate':0.2},name=self.gettrialDate()) #arbitrary rate
            #self.dfSAR = self.dfSAR.append(a)
            self.dfSAR=pd.concat([self.dfSAR,a.to_frame().T])
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


        Rng = np.array(self.dfSAR['age'])  #The Rng

        Lx=np.array(self.dfSAR['Lx'])  #Interest

        self.dirty=False

        return Lx, Rng

    def refresh(self):
        if self.dirty: self.calcs()

    def loadSAR(self):
        file = os.path.dirname(os.path.abspath(__file__))+'/Data/SAR.csv'

        try:
            self.dfSAR = pd.read_csv(file, index_col=0, header=0, parse_dates=True, dayfirst=True)
            print(self.dfSAR)
        except:
            return False

        return True
