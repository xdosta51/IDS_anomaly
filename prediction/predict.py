__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"


#needed imports
import pandas as pd
from geoip2.database import Reader
from sklearn.preprocessing import LabelEncoder
import joblib
import sys
import os
import xgboost as xgb
import numpy as np
import jsonlines

#File path for data to predict
data_file = sys.argv[1]





#Name of columns in data file
columns=[
    "server_bytes", "http_user_agent", "client_pkts", "apps_payload", "server_pkts", "http_referrer", "user_info_username", "dns_host" , "netbios_info_netbios_domain", "proto", "client_bytes", "client_info_version", 
    "http_host", "apps_referred", "service_info_vendor", "apps_client", "service_info_subtype_version", "user_info_id", "apps_misc", "apps_service", "service_info_port", 
    "session_num", "service_info_subtype_service", "pkt_num", "service_info_version", "tls_host", "user_info_login_status", "total_flow_latency", "netbios_info_netbios_name",
    "http_httpx_stream", "http_response_code", "client_info_port", "http_url", "service_ip"
]


#Parse file to dataframe
data = []
with open(data_file, 'r', encoding='Windows-1252', errors='ignore') as file:
    for line_number, line in enumerate(file, start=1):
        try:
            attributes = line.strip().split(';,;')
            if len(attributes) != len(columns):
                continue
            data.append(attributes)
        except UnicodeDecodeError as e:
            continue

#Get dataframe to predict
df = pd.DataFrame(data, columns=columns)

#Add new columns
df["city"] = None
df["country"] = None
df["asn_number"] = None
df["asn_name"] = None


#Add informations about geolocation
asn_path = 'ASNGEO/GeoLite2-ASN.mmdb'
reader_asn = Reader(asn_path)

city_path = 'ASNGEO/GeoLite2-City.mmdb'
reader_city = Reader(city_path)

for i, ip in enumerate(df["service_ip"]):
    try:
        asn_response = reader_asn.asn(ip)
        df.at[i, "asn_number"] = asn_response.autonomous_system_number
        df.at[i, "asn_name"] = asn_response.autonomous_system_organization
        city_response = reader_city.city(ip)
        df.at[i, "city"] = city_response.city.name
        df.at[i, "country"] = city_response.country.name
    except Exception as e:
        pass


real_df = df
#Drop not needed service ip
df = df.drop('service_ip', axis=1)

#Get non numeric columns
non_numeric_columns = df.select_dtypes(exclude=['number']).columns


#Fill unknown to missed data
for column in ['http_user_agent', 'apps_payload', 'http_referrer', 'dns_host', 'proto',
       'client_info_version', 'http_host', 'apps_referred',
       'service_info_vendor', 'apps_client', 'service_info_subtype_version',
       'apps_misc', 'apps_service', 'service_info_subtype_service',
        'service_info_version', 'tls_host',
       'http_url', 'city', 'country', 'asn_name']:
    df[column].fillna('unknown', inplace=True)
    df[column] = df[column].replace('0', 'unknown')

#Encode string to numbers
label_encoder = LabelEncoder()
for column in ['http_user_agent', 'apps_payload', 'http_referrer', 'dns_host', 'proto',
       'client_info_version', 'http_host', 'apps_referred',
       'service_info_vendor', 'apps_client', 'service_info_subtype_version',
       'apps_misc', 'apps_service', 'service_info_subtype_service',
        'service_info_version', 'tls_host',
       'http_url', 'city', 'country', 'asn_name']:
    mapping = joblib.load("prediction/mapping/" + str(column) + "_mapping.pkl")
    df[column] = df[column].map(mapping)


#Convert dataframe to all numberic
for column in non_numeric_columns:
    df[column] = pd.to_numeric(df[column], errors='coerce')

df = df.fillna(0)


#Normalize dataframe
min_vals = pd.read_csv('prediction/min_vals.csv', index_col=0).squeeze("columns")
max_vals = pd.read_csv('prediction/max_vals.csv', index_col=0).squeeze("columns")

min_vals.fillna(0)
max_vals.fillna(1)

scaled_new_df = (df - min_vals) / (max_vals - min_vals)

df = scaled_new_df
df = df.fillna(0)
df["http_response_code"] = df["http_response_code"].clip(lower=0.0)

#Convert dataframe to float
df = df.astype(float)


#Load model for prediction
model = xgb.Booster()
model.load_model("prediction/best_model.xgb")


#Predict data
dtest = xgb.DMatrix(df)
probabilities = model.predict(dtest)
predictions = [1 if prob >= 0.5 else 0 for prob in probabilities]


#Convert predictions 
predictions = np.array(predictions)
count_ones = (predictions == 1).sum()
selected_rows = real_df.loc[predictions == 1]

#Save alerts to json file
try:
    with jsonlines.open('alerts.json', mode='a') as writer:
        for row in selected_rows.to_dict(orient='records'):
            writer.write(row)
except Exception as e:
    print(f"Error writing to alerts.json: {e}")

#Close file
file.close()

#Exit with one if anomalies wrere found
if count_ones > 0:
    exit(1)

exit(0)
