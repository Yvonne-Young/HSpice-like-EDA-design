#This file is the UI definition of MySpice with tkinter
from Tkinter import *
import os
import tkFileDialog
from parse_netlist import *
from simulation import *
from plotting import *

#choose a file to open and show it in the text area
def open_file(text):
    default = "C:/Python27/netlist_test"
    global fname
    fname = tkFileDialog.askopenfilename(title="Choose File to Open",initialdir=(os.path.expanduser(default)))
    fp = open(fname,'r')
    while True:
        line = fp.readline()
        if len(line) == 0:
            break 
        else:
            text.insert(END,line)
    fp.close()
    text.insert(END,'\n================================================\n')
    
def show_readme():
    subwin = Tk()
    subwin.title('Read Me')
    subwin.geometry('800x300')
    content = Label(subwin,text=
"*This app is a Spice-like simulator developed by Yvonne Young*\n\n\
*It provides several analysis functions such as op,dc,ac,trans simulation*\n\n\
*Developed by python2.7,it uses libraries like numpy,matplotlib,scipy etc.*\n\n\
*This is a project done in the EDA course*")
    content.pack(side=TOP,pady=70)

def show_about():
    subwin = Tk()
    subwin.title('About')
    subwin.geometry('400x300')
    content = Label(subwin,text=
"*Author: Yvonne Young(Yifan Yang)*\n\n\
*University: Shanghai Jiao Tong University*\n\n\
*School: Micro/Nano-Electronic Engineering*\n\n\
*E-mail: yangyifan.15.7@sjtu.edu.cn*\n\n\
*Start Date: 2018/3/1*\n\n\
*Finish Date: 2018/5/6*\n\n\
*Version: 1.0*")
    content.pack(side=TOP,pady=50)

#when click on the button 'parse', call this function and print the outputs in the
#output text area
def parse(file_name,text):
    netlist_parse(file_name)
    print_elements = open('output_elements.txt','r')
    print_stamps = open('output_stamps.txt','r')
    while True:
        line = print_elements.readline()
        if len(line) == 0:
            break
        else:
            text.insert(END,line)
    while True:
        line = print_stamps.readline()
        if len(line) == 0:
            break
        else:
            text.insert(END,line)

#when click on the button 'simulate', call this function and print the outputs in the
#output text area
def simulate(file_name,text):
    x,results,analysis_type = simulation(file_name)
    if analysis_type[0] == 'op':
        print_op = open('op_points.txt','r')
        while True:
            line = print_op.readline()
            if len(line) == 0:
                break
            else:
                text.insert(END,line)
        print_op.close()
    elif analysis_type[0] == 'dc':
        print_dc = open('output_dc.txt','r')
        while True:
            line = print_dc.readline()
            if len(line) == 0:
                break
            else:
                text.insert(END,line)
        print_dc.close()
    elif analysis_type[0] == 'ac':
        print_ac = open('output_ac.txt','r')
        while True:
            line = print_ac.readline()
            if len(line) == 0:
                break
            else:
                text.insert(END,line)
        print_ac.close()
    elif analysis_type[0] == 'tran':
        print_tran = open('output_tran.txt','r')
        while True:
            line = print_tran.readline()
            if len(line) == 0:
                break
            else:
                text.insert(END,line)
        print_tran.close()

#when click on the button 'plot', call this function and get the plots
def netlist_plot(file_name):
    plotting(file_name)

#package the frames into a class    
class app:
    def __init__(self,master):
        frame = Frame(master)
        frame.pack()

        #show the netlist file
        self.netlist_text = Text(frame,height=24,width=50)
        self.netlist_text.pack(side=LEFT,pady=15)

        #show the output file
        self.output_text = Text(frame,height=24,width=50)
        self.scroll = Scrollbar(frame)
        self.scroll.pack(side=RIGHT,fill=Y)
        self.output_text.pack(side=LEFT)
        self.scroll.config(command=self.output_text.yview)
        self.output_text.config(yscrollcommand=self.scroll.set)

        #buttons
        frame1 = Frame(master)
        frame1.pack(pady=40)
        
        self.open_btn = Button(frame1,text='Open',command=lambda:open_file(self.netlist_text))
        self.open_btn.configure(width=15,height=2)
        self.open_btn.pack(side=LEFT)
        
        self.parse_btn = Button(frame1,text="Parse",command=lambda:parse(fname,self.output_text))
        self.parse_btn.configure(width=15,height=2)
        self.parse_btn.pack(side=LEFT)
        
        self.sim_btn = Button(frame1,text="Simulate",command=lambda:simulate(fname,self.output_text))
        self.sim_btn.configure(width=15,height=2)
        self.sim_btn.pack(side=LEFT)
        
        self.plot_btn = Button(frame1,text="Plot",command=lambda:netlist_plot(fname))
        self.plot_btn.configure(width=15,height=2)
        self.plot_btn.pack(side=LEFT)

#define the main window
win = Tk()
win.title('MySpice')
win.geometry('800x600')

#add a 'help' menubar
menubar = Menu(win)
helpmenu = Menu(menubar,tearoff=0)
helpmenu.add_command(label='Read Me',command=show_readme)
helpmenu.add_command(label='About',command=show_about)
menubar.add_cascade(label='Help',menu=helpmenu)

win.config(menu=menubar)

APP = app(win)
win.mainloop()
