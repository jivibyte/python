import os
from synthetic_data_generator.conf.proj_conf import get_output_path

def get_output_file(output_filename):
    """
    Retrieve the full file path for the output CSV file.

    Constructs the full file path by joining the output directory path with a predefined
    output file name. Path separators are normalized to forward slashes.

    Returns:
        str: The absolute path to the output CSV file with forward slashes.
    """
    complete_name = os.path.join(get_output_path(), output_filename).replace('\\', '/')
    return complete_name

taxi_trips_data_op_csv = 'taxi_trip_data.csv'
out_file_csv = get_output_file(taxi_trips_data_op_csv)
taxi_trips_data_op_parquet = 'taxi_trip_data.parquet'
out_file_parquet = get_output_file(taxi_trips_data_op_parquet)