import os
import sys

os.environ['SPARK_HOME'] = '/usr/lib/spark'
os.environ['PYSPARK_PYTHON'] = '/usr/local/bin/python2.7'
os.environ['PYSPARK_SUBMIT_ARGS'] = ('--packages com.databricks:spark-csv_2.10:1.5.0 pyspark-shell')
os.environ['JAVA_TOOL_OPTIONS'] = "-Dhttps.protocols=TLSv1.2"

sys.path.append('/usr/lib/spark/python')
sys.path.append('/usr/lib/spark/python/lib/py4j-0.9-src.zip')

# Rerun to clear space (ctrl+F5), select all above this and execute in console option+shift+E, and go on execution in
# console the code
from pyspark import SparkContextfi
from pyspark import HiveContext
from preprocess import *
import math
import CustomGUI as gui
from collections import Counter
import operator
import webbrowser

RESULTS_PER_PAGE = 10
n_profiles = 20950


sc = SparkContext()
sqlContext = HiveContext(sc)

df = sc.textFile('file:///home/cloudera/Desktop/instagram_bio_dataset')
profiles = df.map(lambda line: (line.split(',')[1],line.split(',')[2])).mapValues(preprocess)
keyvalueflat = profiles.flatMapValues(lambda word: word)
invertkey = keyvalueflat.map(lambda (k,v): (v,k))

def to_list(a):
    return [a]

def append(a, b):
    a.append(b)
    return a

def extend(a, b):
    a.extend(b)
    return a

profiles_per_word = invertkey.combineByKey(to_list,append,extend)
inverted_i = profiles_per_word.collect()

inverted_index = {}

for w in inverted_i:
    word = w[0].encode('ascii')
    for u in w[1]:
        user = u.encode('ascii')
        inverted_index.setdefault(word, {})[user] = inverted_index.setdefault(word, {}).get(user, 0) + 1


# document frequency = number of docs containing a specific word, dictionary with key = word, value = num of docs
df = {}
# inverse document frequency
idf = {}

for key in inverted_index.keys():
    df[key] = len(inverted_index[key].keys())
    idf[key] = math.log(n_profiles / df[key], 2)


def tf_idf(w, doc):
    return inverted_index[w][doc] * idf[w]


def inner_product_similarities(query):
    # dictionary in which I'll sum up the similarities of each word of the query with each document in
    # which the word is present, key is the doc number,
    # value is the similarity between query and document
    similarity = {}
    for w in query:
        wq = idf.get(w, 0)
        if wq != 0:
            for doc in inverted_index[w].keys():
                similarity[doc] = similarity.get(doc, 0) + tf_idf(w, doc) * wq
    return similarity


def doc_length(userid):
    words_accounted_for = []
    length = 0
    for w in profiles[userid]:
        if w not in words_accounted_for:
            length += tf_idf(w, userid) ** 2
            words_accounted_for.append(w)
    return math.sqrt(length)


def query_length(query):
    # IMPORTANT: in this HW no query has repeated words, so I can skip the term frequency calculation
    # for the query, and just use idfs quared
    length = 0
    cnt = Counter()
    for w in query:
        cnt[w] += 1
    for w in cnt.keys():
        length += (cnt[w]*idf.get(w, 0)) ** 2
    return math.sqrt(length)


def cosine_similarities(query):
    similarity = inner_product_similarities(query)
    for doc in similarity.keys():
        similarity[doc] = similarity[doc] / doc_length(doc) / query_length(query)
    return similarity


def rank_docs(similarities):
    return sorted(similarities.items(), key=operator.itemgetter(1), reverse=True)


def new_query():
    query = gui.ask_query()
    if query is None:
        exit()
    # print(query)
    query_tokens = preprocess(query)
    ranked_similarities = rank_docs(cosine_similarities(query_tokens))
    handle_show_query(ranked_similarities, query_tokens, RESULTS_PER_PAGE)


def handle_show_query(ranked_similarities, query_tokens, n):
    choice = gui.display_query_results(ranked_similarities[:n], query_tokens)

    if choice == 'Show more results':
        handle_show_query(ranked_similarities, query_tokens, n + RESULTS_PER_PAGE)
    else:
        if choice is None:
            new_query()
        else:
            open_website(choice)


def open_website(url):
    webbrowser.open('https://www.instagram.com/'+url.split()[0]+'/', new=2, autoraise=True)


new_query()



sc.stop()
