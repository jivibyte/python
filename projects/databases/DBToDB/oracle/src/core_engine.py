import pandas as pd
from sqlalchemy import create_engine, text
from projects.databases.DBToDB.oracle.conf.db_config import tgt_db_orcl
from projects.databases.DBToDB.oracle.conf.proj_conf import get_output_path, timer
from datetime import datetime


class QEngineDBToDB:
    def __init__(self, **connection_params: dict):
        self.username = connection_params.get('user')
        self.password = connection_params.get('password')
        self.host = connection_params.get('host')
        self.port = connection_params.get('port')
        self.service_name = connection_params.get('service_name')

        # Create the connection engine
        # Format: oracle+cx_oracle://user:pass@host:port/?service_name=xyz
        self.connection_string = f"oracle+cx_oracle://{self.username}:{self.password}@{self.host}:{self.port}/?service_name={self.service_name}"
        self.engine = create_engine(self.connection_string)  # Performance tip: use arraysize

    def get_table_schema(self, table_name: str):
            """
            Get the schema of a specified table.
            
            :param table_name: Name of the table to get the schema for
            :return: Pandas DataFrame containing the table schema
            """
            query = text(f"SELECT table_name, column_name, data_type, char_length, data_precision, data_scale FROM all_tab_columns WHERE table_name = '{table_name.upper()}'")
            with self.engine.connect() as connection:
                result = connection.execute(query)
                return result.fetchall()

    def fetch_data_as_dataframe(self, query: str) -> pd.DataFrame:
        """
        Fetch data from the database using the provided SQL query and return it as a Pandas DataFrame.
        
        :param query: SQL query to execute
        :return: Pandas DataFrame containing the fetched data
        """
        query = text(query)
        df = pd.read_sql(query, con=self.engine)
        return df

    def execute_query(self, query: str):
        """
        Execute a SQL query on the database.
        
        :param query: SQL query to execute
        :return: Result of the executed query
        """
        query = text(query)
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchall()
    
    def get_row_count(self, table_name: str) -> int:
        """
        Get the row count of a specified table.
        
        :param table_name: Name of the table to count rows
        :return: Number of rows in the specified table
        """
        query = text(f"SELECT COUNT(*) FROM {table_name}")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            row_count = result.scalar()
            return row_count
    
    def close_connection(self):
        """
        Close the database connection.
        """
        self.engine.dispose()
    
    def check_object_existence(self, object_name: str, object_type: str) -> bool:
        """
        Check if a specific object (table, view, etc.) exists in the database.
        
        :param object_name: Name of the object to check
        :param object_type: Type of the object (e.g., 'TABLE', 'VIEW')
        :return: True if the object exists, False otherwise
        """
        query = text(f"SELECT COUNT(*) FROM all_objects WHERE object_name = '{object_name.upper()}' AND object_type = '{object_type.upper()}'")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            exists = result.scalar() > 0
            return exists
       
    def get_db_version(self) -> str:
        """
        Get the version of the connected Oracle database.
        
        :return: Oracle database version as a string
        """
        query = text("SELECT * FROM v$version")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            version_info = result.fetchone()
            return version_info[0] if version_info else "Unknown Version"
    
    def get_current_user(self) -> str:
        """
        Get the current user connected to the Oracle database.
        
        :return: Current user as a string
        """
        query = text("SELECT USER FROM dual")
        with self.engine.connect() as connection:
            result = connection.execute(query)
            current_user = result.scalar()
            return current_user
    
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