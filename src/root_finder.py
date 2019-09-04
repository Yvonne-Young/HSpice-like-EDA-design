from scipy.misc import derivative
from math import *
import numpy as np
import matplotlib.pyplot as plt

def func(x):
    return (2.0/3.0)*x - (5.0/3.0) + exp(40*x)

def root_finder(x):
    f1 = derivative(func,x,dx=1e-6)
    y = x - (1.0/f1)*func(x)
    return y,func(x)

if __name__ == "__main__":
    x = root_finder(0.1)
    x_iteration_process = []
    print x[0]
    func_iteration_process = []
    for i in range(1,10):
        x = root_finder(x[0])
        print x[0]
        x_iteration_process.append(x[0])
        func_iteration_process.append(func(x[0]))
    plt.figure(1)
    plt.subplot(121)
    plt.title("iteration process")
    plt.plot(x_iteration_process,func_iteration_process,'r^')
    m = np.arange(-1.0,1.0,0.02)
    n = [(2.0/3.0)*x - (5.0/3.0) + exp(40*x) for x in m]
    plt.subplot(122)
    plt.title("equation derived from diode circuit")
    plt.plot(m,n)
    plt.show()

