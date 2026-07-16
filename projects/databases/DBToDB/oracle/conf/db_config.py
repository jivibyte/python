# Import
from credentials_vault.oracle_credentials import hr_db

# Using Oracle Instant Client Path
orcl_client_path = r"C:\development\db_files\instantclient_21_3"

# Source and Target Database Connection Details
tgt_db_orcl_conn={'host':'192.168.56.102','port':'1522','service_name':'orclpdb21c'}

# Set up username, password, and DSN for Source and Target Database Connections
tgt_db_orcl = {'user': hr_db['username'], 'password': hr_db['password'], 'host': tgt_db_orcl_conn['host'], 'port': tgt_db_orcl_conn['port'], 'service_name': tgt_db_orcl_conn['service_name']}

