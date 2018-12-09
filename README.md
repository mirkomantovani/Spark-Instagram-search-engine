# Instagram Search Engine

## Fast and Scalable Inverted Index construction with Spark

Mirko Mantovani\
Computer Science department\
University of Illinois at Chicago\
Chicago, Illinois\
[mmanto2@uic.edu](mailto:email@email.com)

# ABSTRACT

This document is a report for the final project of IDS 561 Big Data
Analytics at University of Illinois at Chicago.

I decided to build a search engine for Instagram based on users’
biography. Since Instagram itself only allows the finding of users whose
username contains your query as a substring, finding users based on
their biography, which in most cases contains important keywords, could
be beneficial to users.

The repository containing the software can be accessed through GitHub
at:

[/mirkomantovani/Spark-Instagram-search-engine](https://github.com/mirkomantovani/Spark-Instagram-search-engine)

# 1 SOFTWARE DESCRIPTION

It is clear that a big data approach is needed to solve this problem.
Search engines achieve good performances by using an Inverted Index
which, given a word (key), returns all the documents (values) which
contain that word and their Term Frequencies.

The construction of an inverted index is an extremely parallel task and
in principle, it would be possible to preprocess and index every profile
present on Instagram in parallel. This suggests using a scalable and
distributed framework to build the Inverted Index.

# 2 DATASET

As I mentioned in the project proposal, crawling data from Instagram is
not an easy task, especially since, due to the recent privacy issues,
Instagram limited the number of requests per hour using unofficial APIs
to 200.

Therefore, to have significant amount of data, I deployed a Python
script that used the InstagramAPI Python package on an EC2 instance of
Amazon Web Services and let it run for a few days. I was able to collect
20950 unique profiles with non-null biography, a small dataset that was
sufficient for the purpose of this demo project.

# 3 TECHNICAL DETAILS

## 3.1 Software used

I used Apache Spark and in particular, its Python implementation
(PySpark) on the cloudera virtual machine that we used during the
course. I used Python version 2.7 to write the code.

## 3.2 Preprocessing and user representation

The users’ biography is initially in a text form. The initial
preprocessing consists in creating the user representation following a
bag of word approach and using their biography. The preprocessing is
done by the function preprocess(doc) in preprocess.py. This named
function is passed to the Spark mapValues, after a key-value pair RDD
consisting of username-biography is built.

In particular, the preprocessing function does this: given the biography
as a text string, it splits it on whitespaces, removes punctuations in
each word, removes the digits, removes word which have a length less or
equal to 2 and converts all the words to lowercase, then returns the
list of words.

## 3.3 Building the inverted index

After the preprocessing step, the key-(list of tokens) pairs are
transformed in key-word pairs using the Spark flatMapValues function.
The next step was to invert key-value in value-key, in order to have a
key which is the word and not the user anymore. The last step was to
combineByKey, to build a word-(list of usernames) pair, which basically
is our inverted index. I then computed the IDF of each word and created
a TF-IDF function that uses the inverted index and the IDF to compute
the TF-IDF of that word for a specific user.

## 3.4 Query lookup

At query time, the user inserts the query, which is preprocessed by the
program, and each word present in the query is used as key to retrieve
all the documents containing that word. Using the TF-IDF of each word,
the cosine similarity between the query and each biography that contains
at least one word present in the query is computed, the profiles are
then ordered by cosine similarity and the results are displayed. The
user can decide to show more results or open the profile of a user in
the retrieved list.

# 4 RESULTS

Evaluating the results is not an easy task for this type of
applications, because of the lack of labels in the data, but I manually
tested it and the retrieved results are relevant for the query, which is
usually very specific and short for this type of search engine.



