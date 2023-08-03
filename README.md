# IDS_anomaly

## Nejprve je potreba nainstalovat snort verze 3 z githubu:
https://github.com/snort3/snort3

## Dale je potreba nainstalovat snort3_extra z githubu:
https://github.com/snort3/snort3_extra

## Je potreba stahnout deskriptory pro openappid:
https://www.snort.org/downloads/openappid/33380

## Pravidla jsou ulozeny v zipu snapshot

## Je potreba nahradit soubory ze snort3_extra za ty v repozitari a znovu z buildit

## Pro natrenovani modelu je potreba vytvorit slozku mixed_pcaps a normal_pcaps a naplnit to pcapy ze stranek:
- https://www.stratosphereips.org/datasets-mixed
- https://www.stratosphereips.org/datasets-normal

## Pro natrenovani modelu je zde uveden skript init_model.sh
## Pro dotrenovani na normalnich datech je tu skript train_normal.sh
## Pote staci nastavit snort.lua tak jak je v instalaci a muzete pustit predikci.
