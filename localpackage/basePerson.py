from datetime import datetime, timedelta
import numpy as np
from localpackage.SAR import SAR
from localpackage.utils import names

class baseperson():


    def isFatal(self):
        return self.fatal

    def getSex(self):
        return self.sex

    def setSex(self,sex):
        self.sex=sex
        self.setDirty(True)

    def getDOB(self):
        return self.dob

    def setDOB(self,dob):
        self.dob=dob
        self.age = (self.gettrialDate() - self.dob).days / 365.25
        self.setDirty(True)

    def getAge(self):
        return self.age

    def setAge(self,age):
        self.age=age
        self.dob = self.gettrialDate() - timedelta(days=(self.age * 365.25))
        self.setDirty(True)

    def getAAT(self):
        #return age at trial (will be different if this is a fatal case from age)
        return (self.gettrialDate()-self.dob).days/365.25

    def getdeltaLEB(self):
        return self.deltaLEB

    def getdeltaLEA(self):
        return self.deltaLEA

    def getdiscountRate(self):
        return self.parent.getdiscountRate()

    def getCurve(self,name):
        if name in names:
            return self.curves[name]
        return None

    def M(self, point1, point2=None, name='Uninjured', freq="Y", cont=1, options='AMI'):
        #builds a curve depending on the options and returns the multiplier
        age1=age2=None
        age1= self.getAgeFromPoint(point1)
        if point2: age2= self.getAgeFromPoint(point2)
        c=self.getCurve(name)
        result= c.M(age1,age2,freq=freq,cont=cont,options=options)
#        print(c.calc.show())
#        c.getPlot(result, age1, age2, freq, cont, options)
        return result

    def getStdLE(self): #i.e. the LE with normal life expectancy
        return np.trapz(self.getdataSet(names[0]).getLxLxd(self.age, LxOnly=True))


    def getAgeFromPoint(self, point):
        #point is either a float (i.e. age) or a datetime
        #returns age
        age=None
        if isinstance(point,np.float64) or isinstance(point,np.int64) or type(point) is float or type(point) is int:
            #i.e. age
            age=point
        elif type(point) is datetime:
            age=(point-self.dob).days/365.25
        else:
            #Error, wrong type
            print('Wrong type passed to getAgeFromPoint')
            print(type(point))
        return age

    def getdataSet(self, name):
        if name in names:
            return self.dataSets[name]
        return None

    def getTablesAD(self):
        return self.parent.getTablesAD()

    def getSAR(self):
        return self.SAR

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def setDirty(self,value=True):
        self.dirty=value
        [ds.setdirtyCalcs(value) for ds in self.dataSets.values()]  # make all the future data sets dirty
        self.getSAR().setDirty(value)  # make part data set dirty
        [c.setDirty(value) for c in self.curves.values()] #make all curves dirty

    def refresh(self):
        if self.dirty:
            [ds.refresh() for ds in self.dataSets.values()] #refresh all the future data sets
            self.getSAR().refresh() #refresh the past data set
            [c.refresh() for c in self.curves.values()] #refresh the curves
            self.dirty=False

    def __init__(self, attributes, parent, deceased=None):

        self.parent=parent #reference to game object
        self.attributes=attributes
        self.dirty=True
        self.deceased=deceased
        self.fatal=False


        if 'name' in attributes:
            self.name=attributes['name']
        else:
            self.name='person'

        if 'dob' in attributes and not 'age' in attributes:
            self.dob=attributes['dob']
            self.age=(self.gettrialDate()-self.dob).days/365.25
        if 'age' in attributes and not 'dob' in attributes:
            self.age=attributes['age']
            self.dob=self.gettrialDate() - timedelta(days=(self.age * 365.25))

        if not 'age' in attributes and not 'dob' in attributes:
            print("Missing age information for person")
        if 'age' in attributes and 'dob' in attributes:
            print("Both age and dob supplied for person")

        if 'sex' in attributes:
            self.sex=attributes['sex']
        else:
            print("Missing sex for person")

        if 'deltaLEB' in attributes:
            self.deltaLEB=attributes['deltaLEB']
        else:
            self.deltaLEB=0

        if 'deltaLEA' in attributes:
            self.deltaLEA=attributes['deltaLEA']
        else:
            self.deltaLEA=0

        self.dataSets={} #for the dataSets
        self.curves={} #for the curves (one for each dataset)
        self.SAR=SAR(parent=self)

        self.setUp()
        self.refresh()

    def setUp(self):
        #to be overridden
        pass






