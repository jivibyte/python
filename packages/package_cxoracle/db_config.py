# Import
from credentials_vault.oracle_credentials import hr_db
import cx_Oracle

# Using Oracle Instant Client Path
orcl_client_path = r"C:\development\db_files\instantclient_21_3"

# Source and Target Database Connection Details
src_db_orcl_conn={'host':'192.168.56.102','port':1522,'service_name':'orclpdb21c'}
tgt_db_orcl_conn={'host':'192.168.56.102','port':1522,'service_name':'orclpdb21c'}

# Defining DSN for Source and Target Database Connections : Do not Modify the below code unless you know what you are doing
src_db_dsn = cx_Oracle.makedsn(src_db_orcl_conn['host'], src_db_orcl_conn['port'], service_name=src_db_orcl_conn['service_name'])
tgt_db_dsn = cx_Oracle.makedsn(tgt_db_orcl_conn['host'], tgt_db_orcl_conn['port'], service_name=tgt_db_orcl_conn['service_name'])

# Set up username, password, and DSN for Source and Target Database Connections
src_db_orcl = {'user': hr_db['username'], 'password': hr_db['password'], 'dsn': src_db_dsn}
tgt_db_orcl = {'user': hr_db['username'], 'password': hr_db['password'], 'dsn': tgt_db_dsn}