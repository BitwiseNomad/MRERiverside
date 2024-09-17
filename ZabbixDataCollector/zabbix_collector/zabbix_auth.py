import aiohttp
import logging
from types import TracebackType
from typing import Optional, Type
from zabbix_types import ZabbixInstance

class ZabbixAuth:
    def __init__(self, url: str):
        self.url = url
        self.auth_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self.ensure_session()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        await self.close()

    async def ensure_session(self) -> None:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def login(self, username: str, password: str):
        await self.ensure_session()

        attempts = [
            {'username': username},
            username  # Fallback: send username directly without a key
        ]

        for attempt in attempts:
            login_data = {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {"password": password},
                "id": 1
            }
            if isinstance(attempt, dict):
                login_data["params"].update(attempt)
            else:
                login_data["params"][attempt] = username

            try:
                async with self.session.post(f"{self.url}/api_jsonrpc.php", json=login_data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    if 'result' in result:
                        self.auth_token = result['result']
                        logging.info(f"Successfully logged in using {attempt}")
                        return
                    else:
                        error_message = result.get('error', {}).get('data', 'Unknown error')
                        logging.warning(f"Login attempt with {attempt} failed: {error_message}")
            except Exception as e:
                logging.error(f"Error during login attempt with {attempt}: {str(e)}")

        # If we've reached this point, all attempts have failed
        raise Exception("Login failed with all attempted methods")

    async def logout(self):
        if self.auth_token:
            await self.ensure_session()
            logout_data = {
                "jsonrpc": "2.0",
                "method": "user.logout",
                "params": [],
                "id": 1,
                "auth": self.auth_token
            }
            try:
                async with self.session.post(f"{self.url}/api_jsonrpc.php", json=logout_data) as response:
                    response.raise_for_status()
                self.auth_token = None
                logging.info("Successfully logged out")
            except Exception as e:
                logging.error(f"Error during logout: {str(e)}")

async def get_zabbix_token(url: str, username: str, password: str) -> ZabbixAuth:
    auth = ZabbixAuth(url)
    await auth.login(username, password)
    return auth
