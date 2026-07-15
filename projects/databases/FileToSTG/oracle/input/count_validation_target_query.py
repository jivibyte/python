# This module contains the SQL query to fetch row count from the Oracle database.
# Note: Do not include ";" at the end of the query string as it may cause issues when executing the query."
tgt_query = """SELECT count(*) FROM taxi_trips_data_5"""