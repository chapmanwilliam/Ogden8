from datetime import timedelta
from localpackage.basePerson import baseperson
from localpackage.utils import parsedateString

class person(baseperson):



    def getDict(self):
        return {'age': self.getAge(), 'aai': self.getAAI(), 'sex': self.getSex(), 'dataSet': self.getdataSet().getDict(), 'deltaLE': self.getdeltaLE()}

    def getDOI(self):
        return self.doi

    def getDOD(self):
        return self.dod

    def getAAD(self):
        if self.getDOD():
            return (self.getDOD() - self.getDOB()).days / 365.25
        return None

    def setUp(self):

        self.aad=None #age at death, if fatal
        self.dod=None #date of death, if fatal

        self.aai=None #age at injury
        self.doi=None #date of injury

        if 'dod' in self.attributes and not 'aad' in self.attributes:
            if type(self.attributes['dod']) is str:
                self.attributes['dod']=parsedateString(self.attributes['dod'])
            self.dod=self.attributes['dod']
            self.aad=(self.dod-self.dob).days/365.25
            self.fatal = True
        if 'aad' in self.attributes and not 'dod' in self.attributes:
            if type(self.attributes['aad']) is int or type(self.attributes['aad']) is float:
                self.aad=self.attributes['aad']
                self.dod=self.dob + timedelta(days=(self.aad * 365.25))
                self.fatal=True

        if 'doi' in self.attributes and not 'aai' in self.attributes:
            self.doi=self.attributes['doi']
            self.aai=(self.doi-self.dob).days/365.25
        if 'aai' in self.attributes and not 'doi' in self.attributes:
            self.aai=self.attributes['aai']
            self.doi=self.dob + timedelta(days=(self.aai * 365.25))

        if not 'doi' in self.attributes and not 'aai' in self.attributes:
            pass
            #print("No date of injury submitted for person")

        if not 'name' in self.attributes:
            self.name='CLAIMANT_' + str(len(self.getClaimants()))







