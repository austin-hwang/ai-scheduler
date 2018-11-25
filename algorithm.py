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
            # CSP to be solved.
            self.csp = csp

            # Set the search heuristics requested asked.
            self.mcv = mcv
            self.ac3 = ac3

            # The dictionary of domains of every variable in the CSP.
            self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

            # Perform backtracking search.
            self.backtrack({}, 0, 1)
            self.print_stats()

    def print_stats(self):
            if self.optimalAssignment:
                print "Found %d optimal assignments with weight %f in %d operations" % \
                    (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
                print "First assignment took %d operations" % self.firstAssignmentNumOperations
            else:
                print "No solution was found."


    def get_delta_weight(self, assignment, var, val):
            assert var not in assignment
            w = 1.0
            if self.csp.unaryFactors[var]:
                w *= self.csp.unaryFactors[var][val]
                if w == 0: return w
            for var2, factor in self.csp.binaryFactors[var].iteritems():
                if var2 not in assignment: continue  # Not assigned yet
                w *= factor[val][assignment[var2]]
                if w == 0: return w
            return w

    def backtrack(self, assignment, numAssigned, weight):
            self.numOperations += 1
            assert weight > 0
            if numAssigned == self.csp.numVars:
                # A satisfiable solution have been found. Update the statistics.
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
                return

            # Select the next variable to be assigned.
            var = self.get_unassigned_variable(assignment)
            # Get an ordering of the values.
            ordered_values = self.domains[var]

            # Continue the backtracking recursion using |var| and |ordered_values|.
            if not self.ac3:
                # When arc consistency check is not enabled.
                for val in ordered_values:
                    deltaWeight = self.get_delta_weight(assignment, var, val)
                    if deltaWeight > 0:
                        assignment[var] = val
                        self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                        del assignment[var]
            else:
                # Arc consistency check is enabled.
                for val in ordered_values:
                    deltaWeight = self.get_delta_weight(assignment, var, val)
                    if deltaWeight > 0:
                        assignment[var] = val
                        # create a deep copy of domains as we are going to look
                        # ahead and change domain values
                        localCopy = copy.deepcopy(self.domains)
                        # fix value for the selected variable so that hopefully we
                        # can eliminate values for other variables
                        self.domains[var] = [val]

                        # enforce arc consistency
                        self.arc_consistency_check(var)

                        self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                        # restore the previous domains
                        self.domains = localCopy
                        del assignment[var]

    def get_unassigned_variable(self, assignment):
        if not self.mcv:
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            varConstraintList = []
            for var in self.csp.variables:
                if var not in assignment:
                    possibleValues = 0
                    for val in self.domains[var]:
                        result = self.get_delta_weight(assignment, var, val)
                        possibleValues = possibleValues + result
                    varConstraintList.append((var,possibleValues))
            varConstraintList.sort(key=lambda x: x[1])
            return varConstraintList[0][0]

    def arc_consistency_check(self, var1):
        for val1 in self.domains[var1]:
            if self.csp.unaryFactors[var1] != None:
                if self.csp.unaryFactors[var1][val1] == 0:
                    self.domains[var1].remove(val1)
                    self.arc_consistency_check(var1)
        consistent = False
        for var2 in self.csp.get_neighbor_vars(var1):
            for val2 in self.domains[var2]:
                for val1 in self.domains[var1]:
                    if self.csp.binaryFactors[var1][var2] != None:
                        if self.csp.binaryFactors[var1][var2][val1][val2] != 0:
                            consistent = True
                if consistent == False:
                    self.domains[var2].remove(val2)
                    self.arc_consistency_check(var2)
