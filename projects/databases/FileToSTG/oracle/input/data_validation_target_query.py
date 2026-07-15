# This module contains the SQL query to fetch data from the Oracle database.
# Note: Do not include ";" at the end of the query string as it may cause issues when executing the query."
tgt_query = """SELECT pick_up_time, drop_off_time, trip_distance,trip_fare,payment_method,cab_color,pickup_location,pickup_zone,dropoff_location,dropoff_zone FROM taxi_trips_data"""