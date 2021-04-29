import numpy as np
from parse_netlist import *
from root_finder import *
import pylab as pl
import math
import matplotlib.pyplot as plt
from vsin import *

#add rows or cols to a matrix
def expand_matrix(matrix, add_a_row=False, add_a_col=False):
    n_row, n_col = matrix.shape
    if add_a_col:
        col = np.zeros((n_row, 1))
        matrix = np.concatenate((matrix, col), axis=1)
    if add_a_row:
        if add_a_col:
            n_col = n_col + 1
        row = np.zeros((1, n_col))
        matrix = np.concatenate((matrix, row), axis=0)
    return matrix

#remove rows or cols of a matrix
def remove_row_and_col(matrix, rrow=0, rcol=0):
    if rrow is not None and rcol is not None:
        return np.vstack((np.hstack((matrix[0:rrow, 0:rcol],
                                     matrix[0:rrow, rcol+1:])),
                          np.hstack((matrix[rrow+1:, 0:rcol],
                                     matrix[rrow+1:, rcol+1:]))
                          ))
    elif rrow is not None:
        return np.vstack((matrix[:rrow, :], matrix[rrow+1:, :]))
    elif rcol is not None:
        return np.hstack((matrix[:, :rcol], matrix[:, rcol+1:]))

#get the mna and rhs of the circuit when transient
def get_mna(file_name,time=0,Vc_past=0,Vc_past_past=0,Il_past=0,vd=0,omega = 0,v_dc = 0):
    elements,num_of_nodes,analysis_type,ac_start,ac_end,dc_start,dc_end,dc_step,\
        tran_start,tran_end,MOSFET_flag,diode_flag,option = netlist_parse(file_name)

    if analysis_type[0] == 'ac':
        mna = np.zeros((num_of_nodes,num_of_nodes),dtype = complex)
    elif analysis_type[0] == 'tran':
        mna = np.zeros((num_of_nodes,num_of_nodes),dtype = float)
    else:
        mna = np.zeros((num_of_nodes,num_of_nodes))
    N = np.zeros((num_of_nodes,1))
    h = 0.5     #step
    global index_C      #get the index to search the RHS
    global index_L      #get the index to search the RHS
    global index_diode  #get the index to search the RHS

    index_C = 0
    index_L = 0
    index_diode = 0
    coeff = 0
    
    for elem in elements:
        if isinstance(elem,Resistor):
            mna[elem.n1,elem.n1] = mna[elem.n1,elem.n1] + elem.g
            mna[elem.n1,elem.n2] = mna[elem.n1,elem.n2] - elem.g
            mna[elem.n2,elem.n1] = mna[elem.n2,elem.n1] - elem.g
            mna[elem.n2,elem.n2] = mna[elem.n2,elem.n2] + elem.g
        elif isinstance(elem,Isc):
            N[elem.n1,0] = N[elem.n1,0] + elem.value
            N[elem.n2,0] = N[elem.n2,0] - elem.value
        elif isinstance(elem,VCCS):
            mna[elem.n1,elem.nc1] = mna[elem.n1,elem.nc1] + elem.value
            mna[elem.n1,elem.nc2] = mna[elem.n1,elem.nc2] - elem.value
            mna[elem.n2,elem.nc1] = mna[elem.n2,elem.nc1] - elem.value
            mna[elem.n2,elem.nc2] = mna[elem.n2,elem.nc2] + elem.value
        elif isinstance(elem,diode):    #depend on the vd of last iteration result
            mna[elem.n1,elem.n1] = mna[elem.n1,elem.n1] + 40*exp(40*vd)
            mna[elem.n1,elem.n2] = mna[elem.n1,elem.n2] - 40*exp(40*vd)
            mna[elem.n2,elem.n1] = mna[elem.n2,elem.n1] - 40*exp(40*vd)
            mna[elem.n2,elem.n2] = mna[elem.n2,elem.n2] + 40*exp(40*vd)
            N[elem.n1,0] = N[elem.n1,0] + (40*exp(40*vd)*vd - (exp(40*vd) - 1))
            N[elem.n2,0] = N[elem.n2,0] - (40*exp(40*vd)*vd - (exp(40*vd) - 1))
            diode_flag = 1
            index_diode = int(elem.n1)
        elif isinstance(elem,MOSFET):
            MOSFET_flag = 1
        else:
            index = mna.shape[0]
            mna = expand_matrix(mna,add_a_row=True,add_a_col=True)
            N = expand_matrix(N,add_a_row=True,add_a_col=False)
            mna[elem.n1,index] = 1.0
            mna[elem.n2,index] = -1.0
            mna[index,elem.n1] = 1.0
            mna[index,elem.n2] = -1.0
            if isinstance(elem,Vsrc):
                if analysis_type[0] == 'dc':
                    N[index,0] = 1.0 * v_dc
                if analysis_type[0] == 'tran' and diode_flag == 1:
                    N[index,0] = 1.0 * v_dc
                else:
                    N[index,0] = 1.0 * elem.value
            elif isinstance(elem,VCVS):
                mna[index,elem.nc1] = -1.0 * elem.value
                mna[index,elem.nc2] = 1.0 * elem.value
            elif isinstance(elem,CCVS):
                mna = expand_matrix(mna,add_a_row=True,add_a_col=True)
                index_1 = index + 1
                mna[elem.nc1,index_1] = mna[elem.nc1,index_1] + 1
                mna[elem.nc2,index_1] = mna[elem.nc2,index_1] - 1
                mna[index_1,elem.nc1] = mna[index_1,elem.nc1] + 1
                mna[index_1,elem.nc2] = mna[index_1,elem.nc2] - 1
                mna[index,index_1] = mna[index,index_1] - elem.value
                N[index_1,0] = N[index_1,0] + self.vc
            elif isinstance(elem,CCCS):
                mna[elem.n1,index] = mna[elem.n1,index] + elem.value
                mna[elem.n2,index] = mna[elem.n2,index] - elem.value
                N[index,0] = N[index,0] + elem.vc
            elif isinstance(elem,C):        #need different mnas based on the analysis type
                if analysis_type[0] == 'tran':
                    if option == 'be':
                        mna[index,elem.n1] = mna[index,elem.n1] * elem.value/h
                        mna[index,elem.n2] = mna[index,elem.n2] * elem.value/h
                        mna[index,index] = mna[index,index] - 1
                        N[index,0] = N[index,0] + (elem.value/h) * Vc_past
                        index_C = mna.shape[0] - 2
                    elif option == 'tr':
                        mna[index,elem.n1] = mna[index,elem.n1] * 2 * elem.value / h
                        mna[index,elem.n2] = mna[index,elem.n2] * 2 * elem.value / h
                        mna[index,index] = mna[index,index] - 1
                        N[index,0] = N[index,0] + (2 * elem.value / h) * Vc_past + elem.value * \
                                     (Vc_past - Vc_past_past) / h
                        index_C = mna.shape[0] - 2
                elif analysis_type[0] == 'ac':
                    mna[elem.n1,elem.n1] = mna[elem.n1,elem.n1] + complex(0,omega*elem.value)
                    mna[elem.n1,elem.n2] = mna[elem.n1,elem.n2] - complex(0,omega*elem.value)
                    mna[elem.n2,elem.n1] = mna[elem.n2,elem.n1] - complex(0,omega*elem.value)
                    mna[elem.n2,elem.n2] = mna[elem.n2,elem.n2] + complex(0,omega*elem.value)
                    remove_row_and_col(mna,index,index)
                coeff = h / elem.value
            elif isinstance(elem,L):        #need different mnas based on the analysis type
                if analysis_type[0] == 'tran':
                    if option == 'be':
                        mna[index,index] = mna[index,index] - elem.value/h
                        N[index,0] = N[index,0] - (elem.value/h) * Il_past
                        index_L = mna.shape[0] - 2
                    elif option == 'tr':
                        pass
                elif analysis_type[0] == 'ac':
                    mna[index,index] = mna[index,index] + complex(0,-omega*elem.value)
                    index_L = mna.shape[0] - 2
    mna = remove_row_and_col(mna,0,0)
    N = remove_row_and_col(N,0,None)
    return mna,N,coeff

#dc sweep analysis with a format of '.DC VAR START END STEP'
def dc_sim(file_name,start,end,step):
    elements,num_of_nodes,analysis_type,ac_start,ac_end,dc_start,dc_end,dc_step,\
                tran_start,tran_end,MOSFET_flag,diode_flag,option = netlist_parse(file_name)
    
    if MOSFET_flag == 0:	
        fp = open('output_dc.txt','w')
        results = []
        v_dc = start
        x = []
        size = 0
        while v_dc < end:
            mna,N,coeff = get_mna(file_name,0,0,0,0,0,0,v_dc)
            x.append(v_dc)
            v_dc = v_dc + step
            result = np.linalg.solve(mna,N)
            results.append(result)
            size = mna.shape[0]

        #output the results of each step to the file 'output_dc.txt'
        fp.write('===============DC Sweep results=============\n')
        for i in results:
            fp.write(str(i))
            fp.write('\n')
        fp.close()
        return x,results    #for the convinience of plotting
    else:
        fp = open('output_dc.txt','w')
        v_dc = start
        idss = []
        vdc = []
        
        for e in elements:
            if isinstance(e,MOSFET):
                if e.nmos == 'nmos':
                    while v_dc + step < end:
                        vdc.append(v_dc)
                        if v_dc < e.vgs - e.VT or v_dc == e.vgs - e.VT:
                            ids = (((e.u * e.Cox) * (float(e.W) / e.L)) / 2) * \
                              (2 * (e.vgs - e.VT) * v_dc - v_dc ** 2)
                        elif v_dc > e.vgs - e.VT:
                            ids = ((e.u * e.Cox) / 2) * (float(e.W) / e.L) * \
                              (e.vgs - e.VT) ** 2
                        else:
                            ids = 1
                        idss.append(ids)
                        v_dc = v_dc + step
                else:
                    while v_dc + step < end:
                        vdc.append(v_dc)
                        if abs(v_dc) < abs(e.vgs - e.VT) or abs(v_dc) == abs(e.vgs - e.VT):
                            ids = (((e.u * e.Cox) * (float(e.W) / e.L)) / 2) * \
                              (2 * (-e.vgs + e.VT) * v_dc - v_dc ** 2)
                            idss.append(ids)
                        elif v_dc > e.vgs - e.VT:
                            ids = ((e.u * e.Cox) / 2) * (float(e.W) / e.L) * \
                              (e.vgs - e.VT) ** 2
                            idss.append(ids)
                        v_dc = v_dc + step
            else:
                pass

        fp.write('===============DC Sweep results=============\n')
        for i in idss:
            fp.write(str(i))
            fp.write('\n')
        fp.close()
        return vdc,idss
        

def ac_sim(file_name,startf,endf):
    fp = open('output_ac.txt','w')
    results = []
    AMP = []
    PHASE = []
    for f in range(startf,endf):
        mna,N,coeff = get_mna(file_name,0,0,0,0,0,f)
        result = np.linalg.solve(mna,N)
        results.append(result)

    x = []
    num = 0
    
    for i in range(startf,endf):
        x.append(num)
        num = num + 1

    #output the results of each step to the file 'output_ac.txt'
    fp.write('===============AC Sweep results=============\n')
    for i in results:
        fp.write(str(i))
        fp.write('\n')
    fp.close()
    return x,results    #for the convinience of plotting
            

def tran_sim(file_name,start,end):
    results = []
    V_past = 0      #set the initial value
    I_past = 0      #set the initial value
    V_past_past = 0
    x = []

    elements,num_of_nodes,analysis_type,ac_start,ac_end,dc_start,dc_end,dc_step,\
                tran_start,tran_end,MOSFET_flag,diode_flag,option = netlist_parse(file_name)    
    #BE or TR
    if diode_flag == 0:
        print (diode_flag)
        if option == 'be':
            time = start
            while time < end + 0.5:
                matrix_now = get_mna(file_name,time,V_past,0,I_past)
                mna = matrix_now[0]
                N = matrix_now[1]
                result_now = np.linalg.solve(mna,N)
                results.append(result_now)
                V_past = result_now[index_C]
                I_past = result_now[index_L]
                x.append(time)
                time = time + 0.5
        else:
            for time in range(start,end):
                matrix_now = get_mna(file_name,time,V_past,V_past_past,I_past)
                mna = matrix_now[0]
                N = matrix_now[1]
                coeff = matrix_now[2]
                V_pasta_past = N[index_C] * coeff
                result_now = np.linalg.solve(mna,N)
                results.append(result_now)
                x.append(time)
                V_past = result_now[index_C]
                I_past = result_now[index_L]
    else:
        vsin = sin(0,5,50,100)
        time = start
        while time < end + 0.1:
            vd = 0.1
            v_dc = vsin.__call__(time)
            x.append(time)
            for nr in range(1,21):
                matrix_k = get_mna(file_name,time,V_past,0,I_past,vd,0,v_dc)
                mna = matrix_k[0]
                N = matrix_k[1]
                result_k = np.linalg.solve(mna,N)
                vd = result_k[index_diode - 1]
            matrix_now = get_mna(file_name,time,V_past,0,I_past,vd,0,v_dc)
            mna = matrix_now[0]
            N = matrix_now[1]
            result_now = np.linalg.solve(mna,N)
            results.append(result_now)
            time = time + 0.1
            V_past = result_now[index_C]
            I_past = result_now[index_L]

    fp = open('output_tran.txt','w')

    #output the results of each step to the file 'output_tran.txt'
    fp.write('===============TRAN Sweep results=============\n')
    for i in results:
        fp.write(str(i))
        fp.write('\n')
    fp.close()

    return x,results    #for the convinience of plotting

def op_sim(file_name):
    results = []
    matrix_init = get_mna(file_name)
    mna = matrix_init[0]
    N = matrix_init[1]
    elements,num_of_nodes,analysis_type,ac_start,ac_end,dc_start,dc_end,dc_step,\
        tran_start,tran_end,MOSFET_flag,diode_flag,option = netlist_parse(file_name)
    
    if diode_flag == 0:     #if there's no diode element in the circuit
        result = np.linalg.solve(mna,N)
        results.append(result)
    else:                   #if there's diode elements in the circuit
        vd = 0.1
        for i in range(1,21):   #iterate for 20 times
            matrix_now = get_mna(file_name,0,0,0,0,vd)
            mna = matrix_now[0]
            N = matrix_now[1]
            result_now = np.linalg.solve(mna,N)
            vd = result_now[index_diode-1]
        results.append(result_now)

    fp = open('op_points.txt','w')

    #output the operation points to the file 'op_points.txt'
    fp.write('===============Operation Points=============\n')
    for i in results:
        fp.write(str(i))
        fp.write('\n')   
    fp.close()
    return results

def simulation(file_name):
    elements,num_of_nodes,analysis_type,ac_start,ac_end,dc_start,dc_end,dc_step,\
        tran_start,tran_end,MOSFET_flag,diode_flag,option = netlist_parse(file_name)
    x = []
    results = []
    for an_type in analysis_type:   #choose different simulation functions based on sp file
        if an_type == 'op':
            results = op_sim(file_name)
        elif an_type == 'dc':
            x,results = dc_sim(file_name,int(dc_start),int(dc_end)+1,float(dc_step))
        elif an_type == 'ac':
            x, results = ac_sim(file_name,int(ac_start),int(ac_end)+1)
        elif an_type == 'tran':
            x,results = tran_sim(file_name,float(tran_start),float(tran_end)+1)
    return x,results,analysis_type

if __name__ == '__main__':
    simulation('netlist_test/netlist_test_ac.txt')
