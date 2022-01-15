from datetime import datetime
from pymaybe import maybe
from localpackage.person import person
from localpackage.TablesAD import TablesAD
from localpackage.utils import defaultdiscountRate, defaultOgden, Ogden, parsedateString
from localpackage.errorLogging import errors

class game():


    def getSummaryStatsClaimants(self):
        #returns summary statistics for each Claimant
        claimantStats={}
        for claimant in self.claimants:
            claimantStats[claimant] = self.getClaimant(claimant).getSummaryStats()
        return claimantStats

    def getprojection(self):
        return self.projection

    def getautoYrAttained(self):
        return self.autoYrAttained

    def getAAD(self,name):
        claimant=self.getClaimant(name)
        if claimant:
            return claimant.getAAD()
        else:
            print("Non existent name for claimant in getAAI")
            errors.add("Non existent name for claimant in getAAI")
            return None

    def getAAT(self,name):
        claimant=self.getClaimant(name)
        if claimant:
            return claimant.getAAT()
        else:
            print("Non existent name for claimant in getAAI")
            errors.add("Non existent name for claimant in getAAI")
            return None

    def getDOI(self):
        if hasattr(self,'doi'):
            return self.doi
        else:
            return None

    def getAAI(self,name):
        claimant=self.getClaimant(name)
        if claimant:
            return claimant.getAAI()
        else:
            print("Non existent name for claimant in getAAI")
            errors.add("Non existent name for claimant in getAAI")
            return None

    def addClaimant(self,claimant):
        if not claimant.name in self.claimants:
            self.claimants[claimant.name]=claimant
        else:
            print("Name already exists")
            errors.add("Name already exists")

    def getClaimant(self,name):
        if name in self.claimants:
            return self.claimants[name]
        else:
            return None

    def getClaimants(self):
        return self.claimants

    def getDict(self):
        #encodes the game, claimants, dependents
        cs=[claimant.getDict() for claimant in self.claimants]
        game={'discountRate':self.getdiscountRate(), 'Ogden':self.ogden, 'claimants': cs}
        return game

    def getdiscountRate(self):
        return self.discountRate

    def setdiscountRate(self,rate):
        self.discountRate=rate
        self.setDirty(True) #TODO: actually we only need to make dirty the data set

    def getTablesAD(self):
        return self.TablesAD

    def gettrialDate(self):
        return self.trialDate

    def setDirty(self,value=True):
        [claimant.setDirty(True) for claimant in self.claimants]  #make all claimants dirty
        self.dirty=True


    def settrialDate(self,trialDate):
        self.trialDate=trialDate
        self.setDirty(True)

    def refresh(self):
        [claimant.refresh() for claimant in self.claimants.values()] #refresh all the claimants
        self.dirty=False

    def processRows(self):
        #rows is a list of rows of form
        # row={'name': 'CHRISTOPHER','fromAge':55, 'toAge':125, 'freq': 'Y', 'status': 'Injured', 'options':'AMIC'}
        if self.function=="MULTIPLIER":
            return [maybe(self.getClaimant(row['name'])).M(row['fromAge'], row['toAge'], freq=row['freq'],options=row['options']).or_else([None, None, None, None]) for row in self.rows]
        elif self.function=="INTERESTHOUSE":
            return [maybe(self.getClaimant(row['name'])).INTERESTHOUSE(row['fromAge'], row['toAge']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function=="REVERSION":
            return [maybe(self.getClaimant(row['name'])).REVERSION(row['fromAge'], row['toAge']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function=="REVISEDAGE":
            return [maybe([self.getClaimant(row['name']).getrevisedAge()]).or_else(
                [None]) for row in self.rows]
        elif self.function=="AAD":
            return [maybe([self.getClaimant(row['name']).getEAD()]).or_else(
                [None]) for row in self.rows]

    def process(self):
        #returns row results and summary statistics
        return {'rows': self.processRows(), 'summary': self.getSummaryStatsClaimants(), 'errorLog': errors.getLog()}

    def __init__(self, attributes):

        self.function="MULTIPLIER" #default
        if 'function' in attributes:
            self.function=attributes['function']

        if 'rows' in attributes:
            self.rows=attributes['rows']

        self.autoYrAttained=False
        if 'autoYrAttained' in attributes['game']:
            self.autoYrAttained=attributes['game']['autoYrAttained']

        self.projection=True
        if 'projection' in attributes['game']:
            self.projection = attributes['game']['projection']

        if 'trialDate' in attributes['game']: #if trial date supplied, accept; otherwise use today's date
            if type(attributes['game']['trialDate']) is str:
                attributes['game']['trialDate']=parsedateString(attributes['game']['trialDate'])
            self.trialDate=attributes['game']['trialDate']
        else:
            self.trialDate=datetime.now()

        if 'DOI' in attributes['game']: #if trial date supplied, accept; otherwise use today's date
            if type(attributes['game']['DOI']) is str:
                attributes['game']['DOI']=parsedateString(attributes['game']['DOI'])
            self.doi=attributes['game']['DOI']


        if 'discountRate' in attributes['game']: #if discountrate supplied, accept; otherwise use default
            self.discountRate=attributes['game']['discountRate']
        else:
            self.discountRate=defaultdiscountRate

        if 'Ogden' in attributes['game']: #if correct Ogden supplied, accept; otherwise use default
            if attributes['game']['Ogden'] in Ogden:
                self.ogden=attributes['game']['Ogden']
            else:
                self.ogden=defaultOgden
        else:
            self.ogden=defaultOgden

        self.dirty=True
        self.TablesAD=TablesAD(self.ogden)

        self.claimants={} #dictionary for storing the claimants by name
        self.dependents={} #dictionary for storing the dependents by name

        if 'claimants' in attributes['game']:
            [self.addClaimant(person(cs,parent=self)) for cs in attributes['game']['claimants']]
        else:
            print('No claimants added')
            errors.add("No claimants added")


