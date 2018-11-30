import copy

class BacktrackingSearch():
    def __init__(self):
        self.optimalAssignment = {}
        self.optimalWeight = 0
        self.numOptimalAssignments = 0
        self.numAssignments = 0
        self.numOperations = 0
        self.firstAssignmentNumOperations = 0
        self.allAssignments = []

    def solve(self, csp, mcv = False, ac3 = False):
        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}
        self.backtrack({}, 0, 1)
        self.print_stats()

    def print_stats(self):
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."


    def new_weight(self, assignment, var, val):
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: 
                return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: 
                continue  
            w *= factor[val][assignment[var2]]
            if w == 0: 
                return w
        return w

    def reset(self, assignment, weight):
        self.numAssignments += 1
        newAssignment = {}
        for var in self.csp.variables:
            newAssignment[var] = assignment[var]
        self.allAssignments.append(newAssignment)

        if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
            if weight == self.optimalWeight:
                self.numOptimalAssignments += 1
            else:
                self.numOptimalAssignments = 1
            self.optimalWeight = weight

            self.optimalAssignment = newAssignment
            if self.firstAssignmentNumOperations == 0:
                self.firstAssignmentNumOperations = self.numOperations

    def backtrack(self, assignment, numAssigned, weight):
        self.numOperations += 1
        if numAssigned == self.csp.numVars:
            self.reset(assignment, weight)
            return

        var = self.next_variable(assignment)
        ordered_values = self.domains[var]

        if not self.ac3:
            for val in ordered_values:
                newWeight = self.new_weight(assignment, var, val)
                if newWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * newWeight)
                    del assignment[var]
        else:
            for val in ordered_values:
                newWeight = self.new_weight(assignment, var, val)
                if newWeight > 0:
                    assignment[var] = val
                    localCopy = copy.deepcopy(self.domains)
                    self.domains[var] = [val]
                    self.arc_consistency(var)
                    self.backtrack(assignment, numAssigned + 1, weight * newWeight)
                    self.domains = localCopy
                    del assignment[var]

    def next_variable(self, assignment):
        if not self.mcv:
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            varConstraintList = []
            for var in self.csp.variables:
                if var not in assignment:
                    possibleValues = 0
                    for val in self.domains[var]:
                        result = self.new_weight(assignment, var, val)
                        possibleValues = possibleValues + result
                    varConstraintList.append((var,possibleValues))
            varConstraintList.sort(key=lambda x: x[1])
            return varConstraintList[0][0]
    
    def arc_consistency(self, var1):
        queue = [var1]
        while queue:
            arc = queue.pop(0)
            for val1 in self.domains[arc]:
                if self.csp.unaryFactors[arc] != None:
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
            if self.csp.binaryFactors[var1][var2] != None:
                if self.csp.binaryFactors[var1][var2][val1][val2] != 0:
                    return False
        return True