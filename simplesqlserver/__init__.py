"""Client to connect to SQL Server"""
import os
import time
import bcpy
import pyodbc

# pylint: disable = c-extension-no-member

class SqlServerClient:
    """Client to connect to SQL Server"""
    def __init__(self, server, username, password, database=None):
        self.driver = '{ODBC Driver 17 for SQL Server}'
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = pyodbc.connect(f'''DRIVER={self.driver};
            SERVER={self.server};
            DATABASE={self.database};
            UID={username};
            PWD={password}''')

    def bcp_load(self, table_name, file_path):
        """Bulk loads a flat file into SQL Server via BCP"""
        flat_file = bcpy.FlatFile(qualifier='', path=file_path, newline='\r\n')
        sql_table = bcpy.SqlTable(
            {
                'server': self.server,
                'database': self.database,
                'username': self.username,
                'password': self.password
            },
            table=table_name)
        flat_file.to_sql(sql_table, use_existing_sql_table=True)

    def execute_stored_procedure(self, name, database=None):
        """Execute a stored procedure in ADW"""
        if database is None:
            database = self.database
        sql = f'''DECLARE @return_value int
                EXEC @return_value = {database}.dbo.{name}
                SELECT 'Return Value' = @return_value'''
        result = self.connection.cursor().execute(sql).fetchone()[0]
        self.connection.commit()
        return result

    def execute_sql(self, sql, output='cursor'):
        """Execute SQL statement"""
        outputs = ['cursor', 'row', 'rows']
        if output not in outputs:
            raise ValueError(f'Invalid output_type value. Acceptable values: {outputs}')
        if output == 'row':
            return self.connection.cursor().execute(sql).fetchone()
        if output == 'rows':
            return self.connection.cursor().execute(sql).fetchall()
        return self.connection.cursor().execute(sql)

    def execute_insert(self, table, num_fields, data):
        """Execute insert SQL statement"""
        fields = '?,' * num_fields
        sql = f'INSERT INTO {table} VALUES ('+fields[0:-1]+')'
        cursor = self.connection.cursor()
        cursor.fast_executemany = True
        cursor.executemany(sql, data)
        self.connection.commit()

    def execute_job(self, job_name, wait=True, wait_time=5):
        """Execute SQL Server job
        - 'wait' = True if you want the function to wait until the job is done
        - 'wait' = False if you want to kick off the job and close the function
        - 'wait_time' = number of seconds to wait in between checks to see if job is complete
        """
        sql = f"EXEC msdb.dbo.sp_start_job @job_name = N'{job_name}'"
        self.connection.cursor().execute(sql)
        if wait is True:
            job_finished = False
            while job_finished is False:
                time.sleep(wait_time)
                sql = f"EXEC msdb.dbo.sp_help_jobactivity @job_name = '{job_name}'"
                result = self.execute_sql(sql=sql, output='row')
                if result[13] == 1:
                    job_finished = True
                    return True
                if result[13] == 0:
                    job_finished = True
                    return result[12]
        return True
