
export my_path=~/snort/snort3
pcap_dir="mixed_pcaps/"

for file in "$pcap_dir"/*; do
    if [ -f "$file" ]; then
        $my_path/bin/snort -c "$my_path/etc/snort/snort.lua" -R $my_path/rules/includes.rules --daq-dir /usr/local/lib/daq_s4/lib/daq -r "$file" --plugin-path "$my_path/lib/snort"
        rm prediction/output_predict.txt*
        cat flows.json >> init_model/merged_flows.json
        
    fi
done

cp convertors/convert.py init_model/convert.py
cp convertors/getips.py init_model/getips.py
cp convertors/swap.py init_model/swap.py
cp convertors/readdf.py init_model/readdf.py



mv alert_csv.txt init_model/merged_alerts.csv
cd init_model
python3 convert.py 
python3 swap.py

sed -i '1s/^/1,2,3,4,5,6,7,8,9,10\n/' merged_alerts.csv

python3 getips.py
sed -i '1s/^/ip,port\n/' ipsandports.csv

python3 readdf.py
mkdir mapping
python3 ai.py

cd ..

cp init_model/model.pkl train_model/model.pkl
cp -r init_model/mapping train_model/mapping
