import asyncio
from typing import Dict, Any
import psycopg2
from psycopg2 import OperationalError
from ..base_connector import BaseConnector, ConnectorResponse, ConnectorConfig, ConnectorStatus
import logging

logger = logging.getLogger(__name__)

class PostgreSQLConnector(BaseConnector):
    """PostgreSQL Database Connector"""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.connection = None

    async def connect(self) -> ConnectorResponse:
        """Establish connection with PostgreSQL database."""
        try:
            self.status = ConnectorStatus.AUTHENTICATING
            
            connection_params = {
                "host": self.config.custom_config.get("host", "localhost"),
                "port": self.config.custom_config.get("port", 5432),
                "database": self.config.custom_config.get("database"),
                "user": self.config.custom_config.get("user"),
                "password": self.config.api_key
            }
            
            self.connection = await asyncio.to_thread(psycopg2.connect, **connection_params)
            self.status = ConnectorStatus.CONNECTED
            
            return ConnectorResponse(success=True, data={"status": "Connected to PostgreSQL"})
            
        except OperationalError as error:
            self.status = ConnectorStatus.ERROR
            self.last_error = str(error)
            logger.error(f"Failed to connect to PostgreSQL: {error}")
            return ConnectorResponse(success=False, error=str(error))

    async def disconnect(self) -> ConnectorResponse:
        """Disconnect from PostgreSQL database."""
        try:
            if self.connection:
                await asyncio.to_thread(self.connection.close)
                self.connection = None
            self.status = ConnectorStatus.DISCONNECTED
            return ConnectorResponse(success=True)
        except Exception as error:
            return ConnectorResponse(success=False, error=str(error))

    async def test_connection(self) -> ConnectorResponse:
        """Test the PostgreSQL connection."""
        try:
            if not self.connection:
                return ConnectorResponse(success=False, error="No connection established")
            
            cursor = await asyncio.to_thread(self.connection.cursor)
            await asyncio.to_thread(cursor.execute, "SELECT version();")
            version = await asyncio.to_thread(cursor.fetchone)
            await asyncio.to_thread(cursor.close)
            
            return ConnectorResponse(success=True, data={"version": version[0]})
            
        except Exception as error:
            logger.error(f"PostgreSQL connection test failed: {error}")
            return ConnectorResponse(success=False, error=str(error))

    async def get_data(self, params: Dict[str, Any]) -> ConnectorResponse:
        """Retrieve data from PostgreSQL."""
        try:
            if not self.connection:
                return ConnectorResponse(success=False, error="No connection established")
                
            query = params.get("query", "SELECT 1")
            cursor = await asyncio.to_thread(self.connection.cursor)
            await asyncio.to_thread(cursor.execute, query)
            results = await asyncio.to_thread(cursor.fetchall)
            await asyncio.to_thread(cursor.close)
            
            return ConnectorResponse(success=True, data={"results": results})
            
        except Exception as error:
            logger.error(f"Failed to get data from PostgreSQL: {error}")
            return ConnectorResponse(success=False, error=str(error))

    async def send_data(self, data: Dict[str, Any]) -> ConnectorResponse:
        """Send data to PostgreSQL."""
        try:
            if not self.connection:
                return ConnectorResponse(success=False, error="No connection established")
                
            query = data.get("query")
            if not query:
                return ConnectorResponse(success=False, error="Query is required")
                
            cursor = await asyncio.to_thread(self.connection.cursor)
            await asyncio.to_thread(cursor.execute, query, data.get("params"))
            await asyncio.to_thread(self.connection.commit)
            await asyncio.to_thread(cursor.close)
            
            return ConnectorResponse(success=True, data={"status": "Query executed successfully"})
            
        except Exception as error:
            logger.error(f"Failed to send data to PostgreSQL: {error}")
            return ConnectorResponse(success=False, error=str(error))
