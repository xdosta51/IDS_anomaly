export my_path=~/snort/snort3
pcap_dir="normal_pcaps/"

for file in "$pcap_dir"/*; do
    if [ -f "$file" ]; then
        $my_path/bin/snort -c "$my_path/etc/snort/snort.lua" -R $my_path/rules/includes.rules --daq-dir /usr/local/lib/daq_s4/lib/daq -r "$file" --plugin-path "$my_path/lib/snort"
        cat flows.json >> train_normal/merged_flows.json
        
    fi
done

cp convertors/convert.py train_normal/convert.py
cp convertors/getips.py train_normal/getips.py
cp convertors/swap.py train_normal/swap.py
cp convertors/readdf.py train_normal/readdf.py

mv alert_csv.txt train_normal/merged_alerts.csv
cd train_normal
python3 convert.py 
python3 swap.py

sed -i '1s/^/1,2,3,4,5,6,7,8,9,10\n/' merged_alerts.csv

python3 getips.py
sed -i '1s/^/ip,port\n/' ipsandports.csv

python3 readdf.py
python3 ai.py