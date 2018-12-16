import sys
sys.path.insert(0, './nlp/')
import algorithm
from tui import display, prompt, choice
from wordsToDates import *
from run import sampleNewEvents
from datetime import datetime
import constraint
import testFriendRecommendations

def schedule():
    """
    Takes user input to schedule a new event
    :return: Returns dict of event name, participants, time, and duration
    """

    # Take a sentence describing the event
    display("What is the description of your event? Please include the event location, "
            "preferred times, and people participating.")
    display("ex. Get lunch in Harvard Square with John and Sarah tomorrow at 12pm or Sunday at 1pm")
    description = prompt("Description: ")

    # Parse description for people and event time
    parser = readNewEventInfo()
    descr = parser.run(description)

    # Check if info is correct
    display("Checking if event description is correct.")

    # Confirm event name
    eventName = "".join(descr[3]).capitalize()
    eventCorrect = prompt("Is this your event name (y/n)?: " + "".join(eventName) + "\n")
    eventInput = "".join(eventName)
    if (eventCorrect == 'n'):
        eventInput = prompt("Input the correct event name \n")

    # Check if Location is correct
    locCorrect = prompt("Is this your location (y/n)?: " + " ".join(descr[0]) + "\n")
    locInput = " ".join(descr[0])
    if (locCorrect == 'n'):
        locInput = prompt("Input the correct location \n")

    # Check if event participants are correct
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
        reader = readNewEventInfo()
        timesInput = [reader.parseTime(t.lower()) for t in timesInput]
        timesInput = [(t[0][0], t[1][0]) for t in timesInput]

    # Get event duration
    duration = prompt(
        "How long is your event? Input as a time rounded to nearest hour.\n")

    return {"Event": eventInput, "People": peopleInput, "Time": timesInput, "Duration": duration}

def getFriendRecs():
    """
    Gives friend recommendations to the user from a premade user database.
    :return: No return
    """
    firstName = " "
    lastName = " "

    # Asks for user information to match with friend
    conc = prompt("What's your concentration?: ")
    clubs = prompt("List your club names, separated by commas: ")
    clubs = clubs.split(',')
    userInfo = [firstName, lastName, conc] + clubs

    # Finds friend match
    display("Give us a moment to find a friend recommendation...")
    friendRec = getFriendRecommendation.getFriendRecommendation(userInfo)

    # Displays friend recommendation
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
    """
    Displays event information (event names, attendees, duration, and preferred event times)
    :return:
    """
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
    """
    Reads default constraints for events from 'constraints.txt'
    :return: A list of constraints with people, days, and hours
    """
    with open("constraints.txt") as file:
        data = file.readlines()
        constraints = []
        for lines in data:
            lines = lines.rstrip()
            constraints.append(lines.split(","))
    return constraints

def create_schedule(people, constraints, numDays, dayLength):
    """
    Creates a CSP for the constraints and people provided
    :param people: All people involved in events
    :param constraints: List of constraints
    :param numDays: Number of days to create schedule for
    :param dayLength: Number of equal time segments to segment each day
    :return: A CSP defined by the constraints input
    """
    # Initializes time period for CSP
    csp = constraint.CSP(numDays, dayLength)
    csp.numEvents = len(people)

    # List of all unique people
    peopleFlat = [item for sublist in people for item in sublist]
    peopleFlat = list(set(peopleFlat))

    # Add variables to CSP
    for i in range(len(peopleFlat)):
        dict = {}
        for x in range(csp.numDays):
            dict[x] = {}
            for d in range(csp.dayLength):
                dict[x][d] = 1
        csp.add_variable(peopleFlat[i], dict)
    for i, val in enumerate(people):
        csp.events[i] = val

    # Add constraints to the CSP
    csp.eventConstraints = {e[0]: set() for e in csp.events.iteritems()}
    for c in constraints:
        days = c[1].split(";")
        hours = c[2].split(";")
        varMap = csp.getVarMapping(peopleFlat, range(int(days[0]), int(days[1])+1), range(int(hours[0]), int(hours[1])+1), int(c[3]))
        csp.updateScheduleWeights(varMap)
    csp.updateEventConstraints()

    return csp

def calcSchedule(people, times, duration):
    """
    Calculate a recommended schedule for the events provided
    :param people: List of people by event
    :param times: List of preferred times per event
    :param duration: List of durations of each event
    :return:
    """
    # Creates a CSP based on constraints from 'constraints.txt'
    constraints = readConstraints()
    csp = create_schedule(people, constraints, numDays=7, dayLength=24)

    # Initializes simulated annealing
    sa = algorithm.SA()

    # Updates time weights based on preferred time input in 'times'
    daysDiff = []
    for i, t in enumerate(times):
        diff = []
        for t2 in t:
            d = datetime.strptime(str(t2[1]), '%Y-%m-%d') - datetime.today()
            diff.append(d.days)
            varMap = csp.getVarMapping(people[i], [d.days + 1], range(t2[0][0], t2[0][0] + duration[i]), 100)
            csp.updateScheduleWeights(varMap)
        daysDiff.append(diff)

    # Finds a recommended item via simulated annealing
    sa.solve(csp, people, sampleNewEvents, duration)

def initialize():
    """
    Initializes sample events and their, attendees, durations, and preferred times
    :return: Initialized event names, attendees, durations, and preferred times
    """
    # Initializations
    eventNames = ['Lunch', 'Go to the Gym', 'Dance Meeting']
    eventAttendees = [['A', 'B', 'C', 'G'], ['G', 'D', 'E', 'F'], ['A', 'G', 'H']]
    duration = [5, 3, 2]
    times = [[([12, 0.0, 0], '2018-12-20'), ([13, 0.0, 0], '2018-12-19')],
             [([9, 0.0, 0], '2018-12-19')],
             [([16, 0.0, 0], '2018-12-21'), ([16, 0.0, 0], '2018-12-22')]]
    return eventNames, eventAttendees, duration, times

## UI
if __name__== "__main__":
    # Initializes events
    eventNames, eventAttendees, duration, times = initialize()

    ### UI for scheduler
    display("Welcome to the scheduler!")

    # Get user name
    name = prompt("What's your name?\n")

    # User choices
    userChoice = 0
    choices = ['Input an Event', 'Display Participants and Events to be Scheduled', 'Calculate Schedule for Events',
               'Friend Recommendation', 'Quit']

    # Actions based on user input
    while(userChoice != len(choices) - 1):
        # Get user choice
        userChoice = choice(choices)
        if(userChoice == 0):
            # Input a new event
            eventInfo = schedule()

            # Add events to event names
            eventNames.append(eventInfo["Event"])
            # Add people to attendees list
            peopleList = eventInfo["People"].split()
            peopleList.append(name)
            peopleListNoSpaces = [s.lstrip() for s in peopleList]
            eventAttendees.append(peopleListNoSpaces)
            # Add duration
            duration.append(int(eventInfo["Duration"]))
            # Add preferred times
            times.append(eventInfo["Time"])
        elif(userChoice == 1):
            # Display events stored
            displayEvents()
        elif(userChoice == 2):
            # Calculate schedule for events stored
            calcSchedule(eventAttendees, times, duration)
        elif(userChoice == 3):
            # Get friend recommendations
            getFriendRecs()
        else:
            break

    # Exit UI
    display("Thanks for using the scheduler")




