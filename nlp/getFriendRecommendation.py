import csv
import scipy.stats as ss
import numpy as np
from helpers import *
import sys
sys.path.insert(0, './nlp/')

## Get Created User Data
def getFriendRecommendation(userTraits = ['Erin', 'Li', \
                                          'Statistics', 'Harvard Undergraduate CONSULTING ON BUSINESS AND THE ENVIRONMENT', \
                                          'Veritas Financial Group']):
    """
    Calculates friend recommendation based on similarity of descriptions between concentrations and clubs. Friends are
    from a pre-created database. The closest friend is calculated by ranking the similarities of the concentrations and
    closest club match and summing the two ranks. The lowest rank sum is the closest friend.
    :param userTraits: User concentration and clubs
    :return: A friend recommendation
    """
    # Reads friend data from input
    data = []
    with open('nlp/sample_data.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            #print(row[0], row[1], row[2])
            data.append(row)

    # Load scraped data and description proximity calculations
    concentrations = pickle.load(open( "nlp/concentrations.p", "rb" ))
    descr = pickle.load(open( "nlp/concentration_descr.p", "rb" ))

    org_info = pickle.load(open( "nlp/org_info.p", "rb" ))
    org_names = pickle.load(open( "nlp/org_names.p", "rb" ))

    concTable = pickle.load(open( "nlp/concentrationLists.p", "rb" ))
    orgsTable = pickle.load(open( "nlp/orgInfoLists.p", "rb" ))

    # Compare the new user vs each person
    newPerson = userTraits
    conc = closeStringInList(newPerson[2], concentrations)
    orgs = [closeStringInList(str, org_names) for str in newPerson[3:]]

    # Score the proximity of interests of each person
    scores = [[], []]
    for r in data[1:]:
        concOther = closeStringInList(r[2], concentrations)
        orgsOther = [closeStringInList(str, org_names) for str in r[3:]]

        concSim = concTable[conc][concOther]
        orgsSim = [orgsTable[i][j] for i in orgsOther for j in orgs]
        orgsSim = max(orgsSim)

        scores[0].append(concSim)
        scores[1].append(orgsSim)

    # Calculate ranks for each person
    ranks = [ss.rankdata(scores[0]), ss.rankdata(scores[1])]
    rankSum = np.sum(ranks, axis=0)

    # Give recommendations of the top friend and display their clubs and concentration
    return data[np.where(rankSum==rankSum.max())[0][0] + 1]
