__author__ = "Michal Dostal"
__license__ = "GNU-GPL v2.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"


import pandas as pd
import matplotlib.pyplot as plt
import json

#Open json file with false negatives and positives
with open('false_positives_unique_values.json', 'r') as fp:
    false_positives_unique_values = json.load(fp)

with open('false_negatives_unique_values.json', 'r') as fn:
    false_negatives_unique_values = json.load(fn)



#Plot most five values for country and asn in false positive and negative
def plot_top_5_values(unique_values_dict, title):
    plt.figure(figsize=(12, 6))
    for column, values in unique_values_dict.items():
        top_5_values = sorted(values, key=lambda x: x['count'], reverse=True)[:5]
        labels = [entry["value"] for entry in top_5_values]

        counts = [entry["count"] for entry in top_5_values]
        plt.bar(labels, counts, label=column)
    plt.xlabel("Hodnota")
    plt.ylabel("Počet výskytů")
    plt.title(title)
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


#Call the function for FN and FP
plot_top_5_values(false_positives_unique_values, "Falešně pozitivní predikce (Země, ASN)")
plot_top_5_values(false_negatives_unique_values, "Falešně negativní predikce (Země, ASN)")
