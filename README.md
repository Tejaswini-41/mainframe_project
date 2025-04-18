# DB2 Web Manager

A web-based management tool for IBM DB2 databases, similar to pgAdmin but specialized for DB2. This application allows you to connect to a DB2 instance, browse schemas and tables, view and manipulate data, and execute custom SQL queries through a user-friendly web interface.

![DB2 Web Manager](https://via.placeholder.com/800x450?text=DB2+Web+Manager)

## Features

- **Connection management**: Connect to any DB2 instance with connection profiles
- **Database overview**: View database and server information
- **Schema explorer**: Browse all schemas and tables in the database
- **Table viewer**: Examine table structure and data with pagination
- **SQL executor**: Execute custom SQL queries with results as downloadable CSV
- **Visualization**: Charts and statistics about your database structure

## Prerequisites

- Python 3.7+
- IBM DB2 Client Driver (clidriver)
- IBM DB2 instance to connect to

## Installation

### 1. Install the IBM DB2 Client Driver

Download and install the IBM DB2 client driver from:
[IBM DB2 ODBC CLI Driver Download](https://www.ibm.com/support/pages/db2-odbc-cli-driver-download-and-installation-information)

The driver should be installed at: `C:\Program Files\IBM\clidriver`

### 2. Clone the repository

```bash
git clone <repository-url>
cd mainframe_project
```

### 3. Set up a Python virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install the required packages

```bash
pip install -r requirements.txt
```

Or install the packages individually:

```bash
pip install streamlit pandas plotly ibm_db ibm_db_dbi
```

## Usage

### Running the application

```bash
streamlit run app.py
```

Alternatively, you can use:

```bash
python main.py
```

### Connection Settings

When you start the application, you will need to provide the following information to connect to your DB2 database:

- **Hostname**: The hostname or IP address of your DB2 server (default: localhost)
- **Port**: The port number for the DB2 server (default: 25000)
- **Database**: The name of the database to connect to
- **Username**: Your DB2 username
- **Password**: Your DB2 password

You can save these settings as a connection profile for future use.

## Application Structure

- `app.py`: Main Streamlit application entry point
- `main.py`: Alternative entry point with dependency checking
- `db2_connector.py`: DB2 database connection and operations
- `ui_components.py`: Streamlit UI components

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- IBM for DB2 database and drivers
- Streamlit for the web interface framework