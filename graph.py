from sklearn.neighbors import KDTree
import numpy as np
import math

# from lat long to x, y, z
def cartesian(latitude, longitude, elevation = 0):
    # Convert to radians
    latitude = latitude * (math.pi / 180)
    longitude = longitude * (math.pi / 180)

    R = 6371 # 6378137.0 + elevation  # relative to centre of the earth
    X = R * math.cos(latitude) * math.cos(longitude)
    Y = R * math.cos(latitude) * math.sin(longitude)
    Z = R * math.sin(latitude)
    return [X, Y, Z]

# at the moment matching is supported for one customer. loop breaks if a match is found for one customer.
def match(vol_list,cust_list,callby='vol_class'):
	matched_vol = None
	matched_cust = None
	matched_time = None
	#make a kd-tree of volunteers with lat and lonf
	coordinates = []
	for ind,it in enumerate(vol_list):
		cart_coord = cartesian(float(it.latitude),float(it.longitude))
		coordinates.append(cart_coord)

		coordinates = np.array(coordinates)
		tree = KDTree(coordinates,leaf_size=2)

	# loop to find nearest vol and then check with overlapping timings.
	# TODO: for more customers 
		# remove the previous  matched volunteer
		# modify the return type handling in all the underlyinng functions
	for cust in cust_list:
		query_cart_coord = cartesian(float(cust.latitude),float(cust.longitude))
		query_cart_coord = np.array(query_cart_coord).reshape(1,3)
		dist,inds = tree.query(query_cart_coord,k=min(len(vol_list),3))

		inds= inds[0]
		timing = set(cust.delivery_by)
		for ind in inds:
			a = set(vol_list[ind].available_times)
			overlap = timing.intersection(a)
			if len(overlap) > 0:
				matched_time = list(overlap)[0]
				matched_cust = cust
				matched_vol = vol_list[ind]
				break

	if callby == 'vol_class':
		return matched_vol.number, matched_cust, matched_time
	else:
		return matched_cust.number, matched_vol, matched_time
	# if callby == 'vol_class':
	# 	return vol_list[0].number, cust_list[0]
	# else:
	# 	return cust_list[0].number, vol_list[0]


class VolunteerInfo:
	def __init__(
            self,
            number,
            street_number=None,
            street=None,
            city=None,
            country=None,
            longitude=None,
            latitude=None,
            available_times=None
    ):
		self.number = number
		self.longitude = longitude
		self.latitude = latitude
		self.street_number = street_number
		self.street = street
		self.city = city
		self.country = country
		self.available_times = available_times
		

class CustomerInfo:
	def __init__(
            self,
            number,
            street_number=None,
            street=None,
            city=None,
            country=None,
            longitude=None,
            latitude=None,
            order=None,
            delivery_by=None
    ):
		self.number = number
		self.longitude = longitude
		self.latitude = latitude
		self.street_number = street_number
		self.street = street
		self.city = city
		self.country = country
		self.order= order
		self.delivery_by = delivery_by

class Volunteers:

	# init for the class
	def __init__(self):
		self.list = {}
		self.g = None
		self.ind2phone = {}
		# keep the volunteers waiting to be matched here
		self.active_vol_list = []

	# update the info of a particular volunteer and find a match if exists
	def update_data(self, info, active_customers):

		if [*info][0] == 'phone_num' and len([*info]) == 1:
			cust_info  = {info['phone_num']:VolunteerInfo(number=info['phone_num'])}
			self.list.update(cust_info)
			print('Added a volunteer num:{}'.format(info['phone_num']))
		elif 'address_info' in [*info]:
			self.list[info['phone_num']].longitude = info['address_info'][0]
			self.list[info['phone_num']].latitude = info['address_info'][1]
			self.list[info['phone_num']].street_number = info['address_info'][2]["house_number"]
			self.list[info['phone_num']].street = info['address_info'][2]["road"]
			self.list[info['phone_num']].city = info['address_info'][2]["city"]
			self.list[info['phone_num']].country = info['address_info'][2]["country"]
			print('updated volunteer num:{} coor:{}'.format(info['phone_num'],info['address_info']))
		elif 'available_times' in [*info]:
			self.list[info['phone_num']].available_times = info['available_times']
			print('updated volunteer num:{} is_available:{}'.format(info['phone_num'],info['available_times']))

		number = info['phone_num']
		# if all the required fields are updated, move the volunteer to the active list 
		if self.list[number].longitude is not None and self.list[number].latitude is not None and self.list[number].available_times is not None :
			self.active_vol_list.append(self.list[number])
		
		# if both the customer and voluteer active list is not empty , try to match
		if len(self.active_vol_list)>0 and len(active_customers)>0:
			selected_vol_number, selected_cust, matched_time= match(self.active_vol_list,active_customers,callby='vol_class')
			# no appropriate match found
			if selected_vol_number is None:
				return None, None, None
			selected_vol = self.list[selected_vol_number]
			#remove the selected vol from the active list
			self.active_vol_list.remove(self.list[selected_vol_number])
			#remove the selected customer from the active list
			active_customers.remove(selected_cust)
			return selected_vol, selected_cust, matched_time
		else:
			return None, None, None

	def get_address(self,number):
		address = self.list[number].street + ' ' + self.list[number].street_number + ' ' + self.list[number].city
		return address

	# add a volunteer with their details
	def add_volunteer(self, phone_num, volunteer_info):
		vol_info = {phone_num:volunteer_info}
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


class Customers:

	# init for the class
	def __init__(self):
		self.list = {}
		# keep the customers waiting to be matched here
		self.active_cust_list = []

	# update the info of a particular customer and find a match if exists
	def update_data(self, info, active_vols):
		
		if [*info][0] == 'phone_num' and len([*info]) == 1:
			cust_info = {info['phone_num']:CustomerInfo(number=info['phone_num'])}
			self.list.update(cust_info)
			print('Added a customer num:{}'.format(info['phone_num']))
		elif 'address_info' in [*info]:
			self.list[info['phone_num']].longitude = info['address_info'][0]
			self.list[info['phone_num']].latitude = info['address_info'][1]
			self.list[info['phone_num']].street_number = info['address_info'][2]["house_number"]
			self.list[info['phone_num']].street = info['address_info'][2]["road"]
			self.list[info['phone_num']].city = info['address_info'][2]["city"]
			self.list[info['phone_num']].country = info['address_info'][2]["country"]
			print('updated customer num:{} coor:{}'.format(info['phone_num'],info['address_info']))
		elif 'order' in [*info]:
			self.list[info['phone_num']].order = info['order']
			print('updated customer num:{} order'.format(info['phone_num']))
		elif 'delivery_by' in [*info]:
			self.list[info['phone_num']].delivery_by = info['delivery_by']
			print('updated customer num:{} delivery_by:{}'.format(info['phone_num'],info['delivery_by']))

		number = info['phone_num']
		# if all the required fields are updated, move the customer to the active list 
		if self.list[number].longitude is not None and self.list[number].latitude is not None \
				and self.list[number].order is not None and self.list[number].delivery_by is not None:
			self.active_cust_list.append(self.list[number])
		
		# if both the customer and voluteer active list is not empty , try to match
		if len(self.active_cust_list)>0 and len(active_vols)>0:
			selected_cust_number, selected_vol, matched_time = match(active_vols,self.active_cust_list,callby='cust_class')
			# no appropriate match found
			if selected_cust_number is None:
				return None, None, None
			selected_cust = self.list[selected_cust_number]
			#remove the selected customer from the active list
			self.active_cust_list.remove(self.list[selected_cust_number])
			#remove the selected vol from the active list
			active_vols.remove(selected_vol)
			return selected_vol, selected_cust, matched_time
		else:
			return None, None, None

	def get_address(self,number):
		address = self.list[number].street + ' ' + self.list[number].street_number + ' ' + self.list[number].city	
		return address

	# add a new customer with their details
	def add_customer(self, phone_num, customer_info):
		cust_info = {phone_num:customer_info}
		self.list.update(cust_info)

	# remove a customer
	def remove_customer(self, phone_num):
		self.list.pop(phone_num,None)

	# flag to set if customer is served
	def set_serve():
		self.is_served = True

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
