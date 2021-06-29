
from igraph import Graph
from igraph import plot
from IPython import display
from numpy import histogram, max
import matplotlib.pyplot as plt

def task1():
	n = 13
	d = n/4
	probs = [10**(-i/d) for i in range(n, -1, -1)]
	print(len(probs))
	coef_clustering = []
	avg_shortest_path = []
	coef0 = -1
	avg0 = -1
	for i in range(0,len(probs)):
		ws = Graph.Watts_Strogatz(1,2000,20,probs[i])
		coef_clustering.append(ws.transitivity_undirected())
		avg_shortest_path.append(ws.average_path_length())
		if(coef0 == -1):
			coef0 = coef_clustering[0]
			avg0 = avg_shortest_path[0]
		coef_clustering[i] /= coef0
		avg_shortest_path[i] /= avg0
	
	#print(coef_clustering)
	#print(avg_shortest_path)		
		
	plt.plot(probs, coef_clustering, 's', probs, avg_shortest_path, 'o')
	plt.xlabel('Probability')
	plt.xscale('log')
	#plt.savefig('plot_task_1.png', bbox_inches='tight')
	plt.show()



	
if __name__ == "__main__":
	task1()
	
