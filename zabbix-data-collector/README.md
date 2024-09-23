# Zabbix Data Collector

## Overview

The Zabbix Data Collector is a Python-based tool designed to collect server infrastructure data from multiple Zabbix instances and store it in a centralized SQL Server database. This tool is particularly useful for organizations managing multiple Zabbix servers across different plants or locations.

## Features

- Asynchronous data collection from multiple Zabbix instances
- Centralized storage of collected data in a SQL Server database
- Collects server availability and disk space information
- Configurable via YAML file
- Robust error handling and logging

## Prerequisites

- Python 3.8+
- SQL Server database
- ODBC Driver 17 for SQL Server
- Access to one or more Zabbix instances

## Installation

> [!NOTE]
> This tool is specifically being designed to run on the Windows Server hosting the SQL Server, enabling direct and efficient data collection and storage.

### Windows

1. On the Windows Server, clone or copy the repository to a suitable location:
   ```
   git clone https://github.com/BitwiseNomad/MRERiverside.git
   cd MRERiverside\zabbix-data-collector
   ```

2. Set up a Python virtual environment (optional but recommended):
   ```
   conda create -n <env_name> python=3.xx
   conda activate <env_name>

   ...OR

   python -m venv venv
   venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure the `config.yml` file with your database and Zabbix instance details.

## Configuration

Edit the <table><tr><td>`config.yml`</td></tr></table> file to set up your database connection and Zabbix instances:

```yaml
database:
  driver: "ODBC Driver 17 for SQL Server"
  server: "your_server_address"
  database: "your_database_name"
  username: "your_username"
  password: "your_password"

zabbix_instances:
  - url: "http://zabbix1.example.com/zabbix"
    username: "your_zabbix_username"
    password: "your_zabbix_password"
    plant_name: "Plant1"
  - url: "http://zabbix2.example.com/zabbix"
    username: "your_zabbix_username"
    password: "your_zabbix_password"
    plant_name: "Plant2"
```

## Usage

Run the collector script:

```
python collector.py
```

The script will collect data from all configured Zabbix instances and store it in the specified SQL Server database.

> [!TIP]
> **Windows** - run the script automatically at regular intervals.:

1. Create a batch file (e.g. `run_collector.bat`):
    ```batch
    @echo off
    cd /d C:\path\to\zabbix-data-collector
    call venv\Scripts\activate
    python collector.py
    ```
2. Use Task Scheduler to run batch file at a desired frequency.

## Logging

Logs are stored in the `logs` directory. Each run creates a new log file with a timestamp.


## Troubleshooting

If you encounter any issues:
1. Check the log files for detailed error messages.
2. Ensure your database and Zabbix credentials are correct.
3. Verify that the ODBC driver is properly installed and configured.
4. Check your network connectivity to both the database server and Zabbix instances.
5. Ensure that the Windows Firewall allows the script to access the zabbix instances.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT](https://opensource.org/licenses/MIT)

## Acknowledgements

- [Zabbix API](https://www.zabbix.com/documentation/current/en/manual/api)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [aiohttp](https://docs.aiohttp.org/en/stable/)
