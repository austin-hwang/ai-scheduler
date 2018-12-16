# Multi-Event Scheduling Algorithm Using CSPs and NLP

## Installation Guide
To install:

```sh
pip install pipenv
pipenv shell --python 2.7
pipenv install
```

## Testing Suite
To run the testing suite:
```sh
python run.py
```
The console will output the following: 
```
Tight contraints case
Found 49 optimal assignments with weight 5.000000 in 57 backtrack operations
First assignment has weight 5.000000 and took 3 operations:  {0: [(6, 13)], 1: [(5, 14)]}
Best assignment:  {0: [(0, 13)], 1: [(4, 14)]}
--- 0.00528478622437 seconds ---
```
1. The first line represents the case being tested
2. The second line lists the number of optimal assignments found and the optimal score
3. The third line represents the first correct assignment found, its score, and assignment
4. The fourth line represents the best assignment found
5. The last line is the run-time. 

The assignment output is formatted as such:

`{Event #: [(Day #, Hour #)]}`

The day range is generally from 0-6 to represent the days of the week and the hour range is 0-23 for 24 hours. If the event is more than one hour long, then the assignment will include the consecutive hours for that duration.

## Additional Testing

If you want do perform additional testing, the `test/testCases.txt` file can be modified to add additional tests. 

Test must be formatted in the following way:
```
description: Tight contraints case
events: A B;C D
durations: 1 1
A,0;6,0;12,0
A,0;6,14;23,0
A,0;6,13;13,2
C,0;6,0;13,0
D,0;6,15;23,0
end
```

- Events are separated by a semi-colon with each participant being separated by a space
- Duration of each event is in hours and separated by a space
- Each following line indicates an event constraint based on an individual's schedule. For example: `A,0;6,0;12,0`
    - The first parameter `A` is the person being targeted
    - The second `0;6` indicates the range of days the constraint will be applied. In this case, it is from days 0 to 6.
    - The third `0;12` indicates the range of hours the constraint will be applied. In this case, it is from hours 0 to 12.
    - Finally  `0` indicates the weight of the constraint. Anything less than 0 is a schedule conflict that will be avoided. The more positive the number, the higher the preference towards scheduling around that time.
- The end word indicates the end of a test

## Console UI

To run the interactive UI:

```
python UI.py
```

This will output:
```
Welcome to the scheduler!
What's your name?
Austin
What would you like to do?
    1. Input an Event
    2. Display Participants and Events to be Scheduled
    3. Calculate Schedule for Events
    4. Friend Recommendation
    5. Quit
Type the number or the option:
```

There are 5 options:

1. Schedule an event using NLP
2. Display available events that are already scheduled 
3. Find optimal time for events based on inputted textfile of a person's schedule in `nlp/constraints.txt`
4. Recommend a friend based concentration and club
5. Exit program

## Project Structure

### CSP
- CSP structure is declared in `constraint.py`
- Backtracking and simulated annealing are declared in `algorithm.py`

### Console UI
- Console UI is declared in `UI.py`

### NLP
- NLP related files are located in `nlp/` folder

### Testing
- The evaluation of the algorithms is declared in `run.py`
- The test data is located in `test/testCases.txt`