import numpy as np
import pandas as pd
from localpackage.utils import years, regions, sexes
import os
import json


class dataSet():

    def __init__(self, parent):
        self.parent = parent #parent is baseperson

        self.dataSetOptions = {}  # dictionary to store hashes of results
        self.revisedAgeOptions = {}  # dictionary to store hashes of results

        self.dfCohort = pd.DataFrame()
        self.dfPeriod = pd.DataFrame()

    def getProjection(self):
        return self.parent.getProjection()



    def getautoYrAttained(self):
        return self.parent.getautoYrAttained()

    def calcYrAttained(self):
        if self.getautoYrAttained():
            # we need the last year C was alive i.e. when did he die
            if self.isFatal():
                diedXyearsago = self.parent.getAge() - self.getAge()
                return int(self.gettrialDate().year - diedXyearsago)
            else:
                return self.gettrialDate().year
        else:
            return self.getYrAttainedIn()

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def getDict(self):
        return {'year': self.getYear(), 'region': self.getRegion(), 'yrAttainedIn': self.getYrAttainedIn()}

    def getAge(self):
        if self.isFatal():  # i.e. if this is a fatal case, use age at death
            return self.parent.getAAD()
        return self.parent.getAge()

    def getSex(self):
        return self.parent.getSex()

    def getRegion(self):
        return self.region
    
    def getYear(self):
        return self.parent.getYear()

    def getYrAttainedIn(self):
        return self.parent.getYrAttainedIn()

    def getRegion(self):
        return self.parent.getRegion()

    def getdiscountRate(self):
        return self.parent.getdiscountRate()

    def setdeltaLE(self, deltaLE):
        self.deltaLE = deltaLE

    def getdeltaLE(self):
        return self.parent.getdeltaLE()

    def getrevisedAge(self):
        def createHashObject():
            hObj = {'sex': self.getSex(), 'age': self.getAge(), 'deltaLE': self.getdeltaLE(), 'region': self.getRegion(),
                    'year': self.getYear(), 'projection': self.getProjection(), 'autoyrattained': self.getautoYrAttained()}
            hObjJSON = json.dumps(hObj, sort_keys=True)
            return hash(hObjJSON)

        # First check if we already have calculated this one
        h = createHashObject()
        if h in self.revisedAgeOptions:
            result = self.revisedAgeOptions[h]
            return result

        def getLE(lowerAge, higherAge, targetLE):
            testAge = lowerAge + (higherAge - lowerAge) / 2
            Lx = self.getLx(testAge)[0]
            LE = np.trapz(Lx)
            if abs(targetLE - LE) < tolerance or testAge < tolerance or testAge > 125 - tolerance: return testAge
            if LE > targetLE: lowerAge = testAge
            if LE < targetLE: higherAge = testAge
            return getLE(lowerAge, higherAge, targetLE)

        if self.getdeltaLE() == 0 and not self.gettargetLE():
            result = self.getAge()
            self.revisedAgeOptions[h] = result
            return result
        else:
            tolerance = 0.001
            Lx = self.getLx(self.getAge())[0]
            if self.gettargetLE():
                targetLE = self.gettargetLE()
            else:
                targetLE = min(125, max(0, np.trapz(Lx) + self.getdeltaLE()))
            result = getLE(0, 125, targetLE)
            self.revisedAgeOptions[h] = result
            return result

    def refresh(self):
        self.dataSetOptions.clear()

    def isFatal(self):
        return self.parent.isFatal()

    def gettargetLE(self):
        return self.parent.gettargetLE()

    def calcs(self):
        return

    def getLx(self, revisedAge):
        # returns the Lx for person of revisedAge alive in currentYear
        # revisedAge is a float

        def createHashObject():
            hObj = {'sex': self.getSex(), 'revisedAge': revisedAge, 'region': self.getRegion(), 'year': self.getYear(),
                    'projection': self.getProjection(), 'autoyrattained': self.getautoYrAttained()}
            hObjJSON = json.dumps(hObj, sort_keys=True)
            return hash(hObjJSON)

        # First check if we already have calculated this one for a given SINGLE discount rate
        h = createHashObject()
        if h in self.dataSetOptions:
            result = self.dataSetOptions[h]
            return result['Lx'], result['Rng']

        self.loaddataSetCSV()

        if self.dfCohort.empty or self.dfPeriod.empty: return False

        intAge = int(revisedAge)
        fraction = revisedAge - intAge
        lowerAge = intAge
        upperAge = intAge + 1

        def getCol(age):
            bornYear = self.calcYrAttained() - age
            if self.getProjection():  # use projection
                if self.calcYrAttained() in self.dfPeriod.columns and self.calcYrAttained() + (
                        125 - age) in self.dfPeriod.columns:  # use period data if possible. i.e. if bornYear too early for cohort calculation
                    subFrame = self.dfPeriod.loc[age:, self.calcYrAttained():]
                    col = pd.Series(np.diagonal(subFrame, 0), index=[subFrame.index])
                elif bornYear in self.dfCohort.columns:  # otherwise use cohort data
                    col = self.dfCohort[bornYear][self.dfCohort.index >= age]
                else:
                    # Error - the request is outside the scope of the data
                    print('Insufficient data')
                    return None
            else:  # don't use projection
                if self.calcYrAttained() in self.dfPeriod.columns:
                    # get the data going downwards from age
                    col = self.dfPeriod.loc[age:, self.calcYrAttained()]
                else:
                    # Error - the request is outside the scope of the data
                    print('Insufficient data')
                    return None

            return np.array(col)

        col1 = getCol(lowerAge)  # number of deaths per 100,000 at end of first year for lowerAge
        col2 = getCol(upperAge)  # number of deaths per 100,000 at end of first year for higherAge
        # make same length
        minLen = min(col1.size, col2.size)
        col1 = np.resize(col1, (1, minLen))
        col2 = np.resize(col2, (1, minLen))
        # take weighted average
        col = (1 - fraction) * col1 + (fraction) * col2
        # add zero as very first element
        c = np.array(0)
        col = np.append(c, col)
        Qx = col / 100000  # to get probability of dying by end of period

        Lx = np.cumprod(1 - Qx)  # Lx (mortality only)
        Rng = np.array([self.getAge() + x for x in range(0, Lx.size)])  # Range

        result = {'Lx': Lx, 'Rng': Rng}
        self.dataSetOptions[h] = result

        return Lx, Rng

    def transformLx(self, newRng, shift=0):
        # Takes a newRng and returns a corresponding Lx
        Lx, Rng = self.getLx(self.getrevisedAge())
        newLx = np.array([np.interp(age - shift, Rng, Lx, left=1, right=0) for age in newRng])
        return newLx

    def createCSV(self):
        # creates CSVs of the date
        # Files of type 'cohortMUK2008'
        for year in years:
            periodFile = os.path.dirname(os.path.abspath(__file__)) + '/Data/perioddata ' + str(year) + '.xlsx'
            cohortFile = os.path.dirname(os.path.abspath(__file__)) + '/Data/cohortdata ' + str(year) + '.xlsx'
            for sex in sexes:
                for region in regions:
                    sheet = region + " " + sex + 's'
                    self.dfPeriod = pd.read_excel(periodFile, sheet, index_col=0, header=0)
                    self.dfCohort = pd.read_excel(cohortFile, sheet, index_col=0, header=0)
                    pathPeriod = os.path.dirname(os.path.abspath(__file__)) + "/Data/period" + sex[0] + region + str(
                        year) + '.csv'
                    pathCohort = os.path.dirname(os.path.abspath(__file__)) + "/Data/cohort" + sex[0] + region + str(
                        year) + '.csv'
                    self.dfPeriod.to_csv(pathPeriod, index=True)
                    self.dfCohort.to_csv(pathCohort, index=True)

    def getdataTitle(self):
        return 'ONS ' + self.getSex()[0] + self.getRegion() + str(self.getYear()) + ', year attained in ' + str(
            self.calcYrAttained())

    def loaddataSetCSV(self):
        periodFile = os.path.dirname(os.path.abspath(__file__)) + '/Data/period' + self.getSex()[0] + self.getRegion() + str(
            self.getYear()) + '.csv'
        cohortFile = os.path.dirname(os.path.abspath(__file__)) + '/Data/cohort' + self.getSex()[0] + self.getRegion() + str(
            self.getYear()) + '.csv'
        try:
            self.dfPeriod = pd.read_csv(periodFile, index_col=0, header=0)
            self.dfPeriod.columns = self.dfPeriod.columns.astype(int)
            self.dfCohort = pd.read_csv(cohortFile, index_col=0, header=0)
            self.dfCohort.columns = self.dfCohort.columns.astype(int)
        except:
            return False
        self.dirtyData = False
        return True

    def loaddataSet(self):
        if not self.valid(): return False
        periodFile = os.path.dirname(os.path.abspath(__file__)) + '/Data/perioddata ' + str(self.getYear()) + '.xlsx'
        cohortFile = os.path.dirname(os.path.abspath(__file__)) + '/Data/cohortdata ' + str(self.getYear()) + '.xlsx'
        sheet = self.region + " " + self.getSex()[0] + 's'

        try:
            self.dfPeriod = pd.read_excel(periodFile, sheet, index_col=0, header=0)
            self.dfCohort = pd.read_excel(cohortFile, sheet, index_col=0, header=0)
        except:
            return False

        return True

    def valid(self):
        # returns True if input ok
        if self.getYear() in years and self.getSex()[0] in sexes and self.getRegion() in regions: return True
        return False
