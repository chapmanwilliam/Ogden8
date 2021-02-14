from datetime import datetime
from pymaybe import maybe
from localpackage.person import person
from localpackage.TablesAD import TablesAD
from localpackage.utils import defaultdiscountRate, defaultOgden, Ogden, parsedateString


class game():

    def getautoYrAttained(self):
        return self.autoYrAttained

    def getAAD(self,name):
        claimant=self.getClaimant(name)
        if claimant:
            return claimant.getAAD()
        else:
            print("Non existent name for claimant in getAAI")
            return None

    def getAAT(self,name):
        claimant=self.getClaimant(name)
        if claimant:
            return claimant.getAAT()
        else:
            print("Non existent name for claimant in getAAI")
            return None


    def getAAI(self,name):
        claimant=self.getClaimant(name)
        if claimant:
            return claimant.getAAI()
        else:
            print("Non existent name for clamant in getAAI")
            return None

    def addClaimant(self,claimant):
        if not claimant.name in self.claimants:
            self.claimants[claimant.name]=claimant
        else:
            print("Name already exists")

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
        return [maybe(self.getClaimant(row['name'])).M(row['fromAge'], row['toAge'], freq=row['freq'],options=row['options']).or_else([None, None, None, None]) for row in self.rows]


    def __init__(self, attributes):


        if 'rows' in attributes:
            self.rows=attributes['rows']

        self.autoYrAttained=False
        if 'autoYrAttained' in attributes['game']:
            self.autoYrAttained=attributes['game']['autoYrAttained']

        if 'trialDate' in attributes['game']: #if trial date supplied, accept; otherwise use today's date
            if type(attributes['game']['trialDate']) is str:
                attributes['game']['trialDate']=parsedateString(game['trialDate'])
            self.trialDate=attributes['game']['trialDate']
        else:
            self.trialDate=datetime.now()

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


