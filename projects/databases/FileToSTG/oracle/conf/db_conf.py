import oracledb
from secret_vault.db_credentials import ora_db_local 
from sqlalchemy import create_engine  

ora_db_conf = {'host': 'localhost', 'port': 1521, 'service_name': 'ORCLPDB'}
ora_db_dsn = oracledb.makedsn(ora_db_conf['host'], ora_db_conf['port'], service_name=ora_db_conf['service_name'])
ora_user = ora_db_local['username']
ora_password = ora_db_local['password']
ora_engine = create_engine(f"oracle+oracledb://{ora_user}:{ora_password}@{ora_db_dsn}")