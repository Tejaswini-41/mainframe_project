import os
import pandas as pd

# Add DB2 client driver directory to path
import os.path


current_dir = os.path.dirname(os.path.abspath(__file__))
clidriver_path = os.path.join(current_dir, 'clidriver', 'bin')


os.add_dll_directory(clidriver_path)
import ibm_db
import ibm_db_dbi

class DB2Connector:
    """Class to handle DB2 database connections and operations"""
    
    def __init__(self, hostname, port, database, username, password):
        """Initialize connection parameters"""
        self.hostname = hostname
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.ibm_db_conn = None
        self.conn = None
        self.is_connected = False
        
    def connect(self):
        """Establish connection to DB2 database"""
        conn_string = (
            f"DATABASE={self.database};"
            f"HOSTNAME={self.hostname};"
            f"PORT={self.port};"
            f"PROTOCOL=TCPIP;"
            f"UID={self.username};"
            f"PWD={self.password};"
        )
        
        try:
            # Establish connection
            self.ibm_db_conn = ibm_db.connect(conn_string, "", "")
            # Get connection through DBI (for higher level operations)
            self.conn = ibm_db_dbi.Connection(self.ibm_db_conn)
            
            if ibm_db.active(self.ibm_db_conn):
                self.is_connected = True
                return True
            return False
            
        except Exception as e:
            self.error_message = str(e)
            return False
    
    def close(self):
        """Close the database connection"""
        try:
            if self.ibm_db_conn:
                ibm_db.close(self.ibm_db_conn)
            self.is_connected = False
            return True
        except Exception as e:
            return False
    
    def test_connection(self):
        """Test if the connection is working with a simple query"""
        try:
            if not self.is_connected:
                return False
                
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM SYSIBM.SYSDUMMY1")
            result = cursor.fetchone()
            cursor.close()
            
            return result is not None
        except Exception:
            return False
    
    def get_server_info(self):
        """Get DB2 server information"""
        try:
            if not self.is_connected:
                return None
                
            server_info = ibm_db.server_info(self.ibm_db_conn)
            info = {
                "dbms_name": server_info.DBMS_NAME,
                "dbms_version": server_info.DBMS_VER,
                "db_name": server_info.DB_NAME,
                "instance_name": server_info.INST_NAME,
                "special_chars": server_info.SPECIAL_CHARS,
                "keywords": server_info.KEYWORDS,
                "max_identifier_length": server_info.MAX_IDENTIFIER_LEN
            }
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def get_schemas(self):
        """Get all schemas in the database"""
        try:
            if not self.is_connected:
                return []
                
            query = "SELECT DISTINCT SCHEMANAME FROM SYSCAT.SCHEMATA ORDER BY SCHEMANAME"
            return self._execute_query_to_dataframe(query)
        except Exception:
            return pd.DataFrame({"SCHEMANAME": []})
    
    def get_tables(self, schema=None):
        """Get all tables, optionally filtered by schema"""
        try:
            if not self.is_connected:
                return []
                
            if schema:
                query = f"""
                SELECT TABSCHEMA, TABNAME, CARD AS ROW_COUNT, CREATE_TIME 
                FROM SYSCAT.TABLES 
                WHERE TABSCHEMA = '{schema}' 
                ORDER BY TABNAME
                """
            else:
                query = """
                SELECT TABSCHEMA, TABNAME, CARD AS ROW_COUNT, CREATE_TIME 
                FROM SYSCAT.TABLES 
                ORDER BY TABSCHEMA, TABNAME
                """
            return self._execute_query_to_dataframe(query)
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
    
    def get_columns(self, schema, table):
        """Get column information for a specific table"""
        try:
            if not self.is_connected:
                return []
                
            query = f"""
            SELECT COLNAME, TYPENAME, LENGTH, SCALE, NULLS, DEFAULT, REMARKS
            FROM SYSCAT.COLUMNS
            WHERE TABSCHEMA = '{schema}' AND TABNAME = '{table}'
            ORDER BY COLNO
            """
            return self._execute_query_to_dataframe(query)
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
    
    def execute_query(self, query):
        """Execute a custom SQL query"""
        try:
            if not self.is_connected:
                return None, "Not connected to database"
                
            # For SELECT queries, return a dataframe
            if query.strip().upper().startswith("SELECT"):
                df = self._execute_query_to_dataframe(query)
                return df, "Query executed successfully"
            # For other queries (INSERT, UPDATE, DELETE), execute and return row count
            else:
                cursor = self.conn.cursor()
                cursor.execute(query)
                affected_rows = cursor.rowcount
                self.conn.commit()
                cursor.close()
                return affected_rows, f"{affected_rows} rows affected"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def get_table_data(self, schema, table, limit=100, offset=0, order_by=None):
        """Get data from a specific table with pagination"""
        try:
            if not self.is_connected:
                return []
                
            # Build query with ORDER BY if specified
            order_clause = ""
            if order_by:
                order_clause = f"ORDER BY {order_by}"
                
            query = f"""
            SELECT * FROM {schema}.{table}
            {order_clause}
            FETCH FIRST {limit} ROWS ONLY
            """
                
            return self._execute_query_to_dataframe(query)
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
    
    def get_table_count(self, schema, table):
        """Get the total count of rows in a table"""
        try:
            if not self.is_connected:
                return 0
                
            query = f"SELECT COUNT(*) as COUNT FROM {schema}.{table}"
            df = self._execute_query_to_dataframe(query)
            if not df.empty:
                return df['COUNT'].iloc[0]
            return 0
        except Exception:
            return 0
    
    def get_primary_keys(self, schema, table):
        """Get primary key columns for a table"""
        try:
            if not self.is_connected:
                return []
                
            query = f"""
            SELECT KC.COLNAME 
            FROM SYSCAT.KEYCOLUSE KC
            INNER JOIN SYSCAT.TABCONST TC ON KC.TABSCHEMA = TC.TABSCHEMA AND KC.TABNAME = TC.TABNAME AND KC.CONSTNAME = TC.CONSTNAME
            WHERE KC.TABSCHEMA = '{schema}' AND KC.TABNAME = '{table}' AND TC.TYPE = 'P'
            ORDER BY KC.COLSEQ
            """
            df = self._execute_query_to_dataframe(query)
            if not df.empty:
                return df['COLNAME'].tolist()
            return []
        except Exception:
            return []
    
    def get_indexes(self, schema, table):
        """Get indexes for a table"""
        try:
            if not self.is_connected:
                return []
                
            query = f"""
            SELECT I.INDNAME, I.UNIQUERULE, IC.COLNAME, I.INDEXTYPE
            FROM SYSCAT.INDEXES I
            INNER JOIN SYSCAT.INDEXCOLUSE IC ON I.INDSCHEMA = IC.INDSCHEMA AND I.INDNAME = IC.INDNAME
            WHERE I.TABSCHEMA = '{schema}' AND I.TABNAME = '{table}'
            ORDER BY I.INDNAME, IC.COLSEQ
            """
            return self._execute_query_to_dataframe(query)
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
    
    def _execute_query_to_dataframe(self, query):
        """Execute a query and return results as pandas DataFrame"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            cursor.close()
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=columns)
            return df
        except Exception as e:
            # Return empty DataFrame with error
            return pd.DataFrame({"error": [str(e)]})