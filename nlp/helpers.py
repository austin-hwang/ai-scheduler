import pickle
import textComparison as tc

## Helpers for friend recommendations
# Calculates edit distance between two strings
def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

# Finds closest string (by edit distance) from 'str' in 'list'
def closeStringInList(str, list):
    distances = [levenshteinDistance(str, s) for s in list]
    return distances.index(min(distances))

def preprocDescrip():
    # Load lists
    concentrations = pickle.load(open("concentrations.p", "rb"))
    descr = pickle.load(open("concentrationDescr.p", "rb"))

    orgInfo = pickle.load(open("orgInfo.p", "rb"))
    orgNames = pickle.load(open("orgNames.p", "rb"))

    # Add org names to descriptions; remove the word 'Harvard'
    for i, org in enumerate(orgInfo):
        org = org.replace("harvard", "")
        orgInfo[i] = str(orgNames[i]).lower() + " " + str(org).lower()

    orgInfoLists = tc.getSimilarityLists(orgInfo)
    concentrationLists = tc.getSimilarityLists(descr)

    pickle.dump(orgInfoLists, open("orgInfoLists.p", "wb"))
    pickle.dump(concentrationLists, open("concentrationLists.p", "wb"))

## Helpers for event description translation
from enchant.checker import SpellChecker
from autocorrect import spell

#perform spell correction
def performSpellCorrection(text):
    checker = SpellChecker("en_US", text)
    for word in checker:
        word.replace(spell(word.word))

    return checker.get_text()

# Tokenization, parts of speech tagging

