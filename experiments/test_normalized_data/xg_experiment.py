__author__ = "Michal Dostal"
__license__ = "GNU-GPL v2.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"


#Needed imports
import pandas as pd
import xgboost as xgb
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
from sklearn.model_selection import train_test_split
import json


#Read csv files
file1_path = "df_experiment2_normalized.csv"
df = pd.read_csv(file1_path,  index_col=0)
df33 = pd.read_csv("experiment2_labeled.csv")

#Get values and labels
X = df.drop(columns=["blacklisted"])
y = df["blacklisted"]

#Load trained model
model = xgb.Booster()
model.load_model("best_model.xgb")


#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1, shuffle=False)

#dtrain = xgb.DMatrix(X_train, label=y_train)

#params = {
#    "max_depth": 16,
#    "learning_rate": 0.1,
#}

#model = xgb.train(params, dtrain, xgb_model=model, num_boost_round=100)


#Convert dataframe do DMATRIX
dtest = xgb.DMatrix(X)
#Get predicted values
probabilities_test = model.predict(dtest)

#Convert prediction data from 0,5 to 1 or 0
y_test = y
threshold = 0.5
predictions_test = [1 if prob >= threshold else 0 for prob in probabilities_test]


#Convert y_test to list
y_test_list = y_test.tolist()
int_list = list(map(int, y_test_list))


#Get indexes for false positives and negatives
false_positives = [i for i, (pred, true) in enumerate(zip(predictions_test, y_test_list)) if pred == 1 and true == 0]
false_negatives = [i for i, (pred, true) in enumerate(zip(predictions_test, y_test_list)) if pred == 0 and true == 1]

#Get data from original dataframe
false_positives_df = df33.iloc[false_positives]
false_negatives_df = df33.iloc[false_negatives]

#Get specific column values for false positives and negatives
def count_unique_values_specific(df, attributes):
    result = {}
    for column in attributes:
        unique_values = df[column].unique()
        value_counts = df[column].value_counts()
        result[column] = [{"value": str(val), "count": int(count)} for val, count in zip(unique_values, value_counts)]
    return result

#Save only specific atributes
selected_attributes = ["country", "asn_name"]
false_positives_selected = false_positives_df[selected_attributes]
false_negatives_selected = false_negatives_df[selected_attributes]

#Dump file with false positives and false negatives
with open('false_positives_unique_values.json', 'w') as fp:
    json.dump(count_unique_values_specific(false_positives_selected, selected_attributes), fp)

with open('false_negatives_unique_values.json', 'w') as fn:
    json.dump(count_unique_values_specific(false_negatives_selected, selected_attributes), fn)


#Print accuracy of experiment
accuracy = accuracy_score(y_test, predictions_test)
print("Přesnost modelu:", accuracy)

#Plot confusion matrix
confusion = confusion_matrix(y_test, predictions_test)
confusion_df = pd.DataFrame(confusion, index=['Skutečné negativní', 'Skutečné pozitivní'],
                             columns=['Predikované negativní', 'Predikované pozitivní'])

plt.figure(figsize=(8, 6))
sns.heatmap(confusion_df, annot=True, fmt="d", cmap="YlGnBu", cbar=False)
plt.xlabel("Predikované třídy")
plt.ylabel("Skutečné třídy")
plt.title("Matice záměn")
plt.show()


#Print F1 Score
f1 = f1_score(y_test, predictions_test)
print("F1 Score:", f1)
