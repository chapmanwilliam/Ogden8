import numpy as np
import matplotlib.pyplot as plt
import os
from localpackage.utils import returnFreq, discountFactor, termCertain
from localpackage.calcs import calcs


class curve():

    def __init__(self, parent=None):
        self.parent = parent
        self._LxNoI = self._Lx = None
        self.curveOptions = {}  # dictionary to store different options [discountRate][options] with each entry  [0.0025]['AM'] or 'AMD' etc. Should be 2^4 = 16 options for each discount rate
        self.dirty = True
        self.calc = calcs()

    def getPlot(self, result, fromAge, toAge, freq, cont, options):
        title = self.getTitle(result, fromAge, toAge, freq, cont, options)
        st, en, factor, timeInterval = returnFreq(freq)

        d = []
        Mlegend = ''
        if 'M' in options: d.append('Mortality')
        if 'A' in options: d.append('Accelerated receipt')
        if not cont == 1: d.append('Cont (' + '{:.2f}'.format(cont) + ")")
        if len(d) > 0: Mlegend += 'Disc. for ' + ' and '.join(d)
        if 'I' in options: Mlegend += ', with interest'

        lowestAAD = 125

        plt.plot(self.Rng, self._Lx, label=Mlegend)
        for name in self.getdependentson():
            c = self.getClaimant(name)
            if c:
                shift = self.getAge() - c.age  # the age gap
                aad = c.getAAD() + shift
                if aad < lowestAAD: lowestAAD = aad
                plt.axvline(aad, linestyle='dashed', color='black',
                            label='death ' + c.name)  # age at death pf the deceased

        plt.axvline(self.getAAT(), linestyle='dashed', color='green', label='trial')  # age at trial
        # limits
        leftX = min(lowestAAD, self.getAAT(),
                    fromAge) - 1  # lowest X is lowers of AAD, AAT or fromAge, less one for space
        plt.xlim(leftX, 125)
        Lx = self._Lx[self.Rng >= leftX]  # y values in the range
        plt.ylim(0, max(Lx) + 1)
        # Area under the curve
        if toAge:
            if st or en:  # this is discrete
                if st:
                    ages = np.arange(start=fromAge, stop=toAge, step=timeInterval)
                if en:
                    ages = np.arange(start=fromAge + timeInterval, stop=toAge, step=timeInterval)
                y = np.array([np.interp(age, self.Rng, self._Lx) for age in ages])
                plt.vlines(ages, 0, y, linestyles='dashed', color='red')
            else:  # this is continuous
                ages = np.arange(start=fromAge, stop=toAge, step=0.1)
                y = np.array([np.interp(age, self.Rng, self._Lx) for age in ages])
                plt.fill_between(ages, 0, y, color='red')
        else:  # one off
            plt.vlines(fromAge, 0, np.interp(fromAge, self.Rng, self._Lx), linestyles='dashed', color='red')
        # Labels
        plt.xlabel('Age')
        plt.ylabel('Multiplier')
        plt.title(title)
        plt.legend(loc='upper right', prop={'size': 6})
        if 'D' in options:
            plt.figtext(1, 0.03, 'Dependent: ' + self.getdataSet().getdataTitle(), ha='right', fontsize=6)
            for name in self.getdependentson():
                c = self.getClaimant(name)
                plt.figtext(1, 0.01, 'Dependent on: ' + name + " " + c.getdataSet().getdataTitle(), ha='right',
                            fontsize=6)
        else:
            plt.figtext(1, 0.01, self.getdataSet().getdataTitle(), ha='right', fontsize=6)
        plt.show()

    def getHeading1(self, result, fromAge, toAge=None, freq="Y", cont=1, options='AMI'):
        if 'D' in options:
            s = 'Joint Multiplier '
        else:
            s = " Multiplier "
        # The range
        if toAge:
            s += "from " + '{:.1f}'.format(fromAge) + " to " + '{:.1f}'.format(toAge)
            if not freq == "Y": s += ", " + freq
        else:
            s += "at " + '{:.1f}'.format(fromAge)
        s += " = " + '{:.2f}'.format(result[3])
        return s

    def getHeading2(self):
        str = self.getName().capitalize()
        str += " (" + self.getSex().lower() + ")"
        if self.isFatal(): str += " (deceased)"
        str += ', age ' + '{:.1f}'.format(self.getAge()) + ' at trial'
        return str

    def getTitle(self, result, fromAge, toAge=None, freq="Y", cont=1, options='AMI'):
        str = self.getHeading1(result, fromAge, toAge, freq, cont, options)
        str += os.linesep + ", "
        str += self.getHeading2()
        return str

    def getdataSet(self):
        return self.parent.getdataSet()

    def isFatal(self):
        return self.parent.isFatal()

    def getSAR(self):
        return self.parent.getSAR()

    def getUseMultipleRates(self):
        return self.parent.getUseMultipleRates()

    def getdiscountRate(self, yrs=0):
        return self.parent.getdiscountRate(yrs)

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def getAge(self):
        return self.parent.getAge()

    def getName(self):
        return self.parent.getName()

    def getAAT(self):
        return self.parent.getAAT()

    def getlowestAAI(self):
        lowestAAI = 125
        for c in self.getClaimants().values():
            if c.getAAI():
                if c.getAAI() < lowestAAI: lowestAAI = c.getAAI()
        return lowestAAI

    def getAAI(self, name):
        return self.parent.parent.getAAI(name)

    def getAAD(self, name):
        return self.parent.parent.getAAD(name)

    def getSex(self):
        return self.parent.getSex()

    def getdependentson(self):
        return self.parent.getClaimantsDependentOn()

    def getClaimant(self, name):
        return self.parent.getClaimant(name)

    def getClaimants(self):
        return self.parent.getClaimants()

    def M(self, fromAge, toAge=None, freq="Y", cont=1, options='AMI', discountRate=None):
        # get the right curve

        self.refresh()

        self._LxNoI, self._Lx, self.Rng = self.getCurve(options, cont, discountRate)

        calc1 = calcs()
        result = self.Multiplier(fromAge, toAge, options, freq, cont, calc1, discountRate)

        self.calc.clear()
        self.calc.addText(self.getHeading1(result, fromAge, toAge, freq, cont, options))
        self.calc.addText(self.getHeading2())
        self.calc.inDent()
        self.calc.addCalcs(calc1)
        self.calc.outDent()

        return result

    def Multiplier(self, fromAge, toAge=None, options=None, freq="Y", cont=1, calc=None, discountRate=None):
        if discountRate==None:
            discountRate=self.getdiscountRate()
        st, en, factor, timeInterval = returnFreq(freq, fromAge, toAge)

        if toAge:
            if st or en:  # this is not continuous
                if st:
                    ages = np.arange(start=fromAge, stop=toAge, step=timeInterval)
                if en:
                    ages = np.arange(start=fromAge + timeInterval, stop=toAge, step=timeInterval)
                result = np.sum(
                    np.array([self.Multiplier(fromAge=age, options=options, cont=cont, calc=calc) for age in ages]),
                    axis=0).tolist()
            else:  # this is continuous
                interest, past = self.cont(fromAge, min(self.getAge(), toAge), options)
                if options == 'A' and not self.getUseMultipleRates():
                    futureinterest = 0
                    yrs1 = max(self.getAge(), fromAge) - self.getAge()
                    yrs2 = toAge - self.getAge()
                    TC1 = termCertain(yrs1, self.getdiscountRate(yrs1))
                    TC2 = termCertain(yrs2, self.getdiscountRate(yrs2))
                    future = TC2 - TC1
                    interest *= factor
                    past *= factor
                    future *= factor
                    result = past, interest, future, past + interest + future
                else:
                    futureinterest, future = self.cont(max(self.getAge(), fromAge), toAge, options)
                    interest *= factor
                    past *= factor
                    future *= factor
                    result = past, interest, future, past + interest + future
        else:
            result = list(self.Lx(fromAge, options, discountRate))

        if calc:
            calc.addText(self.getBreakdown(fromAge, toAge, factor, result))
        return result

    def getBreakdown(self, fromAge, toAge, factor, result):
        s = []
        if result[0] > 0: s.append('{:.2f}'.format(result[0]) + ' (past)')
        if result[1] > 0: s.append('{:.2f}'.format(result[1]) + ' (interest)')
        if result[2] > 0: s.append('{:.2f}'.format(result[2]) + ' (future)')
        total = '{:.2f}'.format(result[3])
        s = ' + '.join(s[:3]) + ' = ' + total
        if not (toAge):
            s = 'At age ' + '{:.2f}'.format(fromAge) + ' : ' + s
        else:
            s = 'Age ' + '{:.2f}'.format(fromAge) + ' to {:.2f}'.format(toAge) + ' : ' + s
        return s

    def cont(self, fromAge, toAge, options):
        if fromAge < toAge:
            Tx1I, Tx1 = self.Tx(fromAge, options)
            Tx2I, Tx2 = self.Tx(toAge, options)
            interest = Tx2I - Tx1I
            withoutInterest = Tx2 - Tx1
            return interest, withoutInterest
        return 0, 0

    def Tx(self, age, options):
        if age < 0: return 0
        a = self.Rng[self.Rng <= age]
        if len(a) == 0: return 0, 0
        #        if age>a[-1]: age=a[-1]
        #        if age<a[0]:age=a[0]
        Lx = self._Lx[self.Rng <= age]
        LnoI = self._LxNoI[self.Rng <= age]
        y = np.trapz(Lx, a)  # with interest
        ynoI = np.trapz(LnoI, a)  # withoutinterest

        # additional chunk
        lowerL = Lx[-1]
        higherLpast, higherLinterest, higherLfuture, higherLtotal = self.Lx(age, options)
        yrsBetween = age - a[-1]
        additionalChunk = 0.5 * (lowerL + higherLtotal) * yrsBetween  # with interest

        # additional chunk
        lowerL = LnoI[-1]
        higherLpast, higherLinterest, higherLfuture, higherLtotal = self.Lx(age, options)
        yrsBetween = age - a[-1]
        additionalChunknoI = 0.5 * (lowerL + higherLpast + higherLfuture) * yrsBetween  # without interest

        withInterest = y + additionalChunk
        withoutInterest = ynoI + additionalChunknoI
        interest = withInterest - withoutInterest

        return interest, withoutInterest

    def Lx(self, age, options, discountRate=None):
        if(discountRate==None):
            discountRate = self.getdiscountRate()

        y = np.interp(age, self.Rng, self._Lx)
        ynoI = np.interp(age, self.Rng, self._LxNoI)
        if age < self.getAge():  # past
            past = ynoI
            interest = y - ynoI
            future = 0
        else:  # future
            past = 0
            interest = 0
            if options == "A":  # just acceleration
                yrs = age - self.getAge()
                future = discountFactor(yrs, self.getdiscountRate(yrs))
            else:
                future = y
        return past, interest, future, past + interest + future

    def setDirty(self, value=True):
        self.dirty = value

    def refresh(self):
        if self.dirty:
            self.curveOptions.clear()
            self.dirty = False

    def getCurve(self, options, cont, discountRate=None):
        # Returns the curve for past and future applying all relevant discounts

        if(discountRate==None):
            discountRate = self.getdiscountRate()

        # First check if we already have calculated this one for a given SINGLE discount rate
        if not self.getUseMultipleRates():
            if discountRate in self.curveOptions:
                if options in self.curveOptions[discountRate]: #options is a string like 'AMID' and self.curveOptions is a dictionary
                    result = self.curveOptions[discountRate][options]
                    return result['LxNoI'], result['Lx'], result['Rng']
                else:
                    self.curveOptions[discountRate][options] = {}
            else:
                self.curveOptions[discountRate] = {}

        def expand_past_range():
            # makes the past more granular
            rp = self.getSAR().Rng  # get the range for the change in interest
            yrrp = np.arange(rp[0], rp[-1], 1)  # and for every year
            res = np.concatenate((rp, yrrp))  # join them
            return np.sort(res, axis=None)  # sort them

        age = self.getAge()

        rp = expand_past_range()

        rf = self.getdataSet().Rng[self.getdataSet().Rng >= age]  # range in the future
        Rng = np.concatenate((rp, rf))  # range past and future

        # defaults
        _disc = np.full((Rng.size), 1)
        _cont = np.full((Rng.size), 1)
        _Lx = np.full((Rng.size), 1)
        _interest = np.full(Rng.size, 1)
        _deceased = np.full(Rng.size, 1)

        # discount factor
        if 'A' in options:
            _discp = np.full((rp.size), 1)  # 1 in the past
            _discf = np.array([discountFactor(a - age, self.getdiscountRate(a-age)) for a in rf])
            _disc = np.concatenate((_discp, _discf))
        # mortality
        if 'M' in options:
            if self.isFatal():
                _Lxp = self.getdataSet().transformLx(rp)  # probability of death in the past
                _Lxf = self.getdataSet().transformLx(rf)  # probability of death
            else:
                _Lxp = np.full((rp.size), 1)  # probability 1 in the past
                _Lxf = self.getdataSet()._Lx  # probability of death in the future
            _Lx = np.concatenate((_Lxp, _Lxf))
        # interest
        if 'I' in options:
            _interestp = self.getSAR().transformLx(rp)
            _interestf = np.full((rf.size), 1)
            _interest = np.concatenate((_interestp, _interestf))
        # cont
        if 'C' in options:
            _contp = np.full((rp.size), 1)
            _contf = np.full((rf.size), cont)
            _cont = np.concatenate((_contp, _contf))
        # deceased
        if 'D' in options:
            namesdeceased = self.getdependentson()
            for name in namesdeceased:
                deceased = self.getClaimant(name)
                if deceased:
                    shift = self.getAge() - deceased.age  # the age gap
                    _deceased = np.multiply(_deceased, deceased.getdataSet().transformLx(Rng, shift))

        # multiply together _disc, _Lx, _interest, _cont, _deceased
        A = np.stack((_disc, _Lx, _deceased, _cont))  # without interest
        B = np.stack((_disc, _Lx, _interest, _deceased, _cont))  # with interest

        LxNoI = np.prod(A, axis=0)
        Lx = np.prod(B, axis=0)

        result = {'LxNoI': LxNoI, 'Lx': Lx, 'Rng': Rng}
        if not self.getUseMultipleRates():
            self.curveOptions[discountRate][options]=result

        return LxNoI, Lx, Rng
