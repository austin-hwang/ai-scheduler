import algorithm, json

class CSP:
    def __init__(self, numDays, dayLength):
        self.numVars = 0
        self.numEvents = 3
        self.events = {}
        self.variables = []
        self.values = {}
        self.unaryConstraints = {}
        self.binaryConstraints = {}
        self.eventConstraints = {}
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

    def get_neighbors(self, var, numEvents):
        # All events are neighbors
        return range(var+1, numEvents)

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

    def updateEventConstraints(self):
        for people in self.unaryConstraints.iteritems():
            for days in people[1].iteritems():
                for hours in days[1].iteritems():
                    if hours[1] <= 0:
                        for event in self.events.iteritems():
                            if people[0] in event[1]:
                                self.eventConstraints[event[0]].add((days[0], hours[0]))


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
    for i, val in enumerate(people):
        csp.events[i] = val

    csp.eventConstraints = {e[0]: set() for e in csp.events.iteritems()}
    # Set variable constraints
    # varMap1 = csp.getVarMapping(['A', 'C', 'D'], [5], range(0, csp.dayLength), 20)
    # varMap2 = csp.getVarMapping(['A'], range(csp.numDays), range(1,6), -10000)
    varMap3 = csp.getVarMapping(['B'],[1], [6], 10000)
    varMap4 = csp.getVarMapping(['G'],[2], [7], 10000)
    varMap5 = csp.getVarMapping(['H'],[3], [8], 10000)
    #varMap2 = csp.getVarMapping(['A', 'C', 'D'], range(0,6), range(11,3), 3)
    # csp.updateUnaryWithVarMaps(varMap1)
    # csp.updateUnaryWithVarMaps(varMap2)
    csp.updateUnaryWithVarMaps(varMap3)
    csp.updateUnaryWithVarMaps(varMap4)
    csp.updateUnaryWithVarMaps(varMap5)
    csp.updateEventConstraints()
    # print "Unary: ", json.dumps(csp.unaryConstraints, indent = 2)
    # for people in csp.unaryConstraints.iteritems():
    #     for days in people[1].iteritems():
    #         for hours in days[1].iteritems():
    #             print hours
    #print "Variables: ", csp.variables
    # #csp.updateUnaryWithVarMaps(varMap2)
    # print "Domain: ", csp.domain
    print csp.events
    print csp.eventConstraints
    return csp

import random
def sampleNewEvents(numDays, numHours, numSample):
    return random.sample([(d, h) for d in range(numDays) for h in range(numHours)], numSample)

# List of people
events = [['A', 'B', 'C', 'G'], ['G', 'D', 'E', 'F'], ['A', 'G', 'H']]
# events = [['A','C','D'], ['G', 'D', 'E', 'F']]
# sa = algorithm.SA(create_schedule(events, numDays=7, dayLength=48))
durations = [3, 2, 2]
# ret = sa.simulatedAnnealing(events, sampleNewEvents, durations)
# print(ret)
print "Hello"
bt = algorithm.BacktrackingSearch()
bt.solve(create_schedule(events, numDays=4, dayLength=10), mcv=False, ac3=False, hwv=True, numEvents=len(events), events = events, duration=durations)
print("hello")
