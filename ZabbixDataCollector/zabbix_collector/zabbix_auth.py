import aiohttp
from zabbix_types import ZabbixInstance

class ZabbixAuth:
    def __init__(self, url: str):
        self.url = url
        self.auth_token = None
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def login(self, username: str, password: str):
        login_data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": username,
                "password": password
            },
            "id": 1
        }
        async with self.session.post(f"{self.url}/api_jsonrpc.php", json=login_data) as response:
            response.raise_for_status()
            result = await response.json()
            if 'result' in result:
                self.auth_token = result['result']
            else:
                raise Exception(f"Login failed: {result.get('error', 'Unknown error')}")

    async def logout(self):
        if self.auth_token:
            logout_data = {
                "jsonrpc": "2.0",
                "method": "user.logout",
                "params": [],
                "id": 1,
                "auth": self.auth_token
            }
            async with self.session.post(f"{self.url}/api_jsonrpc.php", json=logout_data) as response:
                response.raise_for_status()
            self.auth_token = None

async def get_zabbix_token(url: str, username: str, password: str) -> ZabbixAuth:
    async with ZabbixAuth(url) as auth:
        await auth.login(username, password)
        return auth
