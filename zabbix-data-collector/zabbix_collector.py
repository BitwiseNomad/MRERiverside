import asyncio
import aiohttp
from typing import List, Optional
from zabbix_types import ZabbixInstance, ServerInfo, DiskSpaceData
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ZabbixCollector:
    def __init__(self, instance: ZabbixInstance):
        self.instance = instance
        self.api_url = f"{instance['url']}/api_jsonrpc.php"
        self.auth_token = instance['token']
        self.servers_group_id = None
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10),
           retry=retry_if_exception_type(aiohttp.ClientError))

    async def api_request(self, method: str, params: dict) -> dict:
        headers = {'Content-Type': 'application/json-rpc'}
        data = {
            'jsonrpc': '2.0',
            'method': method,
            'params': {**params, 'output': 'extend'},
            'auth': self.auth_token,
            'id': 1
        }
        async with self.session.post(self.api_url, json=data, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def get_servers_group_id(self) -> Optional[str]:
        if self.servers_group_id is not None:
            return self.servers_group_id

        try:
            result = await self.api_request('hostgroup.get', {'filter': {'name': ['Servers']}})
            groups = result.get('result', [])
            if groups:
                self.servers_group_id = groups[0]['groupid']
                return self.servers_group_id
            else:
                logging.error("'Servers' group not found")
                return None
        except Exception as e:
            logging.error(f"Error fetching 'Servers' group ID: {str(e)}")
            return None

    async def get_servers(self) -> List[ServerInfo]:
        servers_group_id = await self.get_servers_group_id()
        if not servers_group_id:
            return []

        try:
            result = await self.api_request('host.get', {'groupids': [servers_group_id]})
            return [ServerInfo(name=host['name'], hostid=host['hostid']) for host in result.get('result', [])]
        except Exception as e:
            logging.error(f"Error fetching servers: {str(e)}")
            return []

    async def get_server_availability(self, server: ServerInfo) -> bool:
        try:
            result = await self.api_request('item.get', {
                'hostids': [server['hostid']],
                'search': {'key_': 'agent.ping'},
                'sortfield': 'name'
            })
            items = result.get('result', [])
            if items:
                return items[0]['lastvalue'] == '1'
            return False
        except Exception as e:
            logging.error(f"Error checking server availability: {str(e)}")
            return False

    async def get_server_disk_space(self, hostid: str) -> List[DiskSpaceData]:
        try:
            result = await self.api_request('item.get', {
                'hostids': [hostid],
                'search': {'key_': 'vfs.fs.size'},
                'sortfield': 'name'
            })
            items = result.get('result', [])
            disk_space_data = {}
            for item in items:
                if item['key_'].startswith('vfs.fs.size['):
                    mount_point = item['key_'].split('[')[1].split(',')[0]
                    if mount_point not in disk_space_data:
                        disk_space_data[mount_point] = {}

                    if item['key_'].endswith('total]'):
                        disk_space_data[mount_point]['total_space'] = float(item['lastvalue'])
                    elif item['key_'].endswith('used]'):
                        disk_space_data[mount_point]['used_space'] = float(item['lastvalue'])
                    elif item['key_'].endswith('free]'):
                        disk_space_data[mount_point]['free_space'] = float(item['lastvalue'])

            result = []
            for mount_point, data in disk_space_data.items():
                if all(key in data for key in ['total_space', 'used_space', 'free_space']):
                    total_space = data['total_space']
                    free_space_percent = (data['free_space'] / total_space * 100) if total_space > 0 else 0
                    result.append(DiskSpaceData(
                        mount_point=mount_point,
                        total_space=data['total_space'],
                        used_space=data['used_space'],
                        free_space=data['free_space'],
                        free_space_percent=free_space_percent
                    ))

            return result
        except Exception as e:
            logging.error(f"Error fetching disk space data: {str(e)}")
            return []
