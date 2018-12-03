import copy, random 

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
        if self.csp.unaryFactors[var]:
            weight *= self.csp.unaryFactors[var][val]
            if not weight: 
                return weight
        for var2, factor in self.csp.binaryFactors[var].iteritems():
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
                    possibleValues = possibleValues + result
                varConstraintList.append((var,possibleValues))
        varConstraintList.sort(key = lambda x: x[1])
        return varConstraintList[0][0]
    
    def arc_consistency(self, var1):
        queue = [var1]
        while queue:
            arc = queue.pop(0)
            for val1 in self.domains[arc]:
                if self.csp.unaryFactors[arc] is not None:
                    if self.csp.unaryFactors[arc][val1] == 0:
                        self.domains[arc].remove(val1)
                        queue.append(arc)
            for var2 in self.csp.get_neighbors(arc):
                for val2 in self.domains[var2]:   
                    if self.revise(arc, var2, val2):
                        self.domains[var2].remove(val2)
                        queue.append(var2)

    def revise(self, var1, var2, val2):
        for val1 in self.domains[var1]:
            if self.csp.binaryFactors[var1][var2] is not None:
                if self.csp.binaryFactors[var1][var2][val1][val2]:
                    return False
        return True

class LocalSearch():
    def __init__(self):
        self.bestAssignment = []
        self.optimalWeight = 0
        self.numbestAssignments = 0
        self.numAssignments = 0
        self.numOperations = 0
        self.firstAssignmentNumOperations = 0
        self.allAssignments = []

    def solve(self, csp):
        self.csp = csp
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}
        self.min_conflicts(100)
        self.print_stats()

    def print_stats(self):
        print "Found %d optimal assignments with weight %f in %d operations" % \
            (self.numbestAssignments, self.optimalWeight, self.numOperations)
        print "First assignment took %d operations" % self.firstAssignmentNumOperations

    def num_conflicts(self, assignment):
        score = (0, None)
        for val in self.csp.domain:
            tempScore = 0
            for var1 in self.csp.variables:
                tempScore += self.csp.unaryFactors[var1][val]
                for var2 in self.csp.binaryFactors[var1]:
                    tempScore += self.csp.binaryFactors[var1][var2][val][val]
            if tempScore > score[0] and val not in assignment:
                score = (tempScore, val)
        return score

    def min_conflicts(self, max_steps):
        assignment = random.sample(range(0, 23), self.csp.numEvents) 
        for _ in range(max_steps):
            randIndex = random.randint(0,self.csp.numEvents-1)
            assignment[randIndex] = self.num_conflicts(assignment)[1]
        self.bestAssignment = assignment
        print self.bestAssignment
