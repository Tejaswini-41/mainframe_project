"""
DB2 Explorer - A web-based management tool for IBM DB2 databases

This script runs the Streamlit application. You can run it directly or use 'app.py' as an alternative entry point.
"""

import os
import streamlit as st
import subprocess
import sys

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'ibm_db'
    ]
    
    # Check for IBM DB2 client driver
    if not os.path.exists('clidriver\\bin'):
        st.error("""
        IBM DB2 client driver not found!
        
        Please download and install the IBM DB2 client driver from:
        https://www.ibm.com/support/pages/db2-odbc-cli-driver-download-and-installation-information
        
        The driver should be installed at: C:\\Program Files\\IBM\\clidriver
        """)
        return False
        
    # Check for required Python packages
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        st.error(f"Missing required packages: {', '.join(missing_packages)}")
        
        if st.button("Install Missing Packages"):
            for package in missing_packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    st.success(f"Successfully installed {package}")
                except Exception as e:
                    st.error(f"Failed to install {package}: {e}")
            
            st.info("Please restart the application after installing packages.")
        return False
    
    return True

def main():
    """Main entry point for the application"""
    from app import main as app_main
    
    # First check requirements
    if check_requirements():
        # Run the main application
        app_main()

if __name__ == "__main__":
    main()