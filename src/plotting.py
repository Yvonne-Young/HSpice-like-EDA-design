from simulation import *
import pylab as pl
import math
import matplotlib.pyplot as plt

def plotting(file_name):
    x,results,analysis_type = simulation(file_name)
    v_node = []
    if type(results[0]) == float:
        pass
    else:
        ind = len(results[0]) - 1
    AMP = []
    PHASE = []

    #plot different curves based on analysis type
    if analysis_type[0] == 'op':
        pass
    elif analysis_type[0] == 'dc':
        if type(results[0]) == float:
            plt.title('dc sweep')
            plt.plot(x,results)
            plt.show()
        else:
            while ind != -1:
                for r in results:
                    v_node.append(r[ind])
                plt.title('dc sweep')
                plt.plot(x,v_node)
                plt.show()
                v_node = []
                ind = ind - 1
    elif analysis_type[0] == 'ac':
        while ind != -1:
            for r in results:
                v = r[ind]
                amplitude = math.sqrt((np.real(v))**2 + (np.imag(v))**2)
                AMP.append(amplitude)
                phase = np.angle(v)
                PHASE.append(phase)
            plt.figure(ind)
            plt.subplot(121)
            plt.title('Amplitude')
            plt.plot(x,AMP)
            plt.subplot(122)
            plt.title('Phase')
            plt.plot(x,PHASE)
            plt.show()
            ind = ind - 1
            AMP = []
            PHASE = []
    elif analysis_type[0] == 'tran':
        while ind != -1:
            for r in results:
                v_node.append(r[ind][0])
            plt.plot(x,v_node)
            plt.show()
            v_node = []
            ind = ind - 1
        

if __name__ == '__main__':
    plotting('netlist_test/netlist_test_diode_tran.txt')
