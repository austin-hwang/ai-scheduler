import algorithm

class CSP:
    def __init__(self, numDays, dayLength):
        self.numVars = 0
        self.numEvents = 5
        self.variables = []
        self.values = {}
        self.unaryConstraints = {}
        self.binaryConstraints = {}
        self.domain = []
        self.numDays = numDays
        self.dayLength = dayLength

    def add_variable(self, var, domain):
        if var not in self.variables:
            self.numVars += 1
            self.variables.append(var)
            self.values[var] = domain
            self.domain = domain
            self.unaryConstraints[var] = domain
            self.binaryConstraints[var] = {}

    def updateUnaryDomainVals(self, var, varMap):
        for key1 in varMap:
            for key2 in varMap[key1]:
                self.unaryConstraints[var][key1][key2] = varMap[key1][key2]

    # Map vars to val
    def getVarMapping(self, vars, days, hours, val):
        dict = {}
        for v in vars:
            dict[v] = {}
            for d in days:
                dict[v][d] = {}
                for h in hours:
                    dict[v][d][h] = val
        return dict

    def updateUnaryWithVarMaps(self, varMapDict):
        for key in varMapDict:
            self.updateUnaryDomainVals(key, varMapDict[key])

def create_schedule(people, numDays, dayLength):
    csp = CSP(numDays, dayLength)
    peopleFlat = [item for sublist in people for item in sublist]
    peopleFlat = list(set(peopleFlat))
    # Add variables
    for i in range(len(peopleFlat)):
        dict = {}
        for x in range(csp.numDays):
            dict[x] = {}
            for d in range(csp.dayLength):
                dict[x][d] = 1
        csp.add_variable(peopleFlat[i], dict)

    # Set variable constraints
    varMap1 = csp.getVarMapping(['A', 'C', 'D'], [5], range(0, csp.dayLength), 20)
    #varMap2 = csp.getVarMapping(['A', 'C', 'D'], range(0,6), range(11,3), 3)
    csp.updateUnaryWithVarMaps(varMap1)
    #csp.updateUnaryWithVarMaps(varMap2)
    return csp

import random
def sampleNewEvents(numDays, numHours, numSample):
    return random.sample([(d, h) for d in range(numDays) for h in range(numHours)], numSample)

# List of people
people = [['A', 'B', 'C', 'G'], ['G', 'D', 'E', 'F'], ['A', 'G', 'H']]
sa = algorithm.SA(create_schedule(people, numDays=7, dayLength=48))
durations = [5, 5, 5]
ret = sa.simulatedAnnealing(people, sampleNewEvents, durations)
print(ret)