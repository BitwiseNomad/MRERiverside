import yaml
import logging
import concurrent.futures
from datetime import datetime
from zabbix_collector import ZabbixCollector
from database_manager import DatabaseManager
from zabbix_auth import get_token

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)


def get_zabbix_token(instance):
    if 'token' in instance:
        return instance['token']
    elif 'username' in instance and 'password' in instance:
        return get_token(instance['url'], instance['username'],
                         instance['password'])
    else:
        raise ValueError(f"Neither token nor credentials provided for Zabbix instance: {instance['url']}")


def process_zbx_instance(instance, db_manager):
    try:
        token = get_zabbix_token(instance)
        instance['token'] = token # Update instance with the token
        zabbix_collector = ZabbixCollector(instance)
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

def main():
    try:
        config = load_config('config.yml')
        db_manager = DatabaseManager(config['database'])

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_zbx_instance, instance, db_manager)
                       for instance in config['zabbix_instances']]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error in thread execution: {str(e)}")
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")

if __name__ == '__main__':
    main()
