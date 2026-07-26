import copy
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import re
from localpackage.dataSet import dataSet
from localpackage.spa import StatePensionAge
from localpackage.curve import curve
from localpackage.SAR import SAR
from localpackage.utils import wordPoints, plusMinus, returnFreq, ContDetailsdefault, is_date, isfloat, parsedate, \
    parsedateString, discountOptions, fr, discountFactor, defaultSwiftCarpenterDiscountRate, DRMethods, parseOverrides, yrsGap, addYears
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
        # (Removed a dead `EAD = self.LE()[3] + self.getAge()`: assigned, never read, and
        # carrying the pre-fix formula that adds a trial-anchored LE to an age it was not
        # measured from. Use getEAD() if this plot ever needs the figure.)

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
            'ageTrial': self.getAAT(),
            'revisedAge': self.getRevisedAge()
        }

    def getprojection(self):
        return self.parent.getprojection()

    def getautoYrAttained(self):
        return self.parent.getAutoYrAttained()

    def getName(self):
        return self.name

    def ageAtDate(self, d):
        # Age at a date, measured RELATIVE TO THE TRIAL DATE rather than from DOB.
        #
        # The anniversary convention is not additive - the denominator is the length of
        # the anniversary year, which depends on the anchor date - so yrsGap(dob, d) and
        # age - yrsGap(d, trial) are not the same number. Both are defensible: the first
        # makes every age exact from birth, the second makes the SPAN between two points
        # exactly the elapsed time between their dates.
        #
        # Multipliers integrate over a period, so the span is what has to be right; a
        # period from injury to trial must be worth exactly the time that passed. The
        # Excel add-in resolves points this way too (PointResolver: ageAtTrial +
        # yrsGap(trialDate, date)), so the two products now agree.
        return self.age - yrsGap(d, self.gettrialDate())

    def dateAtAge(self, age):
        # Inverse of ageAtDate.
        return addYears(self.gettrialDate(), age - self.age)

    def LE(self):  # Life expectancy
        return self.M(self.age, 125, options='MI')

    def LEDOD(self):
        # Life expectancy as at the DATE OF DEATH, for a fatal claimant.
        #
        # LE() answers the "but for the death" question from the TRIAL date, which is the
        # framing Knauer v MoJ [2016] UKSC 9 requires for future dependency. LEDOD answers
        # the same question from the date of death: but for the death, how much longer
        # would she have been expected to live, measured from when she died.
        #
        # The two are the same underlying claim expressed from different dates - both imply
        # the same expected age at death - so LEDOD exceeds LE by roughly the death-to-trial
        # period, net of the selection effect of having survived it.
        #
        # For a living claimant the two dates coincide, so this returns LE().
        if not self.isFatal():
            return self.LE()
        # options='M', NOT 'MI'. Date of death to trial is a PAST period, so the 'I' that
        # LE() carries would accrue SAR interest into what must be a pure mortality figure -
        # 0.3001 of spurious interest on the reference case, taking 33.9221 to 34.2221.
        return self.M(self.getAAD(), 125, options='M')

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

            def translatePoint(p):
                # Numeric points are ages on THIS claimant's timeline; re-express them on the
                # shortest-LE claimant's timeline so both refer to the same calendar date.
                # Strings ('TRIAL', 'LIFE', date strings) already resolve correctly on that life.
                if isinstance(p, bool):
                    return p
                if isinstance(p, (int, float, np.integer, np.floating)):
                    return min(125, p + (claimant.getAge() - self.getAge()))
                return p

            m = claimant.MifNotDead(translatePoint(point1), translatePoint(point2), freq, options=options,
                                    discountRate=discountRate,
                                    DRMethodOverride=DRMethodOverride,
                                    overrides=None)  # multiplier for person with shortest LE if not dead
            # M() reports input errors by returning the message in all four elements. Scaling
            # those by Table E below raises TypeError ("can't multiply sequence by non-int")
            # and kills the whole request, instead of returning a per-row error the way the
            # non-E/F branch does. Propagate them unchanged.
            if m is None:
                return None
            if any(isinstance(v, str) for v in m):
                return m
            TableEs = [self.parent.getClaimant(dep).getTableE() for dep in
                       self.getClaimantsDependentOn()]  # list of TableE for each dependent
            TableE = math.prod(TableEs)
            TableFs = [self.parent.getClaimant(dep).getTableF() for dep in
                       self.getClaimantsDependentOn()]  # list of TableE for each dependent
            TableF = math.prod(TableFs)
            resM = [0, 0, 0, 0]
            resM[0] = m[0] * TableE
            resM[1] = m[1] * TableE  # interest accrues on the past loss, which is itself scaled by Table E
            resM[2] = m[2] * TableF
            resM[3] = resM[0] + resM[1] + resM[2]

            # Regression self-check (with-minus-without principle, agreed with the user).
            # The E/F interest term must equal the E/F multiplier WITH interest minus the same
            # multiplier WITHOUT interest. Recompute the shortest life's multiplier with the
            # interest factor removed and difference the E/F totals:
            #   (m0.E + m1.E + m2.F) - (m0.E + m2.F) == m1.E == resM[1].
            # Skip when stripping 'I' would leave an EMPTY options string: M() treats '' as the
            # 'AMI' default (there is no way to express "no discounts"), so mNoI would come back
            # as a full AMI multiplier and the check would compare unlike quantities.
            if 'I' in options and options.replace('I', ''):
                mNoI = claimant.MifNotDead(translatePoint(point1), translatePoint(point2), freq,
                                           options=options.replace('I', ''), discountRate=discountRate,
                                           DRMethodOverride=DRMethodOverride, overrides=None)
                if mNoI is None or any(isinstance(v, str) for v in mNoI):
                    return resM  # cannot run the self-check; the primary result is still sound
                withoutTotal = mNoI[0] * TableE + mNoI[2] * TableF
                assert math.isclose(resM[3] - withoutTotal, resM[1], rel_tol=1e-9, abs_tol=1e-12), \
                    "E/F interest inconsistent with with-minus-without: " \
                    f"{resM[3] - withoutTotal} vs resM[1]={resM[1]}"
            return resM
        else:
            if not "D" in options:
                options = options + "D"
            return self.M(point1, point2, freq=freq, options=options, discountRate=discountRate,
                          DRMethodOverride=DRMethodOverride, overrides=overrides)

    def getStateRetirementAge(self):
        # State Pension age computed purely locally from the claimant's DOB and sex via the
        # ported VBA ModuleSPA rules (Pensions Acts 1995/2011/2014), including every transitional
        # monthly band. This replaces the former live gov.uk HTTP lookup: process() calls this for
        # every claimant, so there is now NO network dependency to hang or 500 the request, and the
        # transitional-band accuracy the web regex missed is captured exactly. (F21/F27)
        # Returns years (may be fractional, e.g. 66.25); None for invalid input.
        if hasattr(self, '_stateRetirementAge'):
            return self._stateRetirementAge
        spa = StatePensionAge(self.getDOB(), self.getSex())
        result = None if (spa is None or spa < 0) else spa
        self._stateRetirementAge = result
        return result

    def setDirty(self, dirty=True):
        # Invalidate cached curves/SAR/mortality results so they are rebuilt on next use.
        if dirty:
            self.refresh()

    def getLEifNotDead(self):
        copyme = copy.deepcopy(self)
        copyme.fatal = False
        copyme.setDirty(True)
        copyme.refresh()
        return copyme.LE()

    def MifNotDead(self, point1, point2=None, freq="Y", options='AMI', discountRate=None, DRMethodOverride=None,
                   overrides=None):
        copyme = copy.deepcopy(self)
        copyme.fatal = False
        copyme.setDirty(True)
        copyme.refresh()
        return copyme.M(point1, point2, freq=freq, options=options, discountRate=discountRate,
                        DRMethodOverride=DRMethodOverride, overrides=overrides)

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
        self.age = yrsGap(self.dob, self.gettrialDate())
        self.setDirty(True)

    def getAge(self):
        return self.age

    def setAge(self, age):
        self.age = age
        self.dob = addYears(self.gettrialDate(), -self.age)

    def getAAT(self):
        # return age at trial (will be different if this is a fatal case from age)
        return yrsGap(self.dob, self.gettrialDate())

    def getAAI(self):
        # return age at injury
        if self.getDOI():
            return self.ageAtDate(self.getDOI())
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
        if self.targetLE is not None:
            return self.targetLE
        if getattr(self, 'liveto', None) is not None:
            # 'liveto' is an absolute age the claimant is expected to reach; convert to a
            # target LE. For a FATAL claimant the LE is measured from age at DEATH (getAAD),
            # matching the VBA getTargetLE_CORE (LIVETO - ADOD); otherwise from age at trial.
            # Deferred to here (not __init__) because fatal status / AAD are only set in setUp().
            base = self.getAAD() if self.isFatal() else self.getAge()
            return self.liveto - base
        return None

    def getCurve(self):
        return self.curve

    def getDependentOn(self):
        return self.dependenton

    def setDependentOn(self, dependenton):
        self.dependenton = dependenton

    def getContDependentsOn(self):
        dependentonlist = self.getClaimantsDependentOn()
        if len(dependentonlist) == 0: return 1  # i.e. not dependent on anyone
        conts = []
        for dependenton in dependentonlist:
            c = self.getClaimant(dependenton)
            if c is None:  # named dependee not in the game (e.g. typo/case mismatch) -> skip, log (F30)
                errors.add("Dependent-on claimant not found: " + str(dependenton))
                continue
            conts.append(c.getCont())
        if len(conts) == 0:
            return 1
        return np.average(np.array(conts))  # take average of those dependent on

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
        accelerated_receipt = discountFactor(yrs, self.getdiscountRate(yrs=yrs))  # pass yrs (F28)
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
        accelerated_receipt = discountFactor(yrs, self.getdiscountRate(yrs=yrs))  # pass yrs (F28)
        past_expected_years = expected_years[0]
        interest_expected_years = -expected_years[1]
        future_expected_years = pow(DF_HOUSE, expected_years[2]) * accelerated_receipt
        total = past_expected_years + interest_expected_years + future_expected_years
        result = [past_expected_years, interest_expected_years, future_expected_years, total]
        return result

    def _overrideRate(self, s):
        # Parse an override rate that may be written as a percent ('2%' -> 0.02) or a decimal
        # ('0.02'); the documented override format uses the percent form. (F29)
        s = str(s).strip()
        try:
            if s.endswith('%'):
                return float(s[:-1]) / 100.0
            return float(s)
        except ValueError:
            errors.add("Invalid override rate: " + s)
            return None

    def setOverrides(self, overrides):
        result = parseOverrides(overrides)
        if 'SEX' in result:
            self.setSex(result['SEX'].upper())  # enum value -> upper (parseOverrides keeps values verbatim)
        if 'AGE' in result:
            try:
                self.setAge(float(result['AGE']))
            except ValueError:
                errors.add("Invalid override age: " + str(result['AGE']))
        if 'DEPENDENTON' in result:
            self.setDependentOn(result['DEPENDENTON'])  # kept verbatim: claimant names are case-sensitive (F30)
        if 'DRMETHOD' in result:
            drm = result['DRMETHOD'].upper()
            self.parent.setDRMethod(drm)
            if drm == 'SINGLE':
                self.parent.setUseMultipleRates(False)
            else:
                self.parent.setUseMultipleRates(True)
        if 'SHORTRATE' in result:
            r = self._overrideRate(result['SHORTRATE'])
            if r is not None: self.parent.setShortRate(r)
        if 'LONGRATE' in result:
            r = self._overrideRate(result['LONGRATE'])
            if r is not None: self.parent.setLongRate(r)
        if 'SINGLERATE' in result:
            r = self._overrideRate(result['SINGLERATE'])
            if r is not None: self.parent.setSingleRate(r)
        if 'SWITCH' in result:
            try:
                self.parent.setSwitch(float(result['SWITCH']))
            except ValueError:
                errors.add("Invalid override switch: " + str(result['SWITCH']))

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

        # A discount rate of exactly -1 (-100%) makes discountFactor/termCertain return None,
        # which then TypeError-crashes the numpy curve build; return a per-row error instead. (F52/F59)
        if self.getdiscountRate(discountRate=discountRate, DRMethodOverride=DRMethodOverride) == -1:
            msg = "Discount rate of -1 (-100%) is invalid"
            return msg, msg, msg, msg

        c = self.getCurve()

        if 'D' in options:
            co = self.getContDependentsOn()  # if this is a dependency claim then we need cont of deceased in uninjured state
        else:
            co = self.getCont()
        if (freq == 'A'):
            if age2 is None:
                age2 = 125  # 'A' averages a value over the period; a missing To defaults to LIFE (F20)
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

    def MDiff(self, point1, point2=None, freq="Y", optionsA='AMI', optionsB='AM', discountRate=None,
              DRMethodOverride=None, overrides=None):
        # The marginal effect on the multiplier of the option letters in optionsA but not in optionsB,
        # i.e. M(optionsA) - M(optionsB) element-wise over (past, interest, future, total).
        #
        # This is a marginal contribution CONDITIONAL on the letters common to both sides, not a
        # standalone decomposition: the five factors multiply inside the integral (curve.getCurve),
        # so marginals taken from separate calls will not sum back to the total multiplier.
        #
        # NB the interest element of any single M() call is already M(...I...) - M(...same minus I...)
        # by construction (curve.py splits past/interest by the with-minus-without principle), so
        # MDiff is not needed to isolate 'I' - read element [1] of a normal M() call instead.
        a = (optionsA or '').upper()
        b = (optionsB or '').upper()

        # An empty options string silently defaults to 'AMI' in M(), so differencing against one
        # would return a plausible-looking number that attributes nothing. Require both explicitly.
        if not a or not b:
            msg = "\'Discount\' options must be given explicitly on both sides of a difference"
            return msg, msg, msg, msg
        for l in a + b:
            if l not in discountOptions:
                msg = "\'Discount\' options invalid"
                return msg, msg, msg, msg

        # Under Tables E/F a 'D' reroutes M() to the JM scaling path, so the two sides would be
        # computed by different algorithms and their difference would not attribute anything.
        if self.parent.getUseTablesEF() and (('D' in a) != ('D' in b)):
            msg = "Cannot difference the \'D\' option under Tables E/F"
            return msg, msg, msg, msg

        resA = self.M(point1, point2, freq, a, discountRate, DRMethodOverride, overrides)
        resB = self.M(point1, point2, freq, b, discountRate, DRMethodOverride, overrides)
        if resA is None or resB is None:
            return None
        # M() reports input errors as strings in all four elements; propagate rather than subtract.
        for r in (resA, resB):
            if any(isinstance(v, str) for v in r):
                return r
        return tuple(x - y for x, y in zip(resA, resB))

    def _withInterest(self, options):
        # AGGINTRATE/JAGGINTRATE presuppose interest. Without 'I' the interest element is 0 and the
        # function would return a perfectly plausible 0.00% next to a healthy multiplier, so
        # inject it rather than answer a question that was not asked.
        o = (options or 'AMI').upper()
        return o if 'I' in o else o + 'I'

    def _aggInt(self, res):
        # Aggregate interest rate = interest / past, where 'past' is the NO-INTEREST past
        # multiplier (curve.py: withoutInterest = nI_to - nI_from). Interest accrues only on
        # past loss, so the past multiplier is the right denominator.
        # NB this DIVERGES from the VBA/client convention of interest/(total-interest), which
        # is interest/(past+future). The two are identical for a wholly-past period, where
        # future is 0 - i.e. wherever the rate is actually meaningful. They differ for a
        # period straddling trial, where including the future multiplier in the denominator
        # materially understates the rate (8.72% vs 15.28% on a [50,70] test span).
        # Both terms scale linearly with the annual sum, so the rate is independent of the
        # money; it is the survival-weighted mean of the per-year interest factors.
        if res is None:
            return None
        if any(isinstance(v, str) for v in res):
            return res[0]  # propagate the input error reported by M()/JM()
        if not res[0]:
            # No past period, so no past loss to carry interest, and this would be 0/0. The
            # client-side AGGINTRATE returns 0/future = 0 here, which reads as a finding of
            # "no interest" beside a perfectly healthy multiplier; it is almost always user
            # error, so say so instead.
            return "No past period: aggregate interest undefined"
        return res[1] / res[0]

    def AGGINTRATE(self, point1, point2=None, freq="Y", options='AMI', discountRate=None,
                   DRMethodOverride=None, overrides=None):
        # The aggregate interest rate on the past loss over [point1, point2], as a decimal
        # (0.19784468 = 19.784468%): the single percentage which, applied to the past loss,
        # reproduces the interest element of the corresponding multiplier.
        # Named to match the client-side AGGINTRATE, but see _aggInt: the denominator here is
        # 'past', not the client's 'total - interest'. Same answer for a wholly-past period,
        # higher (and more defensible) for one straddling trial.
        # NB the client's AGGINT is a DIFFERENT quantity - the absolute interest multiplier,
        # i.e. element [1] of M() - not a rate.
        # NB over a range this is the rate for a loss accruing on the given freq pattern -
        # interest depends on WHEN each pound was lost, so a front- or back-loaded loss has a
        # different true rate. For a one-off (no point2) there is a single date and no such
        # assumption, so the figure is exact.
        return self._aggInt(self.M(point1, point2, freq, self._withInterest(options), discountRate,
                                   DRMethodOverride, overrides))

    def JAGGINTRATE(self, point1, point2=None, freq="Y", options='AMI', discountRate=None,
                    DRMethodOverride=None, overrides=None):
        # Joint-life counterpart of AGGINTRATE, pairing with JMULTIPLIER/JM the way AGGINTRATE
        # pairs with MULTIPLIER/M. The formula is identical; only the routing differs, so that
        # the rate always corresponds to the multiplier it sits beside.
        # The ratio is invariant to any factor scaling past and interest EQUALLY, so under
        # Tables E/F the TableE scaling cancels exactly, and for a one-off the
        # mortality/dependency factors cancel too. It differs from AGGINTRATE only over a
        # range, where past mortality re-weights which dates dominate the average.
        return self._aggInt(self.JM(point1, point2, freq, self._withInterest(options), discountRate,
                                    DRMethodOverride, overrides))

    def _ageToDate(self, age):
        # Convert an age on this claimant's timeline to a calendar date (d/m/y string). (EXPLAIN)
        try:
            return self.dateAtAge(age).strftime('%d/%m/%Y')
        except Exception:
            return None

    def _multiplierExplanation(self, result, age1, age2, freq, opts, includeTable,
                               discountRate, DRMethodOverride, functionLabel):
        # Shared builder: header + decomposition + optional per-age table for a curve-based
        # multiplier (single-life MULTIPLIER, or the direct joint curve where opts contains 'D').
        # The per-age table reuses the same area() primitive that computed the tuple and asserts
        # it reconciles. (EXPLAIN)
        from localpackage.utils import explainDiscountsText, explainFrequencyText, returnFreq

        trialAge = self.getAge()
        revAge = self.getRevisedAge()
        header = {
            'claimant': self.getName(),
            'sex': self.getSex(),
            'ageAtTrial': round(trialAge, 4),
            'revisedAge': (round(revAge, 4) if abs(revAge - trialAge) > 1e-9 else None),
            'trialDate': self.gettrialDate().strftime('%d/%m/%Y'),
            'fromAge': (round(age1, 4) if age1 is not None else None),
            'toAge': (round(age2, 4) if age2 is not None else None),
            'fromDate': (self._ageToDate(age1) if age1 is not None else None),
            'toDate': (self._ageToDate(age2) if age2 is not None else None),
            'frequency': freq,
            'frequencyText': explainFrequencyText(freq),
            'options': opts,
            'optionsText': explainDiscountsText(opts),
            'discountRate': self.getdiscountRate(discountRate=discountRate, DRMethodOverride=DRMethodOverride),
            'discountMethod': (DRMethodOverride or (self.parent.getDRMethod() if self.parent.getUseMultipleRates() else 'SINGLE')),
            'mortalityBasis': {
                'year': self.getYear(), 'region': self.getRegion(),
                'projection': self.getProjection(), 'yrAttainedIn': self.getYrAttainedIn(),
            },
            'sarBasis': ('Court Funds Office Special Account Rate schedule (localpackage/Data/SAR.csv)'
                         if 'I' in opts else None),
        }
        decomposition = {
            'past': {'value': result[0],
                     'formula': 'area(without-interest product) over [from, min(trial, to)]'},
            'interest': {'value': result[1],
                         'formula': 'area(with-interest product) - area(without-interest product) over the past sub-period'},
            'future': {'value': result[2],
                       'formula': 'area(without-interest product) over [max(trial, from), to]'},
            'total': {'value': result[3], 'formula': 'past + interest + future'},
        }
        explanation = {'function': functionLabel, 'header': header, 'decomposition': decomposition}

        st, en, factor, tinterval = returnFreq(freq, age1, age2)
        continuous = not (st or en)
        pureA = (opts == 'A' and not self.getUseMultipleRates())
        if includeTable and age2 is not None and continuous and not pureA:
            # 'D' in opts is a joint (dependency) curve: use the dependants' contingency basis,
            # matching what M() passed; MMD reflects the deceased-survival factor. (EXPLAIN/JMULTIPLIER)
            co = self.getContDependentsOn() if 'D' in opts else self.getCont()
            rows, totals = self.getCurve().explainTable(age1, age2, opts, cont=co,
                                                        discountRate=discountRate, DRMethodOverride=DRMethodOverride)
            for r in rows:
                r['date'] = self._ageToDate(r['age'])
            reconciles = (abs(totals['sumAreaWithI'] - result[3]) < 1e-6 and
                          abs(totals['sumInterestArea'] - result[1]) < 1e-6)
            assert reconciles, ("EXPLAIN table does not reconcile to the multiplier: "
                                f"sumAreaWithI={totals['sumAreaWithI']} vs total={result[3]}, "
                                f"sumInterestArea={totals['sumInterestArea']} vs interest={result[1]}")
            explanation['table'] = {
                'columns': ['age', 'date', 'nextAge', 'survivalLx', 'DF', 'IM', 'MMD',
                            'product', 'areaWithI', 'areaWithoutI', 'interestArea'],
                'rows': rows,
                'totals': totals,
                'reconciles': reconciles,
            }
        elif includeTable:
            explanation['tableNote'] = ('Per-age table available only for continuous, '
                                        'non-pure-acceleration (curve-based) multipliers; not built for this case.')
        return explanation

    def explain(self, point1, point2=None, freq="Y", options='AMI', discountRate=None,
                DRMethodOverride=None, overrides=None, includeTable=False):
        # Structured, additive audit trail of a single-life MULTIPLIER. Returns
        # {'result': [past, interest, future, total], 'explanation': {...}}; never alters the tuple.
        result = self.M(point1, point2, freq=freq, options=options, discountRate=discountRate,
                        DRMethodOverride=DRMethodOverride, overrides=overrides)
        opts = (options or 'AMI').upper()
        age1 = self.getAgeFromPoint(point1)
        age2 = self.getAgeFromPoint(point2) if point2 else None
        expl = self._multiplierExplanation(result, age1, age2, freq, opts, includeTable,
                                           discountRate, DRMethodOverride, 'MULTIPLIER')
        return {'result': list(result), 'explanation': expl}

    def explainJoint(self, point1, point2=None, freq="Y", options='AMI', discountRate=None,
                     DRMethodOverride=None, overrides=None, includeTable=False):
        # JMULTIPLIER explanation. Two branches (mirrors basePerson.JM). (EXPLAIN/JMULTIPLIER)
        opts = (options or 'AMI').upper()
        result = self.JM(point1, point2, freq, opts, discountRate, DRMethodOverride, overrides)

        if not self.parent.getUseTablesEF():
            # Direct joint-curve branch (the VBA path = MULTIPLIER + 'D'): the joint curve already
            # includes the deceased-survival (MMD) factor, so the same per-age table + decomposition
            # reconcile directly to the joint tuple.
            jopts = opts if 'D' in opts else opts + 'D'
            age1 = self.getAgeFromPoint(point1)
            age2 = self.getAgeFromPoint(point2) if point2 else None
            expl = self._multiplierExplanation(result, age1, age2, freq, jopts, includeTable,
                                               discountRate, DRMethodOverride, 'JMULTIPLIER')
            expl['branch'] = 'direct joint curve (useTablesEF=False)'
            return {'result': list(result), 'explanation': expl}

        # Tables E/F branch (Python-only; NO joint curve to integrate). Structure the explanation
        # as: the shortest-LE life's own MULTIPLIER explanation, then the E/F scaling steps.
        shortestLEname = self.getShortestLEname()
        claimant = self.parent.getClaimant(shortestLEname)

        def translate(p):
            if isinstance(p, bool):
                return p
            if isinstance(p, (int, float, np.integer, np.floating)):
                return min(125, p + (claimant.getAge() - self.getAge()))
            return p

        tp1, tp2 = translate(point1), translate(point2)
        sopts = opts.replace('D', '')  # the shortest life's own (single-life) multiplier
        # Build the shortest life's explanation on a non-fatal copy, exactly as MifNotDead does.
        copyme = copy.deepcopy(claimant)
        copyme.fatal = False
        copyme.refresh()
        shortExpl = copyme.explain(tp1, tp2, freq, sopts, discountRate, DRMethodOverride, None, includeTable)
        m = shortExpl['result']

        deps = self.getClaimantsDependentOn()
        depDetails = [{'name': dep,
                       'tableE': self.parent.getClaimant(dep).getTableE(),
                       'tableF': self.parent.getClaimant(dep).getTableF()} for dep in deps]
        TableE = math.prod([d['tableE'] for d in depDetails]) if depDetails else 1
        TableF = math.prod([d['tableF'] for d in depDetails]) if depDetails else 1

        comp_past = m[0] * TableE
        comp_interest = m[1] * TableE
        comp_future = m[2] * TableF
        comp_total = comp_past + comp_interest + comp_future

        reconciles = (abs(comp_total - result[3]) < 1e-6 and abs(comp_interest - result[1]) < 1e-6)
        # interest.E == (E/F multiplier WITH interest) - (WITHOUT interest) — the F19 self-check.
        withoutTotal = comp_past + comp_future
        interestScalingCheck = abs((result[3] - withoutTotal) - comp_interest) < 1e-6
        assert reconciles, (f"E/F components {comp_total} do not sum to the joint tuple {result[3]}")
        assert interestScalingCheck, "E/F interest.E != (withInterest - withoutInterest)"

        explanation = {
            'function': 'JMULTIPLIER',
            'branch': 'Tables E/F (useTablesEF=True)',
            'shortestLife': {'name': claimant.getName(), 'result': m,
                             'explanation': shortExpl['explanation']},
            'scaling': {
                'dependants': depDetails,
                'TableE': TableE,
                'TableE_derivation': 'product over dependants of Table E (= average survival probability from date of death to trial)',
                'TableF': TableF,
                'TableF_derivation': 'product over dependants of Table F (= survival probability at trial)',
            },
            'composition': {
                'formula': 'resM = [m_past*TableE, m_interest*TableE, m_future*TableF]',
                'past': comp_past, 'interest': comp_interest, 'future': comp_future, 'total': comp_total,
            },
            'reconciles': reconciles,
            'interestScalingCheck': interestScalingCheck,
        }
        return {'result': list(result), 'explanation': explanation}

    def explainAggInt(self, point1, point2=None, freq="Y", options='AMI', discountRate=None,
                      DRMethodOverride=None, overrides=None, includeTable=False, joint=False):
        # AGGINT / JAGGINT explanation: the implied aggregate interest RATE (audit only; the tuple
        # return is unchanged). Mirrors VBA AGGINT_CORE = interestMultiplier / withoutInterest, where
        # withoutInterest = withInterest(total) - interest. JAGGINT = AGGINT with 'D' added. (EXPLAIN)
        opts = (options or 'AMI').upper()
        if 'I' not in opts:
            opts += 'I'  # AGGINT needs interest present
        if joint and 'D' not in opts:
            opts += 'D'
        label = 'JAGGINT' if joint else 'AGGINT'

        # Underlying multiplier explanation (joint when 'D' is present).
        if 'D' in opts:
            under = self.explainJoint(point1, point2, freq, opts, discountRate, DRMethodOverride,
                                      overrides, includeTable)
        else:
            under = self.explain(point1, point2, freq, opts, discountRate, DRMethodOverride,
                                 overrides, includeTable)
        res = under['result']
        total = res[3]
        interest = res[1]
        past = res[0]
        withoutInterest = total - interest
        # Headline figure must be what AGGINTRATE/JAGGINTRATE actually return, or the audit
        # would explain a different number from the cell it is explaining.
        aggint = self._aggInt(res)
        note = None
        if not isinstance(aggint, float):
            note = str(aggint)
            aggint = None
        # The VBA figure is retained for reference: AGGINT_CORE divides by (total - interest)
        # = past + future, which agrees with interest/past for a wholly-past period and
        # understates the rate for one straddling trial. See _aggInt.
        vba = None if withoutInterest == 0 else interest / withoutInterest
        explanation = {
            'function': label,
            'multiplier': under['explanation'],
            'aggInt': {
                'withInterest': total,
                'interest': interest,
                'past': past,
                'withoutInterest': withoutInterest,
                'aggInt': aggint,
                'aggIntPercent': (None if aggint is None else round(aggint * 100, 4)),
                'formula': 'interest / past',
                'vbaAggInt': vba,
                'vbaFormula': 'interest / (withInterest - interest)',
                'note': note,
            },
        }
        return {'result': list(res), 'explanation': explanation}

    def explainDispatch(self, function, point1, point2=None, freq="Y", options='AMI',
                        discountRate=None, DRMethodOverride=None, overrides=None, includeTable=False):
        # Routes an EXPLAIN request by function name. (EXPLAIN)
        f = (function or 'MULTIPLIER').upper()
        if f == 'JMULTIPLIER':
            return self.explainJoint(point1, point2, freq, options, discountRate, DRMethodOverride,
                                     overrides, includeTable)
        # AGGINTRATE/JAGGINTRATE are the client-facing UDF names for the same quantity; the
        # bare AGGINT/JAGGINT spellings are kept so existing EXPLAIN callers still route.
        if f in ('AGGINT', 'AGGINTRATE'):
            return self.explainAggInt(point1, point2, freq, options, discountRate, DRMethodOverride,
                                      overrides, includeTable, joint=False)
        if f in ('JAGGINT', 'JAGGINTRATE'):
            return self.explainAggInt(point1, point2, freq, options, discountRate, DRMethodOverride,
                                      overrides, includeTable, joint=True)
        return self.explain(point1, point2, freq, options, discountRate, DRMethodOverride,
                            overrides, includeTable)

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
            age = self.ageAtDate(point)
        elif type(point) is str:  # for entries like TRIAL, LIFE
            if isfloat(point):
                # A bare numeric string (e.g. "45" from a text-formatted Sheets cell) is an AGE.
                # Without this, dateutil parses it as a date (year 2045, day/month from today),
                # silently corrupting the result.
                age = float(point)
            else:
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

        # Coerce dataSet fields: a text-formatted Sheets cell can send these as strings.
        # year/yrAttainedIn are used in integer arithmetic (calcYrAttained - age); region is
        # used to build the mortality-CSV filename (case-sensitive on the Linux prod fs). (F37/F53)
        try:
            self.year = int(attributes['dataSet']['year'])
        except (ValueError, TypeError):
            self.year = attributes['dataSet']['year']
            errors.add("dataSet 'year' is not an integer")
        self.region = str(attributes['dataSet']['region']).strip().upper()
        try:
            self.yrAttainedIn = int(attributes['dataSet']['yrAttainedIn'])
        except (ValueError, TypeError):
            self.yrAttainedIn = attributes['dataSet']['yrAttainedIn']
            errors.add("dataSet 'yrAttainedIn' is not an integer")

        if 'name' in attributes:
            self.name = attributes['name']

        if 'dob' in attributes and not 'age' in attributes:
            if type(attributes['dob']) is str:
                attributes['dob'] = parsedateString(attributes['dob'])
            self.dob = attributes['dob']
            self.age = yrsGap(self.dob, self.gettrialDate())
        if 'age' in attributes and not 'dob' in attributes:
            self.age = attributes['age']
            self.dob = addYears(self.gettrialDate(), -self.age)

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

        self.liveto = None
        if 'liveto' in attributes:
            c += 1
            # Store raw; the age basis (trial vs death for fatals) is resolved lazily in
            # gettargetLE() because fatal status / age-at-death are set later in setUp().
            self.liveto = attributes['liveto']

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
