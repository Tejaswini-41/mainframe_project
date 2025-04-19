import streamlit as st
import pandas as pd
from db2_connector import DB2Connector
import time

def create_table_interface(schema):
    """Interface for creating a new table in the selected schema with improved UI"""
    
    # Use schema-specific key for table name to avoid duplicates
    table_name = st.text_input(
        "Table Name", 
        key=f"{schema}_new_table_name",
        placeholder="Enter table name",
        help="Table name must start with a letter"
    ).strip().upper()
    
    # Validation with better UI feedback
    if table_name and not table_name[0].isalpha():
        st.warning("Table name must start with a letter")
    
    # Column definitions with improved UI
    st.markdown("""
    <div style="background:#f8f9fa; border-radius:6px; padding:1rem; margin:1rem 0; border-left:3px solid #3b71ca;">
        <h3 style="margin-top:0; font-weight:600;">Define Columns</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Use schema-specific session state for columns to avoid conflicts
    column_state_key = f"{schema}_table_columns"
    if column_state_key not in st.session_state:
        st.session_state[column_state_key] = [{"name": "", "type": "VARCHAR", "length": "50", "nullable": True, "default": ""}]
    
    # Available column types in DB2
    db2_types = [
        "VARCHAR", "CHAR", "INTEGER", "SMALLINT", "BIGINT", "DECIMAL", 
        "FLOAT", "DOUBLE", "DATE", "TIME", "TIMESTAMP", "BLOB", "CLOB"
    ]
    
    # Display existing columns with improved UI
    columns_modified = False
    
    # Create a container for column definitions
    col_container = st.container()
    
    with col_container:
        # Header row
        header_cols = st.columns([3, 2, 1, 1, 2, 1])
        with header_cols[0]:
            st.markdown("<p style='font-weight:500;'>Column Name</p>", unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown("<p style='font-weight:500;'>Data Type</p>", unsafe_allow_html=True)
        with header_cols[2]:
            st.markdown("<p style='font-weight:500;'>Length</p>", unsafe_allow_html=True)
        with header_cols[3]:
            st.markdown("<p style='font-weight:500;'>Nullable</p>", unsafe_allow_html=True)
        with header_cols[4]:
            st.markdown("<p style='font-weight:500;'>Default Value</p>", unsafe_allow_html=True)
        with header_cols[5]:
            st.markdown("<p style='font-weight:500;'>Action</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)
        
        # Display each column definition row
        for i, column in enumerate(st.session_state[column_state_key]):
            col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 1, 2, 1])
            
            with col1:
                column["name"] = st.text_input(
                    label="",
                    value=column["name"],
                    key=f"{schema}_col_name_{i}",
                    placeholder="Column name"
                ).strip().upper()
            
            with col2:
                column["type"] = st.selectbox(
                    label="",
                    options=db2_types, 
                    index=db2_types.index(column["type"]) if column["type"] in db2_types else 0, 
                    key=f"{schema}_col_type_{i}"
                )
            
            with col3:
                # For types that need length/precision
                if column["type"] in ["VARCHAR", "CHAR", "DECIMAL"]:
                    column["length"] = st.text_input(
                        label="",
                        value=column["length"],
                        key=f"{schema}_col_len_{i}",
                        placeholder="Length"
                    )
                else:
                    st.text(" ")
                    column["length"] = ""
            
            with col4:
                column["nullable"] = st.checkbox(
                    label=" ",
                    value=column["nullable"],
                    key=f"{schema}_col_null_{i}"
                )
            
            with col5:
                column["default"] = st.text_input(
                    label="",
                    value=column["default"],
                    key=f"{schema}_col_default_{i}",
                    placeholder="Default value"
                )
            
            with col6:
                if st.button("Remove", key=f"{schema}_remove_col_{i}", help="Remove this column"):
                    st.session_state[column_state_key].pop(i)
                    columns_modified = True
            
            if i < len(st.session_state[column_state_key]) - 1:
                st.markdown("<hr style='margin:0.25rem 0; border-top:1px dashed #e5e7eb;'>", unsafe_allow_html=True)
    
    if columns_modified:
        st.rerun()
    
    # Add new column button with improved styling
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Add Column", key=f"{schema}_add_column"):
            st.session_state[column_state_key].append({"name": "", "type": "VARCHAR", "length": "50", "nullable": True, "default": ""})
            st.rerun()
    
    # Primary key selection with improved UI
    st.markdown("""
    <div style="background:#f8f9fa; border-radius:6px; padding:1rem; margin:1.5rem 0 1rem 0; border-left:3px solid #3b71ca;">
        <h3 style="margin-top:0; font-weight:600;">Primary Key</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if len(st.session_state[column_state_key]) > 0 and any(col["name"] for col in st.session_state[column_state_key]):
        valid_columns = [col["name"] for col in st.session_state[column_state_key] if col["name"]]
        pk_cols = st.multiselect(
            "Select Primary Key Column(s)", 
            options=valid_columns, 
            key=f"{schema}_pk_columns",
            help="Select one or more columns to form the primary key"
        )
    else:
        pk_cols = []
        st.info("Define at least one column to select primary key")
    
    # Create table button with improved UI
    st.markdown("<hr>", unsafe_allow_html=True)
    
    create_disabled = not table_name or not any(col["name"] for col in st.session_state[column_state_key])
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("Create Table", type="primary", disabled=create_disabled, key=f"{schema}_create_table_btn"):
            with st.spinner("Creating table..."):
                # Add slight delay for animation
                time.sleep(0.5)
                return execute_create_table(schema, table_name, st.session_state[column_state_key], pk_cols)
    
    # Helpful information
    st.markdown("""
    <div style="background:#f0f9ff; border-radius:6px; padding:1rem; margin-top:1.5rem; border:1px solid #e0f2fe;">
        <h3 style="margin-top:0; font-size:1rem; font-weight:600;">Table Creation Tips</h3>
        <ul style="font-size:0.9rem;">
            <li>Table names should be descriptive and follow your naming conventions</li>
            <li>Consider adding a primary key for better data integrity</li>
            <li>Set appropriate data types to optimize storage and performance</li>
            <li>Use NOT NULL for columns that require values</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
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
    """Interface for inserting data into a table with improved UI"""
    # Get table structure
    connector = st.session_state.db2_connector
    if not connector:
        return None, "Not connected to database"
        
    with st.spinner("Loading table structure..."):
        columns_df = connector.get_columns(schema, table)
        if columns_df.empty or 'error' in columns_df.columns:
            return None, "Error loading table structure"
    
    # Create a form for data entry with better UI
    with st.form(key=f"insert_data_form_{schema}_{table}"):
        st.markdown("""
        <div style="background:#f8f9fa; border-radius:6px; padding:0.75rem; margin-bottom:1rem;">
            <p style="margin:0; font-weight:500;">Enter values for each column below</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Column state for this form
        form_data = {}
        
        # Group columns by type for better organization
        col_types = {
            "Text": ["CHAR", "VARCHAR", "CLOB"],
            "Numeric": ["INTEGER", "SMALLINT", "BIGINT", "DECIMAL", "FLOAT", "DOUBLE"],
            "Date/Time": ["DATE", "TIME", "TIMESTAMP"],
            "Other": ["BLOB"]
        }
        
        # Organize columns by type
        cols_by_type = {k: [] for k in col_types}
        for _, row in columns_df.iterrows():
            col_name = row['COLNAME']
            col_type = row['TYPENAME']
            
            # Determine which group this column belongs to
            group = "Other"
            for type_group, types in col_types.items():
                if any(t in col_type for t in types):
                    group = type_group
                    break
                    
            cols_by_type[group].append(row)
        
        # Remove empty groups
        cols_by_type = {k: v for k, v in cols_by_type.items() if v}
        
        # Create tabs for column groups if there are multiple groups
        if len(cols_by_type) > 1:
            tabs = st.tabs(list(cols_by_type.keys()))
            
            for i, (group, columns) in enumerate(cols_by_type.items()):
                with tabs[i]:
                    _create_input_fields(columns, form_data, schema, table)
        else:
            # Just show all columns if there's only one group
            _create_input_fields(columns_df.iterrows(), form_data, schema, table)
        
        # Submit button with better styling
        col1, col2 = st.columns([1, 3])
        with col1:
            submitted = st.form_submit_button("Insert Row", type="primary", use_container_width=True)
        
    if submitted:
        with st.spinner("Inserting data..."):
            time.sleep(0.5)  # Add slight delay for animation
            return execute_insert_data(schema, table, columns_df, form_data)
    
    return None, None

def _create_input_fields(columns, form_data, schema, table):
    """Helper function to create input fields based on column types"""
    for _, row in columns:
        col_name = row['COLNAME']
        col_type = row['TYPENAME']
        nullable = row['NULLS'] == 'Y'
        
        st.markdown(f"""
        <div style="padding:0.5rem 0; border-bottom:1px solid #f3f4f6;">
            <p style="margin:0; font-weight:500;">{col_name}</p>
            <p style="margin:0; font-size:0.8rem; color:#6b7280;">{col_type} {'' if nullable else '(Required)'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Different input types based on data type with better styling
        if 'INT' in col_type:
            form_data[col_name] = st.number_input(
                label="",
                step=1, 
                value=None if nullable else 0,
                key=f"val_{schema}_{table}_{col_name}"
            )
        elif col_type in ['FLOAT', 'DOUBLE', 'DECIMAL', 'REAL']:
            form_data[col_name] = st.number_input(
                label="",
                step=0.1, 
                value=None if nullable else 0.0,
                key=f"val_{schema}_{table}_{col_name}"
            )
        elif col_type == 'DATE':
            form_data[col_name] = st.date_input(
                label="",
                key=f"val_{schema}_{table}_{col_name}"
            )
        elif col_type == 'TIME':
            form_data[col_name] = st.time_input(
                label="",
                key=f"val_{schema}_{table}_{col_name}"
            )
        elif col_type == 'TIMESTAMP':
            col1, col2 = st.columns(2)
            with col1:
                date_val = st.date_input(
                    "Date component",
                    key=f"date_{schema}_{table}_{col_name}"
                )
            with col2:
                time_val = st.time_input(
                    "Time component",
                    key=f"time_{schema}_{table}_{col_name}"
                )
            form_data[col_name] = f"{date_val} {time_val}"
        elif col_type in ['CHAR', 'VARCHAR']:
            form_data[col_name] = st.text_input(
                label="",
                key=f"val_{schema}_{table}_{col_name}",
                placeholder=f"Enter value for {col_name}"
            )
        elif col_type in ['BLOB', 'CLOB']:
            form_data[col_name] = st.text_area(
                label="",
                key=f"val_{schema}_{table}_{col_name}",
                placeholder=f"Enter value for {col_name}"
            )
        else:
            form_data[col_name] = st.text_input(
                label="",
                key=f"val_{schema}_{table}_{col_name}",
                placeholder=f"Enter value for {col_name}"
            )

def execute_insert_data(schema, table, columns_df, form_data):
    """Execute the INSERT statement with improved error handling"""
    try:
        connector = st.session_state.db2_connector
        if not connector:
            return None, "Not connected to database"
        
        # Format column names and values for SQL
        column_names = []
        column_values = []
        
        # Validation - check for required fields
        missing_required = []
        
        for _, row in columns_df.iterrows():
            col_name = row['COLNAME']
            col_type = row['TYPENAME']
            nullable = row['NULLS'] == 'Y'
            
            # Check required fields
            if not nullable and (col_name not in form_data or form_data[col_name] == "" or form_data[col_name] is None):
                missing_required.append(col_name)
                continue
            
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
        
        # If there are missing required fields, return an error
        if missing_required:
            return None, f"Missing required values for: {', '.join(missing_required)}"
        
        # Build SQL statement
        sql = f'INSERT INTO "{schema}"."{table}" ({", ".join(column_names)}) VALUES ({", ".join(column_values)})'
        
        # Execute query
        with st.spinner(f"Inserting data into {schema}.{table}..."):
            result, message = connector.execute_query(sql)
            
            if result is not None:
                return result, f"Data successfully inserted into {schema}.{table}"
            else:
                # Improved error message handling
                if "SQL0803N" in message:
                    return None, "Duplicate key value violates unique constraint"
                elif "SQL0530N" in message:
                    return None, "Foreign key constraint violation"
                elif "SQL0545N" in message:
                    return None, "Value cannot be NULL for this column"
                else:
                    return None, f"Error inserting data: {message}"
                
    except Exception as e:
        return None, f"Error inserting data: {str(e)}"