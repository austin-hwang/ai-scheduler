import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

from enchant.checker import SpellChecker
from autocorrect import spell

#perform spell correction
def performSpellCorrection(text):
    checker = SpellChecker("en_US", text)
    for word in checker:
        word.replace(spell(word.word))

    return checker.get_text()

# Tokenization, parts of speech tagging
def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

from dateutil import parser
from timex import *
def parse_time(text):
    # Hour and Minute
    d = parser.parse(text, fuzzy=True)
    h = [d.hour, d.minute / 60., d.second / 3600]

    # Date
    taggedLine = tag(text)
    time = ground(taggedLine, gmt())
    try:
        matchObj = re.search(r'val(.*)(">?)', time, flags=0)
        matchObj = re.findall('"([^"]*)"', matchObj.group(0))
    except:
        matchObj = []
    return [h, matchObj]

def get_text_for_attr(processed_text, attr):
    t = processed_text
    entity_names = []
    if hasattr(t, 'label') and t.label:
        if t.label() == attr:
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(get_text_for_attr(child, attr))

    return entity_names

if __name__ == '__main__':
    fname = "input.txt"
    with open(fname) as f:
        content = f.readlines()
    for line in content:
        input_text = line
        input_text = performSpellCorrection(input_text)
        ex = preprocess(input_text)

        # Chunks and gets named entities
        chunked_sentences = nltk.ne_chunk(ex, binary=False)

        # Name, Location, Person, Time
        time = parse_time(input_text);

        person = []
        for tree in chunked_sentences:
            # Print results per sentence
            # print extract_entity_names(tree)
            print(tree)
            person.extend(get_text_for_attr(tree, "PERSON"))

        location = []
        for tree in chunked_sentences:
            # Print results per sentence
            # print extract_entity_names(tree)
            location.extend(get_text_for_attr(tree, "ORGANIZATION"))
        events = [location, person, time]

        # For redo of location
        from nltk.tag import StanfordNERTagger
        from nltk.tokenize import word_tokenize

        # st = StanfordNERTagger('/usr/share/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
        #                        '/usr/share/stanford-ner/stanford-ner.jar',
        #                        encoding='utf-8')
        #
        # text = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'
        #
        # tokenized_text = word_tokenize(text)
        # classified_text = st.tag(tokenized_text)
        # print(classified_text)
        import pyteaser
        print(pyteaser.Summarize("", input_text))
        print(events)

        # sentence = "Mark and John are working at Google."
        #
        # print nltk.ne_chunk(pos_tag(word_tokenize(ex)))
