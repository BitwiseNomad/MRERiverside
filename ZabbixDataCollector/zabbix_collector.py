from zabbix_utils.api import ZabbixAPI
import logging

class ZabbixCollector:
    def __init__(self, instance):
        self.zapi = self.connect_to_zabbix(instance)
        #self.servers_group_id = self.get_servers_group_id()
        self.windows_servers_group_id = self.get_windows_servers_group_id()

    def connect_to_zabbix(self, instance):
        zapi = ZabbixAPI(instance['url'])
        zapi.login(token=instance['token'])
        return zapi

    '''
    def get_servers_group_id(self):
        try:
            hostgroups = self.zapi.hostgroup.get(filter={'name': ['Servers']})
            return hostgroups[0]['groupid'] if hostgroups else None
        except Exception as e:
            logging.error(f"Error getting 'Servers' hostgroup: {str(e)}")
            return None
    '''

    def get_windows_servers_group_id(self):
        try:
            hostgroups = self.zapi.hostgroup.get(filter={'name': ['Windows servers']})
            return hostgroups[0]['groupid'] if hostgroups else None
        except Exception as e:
            logging.error(f"Error getting 'Windows servers' hostgroup: {str(e)}")
            return None


    def get_servers(self):
        try:
            #if self.servers_group_id:
            if self.windows_servers_group_id:
                servers = self.zapi.host.get(
                    groupids=self.windows_servers_group_id,
                    output=['hostid', 'name'],
                    selectItems=['itemid', 'key_', 'lastvalue'],
                    filter={'status': '0'}  # 0 = enabled hosts
                )
                return servers

            else:
                logging.error("'Windows servers' hostgroup not found")
                return []
        except Exception as e:
            logging.error(f"Error getting servers: {str(e)}")
            return []
        '''
                servers = self.zapi.host.get(
                    output=['hostid', 'name'],
                    selectItems=['itemid', 'key_', 'lastvalue'],
                    filter={'status': '0'}
                )

            # Log the structure of the first server for debugging
            if servers:
                logging.debug(f"Server data structure: {servers[0]}")

            return servers
        except Exception as e:
            logging.error(f"Error getting servers: {str(e)}")
            return []
        '''
    def get_server_availability(self, server):
        try:
            if not isinstance(server, dict):
                logging.error(f"Unexpected server data type: {type(server)}")
                return 0

            for item in server.get('items', []):
                if item['key_'] == 'agent.ping':
                    is_available = item['lastvalue'] == '1'
                    logging.debug(f"Server {server.get('name', 'Unknown')} - Agent Ping: {'Available' if is_available else 'Unavailable'}")
                    return 1 if is_available else 0

            logging.warning(f"No agent.ping item found for server {server.get('name', 'Unknown')}")
            return 0
        except Exception as e:
            logging.error(f"Error getting server availability: {str(e)}")
            return 0

    def get_server_disk_space(self, hostid):
        try:
            items = self.zapi.item.get(
                hostids=hostid,
                search={'key_': 'vfs.fs.size'},
                output=['key_', 'lastvalue']
            )

            disk_data = {}
            for item in items:
                try:
                    key_parts = item['key_'].split('[')[1].split(']')[0].split(',')
                    mount_point = key_parts[0]
                    metric = key_parts[1] if len(key_parts) > 1 else 'total'
                    value = float(item['lastvalue'])

                    if mount_point not in disk_data:
                        disk_data[mount_point] = {'total': 0, 'used': 0, 'free': 0}

                    if 'total' in metric:
                        disk_data[mount_point]['total'] = value
                    elif 'used' in metric:
                        disk_data[mount_point]['used'] = value
                    elif 'free' in metric:
                        disk_data[mount_point]['free'] = value
                except Exception as item_error:
                    logging.warning(f"Error processing item {item['key_']}: {str(item_error)}")
                    continue

            result = []
            for mount_point, data in disk_data.items():
                if data['total'] > 0:
                    # Calculate free space if not provided
                    if data['free'] == 0:
                        data['free'] = data['total'] - data['used']

                    # Calculate free space percentage
                    free_percent = (data['free'] / data['total']) * 100

                    result.append({
                        'mount_point': mount_point,
                        'total_space': data['total'],
                        'used_space': data['used'],
                        'free_space': data['free'],
                        'free_space_percent': free_percent
                    })

            return result
        except Exception as e:
            logging.error(f"Error getting server disk space: {str(e)}")
            return []
