__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"

#Needed imports
import pandas as pd
from geoip2.database import Reader

#Input file to load
input_file = "all_flows_swap.csv"

#Read CSV to dataframe
df = pd.read_csv(input_file)

#Get nonnumeric columns
non_numeric_columns = df.select_dtypes(exclude=["number"]).columns

#Add more columns

df["city"] = None
df["country"] = None
df["asn_number"] = None
df["asn_name"] = None
df["blacklisted"] = None

#Path to asn database

asn_path = '../ASNGEO/GeoLite2-ASN.mmdb'

#Create instance for reader
reader = Reader(asn_path)

#Try find ASN for every ip address
for index, row in df.iterrows():
    try:
        response = reader.asn(df.at[index, "service_info_ip"])
        df.at[index, "asn_number"] = response.autonomous_system_number
        df.at[index, "asn_name"] = response.autonomous_system_organization
    except Exception as e:
        continue
    
#Path to city database
city_path = '../ASNGEO/GeoLite2-City.mmdb'
#Create instance for reader
reader = Reader(city_path)

#Try to add country for every instance in dataframe
for index, row in df.iterrows():
    try:
        response = reader.city(df.at[index, "service_info_ip"])
        df.at[index, "city"] = response.city.name
        df.at[index, "country"] = response.country.name

    except Exception as e:
         print(f"Chyba: {str(e)}")
    

#Notnumber atrrs
notanumber_attrs = ["client_info_version", "proto", "service_info_vendor", "apps_client", "service_info_version", "http_user_agent", "service_info_subtype_service", 
"apps_service", "service_info_ip", "http_host", "dns_host", "client_info_ip", "apps_payload", "http_referrer", "apps_misc", "service_info_subtype_version", "apps_referred", 
"pkt_time", "http_url", "tls_host", "city", "country", "asn_number", "asn_name"]

#Import for postgress
import psycopg2

#Connect to database
conn = psycopg2.connect(dbname='blacklistdb', user='postgres', password='postgres', host='localhost', port='5432')
#Create cursor
cur = conn.cursor()

#If ip in database is found blacklist the instance or tag as normal
for index, row in df.iterrows():
    try:
        ip_address = str(df.at[index, "service_info_ip"])
        query = f"SELECT * FROM ips WHERE ip = '{ip_address}';"
        ip_address2 = str(df.at[index, "client_info_ip"])
        query2 = f"SELECT * FROM ips WHERE ip = '{ip_address2}';"
        cur.execute(query)
        result = cur.fetchall()
        if len(result) > 0:
            df.at[index, "blacklisted"] = 1
        else:
            cur.execute(query2)
            result = cur.fetchall()
            if len(result) > 0:
                df.at[index, "blacklisted"] = 1
            else:
                df.at[index, "blacklisted"] = 0
        
    except Exception as e:
         print(f"Chyba: {str(e)}")
         df.at[index, "blacklisted"] = 0
   


#Close connection to database
cur.close()
conn.close()


#Save labeled csv
df.to_csv('all_labeled.csv', index=False)
