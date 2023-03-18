from datetime import datetime
import json
from pymaybe import maybe
from localpackage.person import person
from localpackage.TablesAD import TablesAD
from localpackage.utils import defaultdiscountRate, defaultOgden, Ogden, parsedateString, DRMethods, \
    defaultMultipleRates
from localpackage.errorLogging import errors


class game():

    def getUseTablesEF(self):
        return self.useTablesEF

    def getSummaryStatsClaimants(self):
        # returns summary statistics for each Claimant
        claimantStats = {}
        for claimant in self.claimants:
            claimantStats[claimant] = self.getClaimant(claimant).getSummaryStats()
        return claimantStats

    def getprojection(self):
        return self.projection

    def getautoYrAttained(self):
        return self.autoYrAttained

    def getAAD(self, name):
        claimant = self.getClaimant(name)
        if claimant:
            return claimant.getAAD()
        else:
            print("Non existent name for claimant in getAAI")
            errors.add("Non existent name for claimant in getAAI")
            return None

    def getAAT(self, name):
        claimant = self.getClaimant(name)
        if claimant:
            return claimant.getAAT()
        else:
            print("Non existent name for claimant in getAAI")
            errors.add("Non existent name for claimant in getAAI")
            return None

    def getDOI(self):
        if hasattr(self, 'doi'):
            return self.doi
        else:
            return None

    def getAAI(self, name):
        claimant = self.getClaimant(name)
        if claimant:
            return claimant.getAAI()
        else:
            print("Non existent name for claimant in getAAI")
            errors.add("Non existent name for claimant in getAAI")
            return None

    def addClaimant(self, claimant):
        if not claimant.name in self.claimants:
            self.claimants[claimant.name] = claimant
        else:
            print("Name already exists")
            errors.add("Name already exists")

    def getClaimant(self, name):
        if name in self.claimants:
            return self.claimants[name]
        else:
            return None

    def getClaimants(self):
        return self.claimants

    def getDict(self):
        # encodes the game, claimants, dependents
        cs = [claimant.getDict() for claimant in self.claimants]
        game = {'discountRate': self.getdiscountRate(), 'Ogden': self.ogden, 'claimants': cs}
        return game

    def getUseMultipleRates(self):
        return self.useMultipleRates

    def getdiscountRate(self, yrs=0):
        if not self.useMultipleRates:
            return self.discountRate
        else:
            def getHashObject():
                hObj = {'DRmethod': self.DRMethod, 'rates': self.getMultipleRates(), 'yrs': str(yrs)}
                hJSONObj = json.dumps(hObj, sort_keys=True)
                return hash(hJSONObj)

            h = getHashObject()
            if h in self.discountRateOptions:
                return self.discountRateOptions[h]
            if self.DRMethod == "BLENDED":
                # this method blends the rates together after each switch point
                # after each switch point the discount FACTOR is multiplied by the new discount FACTOR
                # to calculate this you 1) calculate the discount FACTOR 2) convert that back to an equivalent discount rate
                if yrs == 0:  # deal with special case
                    return 1
                cumDF = 1
                last_switch = 0
                for r in self.getMultipleRates():
                    if yrs > r['switch']:  # then we'll take all of it
                        # how many yrs at this rate?
                        yrs_at_this_rate = r['switch'] - last_switch
                        DF = (1 / (1 + r['rate'])) ** yrs_at_this_rate
                        cumDF *= DF
                        last_switch = r['switch']
                    else:
                        yrs_at_this_rate = yrs - last_switch
                        DF = (1 / (1 + r['rate'])) ** yrs_at_this_rate
                        cumDF *= DF
                        break
                # now convert back to equivalent discount rate
                if cumDF > 0:
                    DR = ((1 / cumDF) ** (1 / yrs)) - 1
                else:
                    DR = 0
                self.discountRateOptions[h] = DR
                return DR
            elif self.DRMethod == 'SWITCHED':
                # this method returns the discount rate for the number of years
                # so if yrs is short you get short discount rate; if yrs is long you get long discount rate
                for r in self.getMultipleRates():
                    if yrs <= r['switch']:
                        self.discountRateOptions[h] = r['rate']
                        return r['rate']
            elif self.DRMethod == 'STEPPED':
                # this looks at the longest period in the game.
                # if the longest period is long, then long rate; if short, short rate
                # effectively you use a single rate for whole game depending on that
                # PROBLEM - knowing the full game - think this has to be done client side
                return self.discountRate
            else:
                errors.append('Incorrect DRmethod; using single rate')
                return self.discountRate

    def setdiscountRate(self, rate):
        self.discountRate = rate
        self.setDirty(True)  # TODO: actually we only need to make dirty the data set

    def getTablesAD(self):
        return self.TablesAD

    def gettrialDate(self):
        return self.trialDate

    def setDirty(self, value=True):
        [claimant.setDirty(True) for claimant in self.claimants]  # make all claimants dirty
        self.dirty = True

    def settrialDate(self, trialDate):
        self.trialDate = trialDate
        self.setDirty(True)

    def refresh(self):
        [claimant.refresh() for claimant in self.claimants.values()]  # refresh all the claimants
        self.dirty = False

    def processRows(self):
        # rows is a list of rows of form
        # row={'name': 'CHRISTOPHER','fromAge':55, 'toAge':125, 'freq': 'Y', 'status': 'Injured', 'options':'AMIC'}
        if self.function == "MULTIPLIER":
            return [maybe(self.getClaimant(row['name'])).M(row['fromAge'], row['toAge'], freq=row['freq'],
                                                           options=row['options'],
                                                           discountRate=row['discountRate']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "JMULTIPLIER":
            return [maybe(self.getClaimant(row['name'])).JM(row['fromAge'], row['toAge'], freq=row['freq'],
                                                            options=row['options'],
                                                            discountRate=row['discountRate']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "INTERESTHOUSE":
            return [maybe(self.getClaimant(row['name'])).INTERESTHOUSE(row['fromAge'], row['toAge']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "REVERSION":
            return [maybe(self.getClaimant(row['name'])).REVERSION(row['fromAge'], row['toAge']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "REVISEDAGE":
            return [maybe([self.getClaimant(row['name']).getrevisedAge()]).or_else(
                [None]) for row in self.rows]
        elif self.function == "DF":
            return [maybe(self.getClaimant(row['name'])).M(row['fromAge'],
                                                           options='A',
                                                           discountRate=row['discountRate']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "TC":
            return [maybe(self.getClaimant(row['name'])).M(row['fromAge'], row['toAge'], freq=row['freq'],
                                                           options='AI',
                                                           discountRate=row['discountRate']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "EAD":
            return [maybe([self.getClaimant(row['name']).getEAD()]).or_else(
                [None]) for row in self.rows]
        elif self.function == "EDD":
            return [maybe([json.dumps(self.getClaimant(row['name']).getEDD().isoformat())]).or_else(
                [None]) for row in self.rows]
        elif self.function == "TABLE_E":
            return [maybe([self.getClaimant(row['name']).getTableE()]).or_else(
                [None]) for row in self.rows]
        elif self.function == "TABLE_F":
            return [maybe([self.getClaimant(row['name']).getTableF()]).or_else(
                [None]) for row in self.rows]
        elif self.function == "LE":
            return [maybe(self.getClaimant(row['name']).LE()).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "LM":
            return [maybe(self.getClaimant(row['name']).LM(row['discountRate'])).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "PM":
            return [maybe(self.getClaimant(row['name']).PM(row['discountRate'])).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "EM":
            return [maybe(self.getClaimant(row['name']).EM(row['discountRate'])).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "AEM":
            return [maybe(self.getClaimant(row['name']).AEM(row['discountRate'])).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "JLE":
            return [maybe(self.getClaimant(row['name']).JLE()).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "JLM":
            return [maybe(self.getClaimant(row['name']).JLM(row['discountRate'])).or_else(
                [None, None, None, None]) for row in self.rows]

    def getMultipleRates(self):
        return self.multipleRates

    def validateMultipleRates(self):
        # check rates within bounds and switch is monotonically increasing
        last_switch = 0
        for r in self.getMultipleRates():
            if not r['switch'] > last_switch:
                errors.append("Not monotonically increasing")
                return False
            if r['rate'] > 0.3 or r['rate'] < -0.3:
                errors.append("Rate out of bounds")
                return False
            last_switch = r['switch']
        return True

    def process(self):
        # returns row results and summary statistics
        return {'rows': self.processRows(), 'summary': self.getSummaryStatsClaimants(), 'errorLog': errors.getLog()}

    def __init__(self, attributes):
        self.discountRateOptions = {}  # dictionary to store hashes of results

        self.function = "MULTIPLIER"  # default
        if 'function' in attributes:
            self.function = attributes['function']

        if 'rows' in attributes:
            self.rows = attributes['rows']

        self.autoYrAttained = False
        if 'autoYrAttained' in attributes['game']:
            self.autoYrAttained = attributes['game']['autoYrAttained']

        self.projection = True
        if 'projection' in attributes['game']:
            self.projection = attributes['game']['projection']

        self.useTablesEF = False
        if 'useTablesEF' in attributes['game']:
            self.useTablesEF = attributes['game']['useTablesEF']

        if 'trialDate' in attributes['game']:  # if trial date supplied, accept; otherwise use today's date
            if type(attributes['game']['trialDate']) is str:
                attributes['game']['trialDate'] = parsedateString(attributes['game']['trialDate'])
            self.trialDate = attributes['game']['trialDate']
        else:
            self.trialDate = datetime.now()

        if 'DOI' in attributes['game']:  # if trial date supplied, accept; otherwise use today's date
            if type(attributes['game']['DOI']) is str:
                attributes['game']['DOI'] = parsedateString(attributes['game']['DOI'])
            self.doi = attributes['game']['DOI']

        if 'discountRate' in attributes['game']:  # if discountrate supplied, accept; otherwise use default
            self.discountRate = attributes['game']['discountRate']
        else:
            self.discountRate = defaultdiscountRate

        if 'Ogden' in attributes['game']:  # if correct Ogden supplied, accept; otherwise use default
            if attributes['game']['Ogden'] in Ogden:
                self.ogden = attributes['game']['Ogden']
            else:
                self.ogden = defaultOgden
        else:
            self.ogden = defaultOgden

        self.dirty = True
        self.TablesAD = TablesAD(self.ogden)

        self.claimants = {}  # dictionary for storing the claimants by name
        self.multipleRates = []  # list for storing multiple discount rates

        if 'claimants' in attributes['game']:
            [self.addClaimant(person(cs, parent=self)) for cs in attributes['game']['claimants']]
        else:
            print('No claimants added')
            errors.add("No claimants added")

        if 'useMultipleRates' in attributes['game']:
            self.useMultipleRates = attributes['game']['useMultipleRates']
        else:
            self.useMultipleRates = False

        if 'DRMethod' in attributes['game']:
            if attributes['game']['DRMethod'] in DRMethods:
                self.DRMethod = attributes['game']['DRMethod']
            else:
                self.DRMethod = 'BLENDED'
        else:
            self.DRMethod = 'BLENDED'

        if 'multipleRates' in attributes['game']:
            [self.multipleRates.append(r) for r in attributes['game']['multipleRates']]
            if not self.validateMultipleRates():
                self.multipleRates = defaultMultipleRates
                print('Invalid multiple rates supplied; default used.')
                errors.add('Invalid multiple rates supplied; default used.')
        else:
            print('No multiple rates added')
            errors.add('no multiple rates added')
