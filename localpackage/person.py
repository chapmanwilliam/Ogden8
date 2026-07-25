from datetime import timedelta
from localpackage.basePerson import baseperson
from localpackage.utils import parsedateString
from localpackage.errorLogging import errors


class person(baseperson):

    def getTableE(self):
        # This is average chance of death from date of death until trial
        # Take the multiplier to trial and divide by number of years
        if not self.isFatal(): return 1
        AAD = self.getAAD()
        AAT = self.getAAT()
        if AAD >= AAT: return 1
        return self.M(AAD, AAT, options='M')[3] / (AAT - AAD)

    def getTableF(self):
        # This is chance of death at trial
        # Take the multiplier to trial
        AAT = self.getAAT()
        return self.M(AAT, options='M')[3]

    def getDict(self):
        return {'age': self.getAge(), 'aai': self.getAAI(), 'sex': self.getSex(),
                'dataSet': self.getdataSet().getDict(), 'deltaLE': self.getdeltaLE()}

    def getDOD(self):
        # return date of death of deceased person
        return self.dod

    def getAAD(self):
        # return age at death of deceased person
        if self.getDOD():
            return (self.getDOD() - self.getDOB()).days / 365.25
        return None

    def getEDD(self):
        # return expected date of death
        EAD = self.getEAD()
        dob = self.getDOB()
        return dob + timedelta(days=(EAD * 365.25))

    def getEAD(self):
        # return expected age at death
        #
        # For a fatal claimant this is the age they would have been expected to reach had
        # they survived the date of actual death: age at death plus the life expectancy at
        # that date. Built from that pair directly.
        #
        # Deriving it from the trial age instead (AAT + LE) takes a SECOND mortality lookup
        # at a different age, and the cohort follows from year-attained minus age, so the two
        # lookups imply different birth years and describe slightly different people - worth
        # about 0.02 of a year on the reference case, and avoidable.
        if self.isFatal():
            return self.getAAD() + self.LEDOD()[3]
        return self.getAAT() + self.LE()[3]

    def setUp(self):

        self.aad = None  # age at death, if fatal
        self.dod = None  # date of death, if fatal

        self.aai = None  # age at injury
        self.doi = None  # date of injury

        # Fatal inputs. Guard the both-supplied case and coerce a string aad (Sheets often
        # serialises numbers as strings); previously either case left the claimant silently
        # non-fatal with no error, so fatal-specific results ran on the wrong (living) basis. (F47)
        hasDod = 'dod' in self.attributes and self.attributes['dod'] not in (None, '')
        hasAad = 'aad' in self.attributes and self.attributes['aad'] not in (None, '')
        if hasDod and hasAad:
            errors.add("Both aad and dod supplied for claimant; using dod")
            hasAad = False
        if hasDod:
            if type(self.attributes['dod']) is str:
                self.attributes['dod'] = parsedateString(self.attributes['dod'])
            self.dod = self.attributes['dod']
            if self.dod is not None:
                self.aad = (self.dod - self.dob).days / 365.25
                self.fatal = True
        elif hasAad:
            try:
                self.aad = float(self.attributes['aad'])
                self.dod = self.dob + timedelta(days=(self.aad * 365.25))
                self.fatal = True
            except (ValueError, TypeError):
                errors.add("Invalid aad (age at death): " + str(self.attributes['aad']))

        if 'fatal' in self.attributes:
            self.fatal = self.attributes['fatal']

        if 'name' not in self.attributes:
            self.name = 'CLAIMANT_' + str(len(self.getClaimants()))
