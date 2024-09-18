from sqlalchemy import create_engine, Column, func, Integer, String, DateTime, Boolean, Float, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import pyodbc
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError
from urllib.parse import quote_plus


Base = declarative_base()

class Plant(Base):
    __tablename__ = 'dim_plant'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Server(Base):
    __tablename__ = 'dim_server'
    id = Column(Integer, primary_key=True)
    plant_id = Column(Integer)
    server_name = Column(String)
    zabbix_hostid = Column(String)

class InfraAvailability(Base):
    __tablename__ = 'fact_infra_availability'
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer)
    timestamp = Column(DateTime)
    is_available = Column(Boolean)
    run_id = Column(Integer)

class DiskSpace(Base):
    __tablename__ = 'fact_disk_space'
    id = Column(Integer, primary_key=True)
    server_id = Column(Integer)
    timestamp = Column(DateTime)
    mount_point = Column(String)
    total_space = Column(Float)
    used_space = Column(Float)
    free_space = Column(Float)
    free_space_percent = Column(Float)

class DatabaseManager:
    def __init__(self, db_config):
        self.config = db_config
        self.engine = self._create_engine()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.run_id = self._get_new_run_id()

    def _create_engine(self):
        username = quote_plus(self.config['username'])
        password = quote_plus(self.config['password'])
        server = self.config['server']
        database = self.config['database']
        driver = quote_plus(self.config['driver'])

        conn_str = (
            f"mssql+pyodbc://{username}:{password}@{server}/{database}?"
            f"driver={driver}"
            f"&timeout=60"
            f"&TrustServerCertificate=yes"
            f"&encrypt=yes"
        )
        logging.info(f"Using connection string: {conn_str}")

        return create_engine(
            conn_str,
            connect_args={'timeout': 60},
            echo=True,
            pool_pre_ping=True,
            pool_recycle=3600
        )

    def get_plant_id(self, plant_name):
        try:
            with self.Session() as session:
                plant = session.query(Plant).filter_by(name=plant_name).first()
                return plant.id if plant else None
        except Exception as e:
            logging.error(f"Error getting plant ID: {str(e)}")
            raise

    def get_or_create_server(self, plant_id, server_name, zabbix_hostid=None):
        try:
            with self.Session() as session:
                server = session.query(Server).filter_by(plant_id=plant_id, server_name=server_name).first()
                if not server:
                    server = Server(plant_id=plant_id, server_name=server_name, zabbix_hostid=zabbix_hostid)
                    session.add(server)
                    session.commit()
                return server.id
        except Exception as e:
            logging.error(f"Error in getting server ID: {str(e)}")
            raise

    def _get_new_run_id(self):
        try:
            with self.Session() as session:
                max_run_id = session.query(func.max(InfraAvailability.run_id)).scalar()
                return (max_run_id or 0) + 1
        except Exception as e:
            logging.error(f"Error getting new run ID: {str(e)}")
            raise

    def insert_infra_availability(self, server_id, is_available):
        try:
            with self.Session() as session:
                availability = InfraAvailability(
                    server_id=server_id,
                    timestamp=datetime.now(),
                    is_available=is_available,
                    run_id=self.run_id
                )
                session.add(availability)
                session.commit()
        except Exception as e:
            logging.error(f"Error inserting availability data: {str(e)}")
            raise

    def insert_disk_space(self, server_id, disk_data):
        try:
            with self.Session() as session:
                disk_space = DiskSpace(
                    server_id=server_id,
                    timestamp=datetime.now(),
                    mount_point=disk_data['mount_point'],
                    total_space=disk_data['total_space'],
                    used_space=disk_data['used_space'],
                    free_space=disk_data['free_space'],
                    free_space_percent=disk_data['free_space_percent']
                )
                session.add(disk_space)
                session.commit()
        except Exception as e:
            logging.error(f"Error inserting disk data: {str(e)}")
            raise

