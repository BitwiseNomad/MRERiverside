from typing import TypedDict, List

class ZabbixInstance(TypedDict):
    url: str
    plant_name: str
    token: str

class ServerInfo(TypedDict):
    name: str
    hostid: str

class DiskSpaceData(TypedDict):
    mount_point: str
    total_space: float
    used_space: float
    free_space: float
    free_space_percent: float
