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

    def add_variable(self, var, domain):
        """
        Add variables to CSP
            :param var: current variable
            :param domain: variable's domain
        """   
        if var not in self.variables:
            self.variables.append(var)
            self.values[var] = domain
            self.domain = domain
            self.scheduleWeights[var] = domain

    def updateUnaryDomainVals(self, var, varMap):
        """
        Update the weights for the constraints
            :param var: current variable
            :param varMap: weights associated
        """   
        for key1 in varMap:
            for key2 in varMap[key1]:
                self.scheduleWeights[var][key1][key2] = varMap[key1][key2]

    def get_neighbors(self, var, numEvents):
        """
        Returns a list of neighboring events
            :param var: current event
            :param numEvents: number of events
            :return: list of events
        """   
        # All events are neighbors
        return range(var+1, numEvents)


    def getVarMapping(self, vars, days, hours, val):
        """
        Map vars to val
            :param vars: list of participants
            :param days: list of days
            :param hours: list of hours
            :param val: weight
            :return: dictionary of constraints
        """   
        dict = {}
        for v in vars:
            dict[v] = {}
            for d in days:
                dict[v][d] = {}
                for h in hours:
                    dict[v][d][h] = val
        return dict

    def updateScheduleWeights(self, varMapDict):
        """
        Update event weights
            :param varMapDict: variable to value dictionary
        """   
        for key in varMapDict:
            self.updateUnaryDomainVals(key, varMapDict[key])

    def updateEventConstraints(self):
        """
        Add unary constraints to events
        """   
        for people in self.scheduleWeights.iteritems():
            for days in people[1].iteritems():
                for hours in days[1].iteritems():
                    if hours[1] <= 0:
                        for event in self.events.iteritems():
                            if people[0] in event[1]:
                                self.eventConstraints[event[0]].add((days[0], hours[0]))
