import nltk
from dateutil import parser
from timex import *
from helpers import *

class readNewEventInfo():
    """
    Extracts event information from user input text
    """
    def run(self, text):
        """
        Extracts information from input 'text'
        :param text: Input to extract event description from
        :return: List of event info [location, attendees, preferred times, event title]
        """

        # Preprocess text via spell correction and tokenization
        input_text = text
        input_text = performSpellCorrection(input_text)
        ex = self.preprocessText(input_text)

        # Chunks sentences and gets named entities
        chunkedSentences = nltk.ne_chunk(ex, binary=False)

        # Retrieves Name, Location, Person, Time
        input_text = text.lower()
        time = self.parseTime(input_text)

        # Extracts people in the sentence
        person = []
        for tree in chunkedSentences:
            # Print results per sentence
            # print extract_entity_names(tree)
            person.extend(self.getTextForAttr(tree, "PERSON"))

        # Extracts location in the sentence
        location = []
        for tree in chunkedSentences:
            # Print results per sentence
            # print extract_entity_names(tree)
            location.extend(self.getTextForAttr(tree, "ORGANIZATION"))

        # Get event name via a set phrase pattern
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

        # Returns list of event info
        events = [location, person, time, vps[0]]
        return events

    def preprocessText(self, sent):
        """
        Tokenize and tag each word
        :param sent: Input text to process
        :return: Processed text
        """
        sent = nltk.word_tokenize(sent)
        sent = nltk.pos_tag(sent)
        return sent

    def getTextForAttr(self, processed_text, attr):
        """
        Extracts entity names of type 'attr' from 'processed_text'
        :param processed_text: Pre-processed text with attribute labels
        :param attr: Attribute type to extract from processed text
        :return: Words from processed text with the desired attribute
        """
        t = processed_text
        entity_names = []
        if hasattr(t, 'label') and t.label:
            if t.label() == attr:
                entity_names.append(' '.join([child[0] for child in t]))
            else:
                for child in t:
                    entity_names.extend(self.getTextForAttr(child, attr))

        return entity_names

    def parseTime(self, text):
        """
        Parses time phrases from input 'text'
        :param text: Text to parse
        :return: Times in 'yr-month-day' format
        """
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
