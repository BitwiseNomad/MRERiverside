import pyodbc
from datetime import datetime
import logging


class DatabaseManager:
    def __init__(self, db_config):
        self.conn_str = self._create_conn_str(db_config)

    def _create_conn_str(self, config):
        return (
            f"DRIVER={{{config['driver']}}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
        )

    def _get_connection(self):
        return pyodbc.connect(self.conn_str)

    def get_plant_id(self, plant_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                    "SELECT id FROM dbo.dim_plant WHERE name = ?", (plant_name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_or_create_server(self, plant_id, server_name, zabbix_hostid=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Get existing server
                cursor.execute("""
                SELECT id FROM dbo.dim_server WHERE plant_id = ? AND server_name = ?
                """, (plant_id, server_name))
                result = cursor.fetchone()

                if result:
                    return result[0]
                else:
                    # if not found, insert the new server
                    cursor.execute("""
                    INSERT INTO dbo.dim_server (plant_id, server_name, zabbix_hostid)
                    VALUES (?, ?, ?)
                    """, (plant_id, server_name, zabbix_hostid))
                    conn.commit()

                    # Now get the id of server
                    cursor.execute("""
                    SELECT id FROM dbo.dim_server WHERE plant_id = ? AND server_name = ?
                    """, (plant_id, server_name))
                    result = cursor.fetchone()
                    return result[0]
            except Exception as e:
                logging.error(f"Error in get_or_create_server: {str(e)}")
                conn.rollback()
                raise

    def insert_infra_availability(self, server_id, is_available):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO dbo.fact_infra_availability (server_id, timestamp, is_available)
                VALUES (?, ?, ?)
                """, (server_id, datetime.now(), is_available))
                conn.commit()
            except Exception as e:
                logging.error(f"Error in insert_infra_availability: {str(e)}")
                conn.rollback()
                raise

    def insert_disk_space(self, server_id, disk_data):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                INSERT INTO dbo.fact_disk_space
                (server_id, timestamp, mount_point, total_space, used_space, free_space, free_space_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (server_id, datetime.now(), disk_data['mount_point'],
                      disk_data['total_space'], disk_data['used_space'],
                      disk_data['free_space'], disk_data['free_space_percent']))
                conn.commit()
            except Exception as e:
                logging.error(f"Error in insert_disk_space: {str(e)}")
                conn.rollback()
                raise
