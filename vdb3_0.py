#VDB3_0.PY
import urllib.request, urllib.parse, urllib.error
import re
import sqlite3
from voyager import *
import os
import time

'''
TO EXTRACT THE DATA AND STORE IT INTO TWO TABLES: BIN AND DATA
BIN -> BIN# (AUTOINCREMENTED INTEGER PRIMARY KEY), LOWER LIMIT, UPPER LIMIT, TYPE (HYDROGEN OR HELIUM)
DATA -> TIME, B1F, B1E, B2F, B2E, ..., BNF, BNE
'''

conn = sqlite3.connect('Voyager1.sqlite3')
cur = conn.cursor()
cur.executescript( '''
                        DROP TABLE IF EXISTS Bin;
                        DROP TABLE IF EXISTS Flux;
                        DROP TABLE IF EXISTS Error;
                        
                        CREATE TABLE Bin (
                                            Bin_No INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                            Lower_Limit REAL,
                                            Upper_Limit REAL,
                                            Type TEXT
                                        );
                  ''')

#Retrieve the total number of bins in a single line of data
URL = create_url(1, 1977)
bin_count = retrieve_total_bin(URL)
print(bin_count)

#Create a new URL handle
wwhandle1 = urllib.request.urlopen(URL)

#Fill the table Bin
bin_list = list()
count = 0
for line in wwhandle1 :
    if count > 3 and count <= (bin_count + 3):
        bin_list = binner(line.decode().strip(), count - 3)
    elif count > (bin_count + 3) : break
    count = count + 1
    if len(bin_list) > 0 :
        cur.execute('INSERT INTO Bin (Lower_Limit, Upper_Limit, Type) VALUES (?, ?, ?)', (bin_list[0], bin_list[1], bin_list[2]))
conn.commit()

#storing data in a file
fhandle1 = open('CRS1_data.txt', 'w')
count = 0
year = 1977
while year <= 2019 :
    URL = create_url(1, year)
    wwhandle2 = urllib.request.urlopen(URL)
    for line in wwhandle2 :
        if len(line) > 0 :
            count = count + 1
        if (count > 35) and (len(line) > 0) :
            fhandle1.write(line.decode().strip() + '\n')
    print('|', end = '')
    count = 0
    year = year + 1
print('\n')

#Creation of Flux and Error table
flux_command = table_creator(bin_count, 0)
error_command = table_creator(bin_count, 1)
cur.executescript(flux_command + error_command)
conn.commit()
print("WAIT...")
time.sleep(5)
os.system('CLS')

#Flux and Error filler
fhandle2 = open('CRS1_data.txt', 'r')
for line in fhandle2 :
    if (len(line) > 0) :
        lst = extractor(line.strip())
        print(lst[0])
        command1 = table_populator(lst, bin_count, 0)
        command2 = table_populator(lst, bin_count, 1)
        cur.executescript(command1 + command2)
conn.commit()
print('\aHAHHAHAAHHA DONE!!')