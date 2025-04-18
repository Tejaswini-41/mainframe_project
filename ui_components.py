import streamlit as st
import pandas as pd
import plotly.express as px
from db2_connector import DB2Connector
# Update imports
from table_operations import create_table_interface, insert_data_interface
from schema_operations import create_schema_interface


# Add caching to improve performance
@st.cache_data(ttl=300)
def get_schemas(_connector):
    """Get schemas with caching"""
    schemas_df = _connector.get_schemas()
    if not schemas_df.empty and 'SCHEMANAME' in schemas_df.columns:
        return schemas_df['SCHEMANAME'].tolist()
    return []

@st.cache_data(ttl=300)
def get_tables(_connector, schema):
    """Get tables with caching"""
    tables_df = _connector.get_tables(schema=schema)
    if not tables_df.empty and 'TABNAME' in tables_df.columns:
        return tables_df['TABNAME'].tolist()
    return []


def connection_page():
    """Connection page UI"""
    st.title("DB2 Web Manager")
    st.subheader("Connect to DB2 Database")
    
    # Check if connection profiles exist in session state
    if 'connection_profiles' not in st.session_state:
        st.session_state.connection_profiles = {
            'Default': {
                'hostname': 'localhost',
                'port': '25000',
                'database': 'TEST',
                'username': 'db2admin',
                'password': 'admin@123'
            }
        }
    
    # Create a nice centered connection form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Connection profiles dropdown
        profiles = list(st.session_state.connection_profiles.keys())
        selected_profile = st.selectbox("Connection Profile", options=profiles)
        
        # Load profile data if it exists
        profile_data = st.session_state.connection_profiles[selected_profile]
        
        with st.form("connection_form"):
            st.subheader("Database Connection")
            
            # Connection parameters
            hostname = st.text_input("Hostname", value=profile_data['hostname'])
            port = st.text_input("Port", value=profile_data['port'])
            database = st.text_input("Database", value=profile_data['database'])
            username = st.text_input("Username", value=profile_data['username'])
            password = st.text_input("Password", value=profile_data['password'], type="password")
            
            # Form buttons
            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button("Connect", use_container_width=True)
            with col_b:
                save_profile = st.form_submit_button("Save Profile", use_container_width=True)
        
        if save_profile:
            # Save current connection as a profile
            st.subheader("Save Connection Profile")
            new_profile_name = st.text_input("Profile Name")
            save_btn = st.button("Save", key="save_profile_btn")
            if save_btn and new_profile_name:
                st.session_state.connection_profiles[new_profile_name] = {
                    'hostname': hostname,
                    'port': port,
                    'database': database,
                    'username': username,
                    'password': password
                }
                st.success(f"Profile '{new_profile_name}' saved")
        
        if submitted:
            with st.spinner("Connecting to DB2..."):
                _connector = DB2Connector(
                    hostname=hostname,
                    port=port,
                    database=database,
                    username=username,
                    password=password
                )
                
                if _connector.connect():
                    st.session_state.db2_connector = _connector
                    st.session_state.page = 'main'
                    st.rerun()
                else:
                    st.error(f"Connection failed: {getattr(_connector, 'error_message', 'Unknown error')}")

def main_interface():
    """Main interface after connection"""
    _connector = st.session_state.db2_connector
    
    # Initialize query_result if not exists
    if 'query_result' not in st.session_state:
        st.session_state.query_result = None

    if 'ui_mode' not in st.session_state:
        st.session_state.ui_mode = "default"
    
    # Header with logout button
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("DB2 Web Manager")
    with col2:
        if st.button("Disconnect", type="primary"):
            if st.session_state.db2_connector:
                st.session_state.db2_connector.close()
                st.session_state.db2_connector = None
                st.session_state.page = 'connection'
                st.rerun()
    
    st.markdown(f"Connected to: **{_connector.database}** on **{_connector.hostname}:{_connector.port}**")
    
    # Split into sidebar for navigation and main content
    with st.sidebar:
        st.subheader("Database Explorer")
        
        # Add Create Schema button above Select Schema
        if st.button("Create Schema", key="create_schema_button"):
            st.session_state.ui_mode = "create_schema"
            st.rerun()
        
        # Get schemas using cached function
        schemas = get_schemas(_connector)
        
        if not schemas:
            st.warning("No schemas found in database")
        else:
            # Select a schema (single selection)
            selected_schema = st.selectbox("Select Schema", schemas, key="schema_selector")
            
            # Show actions for the selected schema
            if selected_schema:
                st.subheader(f"Schema: {selected_schema}")
                action = st.radio("Schema Actions", 
                                  ["View Schema", "Create Table", "Drop Schema"],
                                  key="schema_action")
                
                if st.button("Execute Action", key="execute_schema_action"):
                    if action == "View Schema":
                        st.session_state.ui_mode ="default"
                        view_schema_details(selected_schema)
                    elif action == "Create Table":
                        # Just set the UI mode and schema, don't render the interface here
                        st.session_state.current_schema_for_table = selected_schema
                        st.session_state.ui_mode = "create_table"
                        st.rerun()
                    elif action == "Drop Schema":
                        drop_schema(selected_schema)
            
                # Get tables for the selected schema
                tables = get_tables(_connector, selected_schema)
                if tables:
                    st.subheader("Tables")
                    selected_table = st.selectbox("Select Table", tables, key="table_selector")
                    
                    if selected_table:
                        table_action = st.radio("Table Actions", 
                                              ["View Data", "View Structure", "Insert Data", "Drop Table", "Truncate Table"],
                                              key="table_action")
                        
                        if st.button("Execute Action", key="execute_table_action"):
                            if table_action == "View Data":
                                view_table_data(selected_schema, selected_table)
                            elif table_action == "View Structure":
                                view_table_structure(selected_schema, selected_table)
                            elif table_action == "Insert Data":
                                insert_data(selected_schema, selected_table)
                            elif table_action == "Drop Table":
                                drop_table(selected_schema, selected_table)
                            elif table_action == "Truncate Table":
                                truncate_table(selected_schema, selected_table)
                else:
                    st.info(f"No tables found in schema {selected_schema}")
    
    # Main content area with SQL editor and results
    if st.session_state.ui_mode == "create_schema":
        # If we're in schema creation mode, handle it in the main content area
        result, message = create_schema_interface()
        
        if result is not None:
            # Schema was successfully created
            st.session_state.query_result = (result, message)
            # Reset UI mode
            st.session_state.ui_mode = "default"
            # Show success message
            st.success(message)
        elif message:
            if "Permission denied" in message or "SQL0552N" in message:
                st.error(message)
                st.info("""
                **Troubleshooting Permission Issues:**
                
                To create schemas in DB2, you need:
                - SYSADM authority, or
                - SYSCTRL authority, or
                - DBADM authority
                
                Connect with a user that has one of these privileges or ask your DB administrator to grant them.
                """)
            else:
                st.error(message)
        
        # Add a button to cancel and go back
        if st.button("Cancel Schema Creation"):
            st.session_state.ui_mode = "default"
            st.rerun()
            
    elif st.session_state.ui_mode == "create_table":
        # If we're in table creation mode, handle it directly in the main content area
        schema = st.session_state.current_schema_for_table
        result, message = create_table_interface(schema)
        
        if result is not None:
            # Table was successfully created
            st.session_state.query_result = (result, message)
            # Reset UI mode
            st.session_state.ui_mode = "default"
            # Show success message
            st.success(f"Table created successfully in schema {schema}")
        elif message:
            st.error(message)
        
        # Add a button to cancel and go back
        if st.button("Cancel Table Creation"):
            st.session_state.ui_mode = "default"
            st.rerun()
    
    elif st.session_state.ui_mode == "drop_table":
        # Handle drop table confirmation in the main area
        schema = st.session_state.drop_table_info['schema']
        table = st.session_state.drop_table_info['table']
        
        st.subheader(f"Drop Table: {schema}.{table}")
        st.warning("⚠️ WARNING: This action cannot be undone!")
        st.markdown(f"You are about to drop table **{schema}.{table}** and all its data will be permanently deleted.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Drop Table", type="primary", key="confirm_drop_table"):
                with st.spinner(f"Dropping table {schema}.{table}..."):
                    drop_query = f'DROP TABLE "{schema}"."{table}"'
                    result, message = _connector.execute_query(drop_query)
                    
                    if result is not None:
                        # Clear table cache to reflect changes
                        get_tables.clear()
                        st.session_state.query_result = (None, f"Table {schema}.{table} dropped successfully")
                        st.session_state.ui_mode = "default"
                        st.rerun()
                    else:
                        st.session_state.query_result = (None, f"Error dropping table: {message}")
                        
        with col2:
            if st.button("Cancel", key="cancel_drop_table", use_container_width=True):
                st.session_state.ui_mode = "default"
                st.rerun()
    
    elif st.session_state.ui_mode == "insert_data":
        # Handle insert data in the main area
        schema = st.session_state.insert_table_info['schema']
        table = st.session_state.insert_table_info['table']
        
        result, message = insert_data_interface(schema, table)
        
        if result is not None:
            # Data was inserted successfully
            st.session_state.query_result = (result, message)
            # We don't reset UI mode here to allow multiple inserts
            st.success(message)
        elif message:
            st.error(message)
        
        # Add a button to finish inserting
        if st.button("Done", key="finish_insert_data"):
            st.session_state.ui_mode = "default"
            st.rerun()
    
    else:
        st.subheader("SQL Editor")
        
        # SQL query input
        query = st.text_area(
            "Enter SQL Query",
            height=150,
            placeholder="SELECT * FROM SCHEMA.TABLE WHERE condition", 
            key="sql_query"
        )
        
        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("Execute", use_container_width=True):
                execute_query(query)
        
        # Display query results or selected content
        st.subheader("Results")
        
        if st.session_state.query_result is not None:
            result, message = st.session_state.query_result
            
            if result is not None:
                if isinstance(result, pd.DataFrame):
                    st.success(message)
                    
                    # Add download button for query results
                    if not result.empty:
                        csv = result.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download Results as CSV",
                            csv,
                            "query_results.csv",
                            "text/csv",
                            key="download_query_results"
                        )
                    
                    # Show result data - limit for performance
                    if len(result) > 1000:
                        st.dataframe(result.head(1000), use_container_width=True)
                        st.warning(f"Showing first 1,000 rows of {len(result)} total rows")
                    else:
                        st.dataframe(result, use_container_width=True)
                    
                    st.info(f"Query returned {len(result)} rows")
                else:
                    st.success(message)
            else:
                st.error(message)
        else:
            st.info("Execute a query or select an item from the sidebar to see results here")

def execute_query(query):
    """Execute SQL query and store result in session state"""
    if not query.strip():
        st.warning("Please enter a SQL query")
        return
    
    if not st.session_state.db2_connector:
        st.error("Not connected to database")
        return
    
    with st.spinner("Executing query..."):
        result, message = st.session_state.db2_connector.execute_query(query)
        st.session_state.query_result = (result, message)

# Schema actions
def view_schema_details(schema):
    """View schema details"""
    _connector = st.session_state.db2_connector
    if not _connector:
        return
        
    with st.spinner(f"Loading schema {schema} information..."):
        # Get schema details - tables count
        tables_df = _connector.get_tables(schema=schema)
        if not tables_df.empty:
            table_count = len(tables_df)
            result = pd.DataFrame({
                'Schema': [schema],
                'Tables Count': [table_count],
                'Last Updated': ['N/A']  # Could be enhanced with actual schema metadata
            })
            st.session_state.query_result = (result, f"Schema information for {schema}")
        else:
            st.session_state.query_result = (None, f"No information available for schema {schema}")

def create_table(schema):
    """Create table in schema"""
    # This function should only set up the state for the table creation UI
    st.session_state.current_schema_for_table = schema
    st.session_state.ui_mode = "create_table"
    st.rerun()  # Force a rerun to show the table creation UI in the main area

def drop_schema(schema):
    """Drop schema"""
    st.session_state.message = f"Drop schema {schema} (Not implemented yet)"

# Table actions
def view_table_data(schema, table):
    """View table data"""
    _connector = st.session_state.db2_connector
    if not _connector:
        return
        
    with st.spinner(f"Loading data from {schema}.{table}..."):
        result = _connector.get_table_data(schema, table, limit=100)
        st.session_state.query_result = (result, f"Data from {schema}.{table} (Top 100)")

def view_table_structure(schema, table):
    """View table structure"""
    _connector = st.session_state.db2_connector
    if not _connector:
        return
        
    with st.spinner(f"Loading structure of {schema}.{table}..."):
        result = _connector.get_columns(schema, table)
        st.session_state.query_result = (result, f"Structure of {schema}.{table}")

def insert_data(schema, table):
    """Set up for inserting data into a table"""
    _connector = st.session_state.db2_connector
    if not _connector:
        return
    
    # Set UI mode for data insertion
    st.session_state.ui_mode = "insert_data"
    st.session_state.insert_table_info = {
        'schema': schema,
        'table': table,
    }
    st.rerun()

def drop_table(schema, table):
    """Drop table with confirmation"""
    _connector = st.session_state.db2_connector
    if not _connector:
        return
    
    # Set UI mode for drop table confirmation
    st.session_state.ui_mode = "drop_table"
    st.session_state.drop_table_info = {
        'schema': schema,
        'table': table,
    }
    st.rerun()

def truncate_table(schema, table):
    """Truncate table"""
    st.session_state.message = f"Truncate table {schema}.{table} (Not implemented yet)"

def handle_context_menu_actions():
    """Handle actions from context menus"""
    # This function is kept for backward compatibility
    if 'action' in st.session_state:
        del st.session_state['action']