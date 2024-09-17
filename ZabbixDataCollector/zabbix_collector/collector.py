import asyncio
import yaml
import logging
from logging.handlers import RotatingFileHandler
import os
import subprocess
from datetime import datetime
from database_manager import DatabaseManager
from zabbix_auth import ZabbixAuth, get_zabbix_token
from zabbix_collector import ZabbixCollector
from zabbix_types import ZabbixInstance


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # Create a logger for this module
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'collector.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging initialized for collector module")

    # Generate a timestamp for the log filename
    timestamp = datetime.now().strftime("%Y%M%d_%H%M%S")
    log_file = os.path.join(log_dir, f'zabbix_collector_{timestamp}.log')

    # Set up the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5) # 10MB per file, keep 5 backups
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # why dafuq wouldn't you?!
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info(f"logging initialized. log file: {log_file}")


def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

async def get_auth_for_instance(instance: ZabbixInstance) -> ZabbixAuth:
    try:
        if 'token' in instance and instance['token']:
            logging.info(f"Using provided API token for instance {instance['url']}")
            auth = ZabbixAuth(instance['url'])
            auth.auth_token = instance['token']
            return auth
        elif 'username' in instance and 'password' in instance:
            logging.info(f"Generating token using username/password for instance {instance['url']}")
            auth = ZabbixAuth(instance['url'])
            await auth.login(instance['username'], instance['password'])
            return auth
        else:
            raise ValueError(f"Neither valid token nor credentials provided for Zabbix instance: {instance['url']}")
    except Exception as e:
        logging.error(f"Error getting Zabbix auth for instance {instance['url']}: {str(e)}")
        raise

async def process_zbx_instance(instance: ZabbixInstance, db_manager: DatabaseManager) -> bool:
    logging.info(f"Starting to process Zabbix instance: {instance['url']} for plant: {instance['plant_name']}")
    zabbix_auth = None
    try:
        zabbix_auth = await get_auth_for_instance(instance)
        if not zabbix_auth or not zabbix_auth.auth_token:
            logging.error(f"Failed to obtain valid auth for instance {instance['url']}")
            return False

        instance['token'] = zabbix_auth.auth_token  # Update the instance with the token

        async with ZabbixCollector(instance) as zabbix_collector:
            plant_id = db_manager.get_plant_id(instance['plant_name'])

            if plant_id is None:
                logging.error(f"Plant {instance['plant_name']} not found in the database.")
                return False

            servers = await zabbix_collector.get_servers()
            logging.info(f"Found {len(servers)} servers for plant {instance['plant_name']}")

            for server in servers:
                try:
                    server_name = server['name']
                    server_id = db_manager.get_or_create_server(plant_id, server_name, server['hostid'])

                    # Collect and insert availability data
                    is_available = await zabbix_collector.get_server_availability(server)
                    db_manager.insert_infra_availability(server_id, is_available)
                    logging.info(f"Inserted availability data for server {server_name}: {'Available' if is_available else 'Unavailable'}")

                    # Collect and insert disk space data
                    disk_space_data = await zabbix_collector.get_server_disk_space(server['hostid'])
                    for disk_data in disk_space_data:
                        db_manager.insert_disk_space(server_id, disk_data)
                        logging.info(f"Inserted disk space data for server {server_name}, mount point {disk_data['mount_point']}")

                except Exception as e:
                    logging.error(f"Error processing server {server_name} in plant {instance['plant_name']}: {str(e)}")
                    continue

        logging.info(f"Data collection completed for plant {instance['plant_name']}")
        return True
    except Exception as e:
        logging.error(f"Error processing Zabbix instance {instance['url']}: {str(e)}")
        return False
    finally:
        if zabbix_auth:
            await zabbix_auth.logout()

#async def test_database_connection(db_manager):
#    logging.info("Testing database connection...")
#    try:
#        # Test a simple query
#        plant_id = db_manager.get_plant_id("Riverside")
#        logging.info(f"DB connection successful. Test query result: {plant_id}")
#        # Test creating a session
#        with db_manager.Session() as session:
#            result = session.execute("SELECT 1").fetchone()
#            logging.info(f"Session created successfully. Test result: {result}")
#        return True
#    except Exception as e:
#        logging.error(f"Failed to connect to the database: {str(e)}", exc_info=True)
#        if hasattr(e, 'orig'):
#            logging.error(f"Original error: {str(e.orig)}")
#        return False


#def check_odbc_driver():
#    try:
#        res = subprocess.run(['odbcinst', '-q', '-d'], capture_output=True, text=True)
#        logging.info(f"Available ODBC drivers:\n{res.stdout}")
#
#        res = subprocess.run(['odbcinst', '-q', '-d', '-n', "ODBC Driver 17 for SQL Server"], capture_output=True, text=True)
#        logging.info(f"ODBC Driver 17 for SQL Server configuration:\n{res.stdout}")
#    except Exception as e:
#        logging.error(f"Error checking ODBC driver: {str(e)}")
#
#def run_network_diagnostics(server):
#    try:
#        ping_result = subprocess.run(['ping', '-c', '4', server], capture_output=True, text=True)
#        logging.info(f"Ping test results:\n{ping_result.stdout}")
#
#        traceroute_result = subprocess.run(['traceroute', server], capture_output=True, text=True)
#        logging.info(f"Traceroute results:\n{traceroute_result.stdout}")
#
#        nc_result = subprocess.run(['nc', '-zv', server, '1433'], capture_output=True, text=True)
#        logging.info(f"Port 1433 test results:\n{nc_result.stderr}")
#    except Exception as e:
#        logging.error(f"Error running network diagnostics: {str(e)}")
#
#
#def check_firewall_and_sql_config(server):
#    logging.info("Checking firewall and SQL Server configuration...")
#    logging.info("Please ensure that:")
#    logging.info(f"1. The firewall on {server} allows incoming connections on port 1433")
#    logging.info(f"2. SQL Server on {server} is configured to allow remote connections")
#    logging.info("3. The SQL Server Browser service is running on the server")
#    logging.info("4. The server's network adapter has TCP/IP enabled")
#    logging.info("5. Your client machine's firewall is not blocking outgoing connections to port 1433")

async def main():
    setup_logging()
    try:
        config = load_config('config.yml')
        #logging.info(f"Loaded config: {config}")

        #check_odbc_driver()

        try:
            db_manager = DatabaseManager(config['database'])
        except ValueError as ve:
            logging.error(f"Configuration error: {str(ve)}")
            return
        except Exception as e:
            logging.error(f"Error initializing DatabaseManager: {str(e)}", exc_info=True)
            return

        logging.info(f"Initialized DatabaseManager with config: {config['database']}")

        #if not await test_database_connection(db_manager):
        #    logging.error("DB connection test failed. Exiting...")
        #    return

        logging.info(f"Starting data collection run with run_id: {db_manager.run_id}")

        zabbix_instances = config['zabbix_instances']
        logging.info(f"Found {len(zabbix_instances)} Zabbix instances in the configuration")

        tasks = [process_zbx_instance(instance, db_manager) for instance in zabbix_instances]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for instance, result in zip(zabbix_instances, results):
            if isinstance(result, Exception):
                logging.error(f"Error processing instance {instance['url']}: {str(result)}")
            else:
                logging.info(f"Finished processing instance {instance['url']} with result: {'Success' if result else 'Failure'}")

        logging.info("All Zabbix instances have been processed")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}", exc_info=True)

if __name__ == '__main__':
    asyncio.run(main())
