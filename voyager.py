#VOYAGER.PY
import urllib.request, urllib.error, urllib.parse
import re
import os
import sqlite3
import numpy as np
from datetime import datetime, timedelta 
from decimaldate import *

def create_url(num, year) :
    if num == None :
        num = int(input("Voyager 1 or Voyager 2? \n : "))
    if num == 1 :
        base_url = 'https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/particle/crs/six_hour/vy1crs_6hour_'
    elif num == 2 :
        base_url = 'https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager2/particle/crs/six_hour/vy2crs_6hour_'
    else :
        print("WRONG ENTRY!! EXITING THE PROGRAM!!")
        quit()
    if year == None :
        year = input("For which year do you need the six hour daily average CRS data? \n : ")
    else :
        year = str(year)
    url = base_url + year + '.asc'
    return url

def retrieve_total_bin(url) :
    whandle1 = urllib.request.urlopen(url)
    line_count = 0
    for line in whandle1 :
        if line_count == 3 :
            return int(line)
        else :
            line_count = line_count + 1
            
def binner(line, bin_no) :
    lst = line.split(' ')
    flagadd = 0
    size = len(lst) - 1
    mlist = list()
    for item in lst :
        if (item == str(bin_no)) and (len(item) > 0) :
            flagadd = 1
            continue
        if flagadd > 0 :
            if flagadd == 1 and len(item) > 0 :
                mlist.append(float(item))
                flagadd = flagadd + 1
            elif flagadd == 2 and item == '-' :
                flagadd = flagadd + 1
            elif flagadd == 3 and len(item) > 0 :
                mlist.append(float(item))
                flagadd = flagadd + 1
            elif flagadd == 4 :
                item = lst[size - 1]
                if (item == 'Hydrogen') or (item == 'Helium') :
                    mlist.append(item)
                break
    return mlist
    
def table_creator(bin_count, num) :
    flux_command = 'CREATE TABLE Flux (Time DATETIME '
    error_command = 'CREATE TABLE Error (Time DATETIME '
    count = 1
    while count <= bin_count :
        flux_command = flux_command + ', Flux_' + str(count) + ' REAL '
        error_command = error_command + ', Error_' + str(count) + ' REAL '
        print('Bin', str(count), 'done.')
        count = count + 1
    flux_command = flux_command + ');'
    error_command = error_command + ');'
    if num == 0 :
        return flux_command
    elif num == 1 :
        return error_command
    else :    
        return None

def extractor(line) :
    lst1 = line.split()
    lst2 = list()
    index = 0
    for item in lst1 :
        if index == 0 :
            date = re.findall('^(\S+)T', item)
            time = re.findall('^\S+T(\S+)', item)
            datetime = date[0] + ' ' + time[0]
            lst2.append(datetime)
        else :
            lst2.append(float(item))
        index = index + 1
    return lst2

def table_populator(lst, bin_count, order) :
    if order == 0 :
        str1 = 'INSERT INTO Flux (Time'
        str2 = " VALUES ('" + lst[0] + "' "
        for bin in range(bin_count + 1) :
            if bin != 0 :
                str1 = str1 + ', Flux_' + str(bin)
                str2 = str2 + ', ' + str(lst[(2 * bin) - 1])
        command = str1 + ')' + str2 + ');'
    elif order == 1 :
        str1 = 'INSERT INTO Error (Time'
        str2 = " VALUES ('" + lst[0] + "' "
        for bin in range(bin_count + 1) :
            if bin != 0 :
                str1 = str1 + ', Error_' + str(bin)
                str2 = str2 + ', ' + str(lst[2 * bin])
        command = str1 + ')' + str2 + ');'
    return command 

def command_splitter(string, bin_count) :
    set = list()
    if string == '' :
        set.append(string)
    elif string.strip() == 'Hydrogen' or string.strip() == 'Helium' :
        set.append(string.strip())
    else :
        index = 0
        for char in string :
            if char.isdigit() :
                index = index + 1
                continue
            else : 
                if (char == '+') or (char == ' ') :
                    index = index + 1
                    continue
                else :
                    print('\aINVALID CHARACTER: ', char, "'")
                    quit()
        num_list = re.findall('[0-9]+', string)
        for number in num_list :
            if int(number) < 1 or int(number) > bin_count :
                print(number, 'IS OUT OF RANGE\a')
                quit()
            else :
                set.append(int(number))
    return set

def HH_replacer(set) :
    conn = sqlite3.connect('Voyager1.sqlite3')
    cur = conn.cursor()
    if set[0] == 'Hydrogen' or set[0] == 'Helium' :
        lst = list()
        cur.execute('SELECT Bin_No FROM Bin WHERE Type = (?)', (set[0],))
        list1 = cur.fetchall()
        for tuply in list1 :
            for key in tuply :
                lst.append(key)
        return lst
    else : 
        return set

def commander(bin_list) :
    string1 = 'SELECT Flux.Time'
    string2 = ''
    for bin_no in bin_list :
        string2 = string2 + ', Flux.Flux_' + str(bin_no) + ', Error.Error_' + str(bin_no)
    string3 = ' FROM Flux JOIN Error ON Flux.Time = Error.Time WHERE Flux.Time >= (?) AND Flux.Time <= (?)'
    string = string1 + string2 + string3
    return string
    
def hifi_print(lst) :
    for item in lst :
        print(item)

def array_former(lst) : 
    dt_list = np.array([])
    flux_list = np.array([])
    set = list()
    dt = str()
    flux = 0.0
    error = 0.0
    index = 1
    for tuply in lst :
        flux = 0.0
        error = 0.0
        index = 1
        #print(tuply)
        while index < len(tuply) :
            if (index % 2) == 1 :
                flux = flux + tuply[index]
            elif (index % 2) == 0 :
                error = error + tuply[index]
            index = index + 1
        if error == 0.0 or error == -1.0 : continue
        else :
            dt = tuply[0]
            #print(dt)
            #dt_list = np.append(dt_list, year_fraction(dt))
            dt_list = np.append(dt_list, datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S'))
            flux_list = np.append(flux_list, flux)
    set.append(dt_list)
    set.append(flux_list)
    print(set)
    return set