import numpy as np
from Device import *

class Resistor(Device):
	
        def __init__(self, n1, n2, value, rows):
		self.n1 = n1
		self.n2 = n2
		self.rows = rows
		self._value = value
		self._g = 1./value
	
	@property
	def g(self, v=0, time=0):
		return self._g
		
	@g.setter
	def g(self,g):
		self._g = g
		self._value = 1./g
		
	@property
	def value(self, v=0, time=0):
		return self._value
		
	@value.setter
	def value(self, value):
		self._value = value
		self._g = 1./value
		  
	def get_stamp(self):
		stamp = np.zeros((self.rows,self.rows))
		stamp[self.n1,self.n1] = stamp[self.n1,self.n1] + self.g
		stamp[self.n1,self.n2] = stamp[self.n1,self.n2] - self.g
                stamp[self.n2,self.n1] = stamp[self.n2,self.n1] - self.g
                stamp[self.n2,self.n2] = stamp[self.n2,self.n2] + self.g
                return stamp
