"""
.. module:: GeneratePrototypes

GeneratePrototypes
******

:Description: GeneratePrototypes

    Different Auxiliary functions used for different purposes

:Authors:
    bejar

:Version: 

:Date:  14/07/2017
"""

from numpy.random import choice

import argparse

__author__ = 'bejar'

#redefinimos funcion split para que no haya problemas con el path, ya que tenemos dos ":" uno del propio path (C:) y el otro que separa el path y los términos que definen un documento
def split(strng, sep, pos):
    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='documents.txt',  help='Data with the examples')
    parser.add_argument('--nclust', default=2, type=int, help='Number of clusters')

    args = parser.parse_args()

    f = open(args.data, 'r')

    ldocs = []
    for line in f:
        doc, words = split(line, ':', 2) #usando funcion split redefinida
        #doc, words = line.split(':')
        ldocs.append(words)

   # Generate nclust prototypes with nclust random documents
    doc = choice(range(len(ldocs)), args.nclust)
    f = open('prototypes.txt', 'w')
    for i, d in enumerate(doc):
        docvec = ''
        for v in ldocs[d].split():
            docvec += (v+'+1.0 ')
        f.write('CLASS'+str(i) + ':' + docvec.encode('ascii','replace').decode() + '\n')
    f.flush()
    f.close()

