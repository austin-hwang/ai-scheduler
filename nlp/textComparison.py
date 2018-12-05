import gensim
import os
from nltk.tokenize import word_tokenize

class textComparison():
    
    def calcSimilarityMat(self, inputString, eventDescriptions):
        descr = eventDescriptions
        gen_docs = [[w.lower() for w in word_tokenize(text)]
                    for text in descr]

        # Maps each token to a number
        dictionary = gensim.corpora.Dictionary(gen_docs)

        # List of bag-of-words: number of times each word occurs (of those that do) in a document
        corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]

        # Calculates importance of a term in a document (balances term frequency 'frequency' and inverse document frequency 'uniqueness')
        tf_idf = gensim.models.TfidfModel(corpus)
        print(tf_idf)

        # Cosine similarity
        sims = gensim.similarities.Similarity(os.getcwd(), tf_idf[corpus],
                                              num_features=len(dictionary))

        query_doc = [w.lower() for w in word_tokenize(inputString)]
        query_doc_bow = dictionary.doc2bow(query_doc)
        query_doc_tf_idf = tf_idf[query_doc_bow]
        return sims[query_doc_tf_idf]

    def getSimilarityLists(self, eventDescriptions):
        similarityList = []
        cnt = 0
        print("Done", cnt)
        for desc in eventDescriptions:
            similarityList.append(self.calcSimilarityMat(desc, eventDescriptions))
            print("Done", cnt)
            cnt += 1
        return similarityList

