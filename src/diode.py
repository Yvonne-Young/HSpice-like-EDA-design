import numpy as np
from Device import *

class diode(Device):
	
	def __init__(self,n1,n2,AREA=None,T=None,ic=None,off=False):
		self.is_nonlinear = True
		self.AREA = AREA if AREA is not None else 1.0
		self.T = T 
		self.n1 = n1
		self.n2 = n2
		self.ic = ic
		self.off = off
		
		if self.off:
			if self.ic is None:
				self.ic = 0
			else:
				print("(W): IC statement in diodes takes precedence over OFF.")
	
		