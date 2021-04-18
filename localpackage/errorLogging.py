

class err():

    def getLog(self):
        s=''
        for e in self.errors:
            s = s + e + '\n'
        return s

    def getErrors(self):
        return self.errors

    def clear(self):
        self.errors.clear()

    def add(self, e):
        self.errors.append(e)

    def __init__(self):
        self.errors = []


errors=err()
