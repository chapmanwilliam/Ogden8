from localpackage.basePerson import baseperson
from localpackage.dataClass import dataSet
from localpackage.curve import curve
from localpackage.utils import stati


class dependent(baseperson):


    def getDict(self):
        return {'age': self.getAge(), 'sex': self.getSex(), 'dataSet': self.getdataSet(stati[0]).getDict()}

    def MJ(self,point1, point2=None, freq="Y", cont=1, options='AMI'):
        options+='D'
        return self.M(point1=point1, point2=point2, status=stati[0], freq=freq, cont=cont, options=options)

    def getAAI(self,name):
        deceased=self.getClaimant(name)
        if deceased:
            return (deceased.getDOI()-self.getDOB()).days/365.25

    def getAAD(self,name):
        deceased=self.getClaimant(name)
        if deceased:
            if deceased.getDOD():
                return (deceased.getDOD()-self.getDOB()).days/365.25
        return None

    def setUp(self):

        if not 'name' in self.attributes:
            self.name='DEPENDENT_' + str(len(self.getDependents()))

        self.dataSets={stati[0]: dataSet(self.attributes['dataSet'], parent=self, deltaLE=self.deltaLEB)}
        self.curves={stati[0]: curve(stati[0], self)}





