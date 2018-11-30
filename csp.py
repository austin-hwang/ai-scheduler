import json, re, sys, algorithm

class CSP:
    def __init__(self):
        self.numVars = 0
        self.variables = []
        self.values = {}
        self.unaryFactors = {}
        self.binaryFactors = {}

    def add_variable(self, var, domain):
        if var in self.variables:
            raise Exception("Variable name already exists: %s" % str(var))

        self.numVars += 1
        self.variables.append(var)
        self.values[var] = domain
        self.unaryFactors[var] = None
        self.binaryFactors[var] = dict()


    def get_neighbors(self, var):
        return self.binaryFactors[var].keys()

    def add_unary_factor(self, var, factorFunc):
        factor = {val: float(factorFunc(val)) for val in self.values[var]}
        if self.unaryFactors[var] is not None:
            self.unaryFactors[var] = {val: self.unaryFactors[var][val] * factor[val] for val in factor}
        else:
            self.unaryFactors[var] = factor

    def add_binary_factor(self, var1, var2, factor_func):
        self.update_binary_factor_table(var1, var2,
            {val1: {val2: float(factor_func(val1, val2)) for val2 in self.values[var2]} for val1 in self.values[var1]})
        self.update_binary_factor_table(var2, var1, \
            {val2: {val1: float(factor_func(val1, val2)) for val1 in self.values[var1]} for val2 in self.values[var2]})

    def update_binary_factor_table(self, var1, var2, table):
        if var2 not in self.binaryFactors[var1]:
            self.binaryFactors[var1][var2] = table
        else:
            currentTable = self.binaryFactors[var1][var2]
            for i in table:
                for j in table[i]:
                    currentTable[i][j] *= table[i][j]

def weights(x, lower, upper):
    if lower < x < upper:
        return 1.0
    else:
        return 0.1

def create_schedule():
    csp = CSP()
    csp.add_variable('A', [x for x in range(6)])
    csp.add_variable('B', [x for x in range(6)])
    csp.add_variable('C', [x for x in range(6)])
    csp.add_unary_factor('A', lambda x : weights(x, 1, 5))
    csp.add_unary_factor('B', lambda x : x != 1 and x != 3 and x !=2)
    csp.add_unary_factor('C', lambda x : x != 4 and x != 3)
    csp.add_binary_factor('A', 'B', lambda x, y : x == y)
    csp.add_binary_factor('B', 'C', lambda x, y : x == y)
    csp.add_binary_factor('A', 'C', lambda x, y : x == y)
    # print "Unary: ", json.dumps(csp.unaryFactors, indent = 2)
    # print "Binary: ", json.dumps(csp.binaryFactors, indent = 2)
    return csp

search = algorithm.BacktrackingSearch()
print "Without AC"
search.solve(create_schedule())
print "Optimal Assignments: ", search.optimalAssignment
print "All Assignments: ", search.allAssignments

print "With AC"
search.solve(create_schedule(), ac3=True)
print "Optimal Assignments: ", search.optimalAssignment
print "All Assignments: ", search.allAssignments
