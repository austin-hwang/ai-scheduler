import csv
import scipy.stats as ss
import numpy as np
from helpers import *

## Get Created User Data
data = []
with open('sample_data.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        print(row[0], row[1], row[2])
        data.append(row)

# Load scraped data and text proximity calculations
concentrations = pickle.load(open( "concentrations.p", "rb" ))
descr = pickle.load(open( "concentration_descr.p", "rb" ))

org_info = pickle.load(open( "org_info.p", "rb" ))
org_names = pickle.load(open( "org_names.p", "rb" ))

concTable = pickle.load(open( "concentrationLists.p", "rb" ))
orgsTable = pickle.load(open( "orgInfoLists.p", "rb" ))

## Compare new user vs each person
newPerson = ['Erin', 'Li', 'Statistics', 'Harvard Undergraduate CONSULTING ON BUSINESS AND THE ENVIRONMENT', 'Veritas Financial Group']
conc = closeStringInList(newPerson[2], concentrations)
orgs = [closeStringInList(str, org_names) for str in newPerson[3:]]

## Score the proximity of interests of each person
scores = [[], []]

for r in data:
    concOther = closeStringInList(r[2], concentrations)
    orgsOther = [closeStringInList(str, org_names) for str in r[3:]]

    concSim = concTable[conc][concOther]
    orgsSim = [orgsTable[i][j] for i in orgsOther for j in orgs]
    orgsSim = max(orgsSim)

    # Score Function
    scores[0].append(concSim)
    scores[1].append(orgsSim)

ranks = [ss.rankdata(scores[0]), ss.rankdata(scores[1])]
rankSum = np.sum(ranks, axis=0)

## Give recommendations of the top friend and display their clubs and concentration
print(data[np.where(rankSum==rankSum.max())[0][0]])
