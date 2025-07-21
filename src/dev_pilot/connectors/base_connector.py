from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import logging
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ConnectorType(Enum):
    """Enum for different types of connectors"""
    PROJECT_MANAGEMENT = "project_management"
    VERSION_CONTROL = "version_control"
    CI_CD = "ci_cd"
    COMMUNICATION = "communication"
    CLOUD_STORAGE = "cloud_storage"
    DATABASE = "database"
    MONITORING = "monitoring"
    SECURITY = "security"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    CRM = "crm"
    SUPPORT = "support"
    SOCIAL_MEDIA = "social_media"
    NOTIFICATION = "notification"
    AUTHENTICATION = "authentication"

class ConnectorStatus(Enum):
    """Enum for connector connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    AUTHENTICATING = "authenticating"

class ConnectorConfig(BaseModel):
    """Base configuration for connectors"""
    name: str
    connector_type: ConnectorType
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    custom_config: Dict[str, Any] = Field(default_factory=dict)

class ConnectorResponse(BaseModel):
    """Standard response format for connector operations"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class BaseConnector(ABC):
    """Abstract base class for all connectors"""
    
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.status = ConnectorStatus.DISCONNECTED
        self.last_error: Optional[str] = None
        self.connection_time: Optional[datetime] = None
        
    @abstractmethod
    async def connect(self) -> ConnectorResponse:
        """Connect to the external service"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> ConnectorResponse:
        """Disconnect from the external service"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> ConnectorResponse:
        """Test the connection to the external service"""
        pass
    
    @abstractmethod
    async def get_data(self, params: Dict[str, Any]) -> ConnectorResponse:
        """Get data from the external service"""
        pass
    
    @abstractmethod
    async def send_data(self, data: Dict[str, Any]) -> ConnectorResponse:
        """Send data to the external service"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current connector status"""
        return {
            "name": self.config.name,
            "type": self.config.connector_type.value,
            "status": self.status.value,
            "last_error": self.last_error,
            "connection_time": self.connection_time,
            "enabled": self.config.enabled
        }
    
    def is_connected(self) -> bool:
        """Check if connector is connected"""
        return self.status == ConnectorStatus.CONNECTED
    
    async def health_check(self) -> ConnectorResponse:
        """Perform health check on the connector"""
        try:
            if not self.is_connected():
                return ConnectorResponse(
                    success=False,
                    error="Connector is not connected"
                )
            
            return await self.test_connection()
        except Exception as e:
            logger.error(f"Health check failed for {self.config.name}: {str(e)}")
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
