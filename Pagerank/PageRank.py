#!/usr/bin/python

from __future__ import division
from collections import defaultdict
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = set() # set of airports that have this as destination
        self.routeHash = defaultdict(int) # routeHash[origin] = weight
        self.outdegree = 0
        self.pageRank= 0

    def __repr__(self):
        return "{0:4s}\t{1:.8f}\t{2}".format(self.code, self.pageRank, self.name)

edgeList = [] # list of Edge
edgeHash = defaultdict(int) # edgeHash[(origin, destination)] = weight
airportList = [] # list of Airport
airportHash = dict() # airportHash[code] = Airport

EPSILON = 1e-15
MAX_ITERATIONS = 1000
DAMPING_FACTOR = 0.85




def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print("There were {0} Airports with IATA code".format(cont))


def readRoutes(fd):
    print ("Reading Routes file from {0}".format(fd))

    routesTxt = open(fd, "r")
    valid = invalid = 0
    for line in routesTxt.readlines():
        line = line.split(',')
        origin = line[2]
        destination = line[4]

        # Discard invalid IATA codes
        if len(origin) != 3 or len(destination) != 3:
            invalid += 1
            continue
        if origin not in airportHash or destination not in airportHash:
            invalid += 1
            continue

        e = Edge(origin)
        edgeList.append(e)
        edgeHash[(origin, destination)] += 1

        originAirport = airportHash[origin]
        destinationAirport = airportHash[destination]

        # Origin updates
        originAirport.outdegree += 1

        # Destination updates
        destinationAirport.routes.add(origin)
        destinationAirport.routeHash[origin] += 1

        valid += 1

    routesTxt.close()
    print ("There were {0} valid routes".format(valid))
    print ("There were {0} invalid routes".format(invalid))


def stop_condition(it, PageRank_ant):
    if it >= MAX_ITERATIONS:
        return True

    PageRank_act = [airport.pageRank for airport in airportList]
    for act,ant in zip(PageRank_act, PageRank_ant):
        if abs(act - ant) > EPSILON:
            return False

    return True


def computePageRank(i):
    dest_Airport = airportList[i]
    if dest_Airport.outdegree == 0:
        return 1.0/len(airportList)

    pageRank = 0
    for origin in dest_Airport.routes:
        originAirport = airportHash[origin]
        edgeWeight = dest_Airport.routeHash[origin]
        pageRank += originAirport.pageRank * edgeWeight/originAirport.outdegree

    return pageRank


def iniciar_PageRanks(n):
    for airport in airportList:
        airport.pageRank = 1/n


def updatePageRanks(Q, PageRank_ant):
    for i, airport in enumerate(airportList):
        PageRank_ant[i] = airport.pageRank
        airport.pageRank = Q[i]


def computePageRanks():
    print ("")
    print ("The epsilon is {0} ".format(EPSILON))
    print ("The damping factor is {0} ".format(DAMPING_FACTOR))
    print ("The maximum number of iterations is {0} ".format(MAX_ITERATIONS))
    n = len(airportList)
    iniciar_PageRanks(n)

    PageRank_ant = [0] * n
    it = 0
    while not stop_condition(it, PageRank_ant):

        Q = [0] * n
        for i in range(0, n):
            Q[i] = DAMPING_FACTOR*computePageRank(i) + (1-DAMPING_FACTOR)/n
            airport = airportList[i]
        updatePageRanks(Q, PageRank_ant)
        it += 1

    return it


def outputPageRanks():
    print ("")

    print ("IATA\tPageRank\tName")

    ranking = sorted(airportList, key = lambda a: a.pageRank, reverse = True)
    for rank, airport in enumerate(ranking):
        print (str(airport))



def main():
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:",iterations)
    print("Time of computePageRanks():",time2-time1)
    


if __name__ == "__main__":
    sys.exit(main())