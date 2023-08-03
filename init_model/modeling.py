__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"


import pandas as pd
import matplotlib.pyplot as plt

#Read dataframes that are needed for next plot
df1 = pd.read_csv('blacklisted_data.csv')
df2 = pd.read_csv('testblack.csv')

#Fill missing data
df1= df1.fillna('unknown')
df2= df2.fillna('unknown')

#Convert attributes to string
df1 = df1.astype(str)
df2 = df2.astype(str)

#Concatenated dataframe
concatenated_df = pd.concat([df1, df2], ignore_index=True)

#Get only anomalies
filtered_df = concatenated_df[concatenated_df["blacklisted"] == "1"]

#Plot data for country and ASN
plt.figure(figsize=(10, 6))
for column in filtered_df.columns:
    value_counts = filtered_df[column].dropna().value_counts().nlargest(10)
    plt.barh(value_counts.index, value_counts)
    plt.xlabel("Počet výskytů")
    plt.ylabel(column)
    plt.title(f"Top 10 výskytů pro atribut '{column}'")
    plt.show()

