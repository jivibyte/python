from projects.databases.DBToDB.oracle.src.core_engine import QEngineDBToDB
from projects.databases.DBToDB.oracle.input.count_validation_query import *
from projects.databases.DBToDB.oracle.conf.db_config import tgt_db_orcl

source_inst = QEngineDBToDB(**tgt_db_orcl)
target_inst = QEngineDBToDB(**tgt_db_orcl)


src_row_count = (source_inst.execute_query(src_query)[0][0])
tgt_row_count = (target_inst.execute_query(tgt_query)[0][0])

if src_row_count == tgt_row_count:
    print(f"Row count validation successful. Source and Target row counts match: {src_row_count}")
else:
    print(f"Row count validation failed. Source row count: {src_row_count}, Target row count: {tgt_row_count}")
