from datetime import datetime
from pymaybe import maybe
from localpackage.person import person
from localpackage.dependent import dependent
from localpackage.TablesAD import TablesAD
from localpackage.utils import defaultdiscountRate, defaultOgden, Ogden, parsedateString


class game():

    def addDependent(self,dependent):
        self.dependents[dependent.name]=dependent
#        self.dependents.append(dependent)

    def addClaimant(self,claimant):
        self.claimants[claimant.name]=claimant
#        self.claimants.append(claimant)

    def getClaimant(self,name):
        if name in self.claimants:
            return self.claimants[name]
        else:
            return None

    def getClaimants(self):
        return self.claimants

    def getDependents(self):
        return self.dependents

    def getDict(self):
        #encodes the game, claimants, dependents
        cs=[claimant.getDict() for claimant in self.claimants]
        ds = [dependent.getDict() for dependent in self.dependents]
        game={'discountRate':self.getdiscountRate(), 'Ogden':self.ogden, 'claimants': cs, 'dependents':ds}
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
        [dependent.setDirty(True) for dependent in self.dependents]  #make all dependents dirty
        self.dirty=True


    def settrialDate(self,trialDate):
        self.trialDate=trialDate
        self.setDirty(True)

    def refresh(self):
        [claimant.refresh() for claimant in self.claimants.values()] #refresh all the claimants
        [dependent.refresh(True) for dependent in self.dependents.values()]  # make all dependents dirty
        self.dirty=False

    def __init__(self, attributes):

        game=attributes['game']

        if 'trialDate' in game: #if trial date supplied, accept; otherwise use today's date
            if type(game['trialDate']) is str:
                game['trialDate']=parsedateString(game['trialDate'])
            self.trialDate=game['trialDate']
        else:
            self.trialDate=datetime.now()

        if 'discountRate' in game: #if discountrate supplied, accept; otherwise use default
            self.discountRate=game['discountRate']
        else:
            self.discountRate=defaultdiscountRate

        if 'Ogden' in game: #if correct Ogden supplied, accept; otherwise use default
            if game['Ogden'] in Ogden:
                self.ogden=game['Ogden']
            else:
                self.ogden=defaultOgden
        else:
            self.ogden=defaultOgden

        self.dirty=True
        self.TablesAD=TablesAD(self.ogden)

        self.claimants={} #dictionary for storing the claimants by name
        self.dependents={} #dictionary for storing the dependents by name

        if 'claimants' in game:
            [self.addClaimant(person(cs,parent=self)) for cs in game['claimants']]
        if 'dependents' in game:
            [self.addDependent(dependent(ds,parent=self)) for ds in game['dependents']]


