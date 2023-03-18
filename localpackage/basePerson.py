import copy
from datetime import datetime, timedelta
import numpy as np
import re
import requests
from localpackage.dataSet import dataSet
from localpackage.curve import curve
from localpackage.SAR import SAR
from localpackage.utils import wordPoints, plusMinus, returnFreq, ContDetailsdefault, is_date, parsedate, \
    parsedateString, discountOptions, fr, discountFactor, defaultSwiftCarpenterDiscountRate
from localpackage.errorLogging import errors
import math

class baseperson():

    def getSummaryStats(self):
        return {
            'LE': self.LE(),
            'LM': self.LM(),
            'EM': self.EM(),
            'PM': self.PM(),
            'JLE': self.JLE(),
            'JLM': self.JLM(),
            'AutoCont': self.getAutoCont(),
            'StateRetirementAge': self.getStateRetirementAge()
        }

    def getprojection(self):
        return self.parent.getprojection()

    def getautoYrAttained(self):
        return self.parent.getautoYrAttained()

    def getName(self):
        return self.name

    def LE(self): #Life expectancy
        return self.M(self.age,125, options='MI')

    def LM(self, discountRate=None): #Life multiplier
        return self.M(self.age,125, options='AMI',discountRate=discountRate)

    def EM(self, discountRate=None): #Earnings multiplier
        if hasattr(self,'retirement'):
            return self.M(self.age,self.retirement, options='AMI',discountRate=discountRate)
        return self.M(self.age,self.getStateRetirementAge())

    def AEM(self, discountRate=None): #Adjusted earnings multiplier
        cont=self.getCont()
        return [i * cont for i in self.EM(discountRate)]

    def PM(self, discountRate=None): #Pension multiplier
        if hasattr(self,'retirement'):
            return self.M(self.retirement,'LIFE', options='AMI',discountRate=discountRate)
        return self.M(self.getStateRetirementAge(), 'LIFE', options='AMI',discountRate=discountRate)

    def JLE(self): #Joint life expectancy
        if self.parent.getUseTablesEF():
            shortestLEname=self.getShortestLEname()
            claimant=self.parent.getClaimant(shortestLEname)
            m=claimant.MifNotDead(self.age,125,options='MI')
            TableFs = [self.parent.getClaimant(dep).getTableF() for dep in self.getClaimantsDependentOn()] #list of TableE for each dependent
            TableF = math.prod(TableFs)
            resM=[0,0,0,0]
            resM[0]=m[0]
            resM[1]=m[1]
            resM[2]=m[2]*TableF
            resM[3]=resM[0]+resM[1]+resM[2]
            return resM
        else:
            return self.M(self.age,125, options='MID')

    def JLM(self, discountRate=None): #Joint life multiplier
        if self.parent.getUseTablesEF():
            shortestLEname = self.getShortestLEname()
            claimant = self.parent.getClaimant(shortestLEname)
            m = claimant.MifNotDead(self.age,125,options='AMI',discountRate=discountRate)
            TableFs = [self.parent.getClaimant(dep).getTableF() for dep in self.getClaimantsDependentOn()] #list of TableF for each dependent
            TableF = math.prod(TableFs)
            resM=[0,0,0,0]
            resM[0]=m[0]
            resM[1]=m[1]
            resM[2]=m[2]*TableF
            resM[3]=resM[0]+resM[1]+resM[2]
            return resM
        else:
            return self.M(self.age,125, options='AMID',discountRate=discountRate)

    def JM(self, point1, point2=None, freq="Y", options='AMI', discountRate=None): #joint multiplier
        if self.parent.getUseTablesEF():
            options=options.replace('D','')
            shortestLEname=self.getShortestLEname()
            claimant=self.parent.getClaimant(shortestLEname)
            m=claimant.MifNotDead(point1,point2,freq,options=options,discountRate=discountRate) #multiplier for person with shortest LE if not dead
            TableEs = [self.parent.getClaimant(dep).getTableE() for dep in self.getClaimantsDependentOn()] #list of TableE for each dependent
            TableE = math.prod(TableEs)
            TableFs = [self.parent.getClaimant(dep).getTableF() for dep in self.getClaimantsDependentOn()] #list of TableE for each dependent
            TableF = math.prod(TableFs)
            resM=[0,0,0,0]
            resM[0] = m[0] * TableE
            resM[1] = m[1]
            resM[2] = m[2] * TableF
            resM[3] = resM[0] + resM[1] + resM[2]
            return resM
        else:
            if not "D" in options:
                options=options+"D"
            return self.M(point1, point2, freq, options, discountRate)

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

    def getLEifNotDead(self):
        copyme=copy.deepcopy(self)
        copyme.fatal=False
        copyme.setDirty(True)
        copyme.refresh()
        return copyme.LE()

    def MifNotDead(self, point1, point2=None, freq="Y", options='AMI', discountRate=None):
        copyme=copy.deepcopy(self)
        copyme.fatal=False
        copyme.setDirty(True)
        copyme.refresh()
        return copyme.M(point1, point2, freq=freq, options=options, discountRate=discountRate)


    def getDependentWithShortestLE(self):
        #returns name of the dependent with the shortest LE
        deps=self.getClaimantsDependentOn()
        shortestLE=1000
        shortestDepLE=None
        for dep in deps:
            claimant=self.parent.getClaimant(dep)
            LE=claimant.getLEifNotDead()[3]
            if LE<shortestLE:
                shortestLE=LE
                shortestDepLE=dep
        return shortestDepLE

    def getShortestLEname(self):
        #returns name of claimant and deps with shortest LE
        shortestDepLE=self.getDependentWithShortestLE()
        claimant = self.parent.getClaimant(shortestDepLE)
        if shortestDepLE:
            if self.parent.getClaimant(shortestDepLE).getLEifNotDead()[3]>self.getLEifNotDead()[3]:
                return self.getName()
            else:
                return shortestDepLE
        return self.getName()

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

    def getDOI(self):
        return self.parent.getDOI()

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
        # return age at trial (will be different if this is a fatal case from age)
        return (self.gettrialDate()-self.dob).days/365.25

    def getAAI(self):
        # return age at injury
        if self.getDOI():
            return (self.getDOI() - self.getDOB()).days / 365.25
        return None

    def getdeltaLE(self):
        return self.deltaLE

    def getUseMultipleRates(self):
        return self.parent.getUseMultipleRates()

    def getdiscountRate(self, yrs=0):
        return self.parent.getdiscountRate(yrs)

    def getMultipleRates(self):
        return self.parent.getMultipleRates()

    def getdiscountFactor(self,point,discountRate=None):
        if discountRate==None:
            discountRate=self.getdiscountRate()
        return self.M(point, options='A',discountRate=discountRate)

    def gettermCertain(self,point1,point2,freq="Y",discountRate=None):
        if discountRate==None:
            discountRate=self.getdiscountRate()
        return self.M(point1,point2, freq=freq, options='A',discountRate=discountRate)


    def gettargetLE(self):
        return self.targetLE

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

    def INTERESTHOUSE(self,point1,point2="LIFE"):
        #returns the interest in a house (by default for life)
        #query if swiftcarpenter discount applies to past time
        freq="Y"
        options="MI"
        DF_HOUSE=(1/(1+defaultSwiftCarpenterDiscountRate))

        expected_years=self.M(point1,point2,freq,options) #array of 4
        yrs=self.getAgeFromPoint(point1)-self.getAge()
        accelerated_receipt=discountFactor(yrs,self.getdiscountRate())
        past_expected_years=expected_years[0]
        interest_expected_years=expected_years[1]
        future_expected_years=1-pow(DF_HOUSE,expected_years[2])*accelerated_receipt
        total=past_expected_years+interest_expected_years+future_expected_years
        result=[past_expected_years, interest_expected_years, future_expected_years, total]
        return result

    def REVERSION(self,point1,point2="LIFE"):
        #returns the reversionary interest in a house (by default for life)
        #query if swiftcarpenter discount applies to past time
        freq="Y"
        options="MI"
        DF_HOUSE=(1/(1+defaultSwiftCarpenterDiscountRate))

        expected_years=self.M(point1,point2,freq,options) #array of 4
        yrs=self.getAgeFromPoint(point1)-self.getAge()
        accelerated_receipt=discountFactor(yrs,self.getdiscountRate())
        past_expected_years=expected_years[0]
        interest_expected_years=-expected_years[1]
        future_expected_years=pow(DF_HOUSE,expected_years[2])*accelerated_receipt
        total=past_expected_years+interest_expected_years+future_expected_years
        result=[past_expected_years, interest_expected_years, future_expected_years, total]
        return result

    def M(self, point1, point2=None, freq="Y", options='AMI', discountRate=None):
        if self.parent.getUseTablesEF() and 'D' in options:
            return self.JM(point1,point2, freq,options, discountRate)
        #builds a curve depending on the options and returns the multiplier
        if not freq:
            freq="Y"
        if not options:
            options='AMI'
        errors=self.getInputErrors(point1,point2,freq,options)
        if len(errors)>0:
            return "\n".join(errors),"\n".join(errors),"\n".join(errors),"\n".join(errors);
        if point1==None: return None #i.e. if nothing submitted return None
        options=options.upper()
        freq=freq.upper()
        age1=age2=None
        age1= self.getAgeFromPoint(point1)
        if age1==None: return None #i.e. if nothing valid submitted return None
        if point2: age2= self.getAgeFromPoint(point2)
        c=self.getCurve()
        if 'D' in options:
            co=self.getContDependentsOn() #if this is a dependency claim then we need cont of deceased in uninjured state
        else:
            co=self.getCont()
        if(freq=='A'):
            result1 = c.M(age1, age2, freq="Y", cont=co,options="M",discountRate=discountRate); #expected years
            result2 = c.M(age1, age2, freq="Y", cont=co, options=options, discountRate=discountRate);  # normal multiplier
            past=0
            future=0
            interest=0
            if(result1[0] + result1[1]!=0):
                past=result2[0]/(result1[0]+result1[1])
                interest=result2[1]/(result1[0]+result1[1])
            if(result1[2]!=0):
                future=result2[2]/result1[2]
            total=past+interest+future
            result = past, interest, future, total
        else:
            result= c.M(age1,age2,freq=freq,cont=co,options=options,discountRate=discountRate)
#       print(c.calc.show())
#        c.getPlot(result, age1, age2, freq, co, options)
        return result

    def getStdLE(self): #i.e. the LE with normal life expectancy
        return np.trapz(self.getdataSet().getLx(self.age, LxOnly=True))

    def getInputErrors(self, point1, point2, freq, options):
        errors=[]
        age1=age2=None
        age1=self.getAgeFromPoint(point1)
        if point2:
            age2=self.getAgeFromPoint(point2)
        #point 1 - must be number, string, date.
        if age1==None:
            errors.append("\'From\' date invalid")
        #point 2
        if point2: #i.e. if provided
            if age2==None:
                errors.append("\'To\' date invalid")
            if not age1==None and not age2==None:
                if age1>=age2:
                    errors.append("\'To\' date must be after \'From\' date")
        #freq
        if not bool(re.match("^<?(\d+(\.\d+)?)?[YMWDA]>?$",freq)):
            errors.append("\'Frequency\' invalid")
        #options
        for l in options:
            if not l in discountOptions:
                errors.append("\'Discount\' options invalid")
                return errors #i.e. return as soon as error spotted
        return errors

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
            errors.add('Wrong type passed to getAgeFromPoint: ' + type(point).__name__)
        return age

    def parseTextPoint(self,point):
        #where point='TRIAL+1Y" etc
        #check it's not a string date first
        if is_date(point): return self.getAgeFromPoint(parsedate(point))
        #make upper case
        point = point.upper()
        #removes all spaces
        point="".join(point.split())
        #split into component parts
        parts=re.split("([^a-zA-Z0-9_\.])",point)
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
                        errors.add('Retirement (uninjured) age not given')
                        return None
                elif part=='INJURY':
                    AAI=self.getAAI()
                    if not AAI==None:
                        if flag: age+=self.getAAI()
                        if not flag: age-=self.getAAI()
                    else:
                        errors.add('Date of injury not specified')
                        return None
                else:
                    age=age #do nothing
            elif part in plusMinus:
                if part=='+': flag=True
                if part=='-': flag=False
            elif bool(re.match("^<?(\d+(\.\d+)?)?[YMWDA]>?$",part)):
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
                    errors.add("Invalid part of word point, parsewordPoint")
                    return None
            else:
                print("Invalid date")
                errors.add("Invalid date")
                return None
        #return value
        return age

    def getdataSet(self):
        return self.dataSet

    def getrevisedAge(self):
        return self.getdataSet().getrevisedAge(self.getdeltaLE())

    def getTablesAD(self):
        return self.parent.getTablesAD()

    def getSAR(self):
        return self.SAR

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def setDirty(self,value=True):
        self.dirty=value
        self.dataSet.setdirtyCalcs(value)  # make all the future data sets dirty
        self.getSAR().setDirty(value)  # make past data set dirty
        self.curve.setDirty(value) #make all curves dirty

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
            errors.add("Missing age information for person")
        if 'age' in attributes and 'dob' in attributes:
            print("Both age and dob supplied for person")
            errors.add("Both age and dob supplied for person")

        if 'sex' in attributes:
            self.sex=attributes['sex']
        else:
            print("Missing sex for person")
            errors.add("Missing sex for person")

        if 'retirement' in attributes:
            if type(attributes['retirement']) is int or type(attributes['retirement']) is float:
                self.retirement=attributes['retirement']

        #Life expectancy inputs
        c=0
        if 'deltaLE' in attributes:
            c+=1
            self.deltaLE=attributes['deltaLE']
        else:
            self.deltaLE=0

        self.targetLE=None
        if 'targetLE' in attributes:
            c+=1
            self.targetLE=attributes['targetLE']

        if 'liveto' in attributes:
            c+=1
            self.targetLE=attributes['liveto']-self.age

        if c>1:
            print("Specify only one of targetLE, deltaLE or liveto: targetLE will be used.")
            errors.add("Specify only one of targetLE, deltaLE or liveto: targetLE will be used.")

        self.contAutomatic=False #manual by default
        if 'contAutomatic' in attributes: self.contAutomatic=attributes['contAutomatic']

        self.cont=1
        if 'cont' in attributes:self.cont=attributes['cont']

        self.contDetails=ContDetailsdefault
        if 'contDetails' in attributes: self.contDetails=attributes['contDetails'] #should be {'employed','qualification','disabled'}

        if 'dependenton' in self.attributes: self.dependenton=self.attributes['dependenton'].strip()

        self.dataSet=dataSet(attributes['dataSet'], self, self.deltaLE)
        self.curve=curve(self)

        self.SAR=SAR(parent=self)

        self.setUp()
        self.refresh()

    def setUp(self):
        #to be overridden
        pass






