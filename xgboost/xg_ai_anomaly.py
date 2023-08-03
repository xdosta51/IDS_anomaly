__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"


#Load imports
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedKFold, GridSearchCV
import xgboost as xgb_gpu

#Load anomaly dataset
file1_path = "df_anomaly_normalized.csv"
merged_df = pd.read_csv(file1_path,  index_col=0)

#Split values and labels
X = merged_df.drop(columns=["blacklisted"])
y = merged_df["blacklisted"]


#Split dataframe to train, test and valid
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, stratify=y_train, random_state=42)


#Use model XGBClassifier
model = xgb_gpu.XGBClassifier(tree_method='gpu_hist')


#Find best parameters
param_grid = {
    'max_depth': [14, 15],
    'learning_rate': [0.1],
    'n_estimators': [230, 235]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, scoring='f1', cv=cv, verbose=1)
grid_search.fit(X_train, y_train)


#Print best parameters and score for it
print("Nejlepší kombinace hyperparametrů:")
print(grid_search.best_params_)

print("Nejlepší skóre:")
print(grid_search.best_score_)

#Get best model
model = grid_search.best_estimator_

#Get predicted data
y_pred = model.predict(X_test)
y_true = y_test

#Print score of model
accuracy = accuracy_score(y_true, y_pred)
print("Přesnost modelu:", accuracy)

#Plot confusion matrix
confusion = confusion_matrix(y_true, y_pred)
confusion_df = pd.DataFrame(confusion, index=['Skutečné negativní', 'Skutečné pozitivní'],
                             columns=['Predikované negativní', 'Predikované pozitivní'])

plt.figure(figsize=(8, 6))
sns.heatmap(confusion_df, annot=True, fmt="d", cmap="YlGnBu", cbar=False)
plt.xlabel("Predikované třídy")
plt.ylabel("Skutečné třídy")
plt.title("Kontingenční tabulka")
plt.show()

model.save_model("best_model_anomaly.xgb")
