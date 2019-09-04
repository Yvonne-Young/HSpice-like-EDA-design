import numpy as np 
from Device import *

class C(Device):

	def __init__(self, n1, n2, value, rows):
		self.n1 = n1
		self.n2 = n2
		self.value = value
		self.rows = rows

	def get_stamp(self):
		stamp = np.zeros((self.rows,self.rows),dtype=complex)
		stamp[self.n1,self.n1] = complex(0,self.value)
		stamp[self.n1,self.n2] = complex(0,-self.value)
		stamp[self.n2,self.n1] = complex(0,-self.value)
		stamp[self.n2,self.n2] = complex(0,self.value)
		return stamp
