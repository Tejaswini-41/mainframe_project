import streamlit as st
import pandas as pd
from db2_connector import DB2Connector

def create_table_interface(schema):
    """Interface for creating a new table in the selected schema"""
    st.subheader(f"Create Table in {schema}")
    
    # Use schema-specific key for table name to avoid duplicates
    table_name = st.text_input("Table Name", key=f"{schema}_new_table_name").strip().upper()
    
    # Check if table name is valid
    if table_name and not table_name[0].isalpha():
        st.warning("Table name must start with a letter")
    
    # Column definitions
    st.subheader("Define Columns")
    
    # Use schema-specific session state for columns to avoid conflicts
    column_state_key = f"{schema}_table_columns"
    if column_state_key not in st.session_state:
        st.session_state[column_state_key] = [{"name": "", "type": "VARCHAR", "length": "50", "nullable": True, "default": ""}]
    
    # Available column types in DB2
    db2_types = [
        "VARCHAR", "CHAR", "INTEGER", "SMALLINT", "BIGINT", "DECIMAL", 
        "FLOAT", "DOUBLE", "DATE", "TIME", "TIMESTAMP", "BLOB", "CLOB"
    ]
    
    # Display existing columns
    columns_modified = False
    for i, column in enumerate(st.session_state[column_state_key]):
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 1, 2, 1])
        
        with col1:
            column["name"] = st.text_input(f"Name", value=column["name"], key=f"{schema}_col_name_{i}").strip().upper()
        
        with col2:
            column["type"] = st.selectbox(f"Type", options=db2_types, 
                                         index=db2_types.index(column["type"]) if column["type"] in db2_types else 0, 
                                         key=f"{schema}_col_type_{i}")
        
        with col3:
            # For types that need length/precision
            if column["type"] in ["VARCHAR", "CHAR", "DECIMAL"]:
                column["length"] = st.text_input(f"Length", value=column["length"], key=f"{schema}_col_len_{i}")
            else:
                st.text(" ")
                column["length"] = ""
        
        with col4:
            column["nullable"] = st.checkbox("Nullable", value=column["nullable"], key=f"{schema}_col_null_{i}")
        
        with col5:
            column["default"] = st.text_input(f"Default", value=column["default"], key=f"{schema}_col_default_{i}")
        
        with col6:
            if st.button("Remove", key=f"{schema}_remove_col_{i}"):
                st.session_state[column_state_key].pop(i)
                columns_modified = True
    
    if columns_modified:
        st.rerun()
    
    # Add new column button
    if st.button("Add Column", key=f"{schema}_add_column"):
        st.session_state[column_state_key].append({"name": "", "type": "VARCHAR", "length": "50", "nullable": True, "default": ""})
        st.rerun()
    
    # Primary key selection
    if len(st.session_state[column_state_key]) > 0 and any(col["name"] for col in st.session_state[column_state_key]):
        st.subheader("Primary Key")
        valid_columns = [col["name"] for col in st.session_state[column_state_key] if col["name"]]
        pk_cols = st.multiselect("Select Primary Key Column(s)", options=valid_columns, key=f"{schema}_pk_columns")
    else:
        pk_cols = []
    
    # Create table button
    create_disabled = not table_name or not any(col["name"] for col in st.session_state[column_state_key])
    if st.button("Create Table", type="primary", disabled=create_disabled, key=f"{schema}_create_table_btn"):
        return execute_create_table(schema, table_name, st.session_state[column_state_key], pk_cols)
    
    st.markdown("---")
    st.info("Enter table details and click 'Create Table' when ready.")
    
    return None, None

def execute_create_table(schema, table_name, columns, primary_keys):
    """Execute the CREATE TABLE SQL statement"""
    try:
        # Validate inputs
        if not table_name:
            return None, "Table name is required"
            
        if not columns or not any(col["name"] for col in columns):
            return None, "At least one column is required"
        
        # Start building the SQL statement
        sql = f"CREATE TABLE {schema}.{table_name} (\n"
        
        # Add column definitions
        column_defs = []
        for col in columns:
            if not col["name"]:
                continue
                
            # Build the column type with length/precision if applicable
            type_def = col["type"]
            if col["type"] in ["VARCHAR", "CHAR"] and col["length"]:
                type_def = f"{col['type']}({col['length']})"
            elif col["type"] == "DECIMAL" and col["length"]:
                # Decimal can have precision,scale format
                if "," in col["length"]:
                    type_def = f"DECIMAL({col['length']})"
                else:
                    type_def = f"DECIMAL({col['length']},0)"
            
            # Add nullability
            null_clause = "NOT NULL" if not col["nullable"] else "NULL"
            
            # Add default value if specified
            default_clause = ""
            if col["default"]:
                if col["type"] in ["VARCHAR", "CHAR", "DATE", "TIME", "TIMESTAMP"]:
                    # String types need quotes
                    default_clause = f"DEFAULT '{col['default']}'"
                else:
                    # Numeric types don't need quotes
                    default_clause = f"DEFAULT {col['default']}"
            
            # Combine the parts
            parts = [f"{col['name']} {type_def}", null_clause]
            if default_clause:
                parts.append(default_clause)
                
            column_defs.append(" ".join(parts))
        
        # Add primary key constraint if specified
        if primary_keys:
            pk_clause = f",\nPRIMARY KEY ({', '.join(primary_keys)})"
        else:
            pk_clause = ""
        
        # Complete the SQL statement
        sql += ",\n".join(column_defs) + pk_clause + "\n)"
        
        # Execute the SQL
        connector = st.session_state.db2_connector
        if not connector:
            return None, "Not connected to database"
        
        # Execute the CREATE TABLE statement
        with st.spinner("Creating table..."):
            result, message = connector.execute_query(sql)
            
            if result is not None:
                # Clear the form after successful creation - use schema-specific key
                column_state_key = f"{schema}_table_columns"
                st.session_state[column_state_key] = [{"name": "", "type": "VARCHAR", "length": "50", "nullable": True, "default": ""}]
                
                # Force refresh of table list cache
                import ui_components
                if hasattr(ui_components, "get_tables"):
                    ui_components.get_tables.clear()
                
                return result, f"Table {schema}.{table_name} created successfully"
            else:
                return None, message
                
    except Exception as e:
        return None, f"Error creating table: {str(e)}"

def insert_data_interface(schema, table):
    """Interface for inserting data into a table"""
    st.subheader(f"Insert Data into {schema}.{table}")
    
    # Get table structure
    connector = st.session_state.db2_connector
    if not connector:
        return None, "Not connected to database"
        
    with st.spinner("Loading table structure..."):
        columns_df = connector.get_columns(schema, table)
        if columns_df.empty or 'error' in columns_df.columns:
            return None, "Error loading table structure"
    
    # Create a form for data entry
    with st.form(key=f"insert_data_form_{schema}_{table}"):
        st.subheader("Enter Row Data")
        
        # Column state for this form
        form_data = {}
        
        # Create input fields based on column type
        for _, row in columns_df.iterrows():
            col_name = row['COLNAME']
            col_type = row['TYPENAME']
            nullable = row['NULLS'] == 'Y'
            
            st.markdown(f"**{col_name}** ({col_type})")
            
            # Different input types based on data type
            if 'INT' in col_type:
                form_data[col_name] = st.number_input(
                    f"Value for {col_name}", 
                    step=1, 
                    value=None if nullable else 0,
                    key=f"val_{schema}_{table}_{col_name}"
                )
            elif col_type in ['FLOAT', 'DOUBLE', 'DECIMAL', 'REAL']:
                form_data[col_name] = st.number_input(
                    f"Value for {col_name}", 
                    step=0.1, 
                    value=None if nullable else 0.0,
                    key=f"val_{schema}_{table}_{col_name}"
                )
            elif col_type == 'DATE':
                form_data[col_name] = st.date_input(
                    f"Value for {col_name}",
                    key=f"val_{schema}_{table}_{col_name}"
                )
            elif col_type == 'TIME':
                form_data[col_name] = st.time_input(
                    f"Value for {col_name}",
                    key=f"val_{schema}_{table}_{col_name}"
                )
            elif col_type == 'TIMESTAMP':
                date_val = st.date_input(
                    f"Date for {col_name}",
                    key=f"date_{schema}_{table}_{col_name}"
                )
                time_val = st.time_input(
                    f"Time for {col_name}",
                    key=f"time_{schema}_{table}_{col_name}"
                )
                form_data[col_name] = f"{date_val} {time_val}"
            elif col_type in ['CHAR', 'VARCHAR']:
                form_data[col_name] = st.text_input(
                    f"Value for {col_name}",
                    key=f"val_{schema}_{table}_{col_name}"
                )
            elif col_type in ['BLOB', 'CLOB']:
                form_data[col_name] = st.text_area(
                    f"Value for {col_name}",
                    key=f"val_{schema}_{table}_{col_name}"
                )
            else:
                form_data[col_name] = st.text_input(
                    f"Value for {col_name}",
                    key=f"val_{schema}_{table}_{col_name}"
                )
            
            # Add separator between fields
            st.markdown("---")
            
        # Submit button
        submitted = st.form_submit_button("Insert Row", type="primary")
        
    if submitted:
        return execute_insert_data(schema, table, columns_df, form_data)
    
    return None, None

def execute_insert_data(schema, table, columns_df, form_data):
    """Execute the INSERT statement"""
    try:
        connector = st.session_state.db2_connector
        if not connector:
            return None, "Not connected to database"
        
        # Format column names and values for SQL
        column_names = []
        column_values = []
        
        for _, row in columns_df.iterrows():
            col_name = row['COLNAME']
            col_type = row['TYPENAME']
            
            # Skip if no value provided for nullable columns
            if col_name not in form_data or form_data[col_name] == "":
                continue
                
            column_names.append(f'"{col_name}"')
            
            # Format value based on type
            value = form_data[col_name]
            if value is None:
                column_values.append("NULL")
            elif col_type in ['CHAR', 'VARCHAR', 'DATE', 'TIME', 'TIMESTAMP', 'BLOB', 'CLOB']:
                # Add quotes for string types
                column_values.append(f"'{value}'")
            else:
                # No quotes for numeric types
                column_values.append(str(value))
        
        # Build SQL statement
        sql = f'INSERT INTO "{schema}"."{table}" ({", ".join(column_names)}) VALUES ({", ".join(column_values)})'
        
        # Execute query
        with st.spinner(f"Inserting data into {schema}.{table}..."):
            result, message = connector.execute_query(sql)
            
            if result is not None:
                return result, f"Data successfully inserted into {schema}.{table}"
            else:
                return None, f"Error inserting data: {message}"
                
    except Exception as e:
        return None, f"Error inserting data: {str(e)}"