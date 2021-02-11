import numpy as np
import pandas as pd
from localpackage.utils import years, regions, sexes

class dataSet():

    def __init__(self, attributes, parent, deltaLE=0):
        self.parent=parent
        self.year=attributes['year']
        self.region=attributes['region']
        self.yrAttainedIn=attributes['yrAttainedIn']
        self.deltaLE=deltaLE
        self._Lx = self._Lxd = None

        self.dirtyCalcs=True #True means calcs need to be done
        self.dirtyData=True #means data set has to be (re-)loaded

        self.dfCohort=pd.DataFrame()
        self.dfPeriod=pd.DataFrame()

        self.loaddataSetCSV()

    def getDict(self):
        return {'year':self.year,'region':self.region,'yrAttainedIn':self.yrAttainedIn}


    def getAge(self):
        if self.isFatal(): #i.e. if this is a fatal case, use age at death
            return self.parent.getAAD()
        return self.parent.getAge()

    def getSex(self):
        return self.parent.getSex()

    def setdirtyCalcs(self,value=True):
        self.dirtyCalcs=value

    def setdirtyData(self,value=True):
        self.dirtyData=value

    def setYear(self,year):
        self.year=year
        self.dirtyData=True

    def setRegion(self,region):
        self.region=region
        self.dirtyData=True

    def setyrAttained(self,yrAttained):
        self.yrAttainedIn=yrAttained
        self.dirtyCalcs=True

    def getdiscountRate(self):
        return self.parent.getdiscountRate()

    def setdeltaLE(self,deltaLE):
        self.deltaLE=deltaLE
        self.dirtyCalcs=True

    def getrevisedAge(self,deltaLE):
        self.dirtyCalcs=True
        def getLE(lowerAge,higherAge,targetLE):
            testAge=lowerAge+(higherAge-lowerAge)/2
            Lx = self.getLxLxd(testAge, LxOnly=True)
            LE=np.trapz(Lx)
            if abs(targetLE-LE)<tolerance or testAge<tolerance or testAge>125-tolerance: return testAge
            if LE>targetLE: lowerAge=testAge
            if LE<targetLE: higherAge=testAge
            return getLE(lowerAge,higherAge,targetLE)
        if deltaLE==0:
            return self.getAge()
        else:
            tolerance=0.001
            Lx = self.getLxLxd(self.getAge(), LxOnly=True)
            targetLE=min(125,max(0,np.trapz(Lx)+deltaLE))
            return getLE(0,125,targetLE)

    def refresh(self):
        #refresh if dirty data or dirty calcs
        if self.dirtyData:
            self.loaddataSet()
        if self.dirtyCalcs:
            self.calcs()

    def isFatal(self):
        return self.parent.isFatal()

    def calcs(self):
        self.revisedAge = self.getrevisedAge(self.deltaLE)
        self._Lx, self.Rng = self.getLxLxd(self.revisedAge,Fatal=self.isFatal())
        self.dirtyCalcs=False



    def getLxLxd(self,revisedAge,Fatal=False, LxOnly=False):
        #returns the Qx for person of revisedAge alive in currentYear
        #age is a float
        if self.dfCohort.empty or self.dfPeriod.empty: return False

        intAge=int(revisedAge)
        fraction=revisedAge-intAge
        lowerAge=intAge
        upperAge=intAge+1

        def getCol(age):
            bornYear = self.yrAttainedIn - age
            if bornYear in self.dfCohort.columns: #ues cohort data if possible
                col=self.dfCohort[bornYear][self.dfCohort.index>=age]
            elif self.yrAttainedIn in self.dfPeriod.columns: #i.e. if bornYear too early for cohort calculation
                subFrame= self.dfPeriod.loc[age:, self.yrAttainedIn:]
                col=pd.Series(np.diagonal(subFrame,0),index=[subFrame.index])
            else:
                #Error - the request is outside the scope of the data
                print ('Insufficient data')
                return False
            return np.array(col)

        col1=getCol(lowerAge) #number of deaths per 100,000 at end of first year for lowerAge
        col2=getCol(upperAge) #number of deaths per 100,000 at end of first year for higherAge
        #make same length
        minLen=min(col1.size,col2.size)
        col1=np.resize(col1,(1,minLen))
        col2=np.resize(col2,(1,minLen))
        #take weighted average
        col=(1-fraction)*col1+(fraction)*col2
        #add zero as very first element
        c=np.array(0)
        col=np.append(c,col)
        Qx=col/100000 #to get probability of dying by end of period

        #Lx (mortality only)
        Lx=np.cumprod(1-Qx)
        #Range
#        Rng = np.arange(self.getAge(), self.getAge() + Lx.size)
#        Rng = np.linspace(self.getAge(),self.getAge()+Lx.size,num=Lx.size, endpoint=False)
        Rng=np.array([self.getAge() + x for x in range(0,Lx.size)])

        if LxOnly: return Lx

        return Lx, Rng

    def transformLx(self,newRng,shift=0):
        #Takes a newRng and returns a corresponding Lx
        newLx=np.array([np.interp(age-shift, self.Rng, self._Lx, left=1,right=0) for age in newRng])
        return newLx

    def createCSV(self):
        #creates CSVs of the date
        #Files of type 'cohortMUK2008'
        for year in years:
            periodFile = 'localpackage/Data/perioddata ' + str(self.year) + '.xlsx'
            cohortFile = 'localpackage/Data/cohortdata ' + str(year) + '.xlsx'
            for sex in sexes:
                for region in regions:
                    sheet = region + " " + sex + 's'
                    self.dfPeriod = pd.read_excel(periodFile, sheet, index_col=0, header=0)
                    self.dfCohort = pd.read_excel(cohortFile, sheet, index_col=0, header=0)
                    pathPeriod="localpackage/Data/period"+sex[0]+region+str(year) + '.csv'
                    pathCohort="localpackage/Data/cohort"+sex[0]+region+str(year) + '.csv'
                    self.dfPeriod.to_csv(pathPeriod, index=True)
                    self.dfCohort.to_csv(pathCohort, index=True)

    def getdataTitle(self):
        return 'ONS ' + self.getSex()[0] + self.region + str(self.year) + ', year attained in ' + str(self.yrAttainedIn)

    def loaddataSetCSV(self):
        periodFile='localpackage/Data/period'+self.getSex()[0]+self.region+str(self.year)+'.csv'
        cohortFile='localpackage/Data/cohort'+self.getSex()[0]+self.region+str(self.year)+'.csv'
        try:
            self.dfPeriod = pd.read_csv(periodFile, index_col=0, header=0)
            self.dfPeriod.columns=self.dfPeriod.columns.astype(int)
            self.dfCohort = pd.read_csv(cohortFile, index_col=0, header=0)
            self.dfCohort.columns=self.dfCohort.columns.astype(int)
        except:
            return False
        self.dirtyData=False
        return True

    def loaddataSet(self):
        if not self.valid(): return False
        periodFile='localpackage/Data/perioddata ' + str(self.year) + '.xlsx'
        cohortFile='localpackage/Data/cohortdata ' + str(self.year)+ '.xlsx'
        sheet=self.region + " " + self.getSex()[0] + 's'

        try:
            self.dfPeriod=pd.read_excel(periodFile,sheet,index_col=0,header=0)
            self.dfCohort=pd.read_excel(cohortFile,sheet,index_col=0,header=0)
        except:
            return False

        self.dirtyData=False
        return True

    def valid(self):
        #returns True if input ok
        if self.year in years and self.getSex()[0] in sexes and self.region in regions: return True
        return False