#Author: Michal Dostal
#License: GNU-GPL V3

Potrebne aplikace:
- Nejnovejsi verze c++
- Python verze 3.8
- Knihovny pro python jsou v requiremets.txt
- Databaze postgresql
- Snort nejnovejsi githubverze
- Snort extra umistena v teto slozce
- Deskriptory pro openappid
- Pravidla pro snort
- Databaze Geolite2

# Tato sekce je prevzata z me bakalarske prace
# Před spuštěním
V PostgreSQL je důležité změnit heslo pro uživatele **postgres** na heslo "postgres". 
Na linuxu to lze provést následujícimi příkazy.
**sudo -u postgres psql blacklistdb**
**ALTER USER postgres WITH PASSWORD 'postgres';**

Dále je potřeba vytvořit databázi s názvem **blacklistdb**
To se provede následujícím příkazem: **CREATE DATABASE blacklistdb;**

Dále jsou zde dvě různé možnosti naplnění databáze.
- Rychlejší varianta - nahrání dat do databáze z backupu
ve složce **postgres** se nachází backup databáze s blacklistovanými ip adresami a doménami
backup databáze lze spustit příkazem: **psql -U postgres -p 5432 -h localhost -d blacklistdb < db_backup/blacklist-2020.02.23.backup**

- Pomalejší varianta - spuštění skriptu **blacklist.py**
Pokud se rozhodnete pro naplnění živých dat do databáze pomocí skriptu blacklist.py, délka trvání asi 2 hodiny.
Je nejdřív potřeba vytvořit tři tabulky:

### Tabulka pro IP adresy

CREATE TABLE public.ips (
    ip character varying(255) NOT NULL,
    sourceid integer NOT NULL,
    domain character varying(1024)[],
    first_occ timestamp without time zone,
    update_occ timestamp without time zone,
    no_occ timestamp without time zone
);
ALTER TABLE ONLY public.ips
    ADD CONSTRAINT ips_pkey PRIMARY KEY (ip, sourceid);
ALTER TABLE ONLY public.ips
    ADD CONSTRAINT ips_sourceid_fkey FOREIGN KEY (sourceid) REFERENCES public.sources(sourceid);

### Tabulka pro domeny

CREATE TABLE public.domains (
    domain character varying(255) DEFAULT NULL::character varying NOT NULL,
    sourceid integer NOT NULL,
    ip character varying(1024)[],
    first_occ timestamp with time zone,
    update_occ timestamp with time zone,
    no_occ timestamp with time zone
);


ALTER TABLE ONLY public.domains
    ADD CONSTRAINT domains_pkey PRIMARY KEY (domain, sourceid);
ALTER TABLE ONLY public.domains
    ADD CONSTRAINT domains_ibfk_1 FOREIGN KEY (sourceid) REFERENCES public.sources(sourceid);

### Tabulka pro zdroje

CREATE TABLE public.sources (
    sourceid integer DEFAULT nextval('public.sources_seq'::regclass) NOT NULL,
    link character varying(255) DEFAULT NULL::character varying
);
ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_pkey PRIMARY KEY (sourceid);

a spustit skript **blacklist.py**, který tabulky naplní.


Navod na instalaci kompletni aplikace
Stahnout nejnovejsi verzi aplikace Snort3:
https://github.com/snort3/snort3
v readme.md je uvedeno jak toto nainstalovat.

V uvedenych zdrojovych souborech jsou pravidla,
je potrebne je umistit do slozky rules

Deskriptory pro openappid jsou ve slozce odp

Dale je potreba nainstalovat snort3Extra:
- vsechny potrebne soubory i upravene kody se nachazi v slozce snort3_extra
v readme.md je uvedeno jak toto nainstalovat.

V konfiguracnim souboru snort.lua je potrebne nastavit
appid - cestu k deskriptorum
a povolit openappid_listener.


Pro vytvoreni modelu byl vytvoren skript init_model.sh
Pro dotrenovani modelu byl vytvoren skript train_normal.sh
Pro vyvoreni dat pro experimenty nad anomaliemi byl vytvoren skript train_anomaly.sh




Pro natrenovani modelu XGBoost je potreba zkopirovat vytvorena data z init_model.sh a train_normal.sh, a to
df_mixed_normalized a df_normal_normalized do slozky XGBoost a pustit skript xg_ai.py

Pro spravnou funkci predikcniho modelu je potreba upravit cestu v souborech appid_listener ve snort3Extra

pro spusteni sberu dat je potreba nastavit ve snort.lua nasledujici konfiguraci:

appid_listener = {
json_logging = true,
file = ’test.json’
}

Pro detekci anomalii je potreba spustit s nasledujici kofiguraci:

appid_listener = {
anomaly_detection = true,
json_logging = true,
file = ’test.json’
}

spusteni programu snort probiha nasledovne:

/bin/snort -c "/etc/snort/snort.lua" -r "$file" --plugin-path "/lib/snort"

kde plugin path je cesta ke snort3Extra pluginum.
