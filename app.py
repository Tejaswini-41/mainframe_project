import streamlit as st
from db2_connector import DB2Connector
from ui_components import (
    connection_page,
    main_interface,
    handle_context_menu_actions
)

st.set_page_config(
    page_title="DB2 Web Manager",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .context-menu-trigger:hover {
        background-color: #f0f2f6;
    }
    .custom-context-menu button {
        display: block;
        width: 100%;
        text-align: left;
        background: none;
        border: none;
        padding: 5px 10px;
    }
    .custom-context-menu button:hover {
        background-color: #f0f2f6;
    }
    .stButton button {
        border-radius: 4px;
    }
    .main-header {
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize session states if not present
    if 'db2_connector' not in st.session_state:
        st.session_state.db2_connector = None
    
    if 'page' not in st.session_state:
        st.session_state.page = 'connection'
    
    if 'selected_schema' not in st.session_state:
        st.session_state.selected_schema = None
        
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = None
        
    if 'query_result' not in st.session_state:
        st.session_state.query_result = None
        
    if 'message' not in st.session_state:
        st.session_state.message = None
        
    # Handle any actions from context menus
    if 'action' in st.session_state:
        handle_context_menu_actions()
        
    # Display the appropriate page
    if st.session_state.page == 'connection':
        connection_page()
    else:
        main_interface()
            
    # Display temporary messages
    if st.session_state.message:
        st.toast(st.session_state.message)
        st.session_state.message = None

if __name__ == "__main__":
    main()