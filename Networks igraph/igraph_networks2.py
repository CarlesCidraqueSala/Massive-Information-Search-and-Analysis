from igraph import Graph
from igraph import plot
from IPython import display
from numpy import histogram, max
import matplotlib.pyplot as plt


def task2():
    g = Graph(directed=False)
    g = g.Load('./edges.txt', format='edgelist', directed=False)
    print("Número de arcos: ", len(g.es()))
    print("Número de vértices: ", len(g.vs()))
    print("Diámetro del grafo: ", g.diameter())
    print("Transitivity del grafo: ", g.transitivity_undirected())
    print("Degree distribution: ",  g.degree_distribution())
    print(g.degree())
    #plot(g)
    page_ranks = g.pagerank()
    page_ranks = [page_ranks[i]*1000 for i in range(0,len(page_ranks))]
    plot(g,vertex_size = page_ranks)
    
    #PARTE 2
    com = g.community_edge_betweenness()
    #print(com)
    clusters = com.as_clustering()
    #print(clusters)
    clusters_tam = clusters.sizes()
    print(clusters_tam)
    print("Tamaño del community más grande: ",max(clusters_tam))

    plt.hist(clusters_tam, bins=range(min(clusters_tam),max(clusters_tam) + 2, 1), align='left')
    plt.ylabel('Number of communities')
    plt.xlabel('Community size')
    plt.show()
    
    #plot(g, vertex.color=membership(clusters))
    #print(membership(clusters))
    plot(clusters)
    
if __name__ == "__main__":
    task2()
