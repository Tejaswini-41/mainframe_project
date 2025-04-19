# DB2 Explorer

A professional web-based management tool for IBM DB2 databases, similar to pgAdmin but specialized for DB2. This application allows you to connect to a DB2 instance, browse schemas and tables, view and manipulate data, and execute custom SQL queries through an intuitive, modern interface.

![DB2 Explorer](https://via.placeholder.com/800x450?text=DB2+Explorer+Professional+Interface)

## Features

- **Modern UI**: Clean, professional interface with animations and intuitive navigation
- **Connection management**: Connect to any DB2 instance with saved connection profiles
- **Database overview**: View database and server information with visual metrics
- **Schema explorer**: Browse, create, and manage schemas in the database
- **Table management**: Create tables with custom columns, primary keys, and constraints
- **Data operations**: View table structure, insert data, and manage records
- **SQL executor**: Execute custom SQL queries with results as downloadable CSV
- **Optimized performance**: Cached schema and table loading for faster navigation
- **Responsive design**: Works on desktop, tablet, and mobile devices

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

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run main.py
```

## Usage Guide

### Connecting to DB2

1. Launch the application and use the connection form
2. Enter your DB2 server details and credentials
3. Save commonly used connections as profiles

### Managing Schemas

- Create new schemas (requires admin privileges)
- Browse existing schemas
- View schema details and tables within

### Working with Tables

- Create tables with custom column definitions
- View table structure and data
- Insert, update, and delete data
- Execute operations like truncate and drop

### Executing SQL

- Use the built-in SQL editor to write and execute queries
- View results in a paginated data table
- Download results in CSV format

## Development

### Project Structure

```
mainframe_project/
├── app.py               # Main Streamlit application
├── main.py              # Entry point 
├── db2_connector.py     # DB2 database connection handler
├── ui_components.py     # UI components and interfaces
├── table_operations.py  # Table management functionality
├── schema_operations.py # Schema management functionality
└── requirements.txt     # Project dependencies
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.