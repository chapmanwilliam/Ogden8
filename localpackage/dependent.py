from basePerson import baseperson
from dataClass import dataSet
from curve import curve
from utils import names


class dependent(baseperson):

    def getDict(self):
        return {'age': self.getAge(), 'sex': self.getSex(), 'dataSet': self.getdataSet(names[0]).getDict()}

    def MJ(self,point1, point2=None, freq="Y", cont=1, discAcceleratedReceipt=True, discMortality=True, interest=True):
        return self.M(point1=point1, point2=point2, name=names[0], freq=freq, cont=cont, discAcceleratedReceipt=discAcceleratedReceipt, discMortality=discMortality, interest=interest, useDeceased=True)

    def getAAI(self):
        return (self.deceased.getDOI()-self.getDOB()).days/365.25

    def getAAD(self):
        if self.deceased.getDOD():
            return (self.deceased.getDOD()-self.getDOB()).days/365.25
        return None

    def setUp(self):

        self.dataSets={names[0]: dataSet(self.attributes['dataSet'],parent=self,deltaLE=self.deltaLEB)}
        self.curves={names[0]: curve(names[0],self)}



