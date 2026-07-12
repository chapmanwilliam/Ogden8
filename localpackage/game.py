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

    def getProjection(self):
        return self.projection

    def getAutoYrAttained(self):
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
        game = {'discountRate': self.discountRate(), 'Ogden': self.ogden, 'claimants': cs}
        return game

    def getUseMultipleRates(self):
        return self.useMultipleRates

    def getdiscountRate(self, yrs=0, discountRate=None, DRMethodOverride=None):
        if not discountRate==None: #if a discount rate is provided it overrides everything else
            return discountRate
        if not self.useMultipleRates and DRMethodOverride is None:
            if discountRate:
                return discountRate
            return self.discountRate
        else:

            if DRMethodOverride: #take the supplied DRMethod or use the game DRmethod
                DRMethod=DRMethodOverride
            else:
                DRMethod=self.DRMethod

            def getHashObject():
                hObj = {'DRmethod': DRMethod, 'rates': self.getMultipleRates(), 'yrs': str(yrs)}
                hJSONObj = json.dumps(hObj, sort_keys=True)
                return hash(hJSONObj)

            h = getHashObject()
            if h in self.discountRateOptions:
                return self.discountRateOptions[h]
            if DRMethod == "BLENDED":
                # this method blends the rates together after each switch point
                # after each switch point the discount FACTOR is multiplied by the new discount FACTOR
                # to calculate this you 1) calculate the discount FACTOR 2) convert that back to an equivalent discount rate
                if yrs == 0:  # deal with special case: return the first (short) rate,
                    # not the sentinel 1 (a 100% rate). At yrs=0 discountFactor is 1 regardless,
                    # but INTERESTHOUSE/REVERSION read this rate for a >0 deferral (see F28),
                    # so it must be a real rate.
                    rates = self.getMultipleRates()
                    return rates[0]['rate'] if rates else self.discountRate
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
            elif DRMethod == 'SWITCHED':
                # this method returns the discount rate for the number of years
                # so if yrs is short you get short discount rate; if yrs is long you get long discount rate
                for r in self.getMultipleRates():
                    if yrs <= r['switch']:
                        self.discountRateOptions[h] = r['rate']
                        return r['rate']
                # yrs beyond the final switch point: use the last (long) rate rather than
                # falling off the end and returning None (which 500s downstream). (F42)
                rates = self.getMultipleRates()
                if rates:
                    self.discountRateOptions[h] = rates[-1]['rate']
                    return rates[-1]['rate']
                return self.discountRate
            elif DRMethod == 'SINGLE':
                return self.discountRate
            elif DRMethod == 'STEPPED':
                # this looks at the longest period in the game.
                # if the longest period is long, then long rate; if short, short rate
                # effectively you use a single rate for whole game depending on that
                # PROBLEM - knowing the full game - think this has to be done client side
                return self.discountRate
            else:
                errors.add('Incorrect DRmethod; using single rate')
                return self.discountRate

    def setShortRate(self,rate):
        self.getMultipleRates()[0]['rate']=rate

    def setLongRate(self, rate):
        self.getMultipleRates()[1]['rate']=rate

    def setSingleRate(self,rate):
        self.setdiscountRate(rate)

    def setSwitch(self, switch):
        self.getMultipleRates()[0]['switch']=switch

    def getShortRate(self):
        return self.getMultipleRates()[0]['rate']

    def getLongRate(self):
        return self.getMultipleRates()[1]['rate']

    def getSingleRate(self):
        return self.discountRate

    def getSwitch(self):
        return self.getMultipleRates()[0]['switch']

    def setdiscountRate(self, rate):
        self.discountRate = rate

    def getTablesAD(self):
        return self.TablesAD

    def gettrialDate(self):
        return self.trialDate

    def settrialDate(self, trialDate):
        self.trialDate = trialDate

    def refresh(self):
        [claimant.refresh() for claimant in self.claimants.values()]  # refresh all the claimants

    def processRows(self):
        # rows is a list of rows of form
        # row={'name': 'CHRISTOPHER','fromAge':55, 'toAge':125, 'freq': 'Y', 'status': 'Injured', 'options':'AMIC'}

        # EXPLAIN: when the explain flag is set, MULTIPLIER/JMULTIPLIER/AGGINT/JAGGINT rows return
        # {result, explanation} alongside the tuple. Only active when the flag is present, so the
        # default output is unchanged. (EXPLAIN)
        if self.explain and self.function in ("MULTIPLIER", "JMULTIPLIER", "AGGINT", "JAGGINT"):
            fn = self.function
            return [maybe(self.getClaimant(row['name'])).explainDispatch(
                fn, row['fromAge'], row['toAge'], freq=row['freq'], options=row['options'],
                discountRate=row['discountRate'], DRMethodOverride=row['DRMethodOverride'],
                overrides=row['overrides'], includeTable=self.explainTable).or_else(
                {'result': [None, None, None, None], 'explanation': None}) for row in self.rows]

        if self.function == "MULTIPLIER":
            return [maybe(self.getClaimant(row['name'])).M(row['fromAge'], row['toAge'], freq=row['freq'],
                                                           options=row['options'],
                                                           discountRate=row['discountRate'],
                                                           DRMethodOverride=row['DRMethodOverride'],
                                                           overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "JMULTIPLIER":
            return [maybe(self.getClaimant(row['name'])).JM(row['fromAge'], row['toAge'], freq=row['freq'],
                                                            options=row['options'],
                                                            discountRate=row['discountRate'],
                                                            DRMethodOverride=row['DRMethodOverride'],
                                                            overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "INTERESTHOUSE":
            return [maybe(self.getClaimant(row['name'])).INTERESTHOUSE(row['fromAge'], row['toAge']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "REVERSION":
            return [maybe(self.getClaimant(row['name'])).REVERSION(row['fromAge'], row['toAge']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "REVISEDAGE":
            return [[maybe(self.getClaimant(row['name'])).getRevisedAge().or_else(None)] for row in self.rows]
        elif self.function == "DF":
            return [maybe(self.getClaimant(row['name'])).M(row['fromAge'],
                                                           options='A',
                                                           discountRate=row['discountRate'],
                                                           DRMethodOverride=row['DRMethodOverride'],
                                                           overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "TC":
            return [maybe(self.getClaimant(row['name'])).M(row['fromAge'], row['toAge'], freq=row['freq'],
                                                           options='AI',
                                                           discountRate=row['discountRate'],
                                                           DRMethodOverride=row['DRMethodOverride'],
                                                           overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "EAD":
            return [[maybe(self.getClaimant(row['name'])).getEAD().or_else(None)] for row in self.rows]
        elif self.function == "EDD":
            # Return a plain d/m/y string; do NOT json.dumps here (main.py serialises once more,
            # so the old inner json.dumps double-encoded the value). (F61)
            return [[maybe(self.getClaimant(row['name'])).getEDD().strftime('%d/%m/%Y').or_else(None)]
                    for row in self.rows]
        elif self.function == "TABLE_E":
            return [[maybe(self.getClaimant(row['name'])).getTableE().or_else(None)] for row in self.rows]
        elif self.function == "TABLE_F":
            return [[maybe(self.getClaimant(row['name'])).getTableF().or_else(None)] for row in self.rows]
        elif self.function == "LE":
            return [maybe(self.getClaimant(row['name'])).LE().or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "LM":
            return [maybe(self.getClaimant(row['name'])).LM(row['discountRate'],
                                                            DRMethodOverride=row['DRMethodOverride'],
                                                            overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "PM":
            return [maybe(self.getClaimant(row['name'])).PM(row['discountRate'],
                                                            DRMethodOverride=row['DRMethodOverride'],
                                                            overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "EM":
            return [maybe(self.getClaimant(row['name'])).EM(row['discountRate'],
                                                            DRMethodOverride=row['DRMethodOverride'],
                                                            overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "AEM":
            return [maybe(self.getClaimant(row['name'])).AEM(row['discountRate'],
                                                             DRMethodOverride=row['DRMethodOverride'],
                                                             overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "JLE":
            return [maybe(self.getClaimant(row['name'])).JLE().or_else(
                [None, None, None, None]) for row in self.rows]
        elif self.function == "JLM":
            return [maybe(self.getClaimant(row['name'])).JLM(row['discountRate'],
                                                             DRMethodOverride=row['DRMethodOverride'],
                                                             overrides=row['overrides']).or_else(
                [None, None, None, None]) for row in self.rows]
        else:
            # Unrecognised function: log it and return per-row nulls instead of a bare None
            # (which made the endpoint respond 200 with body 'null' and no diagnostic). (F56/F62)
            errors.add("Unknown function: " + str(self.function))
            return [[None, None, None, None] for row in self.rows]

    def processRowsInterestHouse(self):
        # Endpoint wrapper for /InterestHouse/ (main.py) — previously undefined, so the route
        # 500'd on every call. Mirrors the INTERESTHOUSE branch of processRows. (F24/F25)
        return [maybe(self.getClaimant(row['name'])).INTERESTHOUSE(row['fromAge'], row['toAge']).or_else(
            [None, None, None, None]) for row in self.rows]

    def processRowsReversion(self):
        # Endpoint wrapper for /Reversion/ (main.py) — previously undefined. (F24/F25)
        return [maybe(self.getClaimant(row['name'])).REVERSION(row['fromAge'], row['toAge']).or_else(
            [None, None, None, None]) for row in self.rows]

    def getMultipleRates(self):
        return self.multipleRates

    def getUseMultipleRates(self):
        return self.useMultipleRates

    def setUseMultipleRates(self,useMultipleRates):
        self.useMultipleRates=useMultipleRates

    def getDRMethod(self):
        return self.DRMethod

    def setDRMethod(self,drmethod):
        self.DRMethod=drmethod

    def getOriginalValues(self):
        return self.originalValues

    def validateMultipleRates(self):
        # check rates within bounds and switch is monotonically increasing
        rates = self.getMultipleRates()
        # getShortRate/getLongRate/getSwitch index [0] and [1], so at least 2 entries are
        # required; fewer (or empty) would IndexError building originalValues (F41).
        if len(rates) < 2:
            errors.add("Fewer than two multiple rates supplied")
            return False
        last_switch = 0
        for r in rates:
            if not ('rate' in r and 'switch' in r):
                errors.add("Multiple-rate entry missing 'rate'/'switch'")
                return False
            if not isinstance(r['rate'], (int, float)) or not isinstance(r['switch'], (int, float)):
                errors.add("Multiple-rate 'rate'/'switch' not numeric")
                return False
            if not r['switch'] > last_switch:
                errors.add("Not monotonically increasing")  # F39/F46: was errors.append (no such method)
                return False
            if r['rate'] > 0.3 or r['rate'] < -0.3:
                errors.add("Rate out of bounds")
                return False
            last_switch = r['switch']
        return True

    def process(self):
        # returns row results and summary statistics
        return {'rows': self.processRows(), 'summary': self.getSummaryStatsClaimants(), 'errorLog': errors.getLog()}

    def __init__(self, attributes):
        # The errors log is a process-wide singleton (errorLogging.errors); on a warm Cloud
        # Function instance it would otherwise leak this request's errors into later responses
        # and grow unbounded. Reset it at the start of every game/request. (F43/F44/F45)
        errors.clear()

        self.discountRateOptions = {}  # dictionary to store hashes of results

        self.function = "MULTIPLIER"  # default
        if 'function' in attributes:
            self.function = attributes['function']

        # EXPLAIN feature flags (additive; when both absent, output is byte-identical to before).
        self.explain = bool(attributes.get('explain', False))
        self.explainTable = bool(attributes.get('explainTable', False))

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

        self.TablesAD = TablesAD(self.ogden)

        self.claimants = {}  # dictionary for storing the claimants by name
        self.multipleRates = []  # list for storing multiple discount rates

        if 'claimants' in attributes['game']:
            [self.addClaimant(person(cs, parent=self)) for cs in attributes['game']['claimants']]
        else:
            print('No claimants added')
            errors.add("No claimants added")

        if 'useMultipleRates' in attributes['game']:
            self.setUseMultipleRates(attributes['game']['useMultipleRates'])
        else:
            self.setUseMultipleRates(False)

        if 'DRMethod' in attributes['game']:
            if attributes['game']['DRMethod'] in DRMethods:
                self.setDRMethod(attributes['game']['DRMethod'])
            else:
                self.setDRMethod('BLENDED')
        else:
            self.setDRMethod('BLENDED')

        #Add default rates
        r1 = {'rate': -0.015, 'switch': 15}
        r2 = {'rate': +0.015, 'switch': 125}
        self.multipleRates.append(r1)
        self.multipleRates.append(r2)

        if 'multipleRates' in attributes['game']:
            self.multipleRates.clear()
            [self.multipleRates.append(r) for r in attributes['game']['multipleRates']]
            if not self.validateMultipleRates():
                # Copy the module-level default list of dicts; assigning it directly would let a
                # later setShortRate()/setSwitch() mutate the shared default for every subsequent
                # request on a warm instance. (F39/F46)
                self.multipleRates = [dict(r) for r in defaultMultipleRates]
                print('Invalid multiple rates supplied; default used.')
                errors.add('Invalid multiple rates supplied; default used.')

        self.originalValues = {'USEMULTIPLERATES':self.getUseMultipleRates(),
                               'DRMETHOD': self.getDRMethod(),
                               'SHORTRATE':self.getShortRate(),
                               'LONGRATE': self.getLongRate(),
                               'SINGLERATE': self.getSingleRate(),
                               'SWITCH':self.getSwitch()}

