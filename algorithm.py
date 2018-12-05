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

    def solve(self, csp, mcv, ac3):
        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}
        print "CSP: ", self.csp.values
        self.backtrack({}, 0, 1)
        self.print_stats()

    def print_stats(self):
        if self.bestAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numbestAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."


    def new_weight(self, assignment, var, val, weight):
        if self.csp.unaryConstraints[var]:
            weight *= self.csp.unaryConstraints[var][val]
            if not weight: 
                return weight
        for var2, factor in self.csp.binaryConstraints[var].iteritems():
            if var2 in assignment: 
                weight *= factor[val][assignment[var2]]
                if not weight: 
                    return weight
        return weight

    def reset(self, assignment, weight):
        self.numAssignments += 1
        newAssignment = {}
        for var in self.csp.variables:
            newAssignment[var] = assignment[var]
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

    def backtrack(self, assignment, numAssigned, weight):
        self.numOperations += 1
        if numAssigned == self.csp.numVars:
            self.reset(assignment, weight)
        else:
            var = self.next_variable(assignment)
            ordered_values = self.domains[var]

            if not self.ac3:
                for val in ordered_values:
                    newWeight = self.new_weight(assignment, var, val, 1.0)
                    if newWeight > 0:
                        assignment[var] = val
                        self.backtrack(assignment, numAssigned + 1, weight * newWeight)
                        del assignment[var]
            else:
                for val in ordered_values:
                    newWeight = self.new_weight(assignment, var, val, 1.0)
                    if newWeight > 0:
                        assignment[var] = val
                        localCopy = copy.deepcopy(self.domains)
                        self.domains[var] = [val]
                        self.arc_consistency(var)
                        self.backtrack(assignment, numAssigned + 1, weight * newWeight)
                        self.domains = localCopy
                        del assignment[var]

    def next_variable(self, assignment):
        if self.mcv:
            return self.most_constrained_variable(assignment)
        else:
            for var in self.csp.variables:
                if var not in assignment: 
                    return var
    
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
    
    def arc_consistency(self, var1):
        queue = [var1]
        while queue:
            arc = queue.pop(0)
            for val1 in self.domains[arc]:
                if self.csp.unaryConstraints[arc] is not None:
                    if self.csp.unaryConstraints[arc][val1] == 0:
                        self.domains[arc].remove(val1)
                        queue.append(arc)
            for var2 in self.csp.get_neighbors(arc):
                for val2 in self.domains[var2]:   
                    if self.revise(arc, var2, val2):
                        self.domains[var2].remove(val2)
                        queue.append(var2)

    def revise(self, var1, var2, val2):
        for val1 in self.domains[var1]:
            if self.csp.binaryConstraints[var1][var2] is not None:
                if self.csp.binaryConstraints[var1][var2][val1][val2]:
                    return False
        return True

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
