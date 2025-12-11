from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("influxdb")


class InfluxDBConnection:
    """
    InfluxDB connection manager.
    """
    def __init__(self):
        self.client = None
        self.write_api = None
        self.query_api = None
        
    def connect(self):
        """
        Establish connection to InfluxDB.
        """
        try:
            self.client = InfluxDBClient(
                url=settings.INFLUXDB_URL,
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG
            )
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            logger.info("Connected to InfluxDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            raise
    
    def close(self):
        """
        Close InfluxDB connection.
        """
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed")
    
    def write_point(self, measurement: str, tags: dict, fields: dict):
        """
        Write a data point to InfluxDB.
        """
        try:
            point = Point(measurement)
            
            for key, value in tags.items():
                point = point.tag(key, value)
            
            for key, value in fields.items():
                point = point.field(key, value)
            
            self.write_api.write(
                bucket=settings.INFLUXDB_BUCKET,
                org=settings.INFLUXDB_ORG,
                record=point
            )
        except Exception as e:
            logger.error(f"Failed to write to InfluxDB: {e}")


# Global InfluxDB connection instance
influx_db = InfluxDBConnection()


def get_influx_db() -> InfluxDBConnection:
    """
    Dependency to get InfluxDB connection.
    """
    return influx_db
