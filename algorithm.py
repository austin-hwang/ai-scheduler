import copy, random, math
from numpy.random import choice

probs = []
class BacktrackingSearch():
    def __init__(self):
        self.bestAssignment = {}
        self.optimalWeight = 0
        self.numbestAssignments = 0
        self.numAssignments = 0
        self.numOperations = 0
        self.firstAssignmentNumOperations = 0
        self.firstAssignment = {}
        self.firstAssignmentWeight = 0

    def solve(self, csp, mcv, ac3, hwv, numEvents, events, duration):
        """
        Runs backtracking function
            :param csp: import the csp
            :param mcv: flag for mcv heuristic
            :param ac3: flag for ac-3
            :param hwv: flag for hwv heuristic
            :param numEvents: counts number of events
            :param events: list of all events
            :param duration: list of event durations
        """   
        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.hwv = hwv
        self.events = events
        self.numEvents = numEvents
        self.duration = duration
        self.domains = [copy.deepcopy(csp.domain) for i in range(numEvents)]
        self.backtrack({}, 0, 1)
        self.print_stats()

    def print_stats(self):
        """
        Print end results
        """   
        if self.bestAssignment:
            print "Found %d optimal assignments with weight %f in %d backtrack operations" % (self.numbestAssignments, self.optimalWeight, self.numOperations)
            print "First assignment has weight %f and took %d operations: " % (self.firstAssignmentWeight, self.firstAssignmentNumOperations), self.firstAssignment
            print "Best assignment: ", self.bestAssignment
        else:
            print "No solution was found."

    def new_weight(self, event, dayHourList):
        """
        Evaluates the weight at a current value
            :param event: current event evaluated
            :param dayHourList: list of day hour pairs
            :return: updated weight
        """   
        weight = 0
        for var in event[1]:
            for day, hour in dayHourList:
                if (day, hour) in self.csp.eventConstraints[event[0]]:
                    return 0
                else:
                    weight += self.csp.scheduleWeights[var][day][hour]
        return weight

    def reset(self, assignment, weight):
        """
        Resets assignments to find optimal assignment
            :param assignment: completed assignment
            :param weight: weight of assignment
        """   
        self.numAssignments += 1
        newAssignment = {}
        for event in self.csp.events.iteritems():
            newAssignment[event[0]] = assignment[event[0]]

        # Compares to see if current assignment is better than current optimal
        if len(self.bestAssignment) == 0 or weight >= self.optimalWeight:
            if weight == self.optimalWeight:
                self.numbestAssignments += 1
            else:
                self.numbestAssignments = 1
            self.optimalWeight = weight

            self.bestAssignment = newAssignment

        # Track first assignment for heuristics comparison
        if self.firstAssignmentNumOperations == 0:
            self.firstAssignmentNumOperations = self.numOperations
            self.firstAssignment = newAssignment
            self.firstAssignmentWeight = weight

    def backtrack(self, assignment, numAssigned, weight):
        """
        Main backtracking algorithm
            :param assignment: keeps track of current assignment
            :param numAssigned: counts number of events assigned
            :param weight: current weight of assignment
        """   
        self.numOperations += 1
        # Time out backtracking after 1000000 function calls
        if self.numOperations >= 1000000:
            return
        
        # Checks for complete assignment
        if numAssigned == self.csp.numEvents:
            self.reset(assignment, weight)
        else:
            # Get next event and value based on whether heuristics are activated
            event = self.next_event(assignment)
            allAssignments = [a for sublist in assignment.values() for a in sublist]
            values = self.highest_weighted_value(event)
            self.removeUnaryFromDomains()

            # Iterate through domain values
            for day, hour in values:
                if not day in self.domains[numAssigned].keys() and not hour in self.domains[numAssigned].values()[day].keys():
                    continue
                inDuration = self.getTimePeriodsInDuration((day, hour), self.duration[numAssigned])
                newWeight = self.new_weight(event, inDuration)
                # Only add to assignment if valid 
                if newWeight >= 1 and len(set(inDuration + allAssignments)) == len(inDuration + allAssignments):
                    # Calls AC-3 based on whether flag is activated
                    if not self.ac3:
                        assignment[event[0]] = self.getTimePeriodsInDuration((day, hour), self.duration[numAssigned])
                        self.backtrack(assignment, numAssigned + 1, weight + newWeight)
                    else:
                        assignment[event[0]] = copy.deepcopy(inDuration)
                        localCopy = copy.deepcopy(self.domains)
                        self.arc_consistency(event[0], assignment)
                        self.backtrack(assignment, numAssigned + 1, weight + newWeight)
                        self.domains = localCopy
                    # Backtrack 
                    del assignment[event[0]]
                        
    def next_event(self, assignment):
        """
        Determines which event is next based on heuristic
            :param assignment: current assignment
            :return: next event
        """   
        if self.mcv:
            return self.most_constrained_variable(assignment)
        for event in self.csp.events.iteritems():
            if event[0] not in assignment:
                return event
    
    def most_constrained_variable(self, assignment):
        """
        Checks to see which event has most unary constraints
            :param assignment: current assignment
            :return: event with most constraints
        """   
        most_constrained = []
        for event in self.csp.events.iteritems():
            if event[0] not in assignment:
                most_constrained.append((event, len(self.csp.eventConstraints[event[0]])))
        return max(most_constrained, key=lambda x:x[1])[0]

    def highest_weighted_value(self, event):
        """
        Returns a list of all domain values sorted by weight 
            :param event: current event
            :return: sorted list in descending order of weight
        """   
        ordered_values = {}
        for people in self.csp.scheduleWeights.iteritems():
            if people[0] in event[1]:
                for days in people[1].iteritems():
                    for hours in days[1].iteritems():
                        if (days[0], hours[0]) in ordered_values:
                            ordered_values[(days[0], hours[0])] += hours[1]
                        else:
                            ordered_values[(days[0], hours[0])] = hours[1]
                if not self.hwv:
                    return list(ordered_values)
        return sorted(ordered_values, key=ordered_values.__getitem__, reverse=True)

    def arc_consistency(self, event, assignment):
        """
        Runs AC-3 algorithm
            :param event: current event
            :param assignment: current assignment
        """   
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
        """
        Modify domain
            :param event2: current event
            :param assignment: current assignment
            :return: modified domain 
        """   
        modified = False
        for day in self.domains[event2]:
            for hour in self.domains[event2][day]:
                if (day, hour) in assignment:
                    self.domains[event2][day].pop(hour, None)
                    modified = True
        return modified

    def setConflictPairs(self, people):
        """
        Checks for conflicts
            :param people: list of people
        """   
        pairs = []
        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                combinedList = people[i] + people[j]
                if (len(combinedList) > len(set(combinedList))):
                    pairs.append([i, j])
        self.conflictPairs = pairs

    def lenOfDomain(self, domain):
        """
        Length of domain
            :param domain: current domain
            :return: length of domain
        """   
        cnt = 0
        for day in domain:
            cnt += len(domain[day])
        return cnt

    def getTimePeriodsInDuration(self, start, duration):
        """
        Generate a list of all the hours of the event
            :param start: start time of event
            :param duration: duration of event
            :return: list of all event hours
        """   
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
        """
        Preprocesses domain 
        """   
        for i, event in enumerate(self.csp.events.iteritems()):
            for person in event[1]:
                for dayTuple in self.csp.domain.iteritems():
                    day = dayTuple[0]
                    for hour in dayTuple[1].keys():
                        if (day, hour) in self.csp.eventConstraints[event[0]]:
                            self.domains[i][day].pop(hour, None)
# Simulated Annealing
class SA():
    def __init__(self):
        self.bestAssignment = []
        self.optimalWeight = 0
        self.numOperations = 0
        self.conflictPairs = []

    def solve(self, csp, people, sampleNewEvents, durations):
        """
        Runs simulated annealing 
            :param csp: current csp
            :param people: list of events with people
            :param sampleNewEvents: start with random sample
            :param durations: list of durations
        """  
        self.csp = csp
        self.numDays = csp.numDays
        self.dayLength = csp.dayLength
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}
        self.simulatedAnnealing(people, sampleNewEvents, durations)
        self.print_stats()

    def print_stats(self):
        """
        Print end results 
        """   
        print "Found 1 optimal assignments with weight %f" % self.optimalWeight
        print "Best Assignment: ", self.bestAssignment

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
                    score += self.csp.scheduleWeights[p][t[0]][t[1]]
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
        if dayOrTime == 0:
            newTime = ((time[dayOrTime] + shift[0]) % self.numDays, time[1])
        else:
            newTime = (time[0], (time[dayOrTime] + shift[0]) % self.dayLength)
        events[events.index(time)] = newTime
        return [events, assignment[1]]

    def simulatedAnnealing(self, people, sampleNewEvents, durations):
        randRestarts = 400
        trials = 100
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
            if not conflictsList:
                highScore = -1
            else:
                index = conflictsList.index(max(conflictsList))
                highScore = max(conflictsList)
                if (highScore > bestScore):
                    bestScore = highScore
                    bestEvents = assignList[index]

        self.optimalWeight = bestScore
        self.bestAssignment = {bestEvents[0].index(x):self.getTimePeriodsInDuration(x, durations[bestEvents[0].index(x)]) for x in bestEvents[0]}

    def acceptBag(self, newVal, oldVal, T):
        # Accept if val is better
        if(newVal > oldVal):
            return 1
        else:
            if oldVal == 0:
                return 0
            return choice([0, 1], 1, [math.exp(-(oldVal - newVal) / (T * oldVal)), 1 - math.exp(-(oldVal - newVal) / (T * oldVal))])[0]
