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

    display(descr)

    # Get Event Name
    eventCorrect = prompt("Is this your event name (y/n)?: " + " ".join(descr[3]) + "\n")
    eventInput = " ".join(descr[3])
    if (eventCorrect == 'n'):
        eventInput = prompt("Input the correct event name \n")

    # Check if info correct
    display("Checking if event description is correct.")

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

    # Check if dates and times are correct
    display("Are these all of these preferred dates and times correct?")
    minLen = min(len(descr[2][0]), len(descr[2][1]))
    timesInput = ""
    for i in range(minLen):
        timesInput = timesInput + str(descr[2][0][i]) + " " + str(descr[2][1][i]) + ", "
        display('Time: ' + str(descr[2][0][i]) + ' | Date: ' + str(descr[2][1][i]))
    timesCorrect = prompt("Input y/n: \n")
    if (timesCorrect == 'n'):
        timesInput = prompt(
            "Input the correct date and time pairs separated by commas. ex. Tomorrow 12pm, Friday 1pm\n")

def getFriendRecs():
    firstName = prompt("What's your first name?: ")
    lastName = prompt("What's your last name?: ")
    conc = prompt("What's your concentration?: ")
    clubs = prompt("List your club names, separated by commas: ")
    clubs = clubs.split(',')
    userInfo = [firstName, lastName, conc] + clubs
    friendRec = testFriendRecommendations.getFriendRecommendation(userInfo)
    display("Give us a moment to find a friend recommendation")

    display("You should meet " + friendRec[0] + " " + friendRec[1])
    display("They concentrate in " + friendRec[2] + " and are a part of " + " ".join(friendRec[3:]))
    display("We think you'd get along well!")
    display("")

## UI
# parser = wordsToDates()
# descr = parser.run("Get lunch in Harvard Square with John and Sarah this Sunday at 12pm or Wednesday or Monday at 1pm")

display("Welcome to the scheduler!")
userChoice = 0
choices = ['Schedule', 'Friend Recommendation', 'Quit']
while(userChoice != len(choices) - 1):
    userChoice = choice(choices)
    if(userChoice == 0):
        schedule()
    elif(userChoice == 1):
        getFriendRecs()
    else:
        break

display("Thanks for using the scheduler")




