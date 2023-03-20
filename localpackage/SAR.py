import numpy as np
import pandas as pd
import os

class SAR():
    def __init__(self, parent):
        self.parent=parent #parent is baseperson
        self.SAROptions = {} #disctionary for hashing results


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


    def transformLx(self,newRng,shift=0):
        #Takes a newRng and returns a corresponding Lx
        newLx=np.array([np.interp(age-shift, self.getLx()[1], self.getLx()[0], left=1,right=0) for age in newRng])
        return newLx

    def refresh(self):
        self.SAROptions.clear()

    def getLx(self):


        def createHashObject():
            return hash(self.gettrialDate())

        # First check if we already have calculated this one for a given SINGLE discount rate
        h = createHashObject()
        if h in self.SAROptions:
            result = self.SAROptions[h]
            return result['Lx'], result['Rng']

        dfSAR=self.loadSAR()

        #add extra row if necessary
        dfSAR=dfSAR[:self.gettrialDate()]


        if dfSAR.iloc[-1].name<self.gettrialDate():
            a=pd.Series({'Rate':0.2},name=self.gettrialDate()) #arbitrary rate
            #dfSAR = dfSAR.append(a)
            dfSAR=pd.concat([dfSAR,a.to_frame().T])
        dfSAR['Rate']=dfSAR['Rate'].shift(+1)
        dfSAR['tvalue'] = dfSAR.index

        dfSAR=dfSAR.iloc[::-1] #reverse rows

        dfSAR['days'] = (dfSAR['tvalue'].shift() - dfSAR['tvalue']).dt.days
        dfSAR.iat[0,2]=0 #days

        dfSAR['dailyRate'] = dfSAR['Rate'].apply(lambda x: x  / (365.25*100))
        dfSAR['aggInt'] = dfSAR['dailyRate'].shift(1) * dfSAR['days']
        dfSAR.iat[0, 4] = 0  # aggInt


        dfSAR['cumaggInt']=dfSAR['aggInt'].cumsum()
        dfSAR['Lx']=dfSAR['cumaggInt']+1
        dfSAR['age']=dfSAR['tvalue'].apply(lambda x: (x-self.getDOB()).days/365.25) #age of person

        days=np.array(dfSAR['days'])
        self._pastDays=np.cumsum(days)
        dfSAR=dfSAR.iloc[::-1] #reverse rows


        Rng = np.array(dfSAR['age'])  #The Rng

        Lx=np.array(dfSAR['Lx'])  #Interest

        result= {'Lx': Lx, 'Rng': Rng}
        self.SAROptions[h]=result
        return Lx, Rng


    def loadSAR(self):
        file = os.path.dirname(os.path.abspath(__file__))+'/Data/SAR.csv'

        try:
            return pd.read_csv(file, index_col=0, header=0, parse_dates=True, dayfirst=True)
        except:
            return False

        return True
