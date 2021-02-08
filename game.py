from datetime import datetime
from person import person
from dependent import dependent
from TablesAD import TablesAD
from utils import parsedateString, defaultdiscountRate, defaultOgden, Ogden, InjuredContDetailsdefault, UninjuredContDetailsdefault, Ogden7, Ogden8


class game():

    def addDependent(self,dependent):
        self.dependents.append(dependent)

    def addClaimant(self,claimant):
        self.claimants.append(claimant)

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
        [claimant.refresh() for claimant in self.claimants] #refresh all the claimants
        [dependent.refresh(True) for dependent in self.dependents]  # make all dependents dirty
        self.dirty=False

    def __init__(self, attributes):

        if 'trialDate' in attributes: #if trial date supplied, accept; otherwise use today's date
            self.trialDate=attributes['trialDate']
        else:
            self.trialDate=datetime.now()

        if 'discountRate' in attributes: #if discountrate supplied, accept; otherwise use default
            self.discountRate=attributes['discountRate']
        else:
            self.discountRate=defaultdiscountRate

        if 'Ogden' in attributes: #if correct Ogden supplied, accept; otherwise use default
            if attributes['Ogden'] in Ogden:
                self.ogden=attributes['Ogden']
            else:
                self.ogden=defaultOgden
        else:
            self.ogden=defaultOgden

        self.dirty=True
        self.TablesAD=TablesAD(self.ogden)

        self.claimants=[] #for storing the claimants
        self.dependents=[] #for storing the dependents

        if 'claimants' in attributes:
            [self.addClaimant(person(cs,parent=self)) for cs in attributes['claimants']]
        if 'dependents' in attributes:
            [self.addDependent(dependent(ds,parent=self)) for ds in attributes['dependents']]


