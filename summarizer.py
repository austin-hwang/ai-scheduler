"""
Simple-Summarizer
A very simple summarizier built using NLP in Python
https://jodylecompte.com
https://github.com/jodylecompte/Simple-Summarizer
"""
import argparse

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.probability import FreqDist
from heapq import nlargest
from collections import defaultdict


def main():
    """ Drive the process from argument to output """
    args = parse_arguments()

    content = read_file(args.filepath)
    content = sanitize_input(content)

    sentence_tokens, word_tokens = tokenize_content(content)
    sentence_ranks = score_tokens(word_tokens, sentence_tokens)

    return summarize(sentence_ranks, sentence_tokens, args.length)


def parse_arguments():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='File name of text to summarize')
    parser.add_argument('-l', '--length', default=4, help='Number of sentences to return')
    args = parser.parse_args()

    return args


def read_file(path):
    """ Read the file at designated path and throw exception if unable to do so """
    try:
        with open(path, 'r') as file:
            return file.read()

    except IOError as e:
        print("Fatal Error: File ({}) could not be locaeted or is not readable.".format(path))


def sanitize_input(data):
    """
    Currently just a whitespace remover. More thought will have to be given with how
    to handle sanitzation and encoding in a way that most text files can be successfully
    parsed
    """
    replace = {
        ord('\f'): ' ',
        ord('\t'): ' ',
        ord('\n'): ' ',
        ord('\r'): None
    }

    return data.translate(replace)


def tokenize_content(content):
    """
    Accept the content and produce a list of tokenized sentences,
    a list of tokenized words, and then a list of the tokenized words
    with stop words built from NLTK corpus and Python string class filtred out.
    """
    stop_words = set(stopwords.words('english') + list(punctuation))
    words = word_tokenize(content.lower())

    return [
        sent_tokenize(content),
        [word for word in words if word not in stop_words]
    ]


def score_tokens(filterd_words, sentence_tokens):
    """
    Builds a frequency map based on the filtered list of words and
    uses this to produce a map of each sentence and its total score
    """
    word_freq = FreqDist(filterd_words)

    ranking = defaultdict(int)

    for i, sentence in enumerate(sentence_tokens):
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                ranking[i] += word_freq[word]

    return ranking


def summarize(ranks, sentences, length):
    """
    Utilizes a ranking map produced by score_token to extract
    the highest ranking sentences in order after converting from
    array to string.
    """
    if int(length) > len(sentences):
        print("Error, more sentences requested than available. Use --l (--length) flag to adjust.")
        exit()

    indexes = nlargest(length, ranks, key=ranks.get)
    final_sentences = [sentences[j] for j in sorted(indexes)]
    return ' '.join(final_sentences)


if __name__ == "__main__":
    print(main())
