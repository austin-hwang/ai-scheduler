import algorithm, json, random, time, constraint

def create_schedule(people, constraints, numDays, dayLength):
    csp = constraint.CSP(numDays, dayLength)
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

# Evaluate local search function
def localSearchEval():
    with open("test/testCases.txt") as file:
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
                sa = algorithm.SA()
                start_time = time.time()
                sa.solve(csp, attendees, sampleNewEvents, durations)
                print("--- %s seconds ---\n" % (time.time() - start_time))
                attendees = []
                constraints = []
                durations = []
            else:
                constraints.append(lines.split(","))    

# Evlauate backtracking without heuristics by default
def backtrackEval(heuristic=False, ac3=False):
    with open("test/testCases.txt") as file:
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
                bt.solve(csp, mcv=heuristic, ac3=ac3, hwv=heuristic, numEvents=len(attendees), events=attendees, duration=durations)
                print("--- %s seconds ---\n" % (time.time() - start_time))
                attendees = []
                constraints = []
                durations = []
            else:
                constraints.append(lines.split(","))
if __name__== "__main__":
    # print "--------------EVALUATING BACKTRACKING---------------"
    # backtrackEval()
    # print "--------------EVALUATING BACKTRACKING WITH HEURISTICS---------------"
    # backtrackEval(heuristic=True)
    # print "--------------EVALUATING BACKTRACKING WITH AC-3---------------"
    # backtrackEval(heuristic=True, ac3=True)
    print "--------------EVALUATING LOCAL SEARCH---------------"
    localSearchEval()
