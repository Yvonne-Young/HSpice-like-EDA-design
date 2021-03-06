import numpy as np 
from Device import *

class L(Device):

	def __init__(self, n1, n2, value, rows):
		self.n1 = n1
		self.n2 = n2
		self.value = value
		self.rows = rows

	def get_stamp(self):
		rows = self.rows + 1
		stamp = np.zeros((rows,rows),dtype=complex)
		stamp[self.n1,self.rows] = 1.0
		stamp[self.n2,self.rows] = -1.0
		stamp[self.rows,self.n1] = 1.0
		stamp[self.rows,self.n2] = -1.0
		stamp[self.rows,self.rows] = complex(0,-self.value)
		return stamp
