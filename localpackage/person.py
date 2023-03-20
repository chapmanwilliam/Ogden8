from datetime import timedelta
from localpackage.basePerson import baseperson
from localpackage.utils import parsedateString


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
        return self.getAAT() + self.LE()[3]

        if self.getAAD():
            return self.getAAD()
        else:
            return self.getAAT() + self.LE()[3]

    def setUp(self):

        self.aad = None  # age at death, if fatal
        self.dod = None  # date of death, if fatal

        self.aai = None  # age at injury
        self.doi = None  # date of injury

        # Fatal inputs
        if 'dod' in self.attributes and not 'aad' in self.attributes:
            if type(self.attributes['dod']) is str:
                self.attributes['dod'] = parsedateString(self.attributes['dod'])
            self.dod = self.attributes['dod']
            self.aad = (self.dod - self.dob).days / 365.25
            self.fatal = True

        if 'aad' in self.attributes and not 'dod' in self.attributes:
            if type(self.attributes['aad']) is int or type(self.attributes['aad']) is float:
                self.aad = self.attributes['aad']
                self.dod = self.dob + timedelta(days=(self.aad * 365.25))
                self.fatal = True

        if 'fatal' in self.attributes:
            self.fatal = self.attributes['fatal']

        if 'name' not in self.attributes:
            self.name = 'CLAIMANT_' + str(len(self.getClaimants()))
