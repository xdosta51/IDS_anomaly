__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"


#Imports
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedKFold, GridSearchCV
import xgboost as xgb_gpu
import shap
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score

#Read normal and mixed dataset
file1_path = "df_normal_normalized.csv"
df1 = pd.read_csv(file1_path,  index_col=0)

file2_path = "df_mixed_normalized.csv"
df2 = pd.read_csv(file2_path,  index_col=0)

#Merge them
merged_df = pd.concat([df1, df2], ignore_index=True)

#Split to values and labels
X = merged_df.drop(columns=["blacklisted"])
y = merged_df["blacklisted"]

#Split dataset to train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.1, stratify=y_train, random_state=42)

#Create xgbclassifier
model = xgb_gpu.XGBClassifier(tree_method='gpu_hist')


#Param grid for model and find best parameters
param_grid = {
    'max_depth': [15, 16],
    'learning_rate': [0.1],
    'n_estimators': [235, 240]
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, scoring='f1', cv=cv, verbose=1)
grid_search.fit(X_train, y_train)


#Print best parameters and score
print("Nejlepší kombinace hyperparametrů:")
print(grid_search.best_params_)

print("Nejlepší skóre:")
print(grid_search.best_score_)

#Get best model
model = grid_search.best_estimator_


#Get score for test data
y_pred = model.predict(X_test)
y_true = y_test

accuracy = accuracy_score(y_true, y_pred)
print("Přesnost modelu:", accuracy)



#Plot roc curve
y_probs = model.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_probs)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC křivka (plocha pod křivkou = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC křivka')
plt.legend(loc="lower right")
plt.show()

#Plot precision recall curve
precision, recall, _ = precision_recall_curve(y_test, y_probs)
average_precision = average_precision_score(y_test, y_probs)

plt.figure()
plt.step(recall, precision, color='b', alpha=0.2, where='post')
plt.fill_between(recall, precision, step='post', alpha=0.2, color='b')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title('Křivka Precision-Recall: AP={0:0.2f}'.format(average_precision))
plt.show()








#Plot confusion matrix
confusion = confusion_matrix(y_true, y_pred)

confusion_df = pd.DataFrame(confusion, index=['Skutečné negativní', 'Skutečné pozitivní'],
                             columns=['Predikované negativní', 'Predikované pozitivní'])


plt.figure(figsize=(8, 6))
sns.heatmap(confusion_df, annot=True, fmt="d", cmap="YlGnBu", cbar=False)
plt.xlabel("Predikované třídy")
plt.ylabel("Skutečné třídy")
plt.title("Matice záměn")
plt.show()


#Save model
#model.save_model("best_model.xgb")
