import requests
import json
import logging
from datetime import datetime, timedelta


class ZabbixAuth:
    def __init__(self, url):
        self.url = url
        self.api_url = f"{url}/api_jsonrpc.php"
        self.auth_token = None


    def api_request(self, method, params=None):
        headers = {'Content-Type': 'application/json-rpc'}
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
            "auth": self.auth_token
        }

        response = requests.post(self.api_url, data=json.dumps(payload),
                                 headers=headers)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            raise Exception(f"Zabbix API error: {result['error']['data']}")
        return result["result"]


    def login(self, username, password):
        try:
            result = self.api_requestr("user.login", {"user": username,
                                                      "password": password})
            self.auth_token = result
            return result
        except Exception as e:
            logging.error(f"Login failed: {e}")
            raise


    def logout(self):
        if self.auth_token:
            try:
                self.api_request("user.logout")
            except Exception as e:
                logging.error(f"Logout failed: {e}")
            finally:
                self.auth_token = None


    def create_token(self, name, userid=None, description=None,
                     expires_at=None):
        token_params = {
            "name": name,
            "userid": userid,
            "description": description,
            "expires_at": expires_at
        }
        token_params = {k: v for k, v in token_params.items() if v is not None}
        return self.api_request("token.create", [token_params])


    def generate_token(self, tokenid):
        return self.api_request("token.generate", [tokenid])


    def get_token(self, name, userid=None):
        params = {
            "output": "extend",
            "filter": {
                "name": name
            }
        }
        if userid:
            params["userids"] = userid
        return self.api_request("token.get", params)


    def get_or_create_token(self, name, userid=None, description=None,
                            expires_in_days=30):
        existing_tokens = self.get_token(name, userid)
        if existing_tokens:
            token = existing_tokens[0]
            if token['expires_at'] == '0' or int(token['expires_at']) > \
                    int(datetime.now().timestamp()):
                return token['token']

        expires_at = int((datetime.now() +
                          timedelta(days=expires_in_days)).timestamp())
        created_token = self.create_token(name, userid, description, expires_at)
        generated_token = self.generate_token(created_token['tokenids'][0])
        return generated_token[0]['token']


    def get_token(url, username, password, token_name="PythonScriptToken"):
        auth = ZabbixAuth(url)
        try:
            auth.login(username, password)
            token = auth.get_or_create_token(token_name)
            return token
        finally:
            auth.logout()
