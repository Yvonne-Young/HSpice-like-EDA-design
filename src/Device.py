import numpy as np

class Device(object):

    def __init__(self, part_id=None, n1=None, n2=None, value=None):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.value = value

    def g(self, v):
        return 1./self.value