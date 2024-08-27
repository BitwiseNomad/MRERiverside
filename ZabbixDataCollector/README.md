# Zabbix Data Collector

## Overview
This is a Python-based tool designed to collect infrastructure availability
and disk space metrics from multiple Zabbix instances and store the data in a
centralized SQL Server database. It's built with modularity and configurability
in mind, allowing for easy maintenance and scalability.

## Features
* Connects to multiple Zabbix instances concurrently.
* Collects infrastructure availability.
* Calculates/identifies servers with low free disk space.
* Stores collected data in a centralized SQL Server DB.
* Configurable via YAML file

## Structure
* `collector.py`: Main script that orchestrates the data collection process
* `zabbix_collector.py`: Module for interacting with Zabbix instances
* `database_manager.py`: Module for managing database operations
* `config.yaml`: Configuration file for Zabbix instances and database connection

## Prerequisites
* Python3.7+
* Microsoft ODBC Driver for SQL Server
* Required Python packages:
    * pyodbc
    * zabbix-utils -> for `Zabbix API`
    * PyYAML

Install the required packages:
`pip install pyodbc zabbix-utils PyYAML`

## Configuration
Update the `config.yaml` file by appending your Zabbix instance details.

The database information is already provided:
```
database:
    driver: "ODBC Driver 17 for SQL Server"
    server: "COLO SQL Server"
    database: "DB_Name"
    username: "db_user"
    password: "db_pwd"

zabbix_instances:
    - url: "http://your_zabbix_url"
      token: "your_zabbix_api_token"
      plant_name: "Plant Name"
      region: "Region"
      bs_unit: "Business Unity"

    # Append more instances as needed
```

## Usage
Run the main script:

`python collector.py`

The script will connect to all configured Zabbix instances, collect the
specified data, and store it in the configured database.

## Troubleshooting
* Ensure all required Python packages are installed.
* Verify that the ODBC driver for SQL Server is installed on your system.
* Check that the Zabbix API tokens or credentials in `config.yaml` are correct and up-to-date
* Review the log output for any error messages or warning.
