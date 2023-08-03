__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"



#Imports
import pandas as pd
import ipaddress

#Load CSV FILE
data = pd.read_csv('merged_alerts.csv')

#Get unique values
column_7_values = data['7'].unique()
column_8_values = data['8'].unique()

#Variable for ips and port
ipsandports = []

#Parse ips and ports
for one in column_7_values:
    if "10.0.2.15" in one or "8.8.8.8" in one or "192.168.33.254" in one:
        continue
    else:
        ipsandports.append(one[1:])
for one in column_8_values:
    if "10.0.2.15" in one or "8.8.8.8" in one or "192.168.33.254" in one:
        continue
    else:
        ipsandports.append(one[1:])

import csv

#Variable for csv data
csv_data = []

#Parse all items
for item in ipsandports:
    ip_port = item.split(':')
    if len(ip_port) < 2:
        continue
    
    ip_address = ip_port[0].strip()
    port = ip_port[1].strip()
    
    
    try:
        ip_address = ipaddress.ip_address(ip_address)
    except ValueError:
        
        continue

    csv_data.append([str(ip_address), port])

#Save data to csv file
csv_file = 'ipsandports.csv'

with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)
