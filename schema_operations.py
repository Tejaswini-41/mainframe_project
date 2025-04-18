import streamlit as st
import pandas as pd
from db2_connector import DB2Connector

def create_schema_interface():
    """Interface for creating a new schema in the database"""
    st.subheader("Create New Schema")
    
    # Schema name input
    schema_name = st.text_input("Schema Name", key="new_schema_name").strip().upper()
    
    # Check if schema name is valid
    if schema_name and not schema_name[0].isalpha():
        st.warning("Schema name must start with a letter")
        return None, "Schema name must start with a letter"
    
    # Create schema button
    create_disabled = not schema_name
    if st.button("Create Schema", type="primary", disabled=create_disabled):
        return execute_create_schema(schema_name)
    
    # Permission information 
    st.markdown("---")
    st.info("""
    **Note:** Creating a schema requires elevated database privileges. 
    Your user account must have SYSADM, SYSCTRL, or DBADM authority to create schemas.
    
    If you don't have these privileges, please contact your database administrator.
    """)
    
    return None, None

def execute_create_schema(schema_name):
    """Execute the CREATE SCHEMA SQL statement"""
    try:
        # Validate input
        if not schema_name:
            return None, "Schema name is required"
        
        # Get connector from session state
        connector = st.session_state.db2_connector
        if not connector:
            return None, "Not connected to database"
        
        # Build the SQL statement
        sql = f'CREATE SCHEMA "{schema_name}"'
        
        # Execute the SQL
        with st.spinner(f"Creating schema {schema_name}..."):
            result, message = connector.execute_query(sql)
            
            if result is not None:
                # Force refresh of schema list cache
                import ui_components
                if hasattr(ui_components, "get_schemas"):
                    ui_components.get_schemas.clear()
                
                return result, f"Schema {schema_name} created successfully"
            else:
                # Special error handling for permission issues
                if "SQL0552N" in message or "privilege" in message.lower() or "permission" in message.lower():
                    return None, f"""Permission denied: Your user account doesn't have the required privileges to create schemas.
                    
Error details: {message}

To resolve this:
1. Connect with a user account that has SYSADM, SYSCTRL, or DBADM authority
2. Ask your database administrator to grant CREATEIN or DBADM privileges to your user"""
                
                # Generic error
                return None, message
                
    except Exception as e:
        return None, f"Error creating schema: {str(e)}"

def handle_schema_error(error_message):
    """Parse DB2 error messages and return user-friendly guidance"""
    if "SQL0552N" in error_message:
        return "Permission denied: Your user doesn't have the required privileges to perform this operation."
    elif "SQL0601N" in error_message:
        return "Schema name already exists. Please choose a different name."
    else:
        return error_message
