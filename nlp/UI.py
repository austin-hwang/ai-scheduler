from tui import display, prompt, choice
from wordsToDates import *
import testFriendRecommendations

def schedule():
    ## UI
    display(
        "What is the description of your event? Please include the event location, preferred times, and people participating.")
    display("ex. Get lunch in Harvard Square with John and Sarah tomorrow at 12pm or Sunday at 1pm")
    description = prompt("Description: ")

    # Parse description for people and event time
    parser = wordsToDates()
    descr = parser.run(description)

    # Check if info correct
    display("Checking if event description is correct.")

    # Get Event Name
    eventName = "".join(descr[3]).capitalize()
    eventCorrect = prompt("Is this your event name (y/n)?: " + "".join(eventName) + "\n")
    eventInput = "".join(eventName)
    if (eventCorrect == 'n'):
        eventInput = prompt("Input the correct event name \n")

    # Check if Location is Correct
    locCorrect = prompt("Is this your location (y/n)?: " + " ".join(descr[0]) + "\n")
    locInput = " ".join(descr[0])
    if (locCorrect == 'n'):
        locInput = prompt("Input the correct location \n")

    # Check if People are Correct
    peopleCorrect = prompt("Are you going with these people?: " + " ".join(descr[1]) + "(y/n)\n")
    peopleInput = " ".join(descr[1])
    if (peopleCorrect == 'n'):
        peopleInput = prompt("Input the correct people's names separated by commas. ex. John, Sarah \n")
        peopleInput = [x.strip() for x in peopleInput.split(',')]

    # Check if dates and times are correct
    display("Are these all of these preferred dates and times correct?")
    minLen = min(len(descr[2][0]), len(descr[2][1]))
    timesInput = []
    for i in range(minLen):
        timesInput.append((descr[2][0][i], descr[2][1][i]))
        display('Time: ' + str(descr[2][0][i]) + ' | Date: ' + str(descr[2][1][i]))
    timesCorrect = prompt("Input y/n: \n")
    if (timesCorrect == 'n'):
        timesInput = prompt(
            "Input the correct date(s) and time(s), separated by commas. Ex. Tomorrow 12pm, Friday 1pm\n")
        timesInput = timesInput.split(',')
        a = wordsToDates()
        timesInput = [a.parseTime(t.lower()) for t in timesInput]
        timesInput = [(t[0][0], t[1][0]) for t in timesInput]
    duration = prompt(
        "How long is your event? Input as a time rounded to nearest hour.\n")
    return {"Event": eventInput, "People": peopleInput, "Time": timesInput, "Duration": duration}

def getFriendRecs():
    # firstName = prompt("What's your first name?: ")
    # lastName = prompt("What's your last name?: ")
    firstName = " "
    lastName = " "
    conc = prompt("What's your concentration?: ")
    clubs = prompt("List your club names, separated by commas: ")
    clubs = clubs.split(',')
    userInfo = [firstName, lastName, conc] + clubs
    display("Give us a moment to find a friend recommendation...")
    friendRec = testFriendRecommendations.getFriendRecommendation(userInfo)

    display("You should meet " + friendRec[0] + " " + friendRec[1])
    friendRec = list(filter(None, friendRec))
    if(len(friendRec) >= 5):
        display("They concentrate in " + friendRec[2] + " and are a part of " + ", ".join(friendRec[3:-1]) +
                ', and ' + friendRec[-1])
    else:
        display("They concentrate in " + friendRec[2] + " and are a part of " + ", ".join(friendRec[3:]))
    display("We think you'd get along well!")
    raw_input("Press Enter to continue...")

def displayEvents():
    cnt = 1
    print("--List of events---")
    for i, e in enumerate(eventNames):
        print("Event {}: ".format(cnt) + e)
        print("Attendees: " + ', '.join(eventAttendees[i]))
        print("Duration: " + str(duration[i]) + " hours")
        timesPrint = ["Time: " + str(t[0][0]) + ":00" + " | " + t[1] for t in times[i]]
        print("Preferred Times:\n" + "\n".join(timesPrint))
        cnt += 1
        print("\n\n")
    raw_input("Press Enter to continue...")

def readConstraints():
    with open("constraints.txt") as file:
        data = file.readlines()
        constraints = []
        for lines in data:
            lines = lines.rstrip()
            constraints.append(lines.split(","))
    return constraints

import constraint
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
        varMap = csp.getVarMapping(peopleFlat, range(int(days[0]), int(days[1])+1), range(int(hours[0]), int(hours[1])+1), int(c[3]))
        csp.updateScheduleWeights(varMap)

    csp.updateEventConstraints()
    return csp

import algorithm
from run import sampleNewEvents
from datetime import datetime

def calcSchedule(people, times, duration):
    constraints = readConstraints()
    csp = create_schedule(people, constraints, numDays=7, dayLength=24)
    sa = algorithm.SA()
    daysDiff = []
    for i, t in enumerate(times):
        diff = []
        for t2 in t:
            d = datetime.strptime(str(t2[1]), '%Y-%m-%d') - datetime.today()
            diff.append(d.days)
            varMap = csp.getVarMapping(people[i], [d.days + 1], range(t2[0][0], t2[0][0] + duration[i]), 100)
            csp.updateScheduleWeights(varMap)
        daysDiff.append(diff)
    sa.solve(csp, people, sampleNewEvents, duration)
    #sa.simulatedAnnealing(people, sampleNewEvents, duration)

def initialize():
    # Initializations
    eventNames = ['Lunch', 'Go to the Gym', 'Dance Meeting']
    eventAttendees = [['A', 'B', 'C', 'G'], ['G', 'D', 'E', 'F'], ['A', 'G', 'H']]
    duration = [5, 3, 2]
    times = [[([12, 0.0, 0], '2018-12-20'), ([13, 0.0, 0], '2018-12-19')],
             [([9, 0.0, 0], '2018-12-19')],
             [([16, 0.0, 0], '2018-12-21'), ([16, 0.0, 0], '2018-12-22')]]
    return eventNames, eventAttendees, duration, times

## UI
# parser = wordsToDates()
# descr = parser.run("Get lunch in Harvard Square with John and Sarah this Sunday at 12pm or Wednesday or Monday at 1pm")
if __name__== "__main__":
    eventNames, eventAttendees, duration, times = initialize()
    # ret, daysDiff = calcSchedule(eventAttendees, times, duration)
    # print(ret)

    display("Welcome to the scheduler!")
    name = prompt(
        "What's your name?\n")
    userChoice = 0
    choices = ['Input an Event', 'Display Participants and Events to be Scheduled', 'Calculate Schedule for Events',
               'Friend Recommendation', 'Quit']
    while(userChoice != len(choices) - 1):
        userChoice = choice(choices)
        if(userChoice == 0):
            eventInfo = schedule()
            # Add events to event names
            eventNames.append(eventInfo["Event"])
            peopleList = eventInfo["People"].split()
            peopleList.append(name)
            peopleListNoSpaces = [s.lstrip() for s in peopleList]
            duration.append(int(eventInfo["Duration"]))
            times.append(eventInfo["Time"])
            # Add attendees to attendees list
            eventAttendees.append(peopleListNoSpaces)
        elif(userChoice == 1):
            displayEvents()
        elif(userChoice == 2):
            calcSchedule(eventAttendees, times, duration)
        elif(userChoice == 3):
            getFriendRecs()
        else:
            break

    display("Thanks for using the scheduler")




