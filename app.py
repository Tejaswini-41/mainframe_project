import streamlit as st
from db2_connector import DB2Connector
from ui_components import (
    connection_page,
    main_interface,
    handle_context_menu_actions
)

# Configure the page with a professional theme
st.set_page_config(
    page_title="DB2 Explorer",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for modern UI styling
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-163ttbj, .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Cards and containers */
    .stCard {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-bottom: 1rem;
        background: white;
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stCard:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    
    /* Buttons */
    .stButton button, .stDownloadButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    button[data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        font-weight: 500;
    }
    
    /* Form fields */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 6px;
        transition: border-color 0.2s;
    }
    
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #3b71ca;
        box-shadow: 0 0 0 2px rgba(59, 113, 202, 0.25);
    }
    
    /* Tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .stDataFrame thead tr th {
        background-color: #f8f9fa;
        border-top: none;
        border-bottom: 1px solid #e9ecef;
        padding: 0.75rem 1rem;
        font-weight: 600;
    }
    
    /* Alerts and Info Boxes */
    .stAlert {
        border-radius: 6px;
        border-width: 1px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    
    /* Animation for page transitions */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main .block-container {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Custom components */
    .db2-card {
        padding: 1.5rem;
        background: white;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .db2-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Database connection status indicator */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-connected {
        background-color: #10b981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
    
    .status-disconnected {
        background-color: #f43f5e;
        box-shadow: 0 0 0 2px rgba(244, 63, 94, 0.2);
    }
    
    /* SQL Editor styling */
    .sql-editor {
        border-radius: 8px;
        border: 1px solid #e9ecef;
        overflow: hidden;
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
    
    # Add new theme setting in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
        
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