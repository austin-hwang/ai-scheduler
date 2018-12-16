import algorithm, json, random, time

class CSP:
    def __init__(self, numDays, dayLength):
        self.numEvents = 0
        self.events = {}
        self.variables = []
        self.values = {}
        self.scheduleWeights = {}
        self.eventConstraints = {}
        self.domain = []
        self.numDays = numDays
        self.dayLength = dayLength

    def reset(self):
        self.numEvents = 0
        self.events = {}
        self.variables = []
        self.values = {}
        self.scheduleWeights = {}
        self.eventConstraints = {}
        self.domain = []

    def add_variable(self, var, domain):
        if var not in self.variables:
            self.variables.append(var)
            self.values[var] = domain
            self.domain = domain
            self.scheduleWeights[var] = domain

    def updateUnaryDomainVals(self, var, varMap):
        for key1 in varMap:
            for key2 in varMap[key1]:
                self.scheduleWeights[var][key1][key2] = varMap[key1][key2]

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

    # Update event weights
    def updateScheduleWeights(self, varMapDict):
        for key in varMapDict:
            self.updateUnaryDomainVals(key, varMapDict[key])

    # Add unary constraints
    def updateEventConstraints(self):
        for people in self.scheduleWeights.iteritems():
            for days in people[1].iteritems():
                for hours in days[1].iteritems():
                    if hours[1] <= 0:
                        for event in self.events.iteritems():
                            if people[0] in event[1]:
                                self.eventConstraints[event[0]].add((days[0], hours[0]))


def create_schedule(people, constraints, numDays, dayLength):
    csp = CSP(numDays, dayLength)
    csp.numEvents = len(people)
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
    for c in constraints:
        days = c[1].split(";")
        hours = c[2].split(";")
        varMap = csp.getVarMapping(list(c[0]), range(int(days[0]), int(days[1])+1), range(int(hours[0]), int(hours[1])+1), int(c[3]))
        csp.updateScheduleWeights(varMap)

    csp.updateEventConstraints()
    return csp

def sampleNewEvents(numDays, numHours, numSample):
    return random.sample([(d, h) for d in range(numDays) for h in range(numHours)], numSample)

def localSearchEval():
    with open("test/test1.txt") as file:
        data = file.readlines()
        attendees = []
        constraints = []
        durations = []
        for lines in data:
            lines = lines.rstrip()
            if "events" in lines:
                for people in lines[8:].split(";"):
                    attendees.append(people.split(" "))
            elif "durations" in lines:
                durations.extend(lines[11:].split(" "))
                durations = [int(x) for x in durations]
            elif "description" in lines:
                print lines[13:]
            elif "end" in lines:
                csp = create_schedule(attendees, constraints, numDays=7, dayLength=24)
                sa = algorithm.SA(csp)
                start_time = time.time()
                ret = sa.simulatedAnnealing(attendees, sampleNewEvents, durations)
                print(ret)
                print("--- %s seconds ---\n" % (time.time() - start_time))
                attendees = []
                constraints = []
                durations = []
            else:
                constraints.append(lines.split(","))    

def backtrackEval():
    with open("test/test1.txt") as file:
        data = file.readlines()
        attendees = []
        constraints = []
        durations = []
        for lines in data:
            lines = lines.rstrip()
            if "events" in lines:
                for people in lines[8:].split(";"):
                    attendees.append(people.split(" "))
            elif "durations" in lines:
                durations.extend(lines[11:].split(" "))
                durations = [int(x) for x in durations]
            elif "description" in lines:
                print lines[13:]
            elif "end" in lines:
                bt = algorithm.BacktrackingSearch()
                csp = create_schedule(attendees, constraints, numDays=7, dayLength=24)

                start_time = time.time()
                bt.solve(csp, mcv=False, ac3=False, hwv=False, numEvents=len(attendees), events=attendees, duration=durations)
                print("--- %s seconds ---\n" % (time.time() - start_time))
                attendees = []
                constraints = []
                durations = []
            else:
                constraints.append(lines.split(","))

def heuristicsEval():
    with open("test/test1.txt") as file:
        data = file.readlines()
        attendees = []
        constraints = []
        durations = []
        for lines in data:
            lines = lines.rstrip()
            if "events" in lines:
                for people in lines[8:].split(";"):
                    attendees.append(people.split(" "))
            elif "durations" in lines:
                durations.extend(lines[11:].split(" "))
                durations = [int(x) for x in durations]
            elif "description" in lines:
                print lines[13:]
            elif "end" in lines:
                bt = algorithm.BacktrackingSearch()
                csp = create_schedule(attendees, constraints, numDays=7, dayLength=24)

                start_time = time.time()
                bt.solve(csp, mcv=True, ac3=False, hwv=True, numEvents=len(attendees), events=attendees, duration=durations)
                print("--- %s seconds ---\n" % (time.time() - start_time))
                attendees = []
                constraints = []
                durations = []
            else:
                constraints.append(lines.split(","))

print "--------------EVALUATING BACKTRACKING---------------"
backtrackEval()
print "--------------EVALUATING BACKTRACKING WITH HEURISTICS---------------"
heuristicsEval()
print "--------------EVALUATING LOCAL SEARCH---------------"
localSearchEval()