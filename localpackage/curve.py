import numpy as np
import matplotlib.pyplot as plt
import os
from localpackage.utils import returnFreq, discountFactor, termCertain
from localpackage.calcs import calcs
import json

class curve():

    def __init__(self, parent=None):
        self.parent = parent #parent is baseperson
        self._LxNoI = self._Lx = None
        self.curveOptions = {}  # dictionary to store hashes of results
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

    def getdiscountRate(self, yrs=0, discountRate=None, DRMethodOverride=None):
        return self.parent.getdiscountRate(yrs=yrs, discountRate=discountRate, DRMethodOverride=DRMethodOverride)

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def getAge(self):
        return self.parent.getAge()

    def getName(self):
        return self.parent.getName()

    def getRevisedAge(self):
        return self.parent.getRevisedAge()
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

    def getDependeeContingencyStartAge(self):
        # THIS claimant's age at the point the dependency contingency starts running, i.e. at
        # the deceased's date of death. Returned on the claimant's own age axis, because that
        # is what Rng is measured in.
        #
        # None when there is nobody to take it from: no dependees, a dependee who is still
        # alive (a dependency on a living person is not counterfactual, so nothing bites in
        # the past), or a dependee with no date of death recorded.
        #
        # With several fatal dependees the earliest death is used. getContDependentsOn already
        # averages their contingencies into the single `cont` passed here, so there is only one
        # figure to place; starting it at the earliest death is the generalisation that matches
        # the one-dependee case exactly. The Excel add-in models a single dependee.
        ages = []
        for name in self.getdependentson():
            deceased = self.getClaimant(name)
            if deceased is None or not deceased.isFatal():
                continue
            dod = deceased.getDOD()
            if dod is None:
                continue
            ages.append(self.parent.ageAtDate(dod))
        return min(ages) if ages else None

    def getClaimant(self, name):
        return self.parent.getClaimant(name)

    def getClaimants(self):
        return self.parent.getClaimants()

    def M(self, fromAge, toAge=None, freq="Y", cont=1, options='AMI', discountRate=None, DRMethodOverride=None):
        # get the right curve

        self._LxNoI, self._Lx, self.Rng = self.getCurve(options=options, cont=cont, discountRate=discountRate, DRMethodOverride=DRMethodOverride)

        calc1 = calcs()
        result = self.Multiplier(fromAge, toAge, options, freq, cont, calc1, discountRate=discountRate, DRMethodOverride=DRMethodOverride)

        self.calc.clear()
        self.calc.addText(self.getHeading1(result, fromAge, toAge, freq, cont, options))
        self.calc.addText(self.getHeading2())
        self.calc.inDent()
        self.calc.addCalcs(calc1)
        self.calc.outDent()

        return result

    def Multiplier(self, fromAge, toAge=None, options=None, freq="Y", cont=1, calc=None, discountRate=None, DRMethodOverride=None):

        st, en, factor, timeInterval = returnFreq(freq, fromAge, toAge)

        if toAge:
            if st or en:  # this is not continuous
                # Match the VBA oracle (cCurve.sumWithFixedStep: advance start by one interval
                # for arrears, then loop `x <= endAge`), which INCLUDES the instalment due at
                # toAge. np.arange excludes its stop, so extend the stop by half an interval to
                # capture the toAge payment for exact-multiple spans (previously dropped). (F33)
                if st:
                    ages = np.arange(start=fromAge, stop=toAge + timeInterval / 2, step=timeInterval)
                if en:
                    ages = np.arange(start=fromAge + timeInterval, stop=toAge + timeInterval / 2, step=timeInterval)
                if len(ages) == 0:
                    # span shorter than the interval -> no payments; np.sum of an empty array
                    # collapses to a scalar and getBreakdown then subscripts it (crash). (F23)
                    result = [0.0, 0.0, 0.0, 0.0]
                else:
                    result = np.sum(
                        np.array([self.Multiplier(fromAge=age, options=options, cont=cont, calc=calc, discountRate=discountRate, DRMethodOverride=DRMethodOverride) for age in ages]),
                        axis=0).tolist()
            else:  # this is continuous
                interest, past = self.cont(fromAge, min(self.getAge(), toAge), options)
                if options == 'A' and not self.getUseMultipleRates():
                    futureinterest = 0
                    yrs1 = max(self.getAge(), fromAge) - self.getAge()
                    # Clamp at trial age: for a wholly-past span (toAge < age at trial) an
                    # unclamped yrs2 is negative and termCertain returns a negative "future"
                    # that corrupts the (correct) past figure. (F32)
                    yrs2 = max(self.getAge(), toAge) - self.getAge()
                    TC1 = termCertain(yrs1, self.getdiscountRate(yrs=yrs1, discountRate=discountRate, DRMethodOverride=DRMethodOverride))
                    TC2 = termCertain(yrs2, self.getdiscountRate(yrs=yrs2, discountRate=discountRate, DRMethodOverride=DRMethodOverride))
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
            result = list(self.Lx(fromAge, options=options, discountRate=discountRate, DRMethodOverride=DRMethodOverride))

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

    def _integralFromStart(self, values, age):
        # The single integration primitive. Trapezoidally integrates `values` over the shared
        # Rng from the start of the range up to `age`, closing off the final partial segment by
        # linear interpolation at the exact `age`. Replaces the old Tx() and its duplicated
        # "additional chunk" code (the F5/F7 fragility site) with one place that does the work.
        mask = self.Rng <= age
        x = self.Rng[mask]
        if len(x) == 0:
            return 0.0
        v = values[mask]
        return np.trapz(v, x) + 0.5 * (v[-1] + np.interp(age, self.Rng, values)) * (age - x[-1])

    def area(self, values, fromAge, toAge):
        # Trapezoidal integral of `values` over [fromAge, toAge] on the shared Rng, with
        # interpolated partial segments at both bounds (telescoped from the cumulative primitive).
        if fromAge >= toAge:
            return 0.0
        return self._integralFromStart(values, toAge) - self._integralFromStart(values, fromAge)

    def cont(self, fromAge, toAge, options, discountRate=None, DRMethodOverride=None):
        # VBA principle: interest = (multiplier WITH interest) - (multiplier WITHOUT interest),
        # integrated over the same span. _Lx carries the interest factor (=1 in the future, so
        # interest accrues only in the past); _LxNoI is the same curve without it.
        # Grouping is preserved from the legacy Tx-difference so results are byte-for-byte identical:
        #   interest        = (I_Lx(to) - I_NoI(to)) - (I_Lx(from) - I_NoI(from))
        #   withoutInterest = I_NoI(to) - I_NoI(from)      [= area(_LxNoI, from, to)]
        if fromAge < toAge:
            wI_to = self._integralFromStart(self._Lx, toAge)
            wI_from = self._integralFromStart(self._Lx, fromAge)
            nI_to = self._integralFromStart(self._LxNoI, toAge)
            nI_from = self._integralFromStart(self._LxNoI, fromAge)
            interest = (wI_to - nI_to) - (wI_from - nI_from)
            withoutInterest = nI_to - nI_from
            return interest, withoutInterest
        return 0, 0

    def Lx(self, age, options, discountRate=None, DRMethodOverride=None):

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
                future = discountFactor(yrs, self.getdiscountRate(yrs=yrs,discountRate=discountRate,DRMethodOverride=DRMethodOverride))
            else:
                future = y
        return past, interest, future, past + interest + future

    def refresh(self):
        self.curveOptions.clear()

    def getMultipleRates(self):
        return self.parent.getMultipleRates()

    def getRegion(self):
        return self.parent.getRegion()

    def getYear(self):
        return self.parent.getYear()

    def getProjection(self):
        return self.parent.getProjection()

    def getAutoYrAttained(self):
        return self.parent.getAutoYrAttained()

    def getCurve(self, options, cont, discountRate=None, DRMethodOverride=None):
        # Returns the curve for past and future applying all relevant discounts


        def createHashObject(options):
            # multiple rates -> multipleRates, options
            # single rate: -> discountRate, options
            if self.getUseMultipleRates() and DRMethodOverride != 'SINGLE':
                # Include DRMethodOverride and the per-row discountRate: the multi-rates curve's
                # discount factors depend on both (BLENDED vs SWITCHED, and a row rate overrides
                # everything), so omitting them let a later row replay an earlier row's curve. (F31)
                hObj = {'useMultipleRates':True, 'rates':self.getMultipleRates(), 'DRMethodOverride': DRMethodOverride, 'rowRate': discountRate, 'options':options, 'sex': self.getSex(), 'revisedage': self.getRevisedAge(), 'region': self.getRegion(), 'year': self.getYear(), 'autoYrAttained':self.getAutoYrAttained()}
            else:
                hObj = {'useMultipleRates': False, 'rate': self.getdiscountRate(yrs=0, discountRate=discountRate), 'options': options,'sex': self.getSex(), 'revisedage': self.getRevisedAge(), 'region': self.getRegion(), 'year': self.getYear(), 'autoYrAttained':self.getAutoYrAttained()}
            hObjJSON=json.dumps(hObj,sort_keys=True)
            return hash(hObjJSON)

        # First check if we already have calculated this one for a given SINGLE discount rate
        h = createHashObject(options)
        if h in self.curveOptions:
            result = self.curveOptions[h]
            return result['LxNoI'], result['Lx'], result['Rng']

        def expand_past_range():
            # makes the past more granular
            rp = self.getSAR().getLx()[1]  # get the range for the change in interest
            rp=rp[:-1] #get rid of last element to avoid duplication of age at trial
            yrrp = np.arange(rp[0], rp[-1], 1)  # and for every year
            res = np.concatenate((rp, yrrp))  # join them
            # The dependency contingency is a STEP at the deceased's date of death: 1 before,
            # cont after. The trapezoid rule is only exact where the integrand is straight
            # between nodes, so a step landing mid-segment gets smeared across it - and the
            # size of the error depends on where the step happens to fall relative to a mesh
            # that has nothing to do with it. On the reference case that was worth 0.7% of a
            # past dependency multiplier, and the Excel add-in (different past mesh) smeared
            # it differently, so the two products disagreed for no principled reason.
            #
            # A node pair straddling the death resolves it exactly: the lower node still
            # carries 1, the upper carries cont, and the smear is confined to the gap between
            # them. EPS is well above the 1e-9 dedupe threshold used elsewhere and far below
            # any real mesh spacing.
            dodAge = self.getDependeeContingencyStartAge()
            if dodAge is not None and res.size and res[0] < dodAge < res[-1]:
                EPS = 1e-6
                res = np.concatenate((res, [dodAge - EPS, dodAge]))
            return np.sort(res, axis=None)  # sort them

        age = self.getAge()

        rp = expand_past_range()
        rf = self.getdataSet().getLx(self.getRevisedAge())[1][self.getdataSet().getLx(self.getRevisedAge())[1] >= age]  # range in the future

        # Make the past/future split land on the TRIAL AGE.
        #
        # Rng is an annual grid anchored at getAge(), which for a FATAL claimant is the age
        # at death - so the first grid point on or after trial can fall short of the trial
        # age itself (0.2767 of a year on the reference case). expand_past_range() already
        # drops its last element expecting the future range to start exactly at trial, so
        # that sliver belonged to neither side and was taking the past's factors.
        #
        # It matters for the C letter, which applies to FUTURE loss only: the sliver kept
        # contingency 1 instead of the claimant's factor, so a fatal claimant's effective
        # contingency came out ABOVE their real one (0.850516 against 0.85).
        #
        # For a living claimant the grid starts at the trial age already, so this is a no-op
        # - which also keeps _Lxf aligned, since that branch uses the raw Lx array whose
        # length must match rf. The fatal branch interpolates via transformLx and is
        # unaffected by the extra node.
        if rf.size == 0 or rf[0] > age:
            rf = np.concatenate(([age], rf))
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
            _discf = np.array([discountFactor(a - age, self.getdiscountRate(yrs=a - age, discountRate=discountRate,DRMethodOverride=DRMethodOverride)) for a in rf])
            _disc = np.concatenate((_discp, _discf))
        # mortality
        if 'M' in options:
            if self.isFatal():
                _Lxp = self.getdataSet().transformLx(rp)  # probability of death in the past
                _Lxf = self.getdataSet().transformLx(rf)  # probability of death
            else:
                _Lxp = np.full((rp.size), 1)  # probability 1 in the past
                _Lxf = self.getdataSet().getLx(self.getRevisedAge())[0]  # probability of death in the future
            _Lx = np.concatenate((_Lxp, _Lxf))
        # interest
        if 'I' in options:
            _interestp = self.getSAR().transformLx(rp)
            _interestf = np.full((rf.size), 1)
            _interest = np.concatenate((_interestp, _interestf))
        # cont
        if 'C' in options:
            _contp = np.full((rp.size), 1.0)
            # A dependency claim's contingency runs from the deceased's DATE OF DEATH, not
            # from trial - so unlike an ordinary contingency it does bite on past rows.
            #
            # The claimant's own past loss is evidenced rather than predicted, so a
            # contingency for being out of work has no place in it. A dependency claim is
            # different: from the moment the deceased died the period is counterfactual, and
            # the chance they would have been out of work for reasons other than mortality
            # applies to the years since their death just as much as to the years ahead.
            #
            # Previously the past array was 1 unconditionally, which understated the
            # deduction on every fatal-dependency schedule with a gap between death and
            # trial. The Excel add-in has always done it this way; this brings the engine
            # into line. (See DIVERGENCES.md D3 in the Excel repo.)
            if 'D' in options:
                dodAge = self.getDependeeContingencyStartAge()
                if dodAge is not None:
                    _contp = np.where(rp >= dodAge, float(cont), 1.0)
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

        # Also cache the individual factor arrays so the EXPLAIN feature can report the actual
        # per-age factors (survival, discount, interest, deceased) that produced the curve,
        # rather than re-deriving them. Additive — does not affect the return value. (EXPLAIN)
        result = {'LxNoI': LxNoI, 'Lx': Lx, 'Rng': Rng,
                  'components': {'disc': _disc, 'survival': _Lx, 'interest': _interest,
                                 'deceased': _deceased, 'cont': _cont}}
        self.curveOptions[h] = result

        return LxNoI, Lx, Rng

    def getCurveComponents(self, options, cont=1, discountRate=None, DRMethodOverride=None):
        # Returns the cached per-age factor arrays for the given options (building the curve if
        # needed). Used by the EXPLAIN feature. (EXPLAIN)
        self.getCurve(options=options, cont=cont, discountRate=discountRate, DRMethodOverride=DRMethodOverride)
        h = None
        # re-derive the same hash the getCurve just used by calling it again is wasteful; instead
        # find the entry we just stored. getCurve stores under its own hash; recompute that hash:
        if self.getUseMultipleRates() and DRMethodOverride != 'SINGLE':
            hObj = {'useMultipleRates': True, 'rates': self.getMultipleRates(), 'DRMethodOverride': DRMethodOverride, 'rowRate': discountRate, 'options': options, 'sex': self.getSex(), 'revisedage': self.getRevisedAge(), 'region': self.getRegion(), 'year': self.getYear(), 'autoYrAttained': self.getAutoYrAttained()}
        else:
            hObj = {'useMultipleRates': False, 'rate': self.getdiscountRate(yrs=0, discountRate=discountRate), 'options': options, 'sex': self.getSex(), 'revisedage': self.getRevisedAge(), 'region': self.getRegion(), 'year': self.getYear(), 'autoYrAttained': self.getAutoYrAttained()}
        h = hash(json.dumps(hObj, sort_keys=True))
        r = self.curveOptions[h]
        return r['LxNoI'], r['Lx'], r['Rng'], r['components']

    def explainTable(self, age1, age2, options, cont=1, discountRate=None, DRMethodOverride=None):
        # Builds the per-age breakdown table mirroring the VBA cCurve.sumUnderCurve outputArr:
        # for each segment [x1,x2] within [age1,age2], the trapezoidal area of the product curve
        # WITH interest and WITHOUT interest (and their difference = the interest area), plus the
        # per-node factor values. Reuses the same area() primitive and getCurve arrays that
        # produce the multiplier, so the table reconciles exactly to the returned tuple. (EXPLAIN)
        LxNoI, Lx, Rng, comp = self.getCurveComponents(options, cont=cont,
                                                        discountRate=discountRate, DRMethodOverride=DRMethodOverride)
        # breakpoints: age1, age2, and every curve node strictly between them
        interior = [float(a) for a in Rng if age1 < a < age2]
        pts = [age1] + interior + [age2]
        pts = sorted(set(pts))

        def interp(arr, a):
            return float(np.interp(a, Rng, arr))

        rows = []
        sumWithI = 0.0
        sumWithoutI = 0.0
        sumInterest = 0.0
        for x1, x2 in zip(pts[:-1], pts[1:]):
            areaWithI = self.area(Lx, x1, x2)
            areaWithoutI = self.area(LxNoI, x1, x2)
            interestArea = areaWithI - areaWithoutI
            sumWithI += areaWithI
            sumWithoutI += areaWithoutI
            sumInterest += interestArea
            rows.append({
                'age': round(x1, 4),
                'nextAge': round(x2, 4),
                'survivalLx': interp(comp['survival'], x1),   # MM: survival probability
                'DF': interp(comp['disc'], x1),               # discount factor (A)
                'IM': interp(comp['interest'], x1),           # interest multiplier (I)
                'MMD': interp(comp['deceased'], x1),          # deceased-dependant factor (D)
                'product': interp(Lx, x1),                    # product of all factors (with I)
                'areaWithI': areaWithI,
                'areaWithoutI': areaWithoutI,
                'interestArea': interestArea,
            })
        totals = {'sumAreaWithI': sumWithI, 'sumAreaWithoutI': sumWithoutI, 'sumInterestArea': sumInterest}
        return rows, totals
