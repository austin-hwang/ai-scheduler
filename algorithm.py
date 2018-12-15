import copy, random, math
probs = []
class BacktrackingSearch():
    def __init__(self):
        self.bestAssignment = {}
        self.allAssignments = []
        self.optimalWeight = 0
        self.numbestAssignments = 0
        self.numAssignments = 0
        self.numOperations = 0
        self.firstAssignmentNumOperations = 0
        self.totalWeight = 0;

    def solve(self, csp, mcv, ac3, numEvents, events, duration):
        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.events = events
        self.numEvents = numEvents
        self.duration = duration
        self.domains = [copy.deepcopy(csp.domain) for i in range(numEvents)]
        self.backtrack({}, 0, 1)
        self.print_stats()

    def print_stats(self):
        if self.bestAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numbestAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
            print "Best assignment: ", self.bestAssignment
        else:
            print "No solution was found."


    def new_weight(self, event, dayHourList):
        weight = 0
        # print "Var: ", var
        # print "Day: ", day
        # print "Hour: ", hour
        for var in event[1]:
            for day, hour in dayHourList:
                if (day, hour) in self.csp.eventConstraints[event[0]]:
                    return 0
                else:
                    weight += self.csp.unaryConstraints[var][day][hour]
        return weight

    def reset(self, assignment, weight):
        self.numAssignments += 1
        newAssignment = {}
        for event in self.csp.events.iteritems():
            newAssignment[event[0]] = assignment[event[0]]
        self.allAssignments.append(newAssignment)

        if len(self.bestAssignment) == 0 or weight >= self.optimalWeight:
            if weight == self.optimalWeight:
                self.numbestAssignments += 1
            else:
                self.numbestAssignments = 1
            self.optimalWeight = weight

            self.bestAssignment = newAssignment
            if self.firstAssignmentNumOperations == 0:
                self.firstAssignmentNumOperations = self.numOperations
        # print "Best Assignment: ", self.bestAssignment, self.optimalWeight

    def backtrack(self, assignment, numAssigned, weight):
        # print self.numOperations
        self.numOperations += 1
        if numAssigned == self.csp.numEvents:
            print(assignment, weight, numAssigned)
            self.reset(assignment, weight)
        else:
            event = self.next_event(assignment)
            allAssignments = [a for sublist in assignment.values() for a in sublist]
            # var = self.next_variable(assignment, event)
            # ordered_values = self.domains[var]
            self.removeUnaryFromDomains()
            if not self.ac3:
                for day in self.domains[numAssigned].iteritems():
                    for hour in day[1].keys():

                        inDuration = self.getTimePeriodsInDuration((day[0], hour),
                                                                    self.duration[numAssigned])
                        newWeight = self.new_weight(event, inDuration)
                        if newWeight >= 1 and len(set(inDuration + allAssignments)) == len(inDuration + allAssignments):
                            assignment[event[0]] = self.getTimePeriodsInDuration((day[0], hour),
                                                                                 self.duration[numAssigned])
                            self.backtrack(assignment, numAssigned + 1, weight + newWeight)
                            # print assignment
                            del assignment[event[0]]
                            # print "Deleted: ", assignment
            else:
                for day in self.domains[numAssigned].iteritems():
                    for hour in day[1].keys():

                        inDuration = self.getTimePeriodsInDuration((day[0], hour),
                                                                    self.duration[numAssigned])
                        newWeight = self.new_weight(event, inDuration)
                        if newWeight >= 1 and len(set(inDuration + allAssignments)) == len(inDuration + allAssignments):
                            print(inDuration)
                            assignment[event[0]] = copy.deepcopy(inDuration)
                            localCopy = copy.deepcopy(self.domains)
                            self.arc_consistency(event[0], assignment)
                            self.backtrack(assignment, numAssigned + 1, weight * newWeight)
                            self.domains = localCopy
                            del assignment[event[0]]

    def next_variable(self, assignment, event):
        if self.mcv:
            return self.most_constrained_variable(assignment)
        else:
            for var in self.csp.variables:
                if var in event: 
                    return var

    def next_event(self, assignment):
        for event in self.csp.events.iteritems():
            if event[0] not in assignment:
                return event
    
    def most_constrained_variable(self, assignment):
        varConstraintList = []
        for var in self.csp.variables:
            if var not in assignment:
                possibleValues = 0
                for val in self.domains[var]:
                    result = self.new_weight(assignment, var, val, 1.0)
                    possibleValues += result
                varConstraintList.append((var,possibleValues))
        varConstraintList.sort(key = lambda x: x[1])
        return varConstraintList[0][0]
    
    def arc_consistency(self, event, assignment):
        self.setConflictPairs(self.events)
        conflictPairs = self.conflictPairs
        queue = [event]
        while queue:
            arc = queue.pop(0)
            for eventNeighbor in self.csp.get_neighbors(arc, self.numEvents):
                # See if similar people in events
                if([arc, eventNeighbor] in conflictPairs):
                    if self.revise(eventNeighbor, assignment):
                        queue.append(eventNeighbor)

    def revise(self, event2, assignment):
        modified = False
        for day in self.domains[event2]:
            for hour in self.domains[event2][day]:
                if (day, hour) in assignment:
                    self.domains[event2][day].pop(hour, None)
                    modified = True
        return modified

    def setConflictPairs(self, people):
        pairs = []
        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                combinedList = people[i] + people[j]
                if (len(combinedList) > len(set(combinedList))):
                    pairs.append([i, j])
        self.conflictPairs = pairs

    def lenOfDomain(self, domain):
        cnt = 0
        for day in domain:
            cnt += len(domain[day])
        return cnt

    def getTimePeriodsInDuration(self, start, duration):
        timePeriods = [start]
        currPeriod = start
        for i in range(duration - 1):
            if(currPeriod[1] + 1 >= self.csp.dayLength):
                currPeriod = (currPeriod[0] + 1, 0)
            else:
                currPeriod = (currPeriod[0], currPeriod[1] + 1)
            if(currPeriod[0] == self.csp.numDays):
                currPeriod = (0, 0)
            timePeriods.append(currPeriod)
        return timePeriods

    def removeUnaryFromDomains(self):
        for i, event in enumerate(self.csp.events.iteritems()):
            for person in event[1]:
                for dayTuple in self.csp.domain.iteritems():
                    day = dayTuple[0]
                    for hour in dayTuple[1].keys():
                        if (day, hour) in self.csp.eventConstraints[event[0]]:
                            self.domains[i][day].pop(hour, None)
# Simulated Annealing
class SA():
    def __init__(self, csp):
        self.bestAssignment = []
        self.optimalWeight = 0
        self.numbestAssignments = 0
        self.numAssignments = 0
        self.numOperations = 0
        self.firstAssignmentNumOperations = 0
        self.allAssignments = []
        self.csp = csp
        self.conflictPairs = []
        self.numDays = csp.numDays
        self.dayLength = csp.dayLength

    def solve(self, csp):
        self.csp = csp
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}
        self.print_stats()

    def print_stats(self):
        print "Found %d optimal assignments with weight %f in %d operations" % \
            (self.numbestAssignments, self.optimalWeight, self.numOperations)
        print "First assignment took %d operations" % self.firstAssignmentNumOperations

    def num_conflicts(self, assignment, duration):
        events = assignment[0]
        people = assignment[1]
        score = 0

        # Can't assign conflict pairs
        for p in self.conflictPairs:
            group1 = self.getTimePeriodsInDuration(events[p[0]], duration[p[0]])
            group2 = self.getTimePeriodsInDuration(events[p[1]], duration[p[1]])
            inBothLists = set(group1) & set(group2)
            if(inBothLists):
                return -1

        for i, e in enumerate(events):
            for p in people[i]:
                timePeriods = self.getTimePeriodsInDuration(e, duration[i])
                if(len(timePeriods) == 0):
                    return -1
                for t in timePeriods:
                    score += self.csp.unaryConstraints[p][t[0]][t[1]]
        return score

    def getTimePeriodsInDuration(self, start, duration):
        timePeriods = [start]
        currPeriod = start
        for i in range(duration - 1):
            if(currPeriod[1] + 1 >= self.dayLength):
                currPeriod = (currPeriod[0] + 1, 0)
            else:
                currPeriod = (currPeriod[0], currPeriod[1] + 1)
            if(currPeriod[0] == self.numDays):
                return []
            timePeriods.append(currPeriod)
        return timePeriods

    def setConflictPairs(self, people):
        pairs = []
        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                combinedList = people[i] + people[j]
                if (len(combinedList) > len(set(combinedList))):
                    pairs.append([i, j])
        self.conflictPairs = pairs

    def getNeighbor(self, assignment):
        events = assignment[0]
        eventNum = int(random.random() * len(events))
        dayOrTime = int(random.random() * 2)
        time = events[eventNum]
        shift = random.sample([-1, 1], 1)
        if(dayOrTime == 0):
            newTime = ((time[dayOrTime] + shift[0]) % self.numDays, time[1])
        else:
            newTime = (time[0], (time[dayOrTime] + shift[0]) % self.dayLength)
        events[events.index(time)] = newTime
        return [events, assignment[1]]

    def simulatedAnnealing(self, people, sampleNewEvents, durations):
        randRestarts = 100
        trials = 300
        self.setConflictPairs(people)
        bestEvents = sampleNewEvents(self.numDays, self.dayLength, len(people))
        bestScore = 0
        for it in range(randRestarts):
            currEvents = sampleNewEvents(self.numDays, self.dayLength, len(people))
            prevConflicts = 0
            T = 1000.0
            DECAY = 0.98

            conflictsList = []
            assignList = []
            for t in range(trials):
                nextAssign = self.getNeighbor([currEvents, people])
                conflicts = self.num_conflicts(nextAssign, durations)
                if(conflicts < 0):
                    continue

                if(self.acceptBag(conflicts, prevConflicts, T) > 0.99):
                    prevConflicts = conflicts
                    currAssign = nextAssign
                    conflictsList.append(conflicts)
                    assignList.append(copy.deepcopy(currAssign))

                # Update temperature
                T *= DECAY
            index = conflictsList.index(max(conflictsList))
            highScore = max(conflictsList)
            if (highScore > bestScore):
                bestScore = highScore
                bestEvents = assignList[index]

        return bestScore, bestEvents

    def acceptBag(self, newVal, oldVal, T):
        # Accept if val is better
        if(newVal > oldVal):
            return 1
        else:
            #return random.random()
            from numpy.random import choice
            #probs.append(1 - math.exp(-(oldVal - newVal) / (T * oldVal)))
            return choice([0, 1], 1, [math.exp(-(oldVal - newVal) / (T * oldVal)), 1 - math.exp(-(oldVal - newVal) / (T * oldVal))])[0]
