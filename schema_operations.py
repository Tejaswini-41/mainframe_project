import streamlit as st
import pandas as pd
from db2_connector import DB2Connector
import time

def create_schema_interface():
    """Interface for creating a new schema in the database"""
    # Schema name input with improved styling
    schema_name = st.text_input(
        "Schema Name", 
        key="new_schema_name",
        placeholder="Enter schema name (e.g., MYSCHEMA)",
        help="Schema name must start with a letter and can contain letters, numbers, and underscores"
    ).strip().upper()
    
    # Validation with better UI
    is_valid = True
    validation_message = ""
    
    if schema_name:
        if not schema_name[0].isalpha():
            is_valid = False
            validation_message = "Schema name must start with a letter"
        elif len(schema_name) > 30:
            is_valid = False
            validation_message = "Schema name must be 30 characters or less"
        elif not all(c.isalnum() or c == '_' for c in schema_name):
            is_valid = False
            validation_message = "Schema name can only contain letters, numbers, and underscores"
    
    if not is_valid and validation_message:
        st.warning(validation_message)
    
    # Description field (optional)
    schema_description = st.text_area(
        "Description (Optional)",
        placeholder="Add a description for this schema",
        key="schema_description"
    )
    
    # Options and settings
    with st.expander("Advanced Options", expanded=False):
        st.info("No additional options available for schema creation in DB2")
    
    # Create schema button with improved styling
    create_disabled = not schema_name or not is_valid
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Create Schema", type="primary", disabled=create_disabled):
            with st.spinner(f"Creating schema {schema_name}..."):
                # Add slight delay for animation
                time.sleep(0.5)
                return execute_create_schema(schema_name)
    
    # Permission information with improved styling
    st.markdown("---")
    st.markdown("""
    <div style="background:#f0f9ff; border-radius:6px; padding:1rem; border:1px solid #e0f2fe;">
        <h3 style="margin-top:0; font-size:1rem; font-weight:600;">Permission Requirements</h3>
        <p style="font-size:0.9rem;">Creating a schema requires elevated database privileges. 
        Your user account must have one of the following authorities:</p>
        <ul style="font-size:0.9rem;">
            <li><strong>SYSADM</strong> - System Administrator</li>
            <li><strong>SYSCTRL</strong> - System Control</li>
            <li><strong>DBADM</strong> - Database Administrator</li>
        </ul>
        <p style="font-size:0.9rem;">If you don't have these privileges, please contact your database administrator.</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        return {
            "title": "Permission Denied",
            "message": "Your user doesn't have the required privileges to perform this operation.",
            "guidance": "Ask your database administrator to grant the necessary privileges to your user account."
        }
    elif "SQL0601N" in error_message:
        return {
            "title": "Schema Already Exists",
            "message": "A schema with this name already exists in the database.",
            "guidance": "Choose a different schema name or use the existing schema."
        }
    else:
        return {
            "title": "Database Error",
            "message": error_message,
            "guidance": "Check the syntax and permissions for this operation."
        }
