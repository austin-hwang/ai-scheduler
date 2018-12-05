import nltk
with open('sample.txt', 'r') as f:
    sample = f.read()

sentences = nltk.sent_tokenize(sample)
tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

def extractEntityNames(t):
    entityNames = []

    if hasattr(t, 'label') and t.label:
        print("tree")
        print(t)
        print(t.label())
        if t.label() == 'NE':
            entityNames.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entityNames.extend(extractEntityNames(child))

    return entityNames

entityNames = []
for tree in chunked_sentences:
    # Print results per sentence
    # print extractEntityNames(tree)
    entityNames.extend(extractEntityNames(tree))

# Print all entity names
#print entityNames

# Print unique entity names
print set(entityNames)

from dateutil import parser
print(parser.parse("coffee tomorrow at 11am", fuzzy=True))
