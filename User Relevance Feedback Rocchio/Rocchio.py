"""
.. module:: SearchIndexWeight
SearchIndex
*************
:Description: SearchIndexWeight
    Performs a AND query for a list of words (--query) in the documents of an index (--index)
    You can use word^number to change the importance of a word in the match
    --nhits changes the number of documents to retrieve
:Authors: bejar
    
:Version: 
:Created on: 04/07/2017 10:56 
"""

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

import argparse

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from elasticsearch.client import CatClient

import numpy as np
import operator

__author__ = 'bejar'

"""
PREVIOUS LAB FUNCTIONS
"""

def doc_count(client, index):
    """
    Returns the number of documents in an index
    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])

def search_file_by_path(client, index, path):
    """
    Search for a file using its path
    :param path:
    :return:
    """
    s = Search(using=client, index=index)
    q = Q('match', path=path) 
    s = s.query(q)
    result = s.execute()

    lfiles = [r for r in result]
    if len(lfiles) == 0:
        raise NameError('File [' + path + '] not found');
    else:
        return lfiles[0].meta.id

def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term
    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'], doc_type=['_doc'],
                                    positions=False, term_statistics=True, )

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())

def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """
    norm = 0;
    twRet = {};

    for (_, tfidf) in tw.items():
        norm = norm + tfidf**2;

    norm = np.sqrt(norm);

    for (t, tfidf) in tw.items():
        if norm == 0:
            twRet[t] = 0.0
        else: 
            twRet[t] = float(tfidf)/float(norm);

    return twRet;

def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document
    :param file:
    :return:
    """
    file_tv, file_df = document_term_vector(client, index, file_id)

    max_freq = max([f for _, f in file_tv]) # max f en el doc

    dcount = doc_count(client, index)   # num de docs en el indice

    tfidfw = {}
    for (t, w),(_, df) in zip(file_tv, file_df):
        tf  = w / max_freq;
        idf = np.log2((dcount / df));
        tfidfw[t] = tf * idf;
    return normalize(tfidfw) 

def transfDict(query):
    dict_result = {}
    for element in query:
        if '^' in element:
            word, value = element.split('^')
            value = int(value)
            dict_result[word] = value
        else:
            if('~' in element):
                word, value = element.split('~')
                value = 1
                dict_result[word] = value
            else:
                word = element
                value = 1
                dict_result[word] = value
    return (dict_result)

def transfQuery(dic):
    query_result = []
    for word, value in dic.items():
        element = word + '^' + str(value)
        query_result.append(element)
    return query_result

def TFIDFdict(queryDict, reldocs, client, index):
    resTFIDF = {}

    for word,_ in queryDict.items():
        resTFIDF[word] = 0

    for doc in reldocs:
        id = search_file_by_path(client, index, doc.path)
        tfidf_doc = toTFIDF(client, index, id)
        for word,_  in queryDict.items():
            resTFIDF[word] += tfidf_doc[word]

    return resTFIDF

def Rocchio(alpha,beta,queryDict,dictTFIDF,nhits):
    query= {}
    for word, weight in queryDict.items():
        prom = dictTFIDF[word]/nhits
        new = float(alpha)*float(weight) + float(beta)*float(prom)
        query[word] = new
    return query

"""
MAIN 
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nhits', default=10, type=int, help='Number of hits to return')
    parser.add_argument('--nrounds', default=1, type=int, help='Iterations of Rocchio Law formula')
    parser.add_argument('-R', default=None, type=int, help="Maximum number of new terms to be kept in q'")
    parser.add_argument('--alpha', default=None, type=int, help='Alpha')
    parser.add_argument('--beta', default=None, type=int, help='Beta')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    index = args.index
    query = args.query
    nhits = args.nhits
    nrounds = args.nrounds
    r = args.R
    alpha = args.alpha
    beta = args.beta

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        if query is not None:
            q = Q('query_string',query=query[0])
            for i in range(1, len(query)):
                q &= Q('query_string',query=query[i])

            s = s.query(q)
            response = s[0:nhits].execute()

            # transformamos la query en formato dict-> term, peso para llamar a TFIDFdict
            queryDict = transfDict(query)
            print('i = 0, ' + 'q = ' + str(query))
            #tfidfw para cada término de la query
            tfidfw_query = TFIDFdict(queryDict,response,client,index)


            #Aplicamos Rocchio
            for i in range(1,nrounds-1):
                queryDict = Rocchio(alpha, beta, queryDict, tfidfw_query, nhits)
                newQuery = transfQuery(queryDict)
                print('i = ' + str(i-1) + ', q = ' + str(newQuery))

                q = Q('query_string',query=newQuery[0])
                for i in range(1, len(query)):
                    q &= Q('query_string',query=newQuery[i])

                s = s.query(q)
                response = s[0:nhits].execute()
                tfidfw_query = TFIDFdict(queryDict, response, client, index)

            #query n-1, unicamente llamamos a Rocchio para recalcular los nuevos pesos de importancia de la query i
            #transformamos el formato dict -> termino, peso a formato original de la query
            queryDict = Rocchio(alpha, beta, queryDict, tfidfw_query, nhits)
            newQuery = transfQuery(queryDict)
            print('i = ' + str(nrounds-1) + ', q = ' + str(newQuery))


            q = Q('query_string',query=newQuery[0])
            for i in range(1, len(query)):
                q &= Q('query_string',query=newQuery[i])

            s = s.query(q)
            response = s[0:nhits].execute()

            for r in response:
                print('ID=' + r.meta.id + ' SCORE=' + str(r.meta.score))
                print('PATH=' + r.path)
                print('TEXT: ' + r.text[:50])
                print('-----------------------------------------------------------------')

        else:
            print('No query parameters passed')

        print (str(response.hits.total['value']) + " Documents")

    except NotFoundError:
        print('Index ' + str(index) + ' does not exists')