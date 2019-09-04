import numpy as np
from Device import *

un = 3800
up = -1800
Cox = 6
VTN = 0.43
VTP = -0.4

class MOSFET(Device):

	    #def __init__(self,ns,nd,ng,W,L,vgs,vds,nmos):
            def __init__(self,ns,nd,ng,W,L,vgs,nmos):
			
                self.ns = ns
		self.nd = nd
		self.ng = ng
		self.W = W
		self.L = L
		self.vgs = vgs
		#self.vds = vds
		self.nmos = nmos 	#to determine whether a nmos or a pmos
		if self.nmos == 'nmos':
                    self.u = un
                    self.VT = VTN
                else:
                    self.u = up
                    self.VT = VTP
                self.Cox = Cox
            '''
	    def get_gm_and_gds(self):

                if self.nmos = 'nmos':
                    gm = (self.W / self.L) * Kn * self.vds
                    gds = (self.W / self.L) * Kn * (self.vgs - VTn - self.vds)
                elif self.nmos = 'pmos':
                    gm = (self.W / self.L) * Kp * self.vds
                    gds = (self.W / self.L) * Kp * (self.vgs - VTp - self.vds)

                return gm,gds
            '''

            
			
		
