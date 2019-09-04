import numpy as np 
from Device import *

class VCCS(Device):

	def __init__(self, n1, n2, nc1, nc2, value, rows):
		self.n1 = n1
		self.n2 = n2
		self.nc1 = nc1
		self.nc2 = nc2
		self.value = value
		self.rows = rows

	def get_stamp(self):
		stamp = np.zeros((self.rows,self.rows))
		stamp[self.n1,self.nc1] = self.value
		stamp[self.n1,self.nc2] = -self.value
		stamp[self.n2,self.nc1] = -self.value
		stamp[self.n2,self.nc2] = self.value
		return stamp