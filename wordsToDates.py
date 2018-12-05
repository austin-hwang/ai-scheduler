import nltk
from dateutil import parser
from timex import *
from helpers import *

class wordsToDates():

    def run(self, text):
        # fname = "input.txt"
        # with open(fname) as f:
        #     content = f.readlines()
        # for line in content:
        input_text = text
        input_text = performSpellCorrection(input_text)
        ex = self.preprocessText(input_text)

        # Chunks and gets named entities
        chunkedSentences = nltk.ne_chunk(ex, binary=False)

        # Name, Location, Person, Time
        input_text = text.lower()
        time = self.parseTime(input_text)

        person = []
        for tree in chunkedSentences:
            # Print results per sentence
            # print extract_entity_names(tree)
            person.extend(self.getTextForAttr(tree, "PERSON"))

        location = []
        for tree in chunkedSentences:
            # Print results per sentence
            # print extract_entity_names(tree)
            location.extend(self.getTextForAttr(tree, "ORGANIZATION"))


        # Get event name
        pattern = 'VerbPhrase: {<VB>?<NN>*<IN>}'
        cp = nltk.RegexpParser(pattern)
        cs = cp.parse(ex)
        vps = []
        for line in cs:
            try:
                if(line.label() == 'VerbPhrase'):
                    vps.append([x[0] for x in line[:-1]])
            except:
                continue

        events = [location, person, time, vps[0]]
        return events
        # Tokenization, parts of speech tagging

    def preprocessText(self, sent):
        sent = nltk.word_tokenize(sent)
        sent = nltk.pos_tag(sent)
        return sent

    def parseTime(self, text):
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

    def getTextForAttr(self, processed_text, attr):
        t = processed_text
        entity_names = []
        if hasattr(t, 'label') and t.label:
            if t.label() == attr:
                entity_names.append(' '.join([child[0] for child in t]))
            else:
                for child in t:
                    entity_names.extend(self.getTextForAttr(child, attr))

        return entity_names

    def preprocessText(self, sent):
        sent = nltk.word_tokenize(sent)
        sent = nltk.pos_tag(sent)
        return sent

    def parseTime(self, text):
        # Hour and Minute
        h = []
        for word in text.split(' '):
            try:
                d = parser.parse(word, fuzzy=True)
                # Parser will parse days too. Don't want those added to time
                if(d.day == today().day and d.month == today().month and d.year == today().year):
                    h.append([d.hour, d.minute / 60., d.second / 3600])
            except:
                continue

        # Date
        taggedLine = tag(text)
        time = ground(taggedLine, gmt())
        try:
            matchObj = re.search(r'val(.*)(">?)', time, flags=0)
            matchObj = re.findall('"([^"]*)"', matchObj.group(0))
        except:
            matchObj = []

        return [h, matchObj]
