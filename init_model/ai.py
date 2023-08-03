__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
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


#Load dataframes
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
    



#Get blacklisted DF
blacklisted_df = df[df["blacklisted"] == 1]
blacklisted_df.to_csv("blacklisted_data.csv", index=False)

#Fill missing values
non_numeric_columns = df.select_dtypes(exclude=['number']).columns
for column in non_numeric_columns:
    df[column].fillna('unknown', inplace=True)

#Get nonnumeric columns
non_numeric_columns = df.select_dtypes(exclude='number').columns.tolist()

#Encode string values to numbers
label_encoder = LabelEncoder()
mappings = {}

for column in non_numeric_columns:
    df[column] = label_encoder.fit_transform(df[column])
    mappings[column] = {value: label for label, value in enumerate(label_encoder.classes_)}
    filename = f"{column}_mapping.pkl"
    joblib.dump(mappings[column], "./mapping/" + filename)

#Split dataframe
train_df, test_df = train_test_split(df, test_size=0.3, stratify=df['blacklisted'], random_state=42)

#Drop atributes that are not needed
df = df.drop('pkt_time', axis=1)
df = df.drop('client_info_ip', axis=1)
df = df.drop('service_info_ip', axis=1)


#Save min max data to file
def min_max_scale_dataframe(df):
    min_vals = df.min()
    max_vals = df.max()
    scaled_df = (df - min_vals) / (max_vals - min_vals)
    min_vals.to_csv('min_vals.csv', header=True)
    max_vals.to_csv('max_vals.csv', header=True)
    return scaled_df

normalized_df = min_max_scale_dataframe(df)



#Saved normalzied dataframe
attributes = df.columns.tolist()
df = normalized_df
df = df.fillna(0)
df.to_csv('df_mixed_normalized.csv')


#Split dataframe
X = df.drop('blacklisted', axis=1)
y = df['blacklisted']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
test1X = old_df.drop('blacklisted', axis=1)
test1Y = old_df['blacklisted']

testXTrain, testXTest, testYTrain, testYTest = train_test_split(test1X, test1Y, test_size=0.3, random_state=42)



#PAram grid for learning
param_grid = {
    'criterion': ['gini', 'entropy'],
    'max_depth': [None, 5, 10, 15],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}


#Find best parameters
model = DecisionTreeClassifier()
grid_search = GridSearchCV(model, param_grid)
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
model = best_model


#Print accuracy of model
y_pred = model.predict(X_test)
accuracy = model.score(X_test, y_test)
print("Přesnost (Score):", accuracy)


import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

#Plot confusion matrix
confusion = confusion_matrix(y_test, y_pred)
confusion_df = pd.DataFrame(confusion, index=['Skutečné negativní', 'Skutečné pozitivní'],
                             columns=['Predikované negativní', 'Predikované pozitivní'])


plt.figure(figsize=(8, 6))
sns.heatmap(confusion_df, annot=True, fmt="d", cmap="YlGnBu", cbar=False)
plt.xlabel("Predikované třídy")
plt.ylabel("Skutečné třídy")
plt.title("Matice záměn")
plt.show()

exit()
