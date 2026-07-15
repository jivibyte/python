from datetime import date, datetime, timedelta
import random
import pandas as pd
import numpy as np
from synthetic_data_generator.conf.proj_conf import timer
from synthetic_data_generator.conf.output_file import out_file_csv, out_file_parquet

"""
Constants:
    suburbs (list): List of 195 NYC neighborhoods and locations for pickup/dropoff
    output_filename (str): Name of the output CSV file ('taxi_trip_data.csv')
    complete_name (str): Full file path for the output CSV file
"""
suburbs = ['Lenox Hill West', 'Upper West Side South', 'Alphabet City', 'Hudson Sq', 'Midtown East', 'Times Sq/Theatre District', 'Battery Park City', 'Murray Hill', 'East Harlem South', 'Lincoln Square East', 'LaGuardia Airport', 'Lincoln Square West', 'Financial District North', 'Upper West Side North', 'East Chelsea', 'Midtown Center', 'Gramercy', 'Penn Station/Madison Sq West', 'Sutton Place/Turtle Bay North', 'West Chelsea/Hudson Yards', 'Clinton East', 'Clinton West', 'UN/Turtle Bay South', 'Midtown South', 'Midtown North', 'Garment District', 'Lenox Hill East', 'Flatiron', 'TriBeCa/Civic Center', 'Upper East Side North', 'West Village', 'Greenwich Village South', 'JFK Airport', 'East Village', 'Union Sq', 'Yorkville West', 'Central Park', 'Meatpacking/West Village West', 'Kips Bay', 'Morningside Heights', 'Astoria', 'East Tremont', 'Upper East Side South', 'Financial District South', 'Bloomingdale', 'Queensboro Hill', 'SoHo', 'Brooklyn Heights', 'Yorkville East', 'Manhattan Valley', 'DUMBO/Vinegar Hill', 'Little Italy/NoLiTa', 'Mott Haven/Port Morris', 'Greenwich Village North', 'Stuyvesant Heights', 'Lower East Side', 'East Harlem North', 'Chinatown', 'Fort Greene', 'Steinway', 'Central Harlem', 'Crown Heights North', 'Seaport', 'Two Bridges/Seward Park', 'Boerum Hill', 'Williamsburg (South Side)', 'Rosedale', 'Flushing', 'Old Astoria', 'Soundview/Castle Hill', 'Stuy Town/Peter Cooper Village', 'World Trade Center', 'Sunnyside', 'Washington Heights South', 'Prospect Heights', 'East New York', 'Hamilton Heights', 'Cobble Hill', 'Long Island City/Queens Plaza', 'Central Harlem North', 'Manhattanville', 'East Flatbush/Farragut', 'Elmhurst', 'East Concourse/Concourse Village', 'Park Slope', 'Greenpoint', 'Williamsburg (North Side)', 'Long Island City/Hunters Point', 'South Ozone Park', 'Ridgewood', 'Downtown Brooklyn/MetroTech', 'Queensbridge/Ravenswood', 'Williamsbridge/Olinville', 'Bedford', 'Gowanus', 'Jackson Heights', 'South Jamaica', 'Bushwick North', 'West Concourse', 'Queens Village', 'Windsor Terrace', 'Flatlands', 'Van Cortlandt Village', 'Woodside', 'East Williamsburg', 'Fordham South', 'East Elmhurst', 'Kew Gardens', 'Flushing Meadows-Corona Park', 'Marine Park/Mill Basin', 'Carroll Gardens', 'Canarsie', 'East Flatbush/Remsen Village', 'Jamaica', 'Marble Hill', 'Bushwick South', 'Erasmus', 'Claremont/Bathgate', 'Pelham Bay', 'Soundview/Bruckner', 'South Williamsburg', 'Battery Park', 'Forest Hills', 'Maspeth', 'Bronx Park', 'Starrett City', 'Brighton Beach', 'Brownsville', 'Highbridge Park', 'Bensonhurst East', 'Mount Hope', 'Prospect-Lefferts Gardens', 'Bayside', 'Douglaston', 'Midwood', 'North Corona', 'Homecrest', 'Westchester Village/Unionport', 'University Heights/Morris Heights', 'Inwood', 'Washington Heights North', 'Flatbush/Ditmas Park', 'Rego Park', 'Riverdale/North Riverdale/Fieldston', 'Jamaica Estates', 'Borough Park', 'Sunset Park West', 'Belmont', 'Auburndale', 'Schuylerville/Edgewater Park', 'Co-Op City', 'Crown Heights South', 'Spuyten Duyvil/Kingsbridge', 'Morrisania/Melrose', 'Hollis', 'Parkchester', 'Coney Island', 'East Flushing', 'Richmond Hill', 'Bedford Park', 'Highbridge', 'Clinton Hill', 'Sheepshead Bay', 'Madison', 'Dyker Heights', 'Cambria Heights', 'Pelham Parkway', 'Hunts Point', 'Melrose South', 'Springfield Gardens North', 'Bay Ridge', 'Elmhurst/Maspeth', 'Crotona Park East', 'Bronxdale', 'Briarwood/Jamaica Hills', 'Van Nest/Morris Park', 'Murray Hill-Queens', 'Kingsbridge Heights', 'Whitestone', 'Saint Albans', 'Allerton/Pelham Gardens', 'Howard Beach', 'Norwood', 'Bensonhurst West', 'Columbia Street', 'Middle Village', 'Prospect Park', 'Ozone Park', 'Gravesend', 'Glendale', 'Kew Gardens Hills', 'Woodlawn/Wakefield', 'West Farms/Bronx River', 'Hillcrest/Pomonok']

def trip_time():
    """
    Generates a random datetime between start_datetime and end_datetime.
    """
    start_dt = datetime(2024, 1, 1, 0, 0, 0)
    end_dt = datetime(2024, 12, 31, 23, 59, 59)
    # Calculate the total number of seconds in the range
    total_seconds = int((end_dt - start_dt).total_seconds())
    # Generate a random number of seconds to add
    random_seconds = random.randrange(total_seconds + 1)
    # Add the random seconds to the start datetime
    random_time = str(start_dt + timedelta(seconds=random_seconds)).split(' ')[-1]   
    return random_time

@timer
def trip_statistics_data_csv(size):
    """
    Generates a CSV file containing random taxi trip statistics data.
    
    Creates a DataFrame with simulated taxi trip information including pickup and dropoff
    details, trip distance, fare, payment method, and cab characteristics. The data is
    then saved to a CSV file.
    
    Args:
        size (int): The number of trip records to generate.
    
    Returns:
        None: Writes the generated data to a CSV file specified by 'complete_name' variable.
    
    Generates the following columns:
        - pick_up_date (datetime): Random date between 2023-01-01 and 2025-12-31
        - pick_up_time (datetime): Random pickup time with hour (0-23) and minute (0-59)
        - drop_off_time (datetime): Random dropoff time with hour (0-23) and minute (0-59)
        - trip_distance (float): Random distance between 0.1 and 100.0 units
        - trip_fare (float): Random fare between $5.0 and $500.0
        - payment_method (str): Random payment method (cash, debit_card, mobile_payment, credit_card, transit_card, Venmo)
        - cab_color (str): Random cab color (yellow, green, black, white, blue)
        - pickup_location (str): Random pickup location from 'suburbs' list
        - pickup_zone (str): Random pickup zone (airport, business_district, entertainment_district, residential, train_station)
        - dropoff_location (str): Random dropoff location from 'suburbs' list
        - dropoff_zone (str): Random dropoff zone (airport, business_district, entertainment_district, residential, train_station)
    
    Note:
        Requires the 'suburbs' variable and 'complete_name' file path to be defined in the calling scope.
    Generates a dictionary containing random trip statistics data.
    """
    df = pd.DataFrame()
    df['pick_up_date'] = np.random.choice(pd.date_range(start=date(2023, 1, 1), end=date(2025, 12, 31)), size=size)
    df['pick_up_time'] = [trip_time() for _ in range(size)]
    df['drop_off_time'] = [trip_time() for _ in range(size)]
    df['trip_distance'] = np.round(np.random.uniform(low=0.1, high=100.0, size=size), 2)
    df['trip_fare'] = np.round(np.random.uniform(low=10.0, high=100.0, size=size), 2)
    df['payment_method'] = np.random.choice(['cash', 'debit_card', 'mobile_payment', 'credit_card', 'transit_card', 'Venmo'], size=size)
    df['cab_color'] = np.random.choice(['yellow', 'green', 'black', 'white', 'blue'], size=size)
    df['pickup_location'] = np.random.choice(suburbs, size=size)
    df['pickup_zone'] = np.random.choice(['airport', 'business_district', 'entertainment_district', 'residential', 'train_station'], size=size)
    df['dropoff_location'] = np.random.choice(suburbs, size=size)
    df['dropoff_zone'] = np.random.choice(['airport', 'business_district', 'entertainment_district', 'residential', 'train_station'], size=size)
    df.to_csv((out_file_csv), index=False)
    return "Data generation complete. CSV file created at: " + out_file_csv +" with " + str(size) + " records."

@timer
def trip_statistics_data_parquet(size):
    """
    Generate synthetic trip statistics data and save to a Parquet file.
    
    This function creates a pandas DataFrame with randomly generated taxi trip data
    including pickup/dropoff information, times, distances, fares, and payment methods.
    The generated data is written to a Parquet file for efficient storage and retrieval.
    
    Parameters
    ----------
    size : int
        The number of synthetic trip records to generate.
    
    Returns
    -------
    str
        A completion message indicating the Parquet file location and number of records created.
    
    Notes
    -----
    - Pickup dates are randomly selected between January 1, 2023 and December 31, 2025.
    - Trip distances range from 0.1 to 100.0 miles, rounded to 2 decimal places.
    - Trip fares range from $10.0 to $100.0, rounded to 2 decimal places.
    - Pickup and dropoff locations are randomly selected from a predefined suburbs list.
    - Zones include: airport, business_district, entertainment_district, residential, and train_station.
    - Payment methods include: cash, debit_card, mobile_payment, credit_card, transit_card, and Venmo.
    - Cab colors include: yellow, green, black, white, and blue.
    
    Examples
    --------
    >>> result = trip_statistics_data_parquet(1000)
    >>> print(result)
    Data generation complete. Parquet file created at: [path] with 1000 records.
    """
    df = pd.DataFrame()
    df['pick_up_date'] = np.random.choice(pd.date_range(start=date(2023, 1, 1), end=date(2025, 12, 31)), size=size)
    df['pick_up_time'] = [trip_time() for _ in range(size)]
    df['drop_off_time'] = [trip_time() for _ in range(size)]
    df['trip_distance'] = np.round(np.random.uniform(low=0.1, high=100.0, size=size), 2)
    df['trip_fare'] = np.round(np.random.uniform(low=10.0, high=100.0, size=size), 2)
    df['payment_method'] = np.random.choice(['cash', 'debit_card', 'mobile_payment', 'credit_card', 'transit_card', 'Venmo'], size=size)
    df['cab_color'] = np.random.choice(['yellow', 'green', 'black', 'white', 'blue'], size=size)
    df['pickup_location'] = np.random.choice(suburbs, size=size)
    df['pickup_zone'] = np.random.choice(['airport', 'business_district', 'entertainment_district', 'residential', 'train_station'], size=size)
    df['dropoff_location'] = np.random.choice(suburbs, size=size)
    df['dropoff_zone'] = np.random.choice(['airport', 'business_district', 'entertainment_district', 'residential', 'train_station'], size=size)
    df.to_parquet(out_file_parquet, index=False)
    return "Data generation complete. Parquet file created at: " + out_file_parquet +" with " + str(size) + " records."