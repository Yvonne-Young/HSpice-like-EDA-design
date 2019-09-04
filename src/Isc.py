import numpy as np 
from Device import *

class Isc(Device):

	def __init__(self, n1, n2, value, rows):
		self.n1 = n1
		self.n2 = n2
		self.value = value
		self.rows = rows

	def get_stamp(self):
		stamp = np.zeros((self.rows, 1))
		stamp[self.n1,0] = -self.value
		stamp[self.n2,0] = self.value
		return stamp 