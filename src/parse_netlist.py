#This file is to read netlist input and extract elements as well as command lines

import string
from Device import *
from Resistor import *
from Isc import *
from Vsrc import *
from VCVS import *
from CCCS import *
from VCCS import *
from CCVS import *
from C import *
from L import *
from diode import *
from MOSFET import *

def netlist_parse(file_name):
    #open the test input file
    netlist = open(file_name,'r')
    output_elements = open('output_elements.txt','w')
    output_stamps = open('output_stamps.txt','w')
    
    #define some lists and parameters
    title = "title"
    line_n = 0
    line_elements = []
    devices = []
    controls = []
    models = []
    node_labels = []
    values = []
    float_values = []
    names = []
    analysis_type = []

    dc_start = 0
    dc_end = 0
    dc_step = 0
    ac_start = 0
    ac_end = 0
    tran_start = 0
    tran_end = 0
    MOSFET_flag = 0
    diode_flag = 0
    option = None

    #analyze the given circuit
    while True:
        line=netlist.readline()
        if len(line) == 0:
            break               #EOF
        line_n = line_n + 1
        line = line.strip()
        if line_n == 1:
            line = line.lower()
            title = line        #the first line is title
            continue
        elif len(line) == 0:
            line = line.lower()
            continue            #empty line
        if line[0] == "*":
            line = line.lower()
            continue            #comment lines
    
        #read commands
        if line[0] == ".":
            line = line.lower()
            line_elements = line.split()
            if line_elements[0] == '.end':
                break           #end of netlist
            elif line_elements[0] == '.plot':   #plot
                controls.append((line,line_n))
            elif line_elements[0] == '.print':  #print
                controls.append((line,line_n))
            elif line_elements[0] == '.dc':     #dc analysis
                controls.append((line,line_n))
                analysis_type.append('dc')
                dc_vname = line_elements[1]
                dc_start = line_elements[2]
                dc_end = line_elements[3]
                dc_step = line_elements[4]
            elif line_elements[0] == '.op':     #op points
                controls.append((line,line_n))
                analysis_type.append('op')
            elif line_elements[0] == '.ac':     #ac analysis
                controls.append((line,line_n))
                analysis_type.append('ac')
                ac_start = line_elements[1]
                ac_end = line_elements[2]
            elif line_elements[0] == '.tran':   #transient analysis
                controls.append((line,line_n))
                analysis_type.append('tran')
                tran_start = line_elements[1]
                tran_end = line_elements[2]
            elif line_elements[0] == '.model':  #model
                models.append((line,line_n))
            elif line_elements[0] =='.option':
                option = line_elements[1]
        elif line[0].isalpha():                 #devices and to distinguish the magnitude
            devices.append(line)            #of M and m, don't lower the letters
    
    #extract node and value of each device
    for i in devices:
        device = i.split()
        if device[0][0] == 'R':         #Resistor
            names.append(device[0])
            values.append(device[3])
            node_labels.append(device[1:3])
        elif device[0][0] == 'L':       #Inductor
            names.append(device[0])
            values.append(device[3])
            node_labels.append(device[1:3])
        elif device[0][0] == 'C':       #Capacitor
            names.append(device[0])
            values.append(device[3])
            node_labels.append(device[1:3])
        elif device[0][0] == 'I':       #I source
            names.append(device[0])
            values.append(device[3])
            node_labels.append(device[1:3])
        elif device[0][0] == 'V':       #V source
            names.append(device[0])
            #values.append(device[3])
            node_labels.append(device[1:3])
            if device[3] == 'SIN(0':
                values.append('0')
            else:
                values.append(device[3])
        elif device[0][0] == 'E':       #VCVS
            names.append(device[0])
            values.append(device[5])
            node_labels.append(device[1:3])
        elif device[0][0] == 'F':       #CCCS
            names.append(device[0])
            values.append(device[5])
            node_labels.append(device[1:3])
        elif device[0][0] == 'G':       #VCCS
            names.append(device[0])
            values.append(device[5])
            node_labels.append(device[1:3])
        elif device[0][0] == 'H':       #CCVS
            names.append(device[0])
            values.append(device[5])
            node_labels.append(device[1:3])
        elif device[0][0] == 'D':       #diode
            names.append(device[0])
            values.append('0')
            node_labels.append(device[1:3])
            diode_flag = 1
        elif device[0][0] == 'M':       #MOSFET
            names.append(device[0])
            values.append('0')
            node_labels.append(device[1:4])
            MOSFET_flag = 1
       
    #handle the magnitude of values and transform the type of value
    #from string into float
    for value in values:
        value_len = len(value)
        if value[value_len - 1] == 'K' or value[value_len - 1] == 'k':
            tmp = float(value[0:value_len - 1])
            value = tmp * 1000.0
            float_values.append(value)
        elif value[value_len - 1] == 'M':
            tmp = float(value[0:value_len - 1])
            value = tmp * 1000000
            float_values.append(value)
        elif value[value_len - 1] == 'm':
            tmp = float(value[0:value_len - 1])
            value = tmp * 0.001
            float_values.append(value)
        elif value[value_len - 1] == 'U' or value[value_len - 1] == 'u':
            tmp = float(value[0:value_len - 1])
            value = tmp * 0.000001
        elif value[value_len - 1] == 'N' or value[value_len - 1] == 'n':
            tmp = float(value[0:value_len - 1])
            value = tmp / 1000000.0
            float_values.append(value)
        elif value[value_len - 1].isalnum():
            float_values.append(float(value))

        #get the number of nodes of the circuit and then decide the number
    #of rows of the MNA matrix
        num_of_nodes = 0
        for nodes in node_labels:
            if nodes[0] > num_of_nodes:
                num_of_nodes = nodes[0]
            elif nodes[1] > num_of_nodes:
                num_of_nodes = nodes[1]
        num_of_nodes = int(num_of_nodes) + 1

        stamps = []     #to store the stamps of all the elements
        RHS = []        #to store the necessary RHS of some elements

        elements = []   #the list of all the elements and their basic info 
        
        for i in devices:
            device = i.split()
            if device[0][0] == 'R':
                index = devices.index(i)
                v = float_values[index]
                res = Resistor(int(device[1]),int(device[2]),v,num_of_nodes)
                r_stamp = res.get_stamp()
                stamps.append(r_stamp)
                elements.append(res)
            elif device[0][0] == 'I':
                index = devices.index(i)
                v = float_values[index]
                isc = Isc(int(device[1]),int(device[2]),v,num_of_nodes)
                i_stamp = isc.get_stamp()
                RHS.append(i_stamp)
                elements.append(isc)
            elif device[0][0] == 'V':
                index = devices.index(i)
                v = float_values[index]
                vsc = Vsrc(int(device[1]),int(device[2]),v,num_of_nodes)
                v_stamp_with_rhs = vsc.get_stamp()
                tmp = num_of_nodes + 1
                v_stamp = v_stamp_with_rhs[0:tmp,0:tmp]
                stamps.append(v_stamp)
                v_rhs = v_stamp_with_rhs[:,tmp]
                RHS.append(v_rhs)
                elements.append(vsc)
            elif device[0][0] == 'E':
                index = devices.index(i)
                v = float_values[index]
                vcvs = VCVS(int(device[1]),int(device[2]),int(device[3]),int(device[4]),v,num_of_nodes)
                vcvs_stamp = vcvs.get_stamp()
                stamps.append(vcvs_stamp)
                elements.append(vcvs)
            elif device[0][0] == 'F':
                index = devices.index(i)
                v = float_values[index]
                index_vc = node_labels.index(device[3:5])       #get node label of controller
                vc = float_values[index_vc]                     #get the value of controller(the controller must be a voltage source)
                cccs = CCCS(int(device[1]),int(device[2]),int(device[3]),int(device[4]),v,vc,num_of_nodes)
                cccs_stamp_with_rhs = cccs.get_stamp()
                tmp = num_of_nodes + 1
                cccs_stamp = cccs_stamp_with_rhs[0:tmp,0:tmp]
                stamps.append(cccs_stamp)
                cccs_rhs = cccs_stamp_with_rhs[:,tmp]
                RHS.append(cccs_rhs)
                elements.append(cccs)
            elif device[0][0] == 'G':
                index = devices.index(i)
                v = float_values[index]
                vccs = VCCS(int(device[1]),int(device[2]),int(device[3]),int(device[4]),v,num_of_nodes)
                vccs_stamp = vccs.get_stamp()
                stamps.append(vccs_stamp)
                elements.append(vccs)
            elif device[0][0] == 'H':
                index = devices.index(i)
                v = float_values[index]
                index_vc = node_labels.index(device[3:5])       #get node labels of controller
                vc = float_values[index_vc]                     #get the value of controller(the controller must be a voltage source)
                ccvs = CCVS(int(device[1]),int(device[2]),int(device[3]),int(device[4]),v,vc,num_of_nodes)
                ccvs_stamp_with_rhs = ccvs.get_stamp()
                tmp = num_of_nodes + 2
                ccvs_stamp = ccvs_stamp_with_rhs[0:tmp,0:tmp]
                stamps.append(ccvs_stamp)
                ccvs_rhs = ccvs_stamp_with_rhs[:,tmp]
                RHS.append(ccvs_rhs)
                elements.append(ccvs)
            elif device[0][0] == 'C':
                index = devices.index(i)
                v = float_values[index]
                c = []
                c_stamp = []
                c = C(int(device[1]),int(device[2]),v,num_of_nodes)
                c_stamp = c.get_stamp()
                stamps.append(c_stamp)
                elements.append(c)
            elif device[0][0] == 'L':
                index = devices.index(i)
                v = float_values[index]
                l = L(int(device[1]),int(device[2]),v,num_of_nodes)
                l_stamp =  l.get_stamp()
                stamps.append(l_stamp)
                elements.append(l)
            elif device[0][0] == 'D':
                index = devices.index(i)
                dio = diode(int(device[1]),int(device[2]))
                elements.append(dio)
            elif device[0][0] == 'M':
                node = [device[3],device[1]]
                index = node_labels.index(node)
                vgs = float_values[index]
                mos = MOSFET(device[1],device[2],device[3],int(device[4]),int(device[5]),\
                        vgs,device[6])
                elements.append(mos)
                        
    #output the circuit infos to a txt file named output_elements.txt
    output_elements.write("The title of this circuit is:")
    output_elements.write(title)
    output_elements.write('\n')
    output_elements.write("\nThe following lines are definitions of devices:\n")
    for i in devices:
        output_elements.write(str(i))
        output_elements.write('\n')
    
    output_elements.write("\nThe following lines are some command lines:\n")
    for i in controls:
        output_elements.write(str(i))
        output_elements.write('\n')
    
    output_elements.write("\nThe following lines are definitions of models:\n")
    for i in models:
        output_elements.write(str(i))
        output_elements.write('\n')
    
    output_elements.write("\nThe following are the names of the devices:\n")
    for i in names:
        output_elements.write(i)
        output_elements.write(',')
    
    output_elements.write("\n\nThe following are the node labels:\n")
    for i in node_labels:
        output_elements.write(str(i))
        output_elements.write(',')
    
    output_elements.write("\n\nThe following are the values of the devices:\n")
    for i in float_values:
        output_elements.write(str(i))
        output_elements.write('\n')

    #output the stamps to a txt file named output_stamps.txt
    output_stamps.write("The stamps of each elements in this circuit are:\n")
    for i in stamps:
        output_stamps.write(str(i))
        output_stamps.write('\n')
                
    output_stamps.write("The RHSs of this circuit is:\n")
    for i in RHS:
        output_stamps.write(str(i))
        output_stamps.write('\n')
    
    netlist.close()
    output_elements.close()
    
    return elements,num_of_nodes,analysis_type,ac_start,ac_end,dc_start,dc_end,dc_step,\
            tran_start,tran_end,MOSFET_flag,diode_flag,option
