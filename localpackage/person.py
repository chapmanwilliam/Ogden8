from datetime import timedelta
from localpackage.dataClass import dataSet
from localpackage.basePerson import baseperson
from localpackage.curve import curve
from localpackage.utils import stati

class person(baseperson):

    def getDict(self):
        return {'age': self.getAge(), 'aai': self.getAAI(), 'sex': self.getSex(), 'dataSet': self.getdataSet(stati[0]).getDict(), 'deltaLEB': self.getdeltaLEB(), 'deltaLEA': self.getdeltaLEA()}

    def LEB(self):
        return self.M(self.age,125, status=stati[0], options='MI')

    def LEA(self):
        return self.M(self.age,125, status=stati[1], options='MI')

    def LMB(self):
        return self.M(self.age,125, status=stati[0], options='AMI')

    def LMA(self):
        return self.M(self.age,125, status=stati[1], options='AMI')


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
            print("No date of injury submitted for person")

        if not 'name' in self.attributes:
            self.name='CLAIMANT_' + str(len(self.getClaimants()))

        self.dataSets={stati[0]: dataSet(self.attributes['dataSet'], self, self.deltaLEB), stati[1]: dataSet(self.attributes['dataSet'], self, self.deltaLEA)}
        self.curves={stati[0]: curve(stati[0], self), stati[1]: curve(stati[1], self)}





