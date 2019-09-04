import numpy as np 
from Device import *

class CCVS(Device):

	def __init__(self, n1, n2, nc1, nc2, value, vc, rows):
		self.n1 = n1
		self.n2 = n2
		self.nc1 = nc1
		self.nc2 = nc2
		self.value = value
		self.rows = rows
		self.vc = vc

	def get_stamp(self):
		rows = self.rows + 2
		ic_row = self.rows + 1
		cols = rows + 1
		stamp = np.zeros((rows,cols))
		stamp[self.n1,self.rows] = 1.0
		stamp[self.n2,self.rows] = -1.0
		stamp[self.nc1,ic_row] = 1.0
		stamp[self.nc2,ic_row] = -1.0
		stamp[self.rows,self.n1] = 1.0
		stamp[self.rows,self.n2] = -1.0
		stamp[self.rows,ic_row] = -self.value
		stamp[ic_row,self.nc1] = 1.0
		stamp[ic_row,self.nc2] = -1.0
		stamp[ic_row,rows] = self.vc
		return stamp
