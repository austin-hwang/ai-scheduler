import pickle
import textComparison as tc
from enchant.checker import SpellChecker
from autocorrect import spell

## Helpers for friend recommendations
def levenshteinDistance(s1, s2):
    """
    Calculates edit distance between two strings
    :param s1: First string
    :param s2: Second string
    :return: Edit distance between 's1' and 's2'
    """
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

def closeStringInList(str, list):
    """
    Finds closest string (by edit distance) from 'str' in 'list'
    :param str: string to find closest term to
    :param list: list to find closest string within
    :return: Closest string in 'list' to 'str'
    """
    distances = [levenshteinDistance(str, s) for s in list]
    return distances.index(min(distances))

def preprocDescrip():
    """
    Calculates similarities between concentration and club descriptions for friend recommendations
    :return:
    """
    # Load lists of descriptions
    concentrations = pickle.load(open("nlp/concentrations.p", "rb"))
    descr = pickle.load(open("nlp/concentrationDescr.p", "rb"))

    orgInfo = pickle.load(open("nlp/orgInfo.p", "rb"))
    orgNames = pickle.load(open("nlp/orgNames.p", "rb"))

    # Add org names to descriptions; remove the word 'Harvard'
    for i, org in enumerate(orgInfo):
        org = org.replace("harvard", "")
        orgInfo[i] = str(orgNames[i]).lower() + " " + str(org).lower()

    # Calculate pairwise similarities
    orgInfoLists = tc.getSimilarityLists(orgInfo)
    concentrationLists = tc.getSimilarityLists(descr)

    # Store results for future retrieval
    pickle.dump(orgInfoLists, open("nlp/orgInfoLists.p", "wb"))
    pickle.dump(concentrationLists, open("nlp/concentrationLists.p", "wb"))

## Helpers for event description translation
def performSpellCorrection(text):
    """
    Autocorrects spelling
    :param text: Input text to correct spelling for
    :return: Text with spelling corrected
    """
    checker = SpellChecker("en_US", text)
    for word in checker:
        word.replace(spell(word.word))

    return checker.get_text()
