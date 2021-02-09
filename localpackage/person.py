from datetime import timedelta
from localpackage.dataClass import dataSet
from localpackage.basePerson import baseperson
from localpackage.curve import curve
from localpackage.utils import stati, InjuredContDetailsdefault, UninjuredContDetailsdefault

class person(baseperson):

    def getDict(self):
        return {'age': self.getAge(), 'aai': self.getAAI(), 'sex': self.getSex(), 'dataSet': self.getdataSet(stati[0]).getDict(), 'deltaLEB': self.getdeltaLEB(), 'deltaLEA': self.getdeltaLEA()}


    def MB(self,point1, point2=None, freq="Y", cont=1, options='AMI'):
        return self.M(point1=point1, point2=point2, status=stati[0], freq=freq, cont=cont, options=options)

    def MA(self,point1, point2=None, freq="Y", cont=1, options='AMI'):
        return self.M(point1=point1, point2=point2, status=stati[1], freq=freq, cont=cont, options=options)

    def MBJ(self,point1, point2=None, freq="Y", cont=1, options='AMI'):
        options+='D'
        return self.M(point1=point1, point2=point2, status=stati[0], freq=freq, cont=cont, options=options)

    def MAJ(self,point1, point2=None, freq="Y", cont=1, options='AMI'):
        options+='D'
        return self.M(point1=point1, point2=point2, status=stati[1], freq=freq, cont=cont, options=options)

    def LEB(self):
        return self.MB(self.age,125)

    def LEA(self):
        return self.MA(self.age,125)

    def getCont(self,stat):
        if not stat in stati:
            print('Wrong name supplied in getCont.')
            return None
        if self.contAutomatic[stat]:
            if stat in self.contDetails:
                Tables = self.getTablesAD()
                cont = Tables.getCont(sex=self.sex, employed=self.contDetails[stat]['employed'],
                                      qualification=self.contDetails[stat]['qualification'],
                                      disabled=self.contDetails[stat]['disabled'], age=self.age)
                return cont
            else:
                print('No details supplied for getCont')
                return None
        else:
            if stat in self.cont:
                return self.cont[stat]
            else:
                print('No override supplied for getCont')
                return None

    def getDOI(self):
        return self.doi

    def getDOD(self):
        return self.dod

    def getAAI(self):
        if self.getDOI():
            return (self.getDOI() - self.getDOB()).days / 365.25
        return None

    def getAAD(self):
        if self.getDOD():
            return (self.getDOD() - self.getDOB()).days / 365.25
        return None

    def setUp(self):

        self.aad=None #age at death, if fatal
        self.dod=None #date of death, if fatal

        self.aai=None #age at injury
        self.doi=None #date of injury

        self.contAutomatic={stati[0]:True, stati[1]:True} #automatic by default
        if 'contAutomaticUninjured' in self.attributes: self.contAutomatic[stati[0]]=self.attributes['contAutomaticUninjured']
        if 'contAutomaticInjured' in self.attributes: self.contAutomatic[stati[1]]=self.attributes['contAutomaticInjured']

        self.cont={}
        if 'contUninjured' in self.attributes:self.cont[stati[0]]=self.attributes['contUninjured']
        if 'contInjured' in self.attributes:self.cont[stati[1]]=self.attributes['contInjured']

        self.contDetails={stati[0]:UninjuredContDetailsdefault, stati[1]:InjuredContDetailsdefault}
        if 'contDetailsUninjured' in self.attributes: self.contDetails[stati[0]]=self.attributes['contDetailsUninjured'] #should be {'employed',qualification,'disabled'}
        if 'contDetailsInjured' in self.attributes: self.contDetails[stati[1]]=self.attributes['contDetailsInjured'] #should be {'employed',qualification,'disabled'}

        if 'dod' in self.attributes and not 'aad' in self.attributes:
            self.dod=self.attributes['dod']
            self.aad=(self.dod-self.dob).days/365.25
            self.fatal = True
        if 'aad' in self.attributes and not 'dod' in self.attributes:
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





