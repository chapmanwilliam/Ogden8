import os

indentSize=1 #size of the indent

class calcs():
    def __init__(self):
        self.indent=0
        self.txt=[] #text for each line

    def clear(self):
        self.txt.clear()
        self.indent=0

    def addCalcs(self,calc):
        s=[' ' * self.indent+ t for t in calc.txt]
        self.txt += s

    def addText(self,txt):
        txt=' ' * self.indent + txt
        self.txt.append(txt)

    def show(self):
        return os.linesep.join(self.txt)

    def inDent(self):
        self.indent+=indentSize

    def outDent(self):
        if self.indent-indentSize>0:
            self.indent-=indentSize