from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import math

from scipy.interpolate import InterpolatedUnivariateSpline

class sin(object):

    # SIN(VO VA FREQ TD THETA)

    def __init__(self, vo, va, freq, td=0., theta=0., phi=0.):
        self.vo = vo
        self.va = va
        self.freq = freq
        self.td = td
        self.theta = theta
        self.phi = phi
        self._type = "V"

    def __call__(self,time):
        if time is None:
            time = 0
        else:
            return self.vo + self.va*math.sin(2*math.pi*self.freq*time)

    def __str__(self):
        return "type=sin " + \
            self._type.lower() + "o=" + str(self.vo) + " " + \
            self._type.lower() + "a=" + str(self.va) + \
            " freq=" + str(self.freq) + " theta=" + str(self.theta) + \
            " td=" + str(self.td)
