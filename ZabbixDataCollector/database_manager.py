import requests
import json
from collector import setup_logging


logger = setup_logging(__name__)

class ZabbixAuth:
    def __init__(self, url):
        self.url = url
        self.api_url = f"{url}/api_jsonrpc.php"
        self.auth_token = None
        self.zbx_version = None


    def api_request(self, method, params=None, auth_token=None):
        headers = {'Content-Type': 'application/json-rpc'}
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
            "auth": auth_token or self.auth_token
        }

        logger.debug(f"Sending API request: {method}")
        response = requests.post(self.api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            raise Exception(f"Zabbix API error: {result['error']['data']}")
        return result["result"]


    def get_zbx_version(self):
        if not self.zbx_version:
            version_info = self.api_request("apiinfo.version", auth_token=None)
            self.zbx_version = version_info.split('.')
        return self.zbx_version


    def login(self, username, password):
        try:
            logger.debug(f"Attempting to login with username: {username}")
            version = self.get_zbx_version()

            # Use 'user' for zabbix 5.0 and older, 'username' for newer versions
            usr_param = "user" if int(version[0]) <= 5 else "username"

            result = self.api_request("user.login", {usr_param: username, "password": password}, auth_token=None)
            self.auth_token = result
            logger.info("Login successful")
            return result
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise


    def logout(self):
        if self.auth_token:
            try:
                self.api_request("user.logout", auth_token=self.auth_token)
                logger.info("Logout successful")
            except Exception as e:
                logger.error(f"Logout failed: {e}")
            finally:
                self.auth_token = None

    def get_or_create_token(self, name="PythonScriptToken", userid=None, description=None, expires_in_days=30):
        try:
            # We'll use the session token (self.auth_token) for API requests instead of creating a separate API token
            return self.auth_token
        except Exception as e:
            logger.error(f"Error in get_or_create_token: {e}")
            raise

def get_zabbix_token(url, username, password, token_name="PythonScriptToken"):
    auth = ZabbixAuth(url)
    try:
        auth.login(username, password)
        token = auth.get_or_create_token(token_name)
        if not token:
            raise ValueError("Failed to retrieve a valid token")
        logger.debug(f"Retrieved token: {token[:5]}...") # ...for debugging
        return auth  # Return the ZabbixAuth instance instead of just the token
    except Exception as e:
        logger.error(f"Failed to get Zabbix token: {e}")
        raise
