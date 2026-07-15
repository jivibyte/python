import pandas as pd
from projects.databases.FileToSTG.oracle.conf.proj_conf import get_output_path, timer
from projects.databases.FileToSTG.oracle.conf.input_file import desired_columns, input_file_path, delimiter

#@timer
def read_csv_data_to_df(file_path):
    """
    Reads a CSV file from the specified file path and returns it as a pandas DataFrame.
    
    Args:
        file_path (str): The path to the CSV file to be read.
        """
    read_csv_file = pd.read_csv(file_path, usecols=desired_columns, delimiter=delimiter)
    return pd.DataFrame(read_csv_file)

def read_csv_row_count(file_path):
    """
    Reads a CSV file from the specified file path and returns the number of rows in the DataFrame.
    
    Args:
        file_path (str): The path to the CSV file to be read.   
    Returns:
        int: The number of rows in the DataFrame.
    """
    read_csv_file = pd.read_csv(file_path, usecols=desired_columns)
    return read_csv_file.shape[0]

def check_ora_conn(ora_engine):
    """
    Checks the connection to the Oracle database using the provided SQLAlchemy engine.
    
    Args:
        ora_engine: The SQLAlchemy engine object used to connect to the Oracle database.
    
    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        with ora_engine.connect() as connection:
            print("Successfully connected to the Oracle database.")
            return True
    except Exception as e:
        print(f"Failed to connect to the Oracle database: {e}")
        return False
    
def close_ora_conn(ora_engine):
    """
    Closes the connection to the Oracle database.
    
    Args:
        ora_engine: The SQLAlchemy engine object used to connect to the Oracle database.
    """
    try:
        ora_engine.dispose()
        print("Oracle database connection closed successfully.")
    except Exception as e:
        print(f"Failed to close the Oracle database connection: {e}")

#@timer
def pd_read_sql(query, ora_engine):
    """
    Executes a SQL query and returns the result as a pandas DataFrame.
    Args:
        query (str): The SQL query to be executed.
        connection: The database connection object to use for executing the query.
    Returns:
        pd.DataFrame: A DataFrame containing the results of the SQL query.
    """
    if check_ora_conn(ora_engine):
        print("Reading data from Oracle database...")
        return pd.read_sql(query, con=ora_engine.connect())
    return "Unable to read data from Oracle database due to connection issues."

@timer
def data_compare_dataframes(df1, df2):
    """
    Compares two pandas DataFrames for equality and returns a DataFrame containing the differences.
    Args:
        df1 (pd.DataFrame): The first DataFrame to compare.
        df2 (pd.DataFrame): The second DataFrame to compare.    
    Returns:        pd.DataFrame: A DataFrame containing the differences between the two input DataFrames.  """
    if df1.equals(df2):
        return "Src File and Target Table are identical"
    else:
        # Create a DataFrame to hold the differences
        differences = pd.concat([df1, df2]).drop_duplicates(keep=False)
        return differences
    
@timer
def count_compare_dataframes(df1, df2):
    """
    Compares two pandas DataFrames for equality and returns a DataFrame containing the differences.
    Args:
        df1 (pd.DataFrame): The first DataFrame to compare.
        df2 (pd.DataFrame): The second DataFrame to compare.    
    Returns:        pd.DataFrame: A DataFrame containing the differences between the two input DataFrames.  """
    if df1 == df2.values[0][0]:
        return "Row Count in File is Equal to Row Count in Target Table"
    else:
        # Create a DataFrame to hold the differences
        differences = pd.concat([df1, df2]).drop_duplicates(keep=False)
        return differences    