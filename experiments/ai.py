__author__ = "Michal Dostal"
__license__ = "GNU-GPL v2.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"

#Needed imports

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
import joblib
import numpy as np
from sklearn.model_selection import GridSearchCV


#Read all csv files
df = pd.read_csv('experiment2_labeled.csv')
dfips = pd.read_csv('experiment2_ipsandports.csv')
old_df = pd.read_csv('experiment2_labeled.csv')

#Convert ips and ports to list
ip_list = dfips['ip'].tolist()
port_list = dfips['port'].tolist()


#Blacklist instance by ips
for index, row in df.iterrows():
    try:
        ip_address = str(df.at[index, "service_info_ip"])
        service_port = df.at[index, "service_info_port"]
        
        if ip_address in ip_list:
            if service_port in port_list:
                df.at[index, "blacklisted"] = 1
        else:
            df.at[index, "blacklisted"] = 0
        
    except Exception as e:
        print(f"Chyba: {str(e)}")
        df.at[index, "blacklisted"] = 0
    

#Get non numeric columns
non_numeric_columns = df.select_dtypes(exclude=['number']).columns

#Fill unknown to missed values
for column in ['http_user_agent', 'apps_payload', 'http_referrer', 'dns_host', 'proto',
       'client_info_version', 'http_host', 'apps_referred',
       'service_info_vendor', 'apps_client', 'service_info_subtype_version',
       'apps_misc', 'apps_service', 'service_info_subtype_service',
        'service_info_version', 'tls_host',
       'http_url', 'city', 'country', 'asn_name']:
    df[column].fillna('unknown', inplace=True)

#Map values to init values
non_numeric_columns = df.select_dtypes(exclude=['number']).columns
label_encoder = LabelEncoder()
for column in ['http_user_agent', 'apps_payload', 'http_referrer', 'dns_host', 'proto',
       'client_info_version', 'http_host', 'apps_referred',
       'service_info_vendor', 'apps_client', 'service_info_subtype_version',
       'apps_misc', 'apps_service', 'service_info_subtype_service',
        'service_info_version', 'tls_host',
       'http_url', 'city', 'country', 'asn_name']:
    mapping = joblib.load("/home/mike/snort/init_model/mapping/" + str(column) + "_mapping.pkl")
    df[column] = df[column].map(mapping)



#Convert all columns to numeric
for column in non_numeric_columns:
    df[column] = pd.to_numeric(df[column], errors='coerce')

#Fill missed values with zero
df = df.fillna(0)


#Split dataset to train and test instances
train_df, test_df = train_test_split(df, test_size=0.3, stratify=df['blacklisted'], random_state=42)
pocet_radku = (train_df["blacklisted"] == 1).sum()
pocet_radku = (test_df["blacklisted"] == 1).sum()


#Read min and max vals for normalize
min_vals = pd.read_csv('min_vals.csv', index_col=0, squeeze=True)
max_vals = pd.read_csv('max_vals.csv', index_col=0, squeeze=True)

#Scale dataframe
scaled_new_df = (df - min_vals) / (max_vals - min_vals)
df = scaled_new_df

#Clip lower http response code to zero
df["http_response_code"] = df["http_response_code"].clip(lower=0.0)


#Drop columns that are not needed to machine learning
df = df.astype(float)
df = df.drop('pkt_time', axis=1)
df = df.drop('client_info_ip', axis=1)
df = df.drop('service_info_ip', axis=1)

df = df.fillna(0)

#Save file to csv
df.to_csv("df_experiment2_normalized.csv")

exit()
