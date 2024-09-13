import yaml
import logging
from logging.handlers import RotatingFileHandler
import os
import concurrent.futures
from datetime import datetime
from zabbix_collector import ZabbixCollector
from database_manager import DatabaseManager
from zabbix_auth import ZabbixAuth, get_zabbix_token


def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # Generate a timestamp for the log filename
    timestamp = datetime.now().strftime("%Y%M%d_%H%M%S")
    log_file = os.path.join(log_dir, f'zabbix_collector_{timestamp}.log')

    # Set up the root logger
    logger = logging.getlogger()
    logger.setLevel(logging.DEBUG)

    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5) # 10MB per file, keep 5 backups
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Why dafuq NOT?! Can be removed once ready for production
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info(f"Logging initialized. Log file: {log_file}")


def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def get_auth_for_instance(instance):
    try:
        if 'token' in instance and instance['token']:
            logging.info(f"Using provided API token for instance {instance['url']}")
            auth = ZabbixAuth(instance['url'])
            auth.auth_token = instance['token']
            return auth
        elif 'username' in instance and 'password' in instance:
            logging.info(f"Generating token using username/password for instance {instance['url']}")
            return get_zabbix_token(instance['url'], instance['username'], instance['password'])
        else:
            raise ValueError(f"Neither valid token nor credentials provided for Zabbix instance: {instance['url']}")
    except Exception as e:
        logging.error(f"Error getting Zabbix auth for instance {instance['url']}: {str(e)}")
        raise

def process_zbx_instance(instance, db_manager):
    logging.info(f"Starting to process Zabbix instance: {instance['url']} for plant: {instance['plant_name']}")
    zabbix_auth = None
    try:
        zabbix_auth = get_auth_for_instance(instance)
        if not zabbix_auth or not zabbix_auth.auth_token:
            logging.error(f"Failed to obtain valid auth for instance {instance['url']}")
            return False

        instance['token'] = zabbix_auth.auth_token  # Update the instance with the token

        try:
            zabbix_collector = ZabbixCollector(instance)
        except Exception as e:
            logging.error(f"Failed to initialize ZabbixCollector for instance {instance['url']}: {str(e)}")
            return False

        plant_id = db_manager.get_plant_id(instance['plant_name'])

        if plant_id is None:
            logging.error(f"Plant {instance['plant_name']} not found in the database.")
            return False

        servers = zabbix_collector.get_servers()
        logging.info(f"Found {len(servers)} servers for plant {instance['plant_name']}")

        for server in servers:
            try:
                if not isinstance(server, dict):
                    logging.error(f"Unexpected server data type: {type(server)}")
                    continue

                server_name = server.get('name', 'Unknown')
                server_id = db_manager.get_or_create_server(plant_id, server_name, server.get('hostid'))

                # Collect and insert availability data
                is_available = zabbix_collector.get_server_availability(server)
                db_manager.insert_infra_availability(server_id, is_available)
                logging.info(f"Inserted availability data for server {server_name}: {'Available' if is_available else 'Unavailable'} (based on agent.ping)")

                # Collect and insert disk space data
                disk_space_data = zabbix_collector.get_server_disk_space(server.get('hostid'))
                for disk_data in disk_space_data:
                    db_manager.insert_disk_space(server_id, disk_data)
                    logging.info(f"Inserted disk space data for server {server_name}, mount point {disk_data['mount_point']}: "
                                 f"Total: {disk_data['total_space']}, Used: {disk_data['used_space']}, "
                                 f"Free: {disk_data['free_space']}, Free%: {disk_data['free_space_percent']:.2f}%")

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
            zabbix_auth.logout()

def main():
    setup_logging()
    try:
        config = load_config('config.yml')
        db_manager = DatabaseManager(config['database'])

        logging.info(f"Starting data collection run with run_id: {db_manager.run_id}")

        zabbix_instances = config['zabbix_instances']
        logging.info(f"Found {len(zabbix_instances)} Zabbix instances in the configuration")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_instance = {executor.submit(process_zbx_instance, instance, db_manager): instance for instance in zabbix_instances}

            for future in concurrent.futures.as_completed(future_to_instance):
                instance = future_to_instance[future]
                try:
                    result = future.result()
                    logging.info(f"Finished processing instance {instance['url']} with result: {'Success' if result else 'Failure'}")
                except Exception as e:
                    logging.error(f"Error in thread execution for instance {instance['url']}: {str(e)}")

        logging.info("All Zabbix instances have been processed")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == '__main__':
    main()
