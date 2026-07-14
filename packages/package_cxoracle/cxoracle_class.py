import cx_Oracle
import sys
from projects.databases.oracle.conf import db_config

class OracleCoreEngine:

    # Initialize the Oracle client libraries if they aren't in your system path
    # This is needed to be done only once per process, so it is safe to do it in the class constructor
    # If you initialize the client libraries more than once, it will raise an exception
    cx_Oracle.init_oracle_client(lib_dir=db_config.orcl_client_path)
    # Create an Error Code Map as Class Variable to be used in any of the custom methods
    _oracle_error_map = {955: 'Table Already Exists',
                         1109: 'Error: Database Is not Open',
                         12153: 'Error: Not currently connected to a remote host. Please check connection',
                         12154: 'Error: Could not resolve the connect identifier specified',
                         12236: 'Error: Protocol support not loaded',
                         12235: 'Error: Failure to redirect to destination. Please reach out to Network Administrator',
                         12233: 'Error: Failure to accept a connection. Please reach out to Network Administrator',
                         12231: 'Error: No connection possible to destination. Please reach out to Network Administrator',
                         12230: 'Error: Severe Network error occurred in making this connection. Please reach out to Network Administrator',
                         12225: 'Error: Destination host unreachable. Please check your Network Connection or Reach out to Network Administator',
                         12224: 'Error: No Listener. Please check if listener service is running and compare the TNSNAMES.ORA entry with the appropriate LISTENER.ORA file',
                         12223: 'Error: Too many TNS connections open simultaneously. Please close few connections and re-try',
                         12170: 'Error: Connection has timed out',
                         12168: 'Error: Unable to contact LDAP Directory Server',
                         12157: 'Error: Internal error during network communication.'}

    def __init__(self, **connection_params: dict):
        '''
        Initialize the class to load the oracle client
        Arguments to this method is - **kwargs
        **Key word argument (has three params, user, password and the dsn)
        '''
        # get the client version and assign it to initialization attribute
        self.client_version = cx_Oracle.clientversion()
        # assign the user provided db_user to initialization method, for reuse across all methods
        # use _ to make this a private variable, which can be read but cannot be modified
        self._db_user = connection_params.get('user')
        # assign the user provided db_password to initialization method, for reuse across all methods
        # use __ to mangle the variable, so that the instantiated object cannot see this variable and its value
        self.__db_password = connection_params.get('password')
        # assign the user provided connection_dsn to initialization method, for reuse across all methods
        self.connection_dsn = connection_params.get('dsn')
        '''
        By default, connection pools are ‘homogeneous’, meaning that all connections use the same database credentials. 
        However, if the pool option homogeneous is False at the time of pool creation, then a ‘heterogeneous’ pool will 
        be created. This allows different credentials to be used each time a connection is acquired from the pool with 
        acquire(). This approach makes the class more flexible to be used with different instantiated objects
        '''
        self.pool = cx_Oracle.SessionPool(dsn=self.connection_dsn, homogeneous=False)
        try:
            '''
            When a heterogeneous pool is created by setting homogeneous to False and no credentials are supplied during pool
            creation, then a user name and password may be passed to acquire():
            '''
            self.db_auto_connect = self.pool.acquire(user=self._db_user, password=self.__db_password)

        except cx_Oracle.DatabaseError as _errors:
            # Capture the errors in a variable
            _error, = _errors.args
            # The corresponding error code is loaded in to _error.code
            # Check if the encountered error is defined in the error map
            # If its defined, print the custom message based on the mapped key and value
            if _error.code in OracleCoreEngine._oracle_error_map.keys():
                print(OracleCoreEngine._oracle_error_map[_error.code])
                # In case the code enters the except block
                # user will be provided with error brief and code will exit without execute any more statements
                sys.exit()


    def check_object_existence(self, db_schema_name, db_obj_name):
        '''
        Method to check Existence of a Database Object
        Arguments to this Method: schema name and object name
        '''
        # Prepare the query to check the object in Oracle Database
        _existence_qry = f"Select owner, object_name, object_type from all_objects where 1=1 and owner='{db_schema_name}' and object_name='{db_obj_name}'"
        # Connect to Database
        with self.db_auto_connect.cursor() as cursor:
            # Use Ternary operator, validate the bool return type of the query
            # fetchall() is needed to pull the results of the existence query in a list
            # If the list is empty, then the table does not exists
            return ((False, True) [bool(len(cursor.execute(_existence_qry).fetchall()))])

    def create_db_object_auto_commit(self, _sql_query_or_sql_variable):
        '''
        Method to Create a DB object and commit the changes
        Arguments to this Method: Sql Query or SQL Variable
        Note: Method verifies the existence of create keyword in the input statement
        '''
        try:
            # Connect to Database
            with self.db_auto_connect.cursor() as cursor:
                # Execute the query using the cursor
                cursor.execute(_sql_query_or_sql_variable)
            # Commit the DDL
            self.db_commit()
        # In Case Database Error occurs
        except cx_Oracle.DatabaseError as _errors:
            # Capture the errors in a variable
            _error, = _errors.args
            # The corresponding error code is loaded in to _error.code
            # Check if the encountered error is defined in the error map
            # If its defined, print the custom message based on the mapped key and value            
            if _error.code in OracleCoreEngine._oracle_error_map.keys():
                # Following will be generated, if the Object already exists, if thats the case, simply ignore it
                if _error.code == 955:
                    pass
                # Else, present the error code, so that it can be added to the code
                else:
                    print(OracleCoreEngine._oracle_error_map[_error.code])
            else:
                print('Method- create_db_object_auto_commit: Unmapped Errod Code, Please update error mapping for the class')
    
    def db_version(self):
        '''
        Method to get the DB version of the connected DB
        Arguments to this method: None
        '''
        return self.db_auto_connect.version
    
    def db_release_conn_to_pool(self):
        '''
        Method to release connections back to pool
        Argument to this method:- None
        '''
        self.pool.release(self.db_auto_connect)
    
    def db_close_conn_pool(self):
        '''
        Method to close the connection pool
        Argument to this method:- None
        '''
        self.pool.close()
    
    def db_manual_commit(self):
        '''
        Method to manually commit the sql
        Arguments to this method: None
        Note: This is defined, since connection.autocommit is set to False by default, and I have kept it that way
        '''
        self.db_auto_connect.commit()

    def db_cursor_close(self):
        '''
        Method to manually close the cursor
        Arguments to this method: None
        '''
        return self.db_cursor_open().close()

    def db_cursor_open(self):
        '''
        Method to create a cursor on the connected database
        Arguments to this method: None
        '''
        print('Cursor is manually opened, always remember to close it by calling db_cursor_close')
        return self.db_auto_connect.cursor()
    
    def db_disconnect(self):
        '''
        Method to close the connection to database
        Arguments to this method: None
        Note: This method is manual, since I did not use auto object / connection termination using 'with'
        '''
        self.db_auto_connect.close()
    
    def db_get_row_cnt_of_table(self, table_name):
        '''
        Method to get the row count in a given table
        Argument to this method is: Name of the table
        Argument can be provided as standalone table name or with the schema.table_name
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor() as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            '''
            Asserting SQL Object names taken as user input is a good security practice to avoid sql injection attack
            In following line:
            1. callfunc() : Is used to call a user defined or system provided function
            2. sys.dbms_assert.sql_object_name :- Is a Oracle DB provided function to validate if provided input is
                a valid sql object (A Table name in this case)
            3. Input to this function are two parameters (type) "String" and (object_name) "Table name"
            '''
            try:
                asserted_table_name = cursor.callfunc('sys.dbms_assert.sql_object_name', cx_Oracle.STRING, [table_name])
                # Pass the asserted table name as variable to _sql_query
                _sql_query = f'Select count(1) from {asserted_table_name}'
                # Fetch only first item from the cursor in to results
                execute = cursor.execute(_sql_query).fetchone()
                return execute[0]
            except cx_Oracle.DatabaseError as _errors:
                _error, = _errors.args
                if _error.code == 44002:
                    return 'Invalid SQL Object Name, Please verify Object Name provided....'
    
    def db_get_column_names_of_table_by_sql_qry(self, _sql_query_or_sql_variable):
        '''
        Method to get the column names based on the sql query or sql variable
        Argument to this method is: SQL Query or Variable containing the SQL query
        '''
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # Fetch the column names from cursor.description using list comprehension
            # 'description' attribute on a cursor holds the column names for the tables in question
            columns = [row[0] for row in execute.description]
        # return type of this method is a list
        return columns
    
    def db_execute_sql_fetch_all_as_dict(self, _sql_query_or_sql_variable):
        '''
        Method to execute a sql query or a query stored in a variable & fetch all results
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Both Column names & Values are returned as a dictionary
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor() as cursor:
            # 'arraysize' attribute of cursor is a performance tuning parameter
            # For queries returning unknown number of rows (basically large) or production set up
            # It's advisable to leave the 'prefetchrows' attribute to its default value of 2 and only adjust arraysize
            # I have kept the arraysize = 500 (same as in sql developer config), but this number should change
            # based on what kind of production load are we dealing with
            # Additional Info on Tuning is here:- https://cx-oracle.readthedocs.io/en/latest/user_guide/tuning.html?
            cursor.arraysize = 500
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # Fetch the column names from cursor.description using list comprehension
            # 'description' attribute on a cursor holds the column names for the tables in question
            columns = [row[0] for row in execute.description]
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a dictionary
            # dict keys - Are the columns names in the table
            execute.rowfactory = lambda *args: dict(zip(columns, args))
            # FetchALL the rows from cursor in to results
            results = execute.fetchall()
        # return type of this method is dictionary
        return results
    
    def db_execute_sql_fetch_all_as_list(self, _sql_query_or_sql_variable):
        '''
        Method to execute a sql query or a query stored in a variable & fetch all results
        Argument to this method is: SQL Query or Variable containing the SQL query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor() as cursor:
            # 'arraysize' attribute of cursor is a performance tuning parameter
            # For queries returning unknown number of rows (basically large) or production set up
            # It's advisable to leave the 'prefetchrows' attribute to its default value of 2 and only adjust arraysize
            # I have kept the arraysize = 500 (same as in sql developer config), but this number should change
            # based on what kind of production load are we dealing with
            # Additional Info on Tuning is here:- https://cx-oracle.readthedocs.io/en/latest/user_guide/tuning.html?
            cursor.arraysize = 500
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples values to list
            execute.rowfactory = lambda *args: list(args)
            # FetchALL the rows from cursor in to results
            results = execute.fetchall()
        # return type of this method is list
        return results
    
    def db_execute_sql_fetch_all_as_set(self, _sql_query_or_sql_variable):
        '''
        Method to execute a sql query or a query stored in a variable & fetch all results
        Argument to this method is: SQL Query or Variable containing the SQL query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor() as cursor:
            # 'arraysize' attribute of cursor is a performance tuning parameter
            # For queries returning unknown number of rows (basically large) or production set up
            # It's advisable to leave the 'prefetchrows' attribute to its default value of 2 and only adjust arraysize
            # I have kept the arraysize = 500 (same as in sql developer config), but this number should change
            # based on what kind of production load are we dealing with
            # Additional Info on Tuning is here:- https://cx-oracle.readthedocs.io/en/latest/user_guide/tuning.html?
            cursor.arraysize = 500
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples values to a set values
            execute.rowfactory = lambda *args: set(args)
            # FetchALL the rows from cursor in to results
            results = execute.fetchall()
        # return type of this method is set
        return results
    
    def db_execute_sql_fetch_all_as_tuples(self, _sql_query_or_sql_variable):
        '''
        Method to execute a sql query or a query stored in a variable & fetch all results
        Argument to this method is: SQL Query or Variable containing the SQL query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor() as cursor:
            # 'arraysize' attribute of cursor is a performance tuning parameter
            # For queries returning unknown number of rows (basically large) or production set up
            # It's advisable to leave the 'prefetchrows' attribute to its default value of 2 and only adjust arraysize
            # I have kept the arraysize = 500 (same as in sql developer config), but this number should change
            # based on what kind of production load are we dealing with
            # Additional Info on Tuning is here:- https://cx-oracle.readthedocs.io/en/latest/user_guide/tuning.html?
            cursor.arraysize = 500
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # FetchALL the rows from cursor in to results
            results = execute.fetchall()
        # return type of this method is tuple (default behavior)
        return results  
    
    def db_execute_sql_fetch_specific_num_of_rows_as_dict(self, _sql_query_or_sql_variable, _num_of_rows):
        '''
        Method to fetch specific number of rows of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor() as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = _num_of_rows
            cursor.prefetchrows = _num_of_rows + 1
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # Fetch the column names from cursor.description using list comprehension
            # 'description' attribute on a cursor holds the column names for the tables in question
            columns = [row[0] for row in execute.description]
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a dictionary
            execute.rowfactory = lambda *args: dict(zip(columns, args))
            # Fetch only specific number of rows from the cursor in to results
            results = execute.fetchmany(numRows=_num_of_rows)
        # return type of this method is a dictionary
        return results
    
    def db_execute_sql_fetch_specific_num_of_rows_as_list(self, _sql_query_or_sql_variable, _num_of_rows):
        '''
        Method to fetch specific number of rows of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor() as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = _num_of_rows
            cursor.prefetchrows = _num_of_rows + 1
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a list
            execute.rowfactory = lambda *args: list(args)
            # Fetch only specific number of rows from the cursor in to results
            results = execute.fetchmany(numRows=_num_of_rows)
        # return type of this method is a list
        return results
    
    def db_execute_sql_fetch_specific_num_of_rows_as_set(self, _sql_query_or_sql_variable, _num_of_rows):
        '''
        Method to fetch specific number of rows of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor() as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = _num_of_rows
            cursor.prefetchrows = _num_of_rows + 1
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a set
            execute.rowfactory = lambda *args: set(args)
            # Fetch only specific number of rows from the cursor in to results
            results = execute.fetchmany(numRows=_num_of_rows)
        # return type of this method is a set
        return results
    
    def db_execute_sql_fetch_specific_num_of_rows_as_tuples(self, _sql_query_or_sql_variable, _num_of_rows):
        '''
        Method to fetch specific number of rows of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor() as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = _num_of_rows
            cursor.prefetchrows = _num_of_rows + 1
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # Fetch only specific number of rows from the cursor in to results
            results = execute.fetchmany(numRows=_num_of_rows)
        # return type of this method is a tuple
        return results
    
    def db_execute_sql_fetch_last_row_as_dict(self, _sql_query_or_sql_variable):
        '''
        Method to fetch last row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # Fetch the column names from cursor.description using list comprehension
            # 'description' attribute on a cursor holds the column names for the tables in question
            columns = [row[0] for row in execute.description]
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a dictionary
            execute.rowfactory = lambda *args: dict(zip(columns, args))
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='last')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a dictionary
        return results
    
    def db_execute_sql_fetch_last_row_as_list(self, _sql_query_or_sql_variable):
        '''
        Method to fetch last row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a list
            execute.rowfactory = lambda *args: list(args)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='last')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a list
        return results
    
    def db_execute_sql_fetch_last_row_as_set(self, _sql_query_or_sql_variable):
        '''
        Method to fetch last row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a set
            execute.rowfactory = lambda *args: set(args)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='last')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a set
        return results
    
    def db_execute_sql_fetch_last_row_as_tuples(self, _sql_query_or_sql_variable):
        '''
        Method to fetch last row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='last')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a tuples
        return results
    
    def db_execute_sql_fetch_top_row_as_dict(self, _sql_query_or_sql_variable):
        '''
        Method to fetch first row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # Fetch the column names from cursor.description using list comprehension
            # 'description' attribute on a cursor holds the column names for the tables in question
            columns = [row[0] for row in execute.description]
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a dictionary
            execute.rowfactory = lambda *args: dict(zip(columns, args))
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='first')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a dictionary
        return results
    
    def db_execute_sql_fetch_top_row_as_list(self, _sql_query_or_sql_variable):
        '''
        Method to fetch first row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a list
            execute.rowfactory = lambda *args: list(args)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='first')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a list
        return results
    
    def db_execute_sql_fetch_top_row_as_set(self, _sql_query_or_sql_variable):
        '''
        Method to fetch first row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a set
            execute.rowfactory = lambda *args: set(args)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='first')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a set
        return results

    def db_execute_sql_fetch_top_row_as_list(self, _sql_query_or_sql_variable):
        '''
        Method to fetch first row of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query
        Note: Order of the result is driven by sql query
        '''
        # Open the cursor as 'with' so, it's automatically closed upon task completion
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a list
            execute.rowfactory = lambda *args: list(args)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(mode='first')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a list
        return results
    
    def db_execute_qry_fetch_specific_row_as_dict(self, _sql_query_or_sql_variable, _row_idx):
        '''
        Method to fetch specific row number of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query and row number
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            # Fetch the column names from cursor.description using list comprehension
            # 'description' attribute on a cursor holds the column names for the tables in question
            columns = [row[0] for row in execute.description]
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a dictionary
            execute.rowfactory = lambda *args: dict(zip(columns, args))
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(_row_idx, mode='absolute')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a dict
        return results
    
    def db_execute_sql_fetch_specific_row_as_list(self, _sql_query_or_sql_variable, _row_idx):
        '''
        Method to fetch specific row number of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query and row number
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(_row_idx, mode='absolute')
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a list
            execute.rowfactory = lambda *args: list(args)
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a list
        return results
    
    def db_execute_sql_fetch_specific_row_as_set(self, _sql_query_or_sql_variable, _row_idx):
        '''
        Method to fetch specific row number of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query and row number
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(_row_idx, mode='absolute')
            '''
            Special Note:Cursor.rowfactory The rowfactory attribute of the Cursor object defines the method that will be
              called when retrieving the record. This attribute produces tuples by default. By overwriting this movement,
               it is possible to change the format of the record to another form.
            '''
            # Here we are changing the form from tuples to a set
            execute.rowfactory = lambda *args: set(args)
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a set
        return results
    
    def db_execute_sql_fetch_specific_row_as_tuples(self, _sql_query_or_sql_variable, _row_idx):
        '''
        Method to fetch specific row number of sql output
        Argument to this method is: SQL Query or Variable containing the SQL query and row number
        Note: Order of the result is driven by sql query
        '''
        with self.db_auto_connect.cursor(scrollable=True) as cursor:
            '''
            If you are fetching a fixed number of rows, start your tuning by setting arraysize to the number of expected 
            rows, and set prefetchrows to one greater than this value. (Adding one removes the need for a round-trip to 
            check for end-of-fetch)
            '''
            cursor.arraysize = 1
            cursor.prefetchrows = 2
            # Execute the SQL Query or Variable containing the SQL query
            execute = cursor.execute(_sql_query_or_sql_variable)
            '''
            Special Note:  Cursor.scroll(value=0, mode='relative')
            Scroll the cursor in the result set to a new position according to the mode.
            If mode is “relative” (the default value), the value is taken as an offset to the current position in the 
            result set. If set to “absolute”, value states an absolute target position. If set to “first”, the cursor 
            is positioned at the first row and if set to “last”, the cursor is set to the last row in the result set.

            An error is raised if the mode is “relative” or “absolute” and the scroll operation would position the 
            cursor outside of the result set.
            '''
            execute.scroll(_row_idx, mode='absolute')
            # Fetch only first item from the cursor in to results
            results = execute.fetchone()
        # return type of this method is a tuple
        return results