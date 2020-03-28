from sklearn.neighbors import KDTree
import numpy as np

# create a new tree for the given list of volunteers coordinates
def update_graph(volunteer_coordinates):
	g = KDTree(volunteer_coordinates,leaf_size=2)
	return g

# find closest volunteers, given the search/query coordinate and the graph
def find_nearest_volunteers(search_coord,graph,num_volunteers=1):
	dist, ind = graph.query(search_coord,k=num_volunteers)
	return dist,ind

if __name__ == "__main__":
	X = np.random.randint(10,size=10).reshape(5,2)
	g = update_graph(X)
	query = np.random.randint(10,size=2).reshape(1,2)
	dist,ind = find_nearest_volunteers(query,g,num_volunteers=3)
	print(X)
	print(query)
	print(dist)
	print(X[ind])
