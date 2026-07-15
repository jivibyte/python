from projects.databases.FileToSTG.oracle.conf.proj_conf import get_input_path

input_file_name = 'taxi_trip_data.csv'
delimiter = ','
desired_columns = ['pick_up_time', 'drop_off_time', 'trip_distance', 'trip_fare', 'payment_method', 'cab_color', 'pickup_location', 'pickup_zone', 'dropoff_location', 'dropoff_zone']

def get_input_file(input_file_name):
    """
    Retrieve the full file path for the input CSV file.

    Constructs the full file path by joining the input directory path with a predefined
    input file name. Path separators are normalized to forward slashes.

    Returns:
        str: The absolute path to the input CSV file with forward slashes.
    """
    return f"{get_input_path()}/{input_file_name}"

input_file_path = get_input_file(input_file_name)
