import copy
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import re
import requests
from localpackage.dataSet import dataSet
from localpackage.curve import curve
from localpackage.SAR import SAR
from localpackage.utils import wordPoints, plusMinus, returnFreq, ContDetailsdefault, is_date, parsedate, \
    parsedateString, discountOptions, fr, discountFactor, defaultSwiftCarpenterDiscountRate, DRMethods, parseOverrides
from localpackage.errorLogging import errors
import math
import seaborn as sns
import matplotlib.pyplot as plt


class baseperson():

    def showLEPlot(self):
        results = self.getLEDistribution()
        ax = sns.lineplot(results, x='age', y='mort%')
        title = 'Dist. of LE: ' + self.getSex() + ', age ' + '{:.1f}'.format(self.getAge())
        if self.getRevisedAge() != self.getAge():
            title += " (revised age " + '{:.1f}'.format(self.getRevisedAge()) + ")"
        ax.set(title=title)
        ax.set_ylim(bottom=0)

        results['dfprod'] = results['mort%'] * (results['age'] - 0.5)
        mean = results['dfprod'].sum()
        EAD = self.LE()[3] + self.getAge()

        results['dfdev'] = (((results['age'] - 0.5) - mean) ** 2) * results['mort%']
        stdev = results['dfdev'].sum() ** 0.5

        results['cummort%'] = results['mort%'].cumsum()
        median = results[results['cummort%'] <= 0.5]['age'].iloc[-1]
        lower5 = results[results['cummort%'] <= 0.05]['age'].iloc[-1]
        upper5 = results[results['cummort%'] <= 0.95]['age'].iloc[-1]

        mode = results.loc[results['mort%'].idxmax()]['age']

        txt = ""
        txt += "{:,.2f}".format(mode) + ' mode' + "\n"
        txt += "{:,.2f}".format(median) + ' median' + "\n"
        txt += "{:,.2f}".format(mean) + ' mean' + "\n"
        txt += "{:,.2f}".format(stdev) + ' std dev' + "\n"
        txt += "90% range: " + "{:,.2f}".format(lower5) + ' to ' + "{:,.2f}".format(upper5)
        plt.text(0.025, 0.9, txt, horizontalalignment='left', verticalalignment='top', size='medium', color='black',
                 weight='semibold', transform=ax.transAxes)
        plt.show()

    def showCapitalLeftPlot(self, lump_sum, annual_expense, avg_annual_return=None, std_dev_return=None):
        results = self.monteCarlo(lump_sum, annual_expense, avg_annual_return, std_dev_return)
        ax = sns.histplot(results)
        title = "Distribution of capital left with lump sum of £" + '{:,}'.format(
            lump_sum) + "\n" + "with avg real return of " + '{:.2%}'.format(
            avg_annual_return) + ", " + "with stdev of " + '{:.2%}'.format(std_dev_return)
        title += '\n' + self.getSex() + ', age ' + '{:.1f}'.format(self.getAge())
        if self.getRevisedAge() != self.getAge():
            title += " (revised age " + '{:.1f}'.format(self.getRevisedAge()) + ")"
        ax.set(xlabel="capital left, £")
        plt.title(title, fontsize=10)
        plt.legend([], [], frameon=False)

        lower5, upper5 = np.percentile(results, [5, 95])

        less_than_zero = results[results < 0].count()
        total_count = results.count()
        percent = less_than_zero.iloc[0] / total_count.iloc[0]
        median = results.median().iloc[0]
        mean = results.mean().iloc[0]
        stdev = results.std().iloc[0]

        txt = ""
        txt += "{0:.0%}".format(percent) + ' chance of < £0' + "\n"
        txt += "£" + "{:,.0f}".format(median) + ' median' + "\n"
        txt += "£" + "{:,.0f}".format(mean) + ' mean' + "\n"
        txt += "£" + "{:,.0f}".format(stdev) + ' std dev' + "\n"
        txt += "90% range: £" + "{:,.0f}".format(lower5) + ' to £' + "{:,.0f}".format(upper5)
        plt.text(0.4, 0.9, txt, horizontalalignment='left', verticalalignment='top', size='medium', color='red',
                 weight='semibold', transform=ax.transAxes)

        results.describe()
        plt.show()

    def monteCarlo(self, lump_sum, annual_expense, avg_annual_return=None, std_dev_return=None):
        # Use a breakpoint in the code line below to debug your script.
        if avg_annual_return is None:
            avg_annual_return = 1.5 / 100
        if std_dev_return is None:
            std_dev_return = 0.5 / 100

        start_capital = lump_sum

        num_simulations = 100000
        num_reps = 1000

        all_stats = []

        rv_life_left = self.getSampleLifeLeft(num_reps)
        rv_annual_return = np.random.normal(avg_annual_return, std_dev_return, 1000)

        for i in range(num_simulations):
            print(i)
            all_stats.append(
                self.capital_left(start_capital, rv_annual_return, annual_expense, np.random.choice(rv_life_left)))

        results = np.array(all_stats)
        results = pd.DataFrame(all_stats, columns=['capital_left'])
        return results

    def capital_left(self, start_capital, rv_annual_return, annual_expense, life_left):
        def next_years_capital(capital, annual_return, annual_expense):
            capital *= 1 + annual_return  # increase
            capital -= annual_expense  # decrease
            return capital

        for r in range(0, int(life_left)):  # capital left after many years
            start_capital = next_years_capital(start_capital, np.random.choice(rv_annual_return), annual_expense)

        return start_capital

    def getLEDistribution(self):
        # returns data frame of life expectancy distribution
        df = pd.DataFrame(data={'age': self.getCurve().getCurve('M', 1)[2],
                                'Lx': self.getCurve().getCurve('M', 1)[1]})
        df = df[(df['age'] >= self.getAge())]
        df['mort%'] = -df.diff()['Lx']
        df['prod'] = df['age'] * df['mort%']
        return df[['age', 'mort%']]

    def getSampleLifeLeft(self, num_reps):
        # returns numpy of LE sample
        df = self.getLEDistribution()
        df['yrs_left'] = df['age'] - self.getAge()
        df['freq'] = df['mort%'] * num_reps
        x = df[['yrs_left', 'freq']].to_numpy()[1:]
        l = []

        def add_to_list(r):
            value = r[0]
            freq = r[1]
            rnd_freq = int(freq.round(0))
            for i in range(rnd_freq):
                l.append(value - 0.5)

        np.apply_along_axis(add_to_list, axis=1, arr=x)
        result = np.array(l)
        #        print(np.mean(result))
        #        print(np.std(result))
        return result

    def getSummaryStats(self):
        return {
            'LE': self.LE(),
            'LM': self.LM(),
            'EM': self.EM(),
            'PM': self.PM(),
            'JLE': self.JLE(),
            'JLM': self.JLM(),
            'AutoCont': self.getAutoCont(),
            'StateRetirementAge': self.getStateRetirementAge(),
            'revisedAge': self.getRevisedAge()
        }

    def getprojection(self):
        return self.parent.getprojection()

    def getautoYrAttained(self):
        return self.parent.getAutoYrAttained()

    def getName(self):
        return self.name

    def LE(self):  # Life expectancy
        return self.M(self.age, 125, options='MI')

    def LM(self, discountRate=None, DRMethodOverride=None, overrides=None):  # Life multiplier
        return self.M('TRIAL', 'LIFE', options='AMI', discountRate=discountRate, DRMethodOverride=DRMethodOverride,
                      overrides=overrides)

    def EM(self, discountRate=None, DRMethodOverride=None, overrides=None):  # Earnings multiplier
        if hasattr(self, 'retirement'):
            return self.M('TRIAL', self.retirement, options='AMI', discountRate=discountRate,
                          DRMethodOverride=DRMethodOverride, overrides=overrides)
        return self.M('TRIAL', self.getStateRetirementAge(), options='AMI', discountRate=discountRate,
                      DRMethodOverride=DRMethodOverride, overrides=overrides)

    def AEM(self, discountRate=None, DRMethodOverride=None, overrides=None):  # Adjusted earnings multiplier
        cont = self.getCont()
        return [i * cont for i in
                self.EM(discountRate=discountRate, DRMethodOverride=DRMethodOverride, overrides=overrides)]

    def PM(self, discountRate=None, DRMethodOverride=None, overrides=None):  # Pension multiplier
        if hasattr(self, 'retirement'):
            return self.M(self.retirement, 'LIFE', options='AMI', discountRate=discountRate,
                          DRMethodOverride=DRMethodOverride, overrides=overrides)
        return self.M(self.getStateRetirementAge(), 'LIFE', options='AMI', discountRate=discountRate,
                      DRMethodOverride=DRMethodOverride, overrides=overrides)

    def JLE(self):  # Joint life expectancy
        if self.parent.getUseTablesEF():
            shortestLEname = self.getShortestLEname()
            claimant = self.parent.getClaimant(shortestLEname)
            m = claimant.MifNotDead('TRIAL', 'LIFE', options='MI')
            TableFs = [self.parent.getClaimant(dep).getTableF() for dep in
                       self.getClaimantsDependentOn()]  # list of TableE for each dependent
            TableF = math.prod(TableFs)
            resM = [0, 0, 0, 0]
            resM[0] = m[0]
            resM[1] = m[1]
            resM[2] = m[2] * TableF
            resM[3] = resM[0] + resM[1] + resM[2]
            return resM
        else:
            return self.M('TRIAL', 'LIFE', options='MID')

    def JLM(self, discountRate=None, DRMethodOverride=None, overrides=None):  # Joint life multiplier
        if self.parent.getUseTablesEF():
            shortestLEname = self.getShortestLEname()
            claimant = self.parent.getClaimant(shortestLEname)
            m = claimant.MifNotDead('TRIAL', 'LIFE', options='AMI', discountRate=discountRate,
                                    DRMethodOverride=DRMethodOverride, overrides=overrides)
            TableFs = [self.parent.getClaimant(dep).getTableF() for dep in
                       self.getClaimantsDependentOn()]  # list of TableF for each dependent
            TableF = math.prod(TableFs)
            resM = [0, 0, 0, 0]
            resM[0] = m[0]
            resM[1] = m[1]
            resM[2] = m[2] * TableF
            resM[3] = resM[0] + resM[1] + resM[2]
            return resM
        else:
            return self.M('TRIAL', 'LIFE', options='AMID', discountRate=discountRate, DRMethodOverride=DRMethodOverride,
                          overrides=overrides)

    def JM(self, point1, point2=None, freq="Y", options='AMI', discountRate=None,
           DRMethodOverride=None, overrides=None):  # joint multiplier
        if self.parent.getUseTablesEF():
            options = options.replace('D', '')
            shortestLEname = self.getShortestLEname()
            claimant = self.parent.getClaimant(shortestLEname)
            m = claimant.MifNotDead(point1, point2, freq, options=options, discountRate=discountRate,
                                    DRMethodOverride=DRMethodOverride,
                                    overrides=None)  # multiplier for person with shortest LE if not dead
            TableEs = [self.parent.getClaimant(dep).getTableE() for dep in
                       self.getClaimantsDependentOn()]  # list of TableE for each dependent
            TableE = math.prod(TableEs)
            TableFs = [self.parent.getClaimant(dep).getTableF() for dep in
                       self.getClaimantsDependentOn()]  # list of TableE for each dependent
            TableF = math.prod(TableFs)
            resM = [0, 0, 0, 0]
            resM[0] = m[0] * TableE
            resM[1] = m[1]
            resM[2] = m[2] * TableF
            resM[3] = resM[0] + resM[1] + resM[2]
            return resM
        else:
            if not "D" in options:
                options = options + "D"
            return self.M(point1, point2, freq=freq, options=options, discountRate=discountRate,
                          DRMethodOverride=DRMethodOverride, overrides=overrides)

    def getStateRetirementAge(self):
        # returns state retirement age from government web-site
        dob = self.getDOB()
        yr = str(dob.year)
        mo = str(dob.month).zfill(2)
        dy = str(dob.day).zfill(2)
        urlsuffix = yr + "-" + mo + "-" + dy
        url = 'https://www.gov.uk/state-pension-age/y/age/'
        response = requests.get(url + urlsuffix)
        if response:
            y = re.search('Your State Pension age is (\d+) years', response.text)
            if y:
                return int(y[1])
            else:
                return None
        else:
            return None

    def getLEifNotDead(self):
        copyme = copy.deepcopy(self)
        copyme.fatal = False
        copyme.setDirty(True)
        copyme.refresh()
        return copyme.LE()

    def MifNotDead(self, point1, point2=None, freq="Y", options='AMI', discountRate=None, DRMethodOverride=None):
        copyme = copy.deepcopy(self)
        copyme.fatal = False
        copyme.setDirty(True)
        copyme.refresh()
        return copyme.M(point1, point2, freq=freq, options=options, discountRate=discountRate,
                        DRMethodOverride=DRMethodOverride)

    def getDependentWithShortestLE(self):
        # returns name of the dependent with the shortest LE
        deps = self.getClaimantsDependentOn()
        shortestLE = 1000
        shortestDepLE = None
        for dep in deps:
            claimant = self.parent.getClaimant(dep)
            LE = claimant.getLEifNotDead()[3]
            if LE < shortestLE:
                shortestLE = LE
                shortestDepLE = dep
        return shortestDepLE

    def getShortestLEname(self):
        # returns name of claimant and deps with shortest LE
        shortestDepLE = self.getDependentWithShortestLE()
        claimant = self.parent.getClaimant(shortestDepLE)
        if shortestDepLE:
            if self.parent.getClaimant(shortestDepLE).getLEifNotDead()[3] > self.getLEifNotDead()[3]:
                return self.getName()
            else:
                return shortestDepLE
        return self.getName()

    def getClaimantsDependentOn(self):
        # returns list of names claimant is dependent on
        listofnames = []
        if self.dependenton:
            listofnames = self.dependenton.split(',')  # turn comma delimited string into array of names
            listofnames = [n.strip() for n in listofnames]  # removes leading and trailing space
        return listofnames

    def getClaimants(self):
        return self.parent.getClaimants()

    def getClaimant(self, name):
        return self.parent.getClaimant(name)

    def isFatal(self):
        return self.fatal

    def getDeltaLE(self):
        return self.deltaLE

    def getSex(self):
        return self.sex

    def setSex(self, sex):
        self.sex = sex

    def getDOI(self):
        return self.parent.getDOI()

    def getDOB(self):
        return self.dob

    def setDOB(self, dob):
        self.dob = dob
        self.age = (self.gettrialDate() - self.dob).days / 365.25
        self.setDirty(True)

    def getAge(self):
        return self.age

    def setAge(self, age):
        self.age = age
        self.dob = self.gettrialDate() - timedelta(days=(self.age * 365.25))

    def getAAT(self):
        # return age at trial (will be different if this is a fatal case from age)
        return (self.gettrialDate() - self.dob).days / 365.25

    def getAAI(self):
        # return age at injury
        if self.getDOI():
            return (self.getDOI() - self.getDOB()).days / 365.25
        return None

    def getdeltaLE(self):
        return self.deltaLE

    def getRegion(self):
        return self.parent.getRegion()

    def getYear(self):
        return self.parent.getYear()

    def getProjection(self):
        return self.parent.getProjection()

    def getAutoYrAttained(self):
        return self.parent.getAutoYrAttained()

    def getRevisedAge(self):
        return self.dataSet.getrevisedAge()

    def getUseMultipleRates(self):
        return self.parent.getUseMultipleRates()

    def getdiscountRate(self, yrs=0, discountRate=None, DRMethodOverride=None):
        return self.parent.getdiscountRate(yrs=yrs, discountRate=discountRate, DRMethodOverride=DRMethodOverride)

    def getMultipleRates(self):
        return self.parent.getMultipleRates()

    def gettargetLE(self):
        return self.targetLE

    def getCurve(self):
        return self.curve

    def getDependentOn(self):
        return self.dependenton

    def setDependentOn(self, dependenton):
        self.dependenton = dependenton

    def getContDependentsOn(self):
        dependentonlist = self.getClaimantsDependentOn()
        if len(dependentonlist) == 0: return 1  # i.e. not dependent on anyone
        conts = np.array([self.getClaimant(dependenton).getCont() for dependenton in dependentonlist])
        return np.average(conts)  # take average of those dependent on

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

    def INTERESTHOUSE(self, point1, point2="LIFE"):
        # returns the interest in a house (by default for life)
        # query if swiftcarpenter discount applies to past time
        freq = "Y"
        options = "MI"
        DF_HOUSE = (1 / (1 + defaultSwiftCarpenterDiscountRate))

        expected_years = self.M(point1, point2, freq, options)  # array of 4
        yrs = self.getAgeFromPoint(point1) - self.getAge()
        accelerated_receipt = discountFactor(yrs, self.getdiscountRate())
        past_expected_years = expected_years[0]
        interest_expected_years = expected_years[1]
        future_expected_years = 1 - pow(DF_HOUSE, expected_years[2]) * accelerated_receipt
        total = past_expected_years + interest_expected_years + future_expected_years
        result = [past_expected_years, interest_expected_years, future_expected_years, total]
        return result

    def REVERSION(self, point1, point2="LIFE"):
        # returns the reversionary interest in a house (by default for life)
        # query if swiftcarpenter discount applies to past time
        freq = "Y"
        options = "MI"
        DF_HOUSE = (1 / (1 + defaultSwiftCarpenterDiscountRate))

        expected_years = self.M(point1, point2, freq, options)  # array of 4
        yrs = self.getAgeFromPoint(point1) - self.getAge()
        accelerated_receipt = discountFactor(yrs, self.getdiscountRate())
        past_expected_years = expected_years[0]
        interest_expected_years = -expected_years[1]
        future_expected_years = pow(DF_HOUSE, expected_years[2]) * accelerated_receipt
        total = past_expected_years + interest_expected_years + future_expected_years
        result = [past_expected_years, interest_expected_years, future_expected_years, total]
        return result

    def setOverrides(self, overrides):
        result = parseOverrides(overrides)
        if 'SEX' in result:
            self.setSex(result['SEX'])
        if 'AGE' in result:
            self.setAge(float(result['AGE']))
        if 'DEPENDENTON' in result:
            self.setDependentOn(result['DEPENDENTON'])
        if 'DRMETHOD' in result:
            self.parent.setDRMethod(result['DRMETHOD'])
            if result['DRMETHOD'] == 'SINGLE':
                self.parent.setUseMultipleRates(False)
            else:
                self.parent.setUseMultipleRates(True)
        if 'SHORTRATE' in result:
            self.parent.setShortRate(float(result['SHORTRATE']))
        if 'LONGRATE' in result:
            self.parent.setLongRate(float(result['LONGRATE']))
        if 'SINGLERATE' in result:
            self.parent.setSingleRate(float(result['SINGLERATE']))
        if 'SWITCH' in result:
            self.parent.setSwitch(float(result['SWITCH']))

    def getOriginalValues(self):
        return self.originalValues

    def setOriginalValues(self):
        self.setSex(self.getOriginalValues()['SEX'])
        self.setAge(self.getOriginalValues()['AGE'])
        self.setDependentOn(self.getOriginalValues()['DEPENDENTON'])
        self.parent.setDRMethod(self.parent.getOriginalValues()['DRMETHOD'])
        self.parent.setUseMultipleRates(self.parent.getOriginalValues()['USEMULTIPLERATES'])
        self.parent.setShortRate(self.parent.getOriginalValues()['SHORTRATE'])
        self.parent.setLongRate(self.parent.getOriginalValues()['LONGRATE'])
        self.parent.setSingleRate(self.parent.getOriginalValues()['SINGLERATE'])
        self.parent.setSwitch(self.parent.getOriginalValues()['SWITCH'])

    def M(self, point1, point2=None, freq="Y", options='AMI', discountRate=None, DRMethodOverride=None, overrides=None):
        # deal with overrides
        self.setOriginalValues()
        if (overrides):
            self.setOverrides(overrides)

        if self.parent.getUseTablesEF() and 'D' in options:
            return self.JM(point1, point2, freq, options, discountRate, DRMethodOverride)
        # builds a curve depending on the options and returns the multiplier
        if not freq:
            freq = "Y"
        if not options:
            options = 'AMI'
        errors = self.getInputErrors(point1, point2, freq, options, DRMethodOverride)
        if len(errors) > 0:
            return "\n".join(errors), "\n".join(errors), "\n".join(errors), "\n".join(errors);
        if point1 == None: return None  # i.e. if nothing submitted return None
        options = options.upper()
        freq = freq.upper()
        age1 = age2 = None
        age1 = self.getAgeFromPoint(point1)
        if age1 == None: return None  # i.e. if nothing valid submitted return None
        if point2: age2 = self.getAgeFromPoint(point2)

        c = self.getCurve()

        if 'D' in options:
            co = self.getContDependentsOn()  # if this is a dependency claim then we need cont of deceased in uninjured state
        else:
            co = self.getCont()
        if (freq == 'A'):
            result1 = c.M(age1, age2, freq="Y", cont=co, options="M", discountRate=discountRate,
                          DRMethodOverride=DRMethodOverride);  # expected years
            result2 = c.M(age1, age2, freq="Y", cont=co, options=options,
                          discountRate=discountRate, DRMethodOverride=DRMethodOverride);  # normal multiplier
            past=result2[0]
            interest=result2[1]
            future=result2[2]
            totalYrs = age2-age1
            if(totalYrs>0):
                past /= totalYrs
                interest /= totalYrs
                future /= totalYrs
            total = past + interest + future
            result = past, interest, future, total
        else:
            result = c.M(age1, age2, freq=freq, cont=co, options=options, discountRate=discountRate,
                         DRMethodOverride=DRMethodOverride)
        #       print(c.calc.show())
        #        c.getPlot(result, age1, age2, freq, co, options)
        return result

    def getStdLE(self):  # i.e. the LE with normal life expectancy
        return np.trapz(self.getdataSet().getLx(self.age, LxOnly=True))

    def getInputErrors(self, point1, point2, freq, options, DRMethodOverride):
        errors = []
        age1 = age2 = None
        age1 = self.getAgeFromPoint(point1)
        if point2:
            age2 = self.getAgeFromPoint(point2)
        # point 1 - must be number, string, date.
        if age1 == None:
            errors.append("\'From\' date invalid")
        # point 2
        if point2:  # i.e. if provided
            if age2 == None:
                errors.append("\'To\' date invalid")
            if not age1 == None and not age2 == None:
                if age1 >= age2:
                    errors.append("\'To\' date must be after \'From\' date")
        # freq
        if not bool(re.match("^<?(\d+(\.\d+)?)?[YMWDA]>?$", freq)):
            errors.append("\'Frequency\' invalid")
        # options
        for l in options:
            if l not in discountOptions:
                errors.append("\'Discount\' options invalid")
                return errors  # i.e. return as soon as error spotted
        # DRMethodOverride
        if DRMethodOverride:
            if DRMethodOverride not in DRMethods:
                errors.append("\'Discount method override\' option invalid")
                return errors
        return errors

    def getAgeFromPoint(self, point):
        # point is either a float (i.e. age) or a datetime
        # returns age
        age = None
        if isinstance(point, np.float64) or isinstance(point, np.int64) or type(point) is float or type(point) is int:
            # i.e. age
            age = point
        elif type(point) is datetime:
            age = (point - self.dob).days / 365.25
        elif type(point) is str:  # for entries like TRIAL, LIFE
            age = self.parseTextPoint(point)
        else:
            # Error, wrong type
            print('Wrong type passed to getAgeFromPoint')
            print(type(point))
            errors.add('Wrong type passed to getAgeFromPoint: ' + type(point).__name__)
        return age

    def parseTextPoint(self, point):
        # where point='TRIAL+1Y" etc
        # check it's not a string date first
        if is_date(point): return self.getAgeFromPoint(parsedate(point))
        # make upper case
        point = point.upper()
        # removes all spaces
        point = "".join(point.split())
        # split into component parts
        parts = re.split("([^a-zA-Z0-9_\.])", point)
        # evaluate each part - each part is either 'TRIAL' or '5Y' or '+' or '-'
        # add or subtract
        age = 0
        flag = True  # add if true
        for part in parts:
            if part in wordPoints:
                if part == 'TRIAL':
                    if flag: age += self.getAge()
                    if not flag: age -= self.getAge()
                elif part == 'LIFE':
                    if flag: age += 125
                    if not flag: age -= 125
                elif part == 'RETIREMENT':
                    if hasattr(self, 'retirement'):
                        if flag: age += self.retirement
                        if not flag: age -= self.retirement
                    else:
                        print('Retirement (uninjured) age not given')
                        errors.add('Retirement (uninjured) age not given')
                        return None
                elif part == 'INJURY':
                    AAI = self.getAAI()
                    if not AAI == None:
                        if flag: age += self.getAAI()
                        if not flag: age -= self.getAAI()
                    else:
                        errors.add('Date of injury not specified')
                        return None
                else:
                    age = age  # do nothing
            elif part in plusMinus:
                if part == '+': flag = True
                if part == '-': flag = False
            elif bool(re.match("^<?(\d+(\.\d+)?)?[YMWDA]>?$", part)):
                # test value
                # strip any '<' or '>'
                part = part.strip('<')
                part = part.strip('>')
                st, en, factor, tinterval = returnFreq(part)
                if tinterval:
                    if flag: age += tinterval
                    if not flag: age -= tinterval
                else:
                    print('Invalid part of word point, parsewordPoint')
                    errors.add("Invalid part of word point, parsewordPoint")
                    return None
            else:
                print("Invalid date")
                errors.add("Invalid date")
                return None
        # return value
        return age

    def getdataSet(self):
        return self.dataSet

    #    def getrevisedAge(self):
    #        return self.getdataSet().getrevisedAge(self.getdeltaLE())

    def getTablesAD(self):
        return self.parent.getTablesAD()

    def getSAR(self):
        return self.SAR

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def getYear(self):
        return self.year

    def getYrAttainedIn(self):
        return self.yrAttainedIn

    def getRegion(self):
        return self.region

    def refresh(self):
        self.getSAR().refresh()
        self.getdataSet().refresh()
        self.getCurve().refresh()  # refresh the curves

    def __init__(self, attributes, parent):

        self.parent = parent  # reference to game object
        self.attributes = attributes
        self.fatal = False
        self.dependenton = None

        self.year = attributes['dataSet']['year']
        self.region = attributes['dataSet']['region']
        self.yrAttainedIn = attributes['dataSet']['yrAttainedIn']

        if 'name' in attributes:
            self.name = attributes['name']

        if 'dob' in attributes and not 'age' in attributes:
            if type(attributes['dob']) is str:
                attributes['dob'] = parsedateString(attributes['dob'])
            self.dob = attributes['dob']
            self.age = (self.gettrialDate() - self.dob).days / 365.25
        if 'age' in attributes and not 'dob' in attributes:
            self.age = attributes['age']
            self.dob = self.gettrialDate() - timedelta(days=(self.age * 365.25))

        if not 'age' in attributes and not 'dob' in attributes:
            print("Missing age information for person")
            errors.add("Missing age information for person")
        if 'age' in attributes and 'dob' in attributes:
            print("Both age and dob supplied for person")
            errors.add("Both age and dob supplied for person")

        if 'sex' in attributes:
            self.sex = attributes['sex']
        else:
            print("Missing sex for person")
            errors.add("Missing sex for person")

        if 'retirement' in attributes:
            if type(attributes['retirement']) is int or type(attributes['retirement']) is float:
                self.retirement = attributes['retirement']

        # Life expectancy inputs
        c = 0
        if 'deltaLE' in attributes:
            c += 1
            self.deltaLE = attributes['deltaLE']
        else:
            self.deltaLE = 0

        self.targetLE = None
        if 'targetLE' in attributes:
            c += 1
            self.targetLE = attributes['targetLE']

        if 'liveto' in attributes:
            c += 1
            self.targetLE = attributes['liveto'] - self.age

        if c > 1:
            print("Specify only one of targetLE, deltaLE or liveto: targetLE will be used.")
            errors.add("Specify only one of targetLE, deltaLE or liveto: targetLE will be used.")

        self.contAutomatic = False  # manual by default
        if 'contAutomatic' in attributes: self.contAutomatic = attributes['contAutomatic']

        self.cont = 1
        if 'cont' in attributes: self.cont = attributes['cont']

        self.contDetails = ContDetailsdefault
        if 'contDetails' in attributes: self.contDetails = attributes[
            'contDetails']  # should be {'employed','qualification','disabled'}

        if 'dependenton' in self.attributes: self.setDependentOn(self.attributes['dependenton'].strip())

        self.dataSet = dataSet(self)
        self.curve = curve(self)

        self.SAR = SAR(parent=self)

        self.originalValues = {'SEX': self.getSex(), 'AGE': self.getAge(), 'DEPENDENTON': self.getDependentOn()}

        self.setUp()

    def setUp(self):
        # to be overridden
        pass
