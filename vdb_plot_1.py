#VDB_PLOT_1.PY
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import os
import re
import sqlite3
from voyager import *
from datetime import datetime, timedelta 

#BIN LISTING
conn = sqlite3.connect('Voyager1.sqlite3')
cur = conn.cursor()
print('BIN LISTING')
cur.execute('SELECT Bin_No, Lower_Limit, Upper_Limit, Type FROM Bin')
row = cur.fetchall()
for record in row :
    print(record[0], '.',  record[1], '-', record[2], ':', record[3])
print('\aEND OF BIN LISTING\n')
bin_count = record[0]

#LIST OF FLUXES ENTERED BY THE USER
command = input("Enter the command: ")
lst1 = list()
num_list = list()
set1 = list()
set2 = list()
if re.search(':', command) :
    lst1 = re.findall('(.*)\s*:', command)
    lst1.append(re.findall(':\s*(.*)', command)[0])
else :
    lst1 = re.findall('\s*(.*)', command.rstrip())
print(lst1)
set1 = command_splitter(lst1[0], bin_count)
set2 = command_splitter(lst1[1], bin_count)
set1 = HH_replacer(set1)
set2 = HH_replacer(set2)
print(set1)
print(set2)

#DATE-TIME RANGE ENTERED BY THE USER
os.system('PAUSE')
#os.system('CLS')
print('DATE-TIME FORMAT : YYYY-MM-DD HH:mm:ss')
dstr1 = input('Enter the starting date: ')
dstr2 = input('Enter the ending date: ')

#COMMAND FORMATION
command1 = commander(set1) 
cur.execute(command1, (dstr1, dstr2,))
set1 = cur.fetchall()
#hifi_print(set1)
if set2[0] != '' :
    command2 = commander(set2)
    cur.execute(command2, (dstr1, dstr2,))
    set2 = cur.fetchall()
    #hifi_print(set2)

#EXTRACTION 
dt_list1 = np.array([])
dt_list2 = np.array([])
flux_list1 = np.array([])
flux_list2 = np.array([])
lst = array_former(set1)
dt_list1 = lst[0]
flux_list1 = lst[1]
if set2[0] != '' :
    lst = array_former(set2)
    dt_list2 = lst[0]
    flux_list2 = lst[1]

#PLOTTING
print('PRODUCING THE PLOTS')
if set2[0] != '' :
    plt.figure()
    plt.subplot(211)
    plt.plot(dt_list1, flux_list1, color = 'red')
    plt.subplot(212)
    plt.plot(dt_list2, flux_list2, color = 'blue')
else :
    plt.figure()
    plt.plot(dt_list1, flux_list1, color = 'red')
plt.show()
