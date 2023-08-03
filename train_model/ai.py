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

#Read all dataframes
df = pd.read_csv('all_labeled.csv')
dfips = pd.read_csv('ipsandports.csv')
old_df = pd.read_csv('all_labeled.csv')

#Get ips and ports
ip_list = dfips['ip'].tolist()
port_list = dfips['port'].tolist()

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
   

#Get non numeric columns fill missed values and map string to number
pocet_radku = (df["blacklisted"] == 1).sum()
non_numeric_columns = df.select_dtypes(exclude=['number']).columns

print(non_numeric_columns)

for column in ['http_user_agent', 'apps_payload', 'http_referrer', 'dns_host', 'proto',
       'client_info_version', 'http_host', 'apps_referred',
       'service_info_vendor', 'apps_client', 'service_info_subtype_version',
       'apps_misc', 'apps_service', 'service_info_subtype_service',
        'service_info_version', 'tls_host',
       'http_url', 'city', 'country', 'asn_name']:
    df[column].fillna('unknown', inplace=True)


non_numeric_columns = df.select_dtypes(exclude=['number']).columns
label_encoder = LabelEncoder()
for column in ['http_user_agent', 'apps_payload', 'http_referrer', 'dns_host', 'proto',
       'client_info_version', 'http_host', 'apps_referred',
       'service_info_vendor', 'apps_client', 'service_info_subtype_version',
       'apps_misc', 'apps_service', 'service_info_subtype_service',
        'service_info_version', 'tls_host',
       'http_url', 'city', 'country', 'asn_name']:
    mapping = joblib.load("/home/mike/snort/train_model/mapping/" + str(column) + "_mapping.pkl")
    df[column] = df[column].map(mapping)



#Convert dataframe to numeric
for column in non_numeric_columns:
    df[column] = pd.to_numeric(df[column], errors='coerce')

df = df.fillna(0)



#Split dataframe to train and test data
train_df, test_df = train_test_split(df, test_size=0.15, stratify=df['blacklisted'], random_state=42)
pocet_radku = (train_df["blacklisted"] == 1).sum()
pocet_radku = (test_df["blacklisted"] == 1).sum()

#Normalize dataframe
min_vals = pd.read_csv('min_vals.csv', index_col=0, squeeze=True)
max_vals = pd.read_csv('max_vals.csv', index_col=0, squeeze=True)

scaled_new_df = (df - min_vals) / (max_vals - min_vals)

df = scaled_new_df

df["http_response_code"] = df["http_response_code"].clip(lower=0.0)
data_file = "dftesting.csv"

df = df.astype(float)


#Load model for training
model = joblib.load('/home/mike/snort/train_model/model.pkl')

#Drop attrs that are not needed
df = df.drop('pkt_time', axis=1)
df = df.drop('client_info_ip', axis=1)
df = df.drop('service_info_ip', axis=1)
df = df.fillna(0)


#Save csv for xgboost training
df.to_csv("df_anomaly_normalized.csv")

X = df.drop('blacklisted', axis=1)
y = df['blacklisted']


#Split dataset for train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print(old_df)
test1X = old_df.drop('blacklisted', axis=1)
test1Y = old_df['blacklisted']

testXTrain, testXTest, testYTrain, testYTest = train_test_split(test1X, test1Y, test_size=0.3, random_state=42)

#Calculate score of model
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = model.score(X_test, y_test)
print("Přesnost (score):", accuracy)

#Plot confusion matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix


#Save model for testing
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.xlabel("Predicted label")
plt.ylabel("True label")
joblib.dump(model, 'model.pkl')
plt.show()

exit()