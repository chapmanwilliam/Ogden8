import numpy as np
from utils import returnFreq, discountFactor,termCertain, names
import matplotlib.pyplot as plt
import os
from calcs import calcs

class curve():

    def __init__(self, name, parent=None):
        self.name=name
        self.parent=parent
        self._LxNoI=self._Lx=None
        self.curveOptions={} #dictionary to store different options with each entry 'AM' or 'AMD' etc. Should be 2^3 = 8 options
        self.dirty=True
        self.calc=calcs()

    def getPlot(self, result, fromAge, toAge, freq, cont, options):
        title=self.getTitle(result, fromAge, toAge, freq, cont, options)
        st,en,factor,timeInterval=returnFreq(freq)

        d=[]
        Mlegend=''
        if 'M' in options: d.append('Mortality')
        if 'A' in options: d.append('Accelerated receipt')
        if not cont==1: d.append('Cont (' + '{:.2f}'.format(cont)+")")
        if len(d)>0: Mlegend+='Disc. for '+ ' and '.join(d)
        if 'I' in options: Mlegend+=', with interest'


        plt.plot(self.Rng, self._Lx, label=Mlegend)
        if self.getAAD(): plt.axvline(self.getAAD(),linestyle='dashed',color='black', label='death') #age at death
        plt.axvline(self.getAAT(),linestyle='dashed',color='green', label='trial') #age at trial
        if self.getAAI(): #set the x=range from date of injury to 125
            plt.xlim(self.getAAI(),125)
            plt.ylim(0,self.Lx(self.getAAI(),options)[3])
        #Area under the curve
        if toAge:
            if st or en: #this is discrete
                if st:
                    ages = np.arange(start=fromAge, stop=toAge, step=timeInterval)
                if en:
                    ages = np.arange(start=fromAge+1, stop=toAge, step=timeInterval)
                y= np.array([np.interp(age,self.Rng,self._Lx) for age in ages])
                plt.vlines(ages,0,y,linestyles='dashed',color='red')
            else: #this is continuous
                ages = np.arange(start=fromAge, stop=toAge, step=0.1)
                y= np.array([np.interp(age,self.Rng,self._Lx) for age in ages])
                plt.fill_between(ages,0,y, color='red')
        else: #one off
            plt.vlines(fromAge,0,np.interp(fromAge,self.Rng,self._Lx),linestyles='dashed',color='red')
        #Labels
        plt.xlabel('Age')
        plt.ylabel('Multiplier')
        plt.title(title)
        plt.legend(loc='upper right', prop={'size':6})
        if 'D' in options:
            plt.figtext(1, 0.03, 'Dependent: ' + self.getdataSet().getdataTitle(), ha='right', fontsize=6)
            plt.figtext(1,0.01,'Deceased: ' + self.getDeceased().getdataSet(names[0]).getdataTitle(), ha='right', fontsize=6)
        else:
            plt.figtext(1, 0.01, self.getdataSet().getdataTitle(), ha='right', fontsize=6)

        plt.show()

    def getHeading1(self,result, fromAge, toAge=None, freq="Y", cont=1, options='AMI'):
        if 'D' in options:
            s='Joint Multiplier '
        else:
            s = self.name.capitalize() + " Multiplier "
        # The range
        if toAge:
            s += "from " + '{:.1f}'.format(fromAge) + " to " + '{:.1f}'.format(toAge)
            if not freq == "Y": s += ", " + freq
        else:
            s += "at " + '{:.1f}'.format(fromAge)
        s += " = " + '{:.2f}'.format(result[3])
        return s

    def getHeading2(self):
        str = self.getSex()
        if self.isFatal(): str+= " (deceased)"
        str += ', age ' + '{:.1f}'.format(self.getAge()) + ' at trial'
        return str

    def getTitle(self, result, fromAge, toAge=None, freq="Y", cont=1, options='AMI'):
        str=self.getHeading1(result,fromAge,toAge,freq,cont,options)
        str += os.linesep
        str +=self.getHeading2()
        return str

    def getdataSet(self):
        return self.parent.getdataSet(self.name)

    def isFatal(self):
        return self.parent.isFatal()

    def getSAR(self):
        return self.parent.getSAR()

    def getdiscountRate(self):
        return self.parent.getdiscountRate()

    def gettrialDate(self):
        return self.parent.gettrialDate()

    def getAge(self):
        return self.parent.getAge()

    def getAAT(self):
        return self.parent.getAAT()

    def getAAI(self):
        return self.parent.getAAI()

    def getAAD(self):
        return self.parent.getAAD()

    def getSex(self):
        return self.parent.getSex()

    def getDeceased(self):
        return self.parent.deceased

    def M(self, fromAge, toAge=None, freq="Y", cont=1, options='AMI'):
        #get the right curve

        self.refresh()

        self._LxNoI, self._Lx, self.Rng = self.getCurve(options)

        calc1=calcs()
        result=self.Multiplier(fromAge, toAge, options, freq, cont,calc1)

        self.calc.clear()
        self.calc.addText(self.getHeading1(result,fromAge,toAge,freq,cont,options))
        self.calc.addText(self.getHeading2())
        self.calc.inDent()
        self.calc.addCalcs(calc1)
        self.calc.outDent()

        return result

    def Multiplier(self,fromAge, toAge=None, options=None, freq="Y", cont=1,calc=None):
        st,en,factor,timeInterval=returnFreq(freq)
        if toAge:
            if st or en: #this is not continuous
                if st:
                    ages=np.arange(start=fromAge,stop=toAge, step=timeInterval)
                if en:
                    ages=np.arange(start=fromAge+1,stop=toAge, step=timeInterval)
                result= np.sum(np.array([self.Multiplier(fromAge=age,options=options,cont=cont, calc=calc) for age in ages]),axis=0)
            else: #this is continuous
                interest,past=self.cont(fromAge,min(self.getAge(),toAge),options)
                if options=='A':
                    futureinterest=0
                    yrs1=max(self.getAge(),fromAge)-self.getAge()
                    yrs2=toAge-self.getAge()
                    TC1=termCertain(yrs1,self.getdiscountRate())
                    TC2=termCertain(yrs2,self.getdiscountRate())
                    future=TC2-TC1
                else:
                    futureinterest,future=self.cont(max(self.getAge(),fromAge),toAge,options)
                interest*=factor
                past*=factor
                future*=factor*cont
                result= past,interest,future,past+interest+future
        else:
            result=self.Lx(fromAge, options)

        if calc:
            calc.addText(self.getBreakdown(fromAge,toAge,factor, result))
        return result

    def getBreakdown(self,fromAge,toAge,factor,result):
        s=[]
        if result[0]>0: s.append('{:.2f}'.format(result[0]) + ' (past)')
        if result[1]>0: s.append('{:.2f}'.format(result[1]) + ' (interest)')
        if result[2]>0: s.append('{:.2f}'.format(result[2]) + ' (future)')
        total='{:.2f}'.format(result[3])
        s= ' + '. join(s[:3]) + ' = ' + total
        if not (toAge):
            s= 'At age ' + '{:.2f}'.format(fromAge) + ' : ' + s
        else:
            s= 'Age ' + '{:.2f}'.format(fromAge) + ' to {:.2f}'.format(toAge) + ' : ' + s
        return s

    def cont(self,fromAge,toAge,options):
        if fromAge<toAge:
            Tx1I, Tx1=self.Tx(fromAge,options)
            Tx2I, Tx2=self.Tx(toAge,options)
            interest=Tx2I-Tx1I
            withoutInterest=Tx2-Tx1
            return interest,withoutInterest
        return 0,0

    def Tx(self, age,options):
        if age<0: return 0
        a=self.Rng[self.Rng<=age]
        Lx=self._Lx[self.Rng<=age]
        LnoI=self._LxNoI[self.Rng<=age]
        y=np.trapz(Lx,a) #with interest
        ynoI=np.trapz(LnoI,a) #withoutinterest

        #additional chunk
        lowerL=Lx[-1]
        higherLpast,higherLinterest,higherLfuture,higherLtotal=self.Lx(age,options)
        yrsBetween=age-a[-1]
        additionalChunk=0.5*(lowerL+higherLtotal)*yrsBetween #with interest

        # additional chunk
        lowerL = LnoI[-1]
        higherLpast, higherLinterest, higherLfuture, higherLtotal = self.Lx(age,options)
        yrsBetween = age - a[-1]
        additionalChunknoI = 0.5 * (lowerL + higherLpast+higherLfuture) * yrsBetween #without interest

        withInterest=y+additionalChunk
        withoutInterest=ynoI+additionalChunknoI
        interest=withInterest-withoutInterest

        return interest, withoutInterest

    def Lx(self,age,options):
        y=np.interp(age,self.Rng,self._Lx)
        ynoI=np.interp(age,self.Rng,self._LxNoI)
        if age<self.getAge(): #past
            past=ynoI
            interest=y-ynoI
            future=0
        else: #future
            past=0
            interest=0
            if options=="A": #just acceleration
                yrs=age-self.getAge()
                future=discountFactor(yrs,self.getdiscountRate())
            else:
                future=y
        return past,interest,future,past+interest+future

    def setDirty(self,value=True):
        self.dirty=value

    def refresh(self):
        if self.dirty:
            self.curveOptions.clear()
            self.dirty=False

    def getCurve(self, options):
        #Returns the curve for past and future applying all relevant discounts

        #First check if we already have calculated this one
        if options in self.curveOptions:
            result=self.curveOptions[options]
            return result['LxNoI'],result['Lx'], result['Rng']

        age=self.getAge()
        rp=self.getSAR().Rng #range in the past
        rf=self.getdataSet().Rng[self.getdataSet().Rng>=age] #range in the future
        Rng=np.concatenate((rp,rf)) #range past and future
        discountRate=self.getdiscountRate()

        #defaults
        _disc = np.full((Rng.size), 1)
        _Lx = np.full((Rng.size), 1)
        _interest = np.full((Rng.size), 1)
        _deceased = np.full((Rng.size), 1)

        #discount factor
        if 'A' in options:
            _discp=np.full((rp.size),1) #1 in the past
            _discf=np.array([discountFactor(a-age,discountRate) for a in rf])
            _disc=np.concatenate((_discp,_discf))
        #mortality
        if 'M' in options:
            if self.isFatal():
                _Lxp=self.getdataSet().transformLx(rp)
                _Lxf=self.getdataSet().transformLx(rf) #probability of death
                pass
            else:
                _Lxp=np.full((rp.size),1) #1 in the past
                _Lxf=self.getdataSet()._Lx #probability of death
            _Lx=np.concatenate((_Lxp,_Lxf))
        #interest
        if 'I' in options:
            _interestp=self.getSAR()._Lx
            _interestf=np.full((rf.size),1)
            _interest=np.concatenate((_interestp,_interestf))
        #deceased
        if 'D' in options:
            deceased=self.getDeceased()
            if deceased:
                shift = self.getAge() - deceased.age  # the age gap
                _deceased=deceased.getdataSet(names[0]).transformLx(Rng,shift)

        #multiply together _disc, _Lx, _interest, _cont, _factor, _deceased
        A=np.stack((_disc,_Lx,_deceased)) #without interest
        B=np.stack((_disc,_Lx,_interest,_deceased)) #with interest

        LxNoI=np.prod(A,axis=0)
        Lx=np.prod(B,axis=0)

        result={'LxNoI':LxNoI,'Lx': Lx, 'Rng':Rng}
        self.curveOptions[options]=result

        return LxNoI,Lx, Rng



