__author__ = "Michal Dostal"
__license__ = "GNU-GPL v3.0"
__version__ = "1.0.1"
__email__ = "xdosta51@stud.fit.vutbr.cz"

#Imports
import pandas as pd

#Read csv that is not in usable format
df = pd.read_csv('all_flows.csv')

#Columns in good shape
df = df[['server_bytes', 'http_user_agent', 'client_pkts', 'apps_payload', 'server_pkts',
         'http_referrer', 'user_info_username', 'dns_host', 'netbios_info_netbios_domain',
         'proto', 'pkt_time', 'client_bytes', 'client_info_version', 'http_host',
         'apps_referred', 'service_info_vendor', 'apps_client', 'service_info_subtype_version',
         'user_info_id', 'apps_misc', 'apps_service', 'service_info_port', 'session_num',
         'service_info_subtype_service', 'pkt_num', 'client_info_ip', 'service_info_ip',
         'service_info_version', 'tls_host', 'user_info_login_status', 'total_flow_latency',
         'netbios_info_netbios_name', 'http_httpx_stream', 'http_response_code',
         'client_info_port', 'http_url']]

#Save swapped dataframe
df.to_csv('all_flows_swap.csv', index=False)
