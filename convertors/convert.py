__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"


#Imports
import json
import csv
import codecs
import chardet
import glob

#input files
input_file = "merged_flows.json"
output_file = "all_flows.csv"
input_path = "./*.json"

#variables for data
data = []
fieldnames = set()

#parse every json file and output to csv
for file_path in glob.glob(input_path):
    with codecs.open(file_path, "r", encoding='Windows-1254', errors='ignore') as file:
        for line in file:
            try:
                json_obj = json.loads(line)

            
                def flatten_dict(d, prefix=""):
                    for key, value in d.items():
                        if isinstance(value, dict):
                            flatten_dict(value, prefix + key + "_")
                        else:
                            fieldnames.add(prefix + key)
                            data[-1][prefix + key] = value

                data.append({})
                flatten_dict(json_obj)
            except:
                continue

#save collected data to csv
with open(output_file, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
