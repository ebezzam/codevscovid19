from sklearn.neighbors import KDTree
import numpy as np

class Volunteers:
	def __init__(self):
		self.list = {}
		self.g = None
		self.ind2phone = {}

	def add_volunteer(self, phone_num,coordinates,is_available,delivery_slots):
		vol_info = {phone_num:[coordinates,is_available,delivery_slots]}
		self.list.update(vol_info)
		self.update_graph()

	# create a new tree with the volunteers coordinates
	def update_graph(self):
		coordinates = []
		for ind,it in enumerate(self.list.items()):
			key,vals = it
			coordinates.append(vals[0])
			self.ind2phone[ind] = key

		coordinates = np.array(coordinates)
		self.g = KDTree(coordinates,leaf_size=2)

	# find closest volunteers, given the search/query coordinate
	def find_nearest_volunteers(self,search_coord,num_volunteers=1):
		dists, inds = self.g.query(search_coord,k=num_volunteers)
		nearest_volunteers = []

		for i in inds[0]:
			phone_num = self.ind2phone[i]
			vol_info = {phone_num:self.list[phone_num]}
			nearest_volunteers.append(vol_info)
		return dists, nearest_volunteers

if __name__ == "__main__":
	vols = Volunteers()
	vols.add_volunteer(1,[2,9],1,1)
	vols.add_volunteer(2,[6,1],1,1)
	vols.add_volunteer(3,[7,6],1,1)
	vols.add_volunteer(4,[2,3],1,1)
	vols.add_volunteer(5,[4,0],1,1)
	query = np.array([[5,1]])
	dists,nn_vols = vols.find_nearest_volunteers(query,3)
	print(dists)
	print(nn_vols)
