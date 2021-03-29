from datetime import datetime, timedelta
import numpy as np
import re
import requests
from localpackage.dataSet import dataSet
from localpackage.curve import curve
from localpackage.SAR import SAR
from localpackage.utils import wordPoints, plusMinus, returnFreq, ContDetailsdefault, is_date, parsedate,parsedateString

class baseperson():

    def getSummaryStats(self):
        return {
            'LE': self.LE(),
            'LM': self.LM(),
            'JLE': self.JLE(),
            'JLM':self.JLM(),
            'AutoCont':self.getAutoCont(),
            'StateRetirementAge':self.getStateRetirementAge()
        }

    def getprojection(self):
        return self.parent.getprojection()

    def getautoYrAttained(self):
        return self.parent.getautoYrAttained()

    def getName(self):
        return self.name

    def LE(self):
        return self.M(self.age,125, options='MI')

    def LM(self):
        return self.M(self.age,125, options='AMI')

    def JLE(self):
        return self.M(self.age,125, options='MID')

    def JLM(self):
        return self.M(self.age,125, options='AMID')

    def getStateRetirementAge(self):
        #returns state retirement age from government web-site
        dob=self.getDOB()
        yr=str(dob.year)
        mo=str(dob.month).zfill(2)
        dy=str(dob.day).zfill(2)
        urlsuffix=yr+"-"+mo+"-"+dy
        url='https://www.gov.uk/state-pension-age/y/age/'
        response=requests.get(url+urlsuffix)
        if response:
            y=re.search('Your State Pension age is (\d+) years',response.text)
            if y:
                return int(y[1])
            else:
                return None
        else:
            return None



    def getClaimantsDependentOn(self):
        #returns list of names claimant is dependent on
        listofnames=[]
        if self.dependenton:
            listofnames = self.dependenton.split(',')  # turn comma delimited string into array of names
            listofnames=[n.strip() for n in listofnames] #removes leading and trailing space
        return listofnames

    def getClaimants(self):
        return self.parent.getClaimants()

    def getClaimant(self,name):
        return self.parent.getClaimant(name)

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

    def getAAI(self):
        if self.getDOI():
            return (self.getDOI() - self.getDOB()).days / 365.25
        return None

    def getdeltaLE(self):
        return self.deltaLE

    def getdiscountRate(self):
        return self.parent.getdiscountRate()

    def getCurve(self):
        return self.curve

    def getContDependentsOn(self):
        dependentonlist=self.getClaimantsDependentOn()
        if len(dependentonlist)==0: return 1 #i.e. not dependent on anyone
        conts=np.array([self.getClaimant(dependenton).getCont() for dependenton in dependentonlist])
        return np.average(conts) #take average of those dependent on

    def getAutoCont(self):
        Tables = self.getTablesAD()
        cont = Tables.getCont(sex=self.sex, employed=self.contDetails['employed'],
                              qualification=self.contDetails['qualification'],
                              disabled=self.contDetails['disabled'], age=self.age)
        return cont

    def getCont(self):
        if self.contAutomatic:
            return self.getAutoCont()
        else:
            return self.cont

    def M(self, point1, point2=None, freq="Y", options='AMI'):
        #builds a curve depending on the options and returns the multiplier
        if point1==None: return None #i.e. if nothing submitted return None
        options=options.upper()
        freq=freq.upper()
        age1=age2=None
        age1= self.getAgeFromPoint(point1)
        if point2: age2= self.getAgeFromPoint(point2)
        c=self.getCurve()
        if 'D' in options:
            co=self.getContDependentsOn() #if this is a dependency claim then we need cont of deceased in uninjured state
        else:
            co=self.getCont()
        result= c.M(age1,age2,freq=freq,cont=co,options=options)
#       print(c.calc.show())
#        c.getPlot(result, age1, age2, freq, co, options)
        return result

    def getStdLE(self): #i.e. the LE with normal life expectancy
        return np.trapz(self.getdataSet().getLx(self.age, LxOnly=True))


    def getAgeFromPoint(self, point):
        #point is either a float (i.e. age) or a datetime
        #returns age
        age=None
        if isinstance(point,np.float64) or isinstance(point,np.int64) or type(point) is float or type(point) is int:
            #i.e. age
            age=point
        elif type(point) is datetime:
            age=(point-self.dob).days/365.25
        elif type(point) is str: #for entries like TRIAL, LIFE
            age=self.parseTextPoint(point)
        else:
            #Error, wrong type
            print('Wrong type passed to getAgeFromPoint')
            print(type(point))
        return age

    def parseTextPoint(self,point):
        #where point='TRIAL+1Y" etc
        #check it's not a string date first
        if is_date(point): return self.getAgeFromPoint(parsedate(point))
        #make upper case
        point = point.upper()
        #removes all spaces
        point=" ".join(point.split())
        #split into component parts
        parts=re.split("(\W)",point)
        #evaluate each part - each part is either 'TRIAL' or '5Y' or '+' or '-'
        #add or subtract
        age=0
        flag=True #add if true
        for part in parts:
            if part in wordPoints:
                if part=='TRIAL':
                    if flag: age+=self.getAge()
                    if not flag: age-=self.getAge()
                elif part=='LIFE':
                    if flag: age+=125
                    if not flag: age-=125
                elif part=='RETIREMENT':
                    if hasattr(self,'retirement'):
                        if flag: age+=self.retirement
                        if not flag: age-=self.retirement
                    else:
                        print('Retirement (uninjured) age not given')
                else:
                    age=age #do nothing
            elif part in plusMinus:
                if part=='+': flag=True
                if part=='-': flag=False
            else:
                #test value
                #strip any '<' or '>'
                part=part.strip('<')
                part=part.strip('>')
                st, en, factor, tinterval= returnFreq(part)
                if tinterval:
                    if flag: age+=tinterval
                    if not flag: age-=tinterval
                else:
                    print('Invalid part of word point, parsewordPoint')
                    return None
        #return value
        return age

    def getdataSet(self):
        return self.dataSet
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
            self.getdataSet().refresh() #refresh all the future data sets
            self.getSAR().refresh() #refresh the past data set
            self.getCurve().refresh() #refresh the curves
            self.dirty=False


    def __init__(self, attributes, parent):


        self.parent=parent #reference to game object
        self.attributes=attributes
        self.dirty=True
        self.fatal=False
        self.dependenton=None


        if 'name' in attributes:
            self.name=attributes['name']

        if 'dob' in attributes and not 'age' in attributes:
            if type(attributes['dob']) is str:
                attributes['dob']=parsedateString(attributes['dob'])
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

        if 'retirement' in attributes:
            if type(attributes['retirement']) is int or type(attributes['retirement']) is float:
                self.retirement=attributes['retirement']

        if 'deltaLE' in attributes:
            self.deltaLE=attributes['deltaLE']
        else:
            self.deltaLE=0

        self.contAutomatic=False #manual by default
        if 'contAutomatic' in attributes: self.contAutomatic=attributes['contAutomatic']

        self.cont=1
        if 'cont' in attributes:self.cont=attributes['cont']

        self.contDetails=ContDetailsdefault
        if 'contDetails' in attributes: self.contDetails=attributes['contDetails'] #should be {'employed','qualification','disabled'}

        if 'dependenton' in self.attributes: self.dependenton=self.attributes['dependenton'].strip().upper()

        self.dataSet=dataSet(attributes['dataSet'], self, self.deltaLE)
        self.curve=curve(self)

        self.SAR=SAR(parent=self)

        self.setUp()
        self.refresh()

    def setUp(self):
        #to be overridden
        pass






