#VDB_CRUDE.PY
import sqlite3
from voyager import *
import os
import time

conn = sqlite3.connect('Voyager1.sqlite3')
cur = conn.cursor()

bin_count = 31

#Flux and Error filler
fhandle2 = open('CRS1_missing_data.txt', 'r')
for line in fhandle2 :
    if (len(line) > 0) :
        lst = extractor(line.strip())
        print(lst[0])
        command1 = table_populator(lst, bin_count, 0)
        command2 = table_populator(lst, bin_count, 1)
        cur.executescript(command1 + command2)
conn.commit()
print('\aHAHHAHAAHHA DONE!!')