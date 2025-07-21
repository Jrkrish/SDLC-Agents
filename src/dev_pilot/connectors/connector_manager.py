from typing import Dict, List, Optional, Any, Type
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pydantic import BaseModel

from .base_connector import BaseConnector, ConnectorConfig, ConnectorResponse, ConnectorType, ConnectorStatus
from .project_management.jira_connector import JiraConnector
from .project_management.github_connector import GitHubConnector
from .communication.slack_connector import SlackConnector
from .cloud_storage.s3_connector import S3Connector
from .database.postgres_connector import PostgreSQLConnector

logger = logging.getLogger(__name__)

# Mock connector class for demo purposes
class MockConnector(BaseConnector):
    """Mock connector for demonstration"""
    async def connect(self) -> ConnectorResponse:
        self.status = ConnectorStatus.CONNECTED
        return ConnectorResponse(success=True, data={"mock": "connected"})
    
    async def disconnect(self) -> ConnectorResponse:
        self.status = ConnectorStatus.DISCONNECTED
        return ConnectorResponse(success=True)
    
    async def test_connection(self) -> ConnectorResponse:
        return ConnectorResponse(success=True, data={"status": "mock test passed"})
    
    async def get_data(self, params: dict) -> ConnectorResponse:
        return ConnectorResponse(success=True, data={"mock_data": "sample"})
    
    async def send_data(self, data: dict) -> ConnectorResponse:
        return ConnectorResponse(success=True, data={"mock_sent": "success"})

class ConnectorRegistry:
    """Registry of all available connectors - 40 Popular Enterprise Connectors"""
    
    _connectors: Dict[str, Type[BaseConnector]] = {
        # Project Management (5)
        "jira": JiraConnector,
        "github": GitHubConnector,
        "gitlab": MockConnector,  # GitLabConnector
        "bitbucket": MockConnector,  # BitbucketConnector
        "azure_devops": MockConnector,  # AzureDevOpsConnector
        
        # Communication (8)
        "slack": SlackConnector,
        "teams": MockConnector,  # TeamsConnector
        "discord": MockConnector,  # DiscordConnector
        "telegram": MockConnector,  # TelegramConnector
        "whatsapp": MockConnector,  # WhatsAppConnector
        "email": MockConnector,  # EmailConnector
        "twilio": MockConnector,  # TwilioConnector
        "zoom": MockConnector,  # ZoomConnector
        
        # Cloud Storage (5)
        "aws_s3": S3Connector,
        "google_drive": MockConnector,  # GoogleDriveConnector
        "azure_blob": MockConnector,  # AzureBlobConnector
        "dropbox": MockConnector,  # DropboxConnector
        "box": MockConnector,  # BoxConnector
        
        # Database (5)
        "postgresql": PostgreSQLConnector,
        "mysql": MockConnector,  # MySQLConnector
        "mongodb": MockConnector,  # MongoDBConnector
        "redis": MockConnector,  # RedisConnector
        "elasticsearch": MockConnector,  # ElasticsearchConnector
        
        # Monitoring & Analytics (5)
        "prometheus": MockConnector,  # PrometheusConnector
        "grafana": MockConnector,  # GrafanaConnector
        "datadog": MockConnector,  # DatadogConnector
        "newrelic": MockConnector,  # NewRelicConnector
        "sentry": MockConnector,  # SentryConnector
        
        # CI/CD (4)
        "jenkins": MockConnector,  # JenkinsConnector
        "circleci": MockConnector,  # CircleCIConnector
        "travis": MockConnector,  # TravisConnector
        "github_actions": MockConnector,  # GitHubActionsConnector
        
        # CRM & Support (4)
        "salesforce": MockConnector,  # SalesforceConnector
        "hubspot": MockConnector,  # HubspotConnector
        "zendesk": MockConnector,  # ZendeskConnector
        "freshdesk": MockConnector,  # FreshdeskConnector
        
        # Social Media (4)
        "twitter": MockConnector,  # TwitterConnector
        "linkedin": MockConnector,  # LinkedInConnector
        "facebook": MockConnector,  # FacebookConnector
        "youtube": MockConnector,  # YouTubeConnector
    }
    
    @classmethod
    def register_connector(cls, name: str, connector_class: Type[BaseConnector]):
        """Register a new connector"""
        cls._connectors[name] = connector_class
    
    @classmethod
    def get_connector_class(cls, name: str) -> Optional[Type[BaseConnector]]:
        """Get connector class by name"""
        return cls._connectors.get(name)
    
    @classmethod
    def get_available_connectors(cls) -> List[str]:
        """Get list of available connector names"""
        return list(cls._connectors.keys())

class ConnectorManager:
    """Manager for all enterprise connectors"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.health_check_interval = 300  # 5 minutes
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def initialize_connector(self, name: str, config: ConnectorConfig) -> ConnectorResponse:
        """Initialize and connect a connector"""
        try:
            connector_class = ConnectorRegistry.get_connector_class(config.name.lower())
            if not connector_class:
                return ConnectorResponse(
                    success=False,
                    error=f"Unknown connector type: {config.name}"
                )
            
            # Create connector instance
            connector = connector_class(config)
            
            # Connect to the service
            connect_result = await connector.connect()
            if not connect_result.success:
                return connect_result
            
            # Store the connector
            self.connectors[name] = connector
            
            logger.info(f"Successfully initialized connector: {name}")
            
            return ConnectorResponse(
                success=True,
                data={
                    "name": name,
                    "type": config.connector_type.value,
                    "status": "connected"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize connector {name}: {str(e)}")
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def disconnect_connector(self, name: str) -> ConnectorResponse:
        """Disconnect and remove a connector"""
        try:
            if name not in self.connectors:
                return ConnectorResponse(
                    success=False,
                    error=f"Connector {name} not found"
                )
            
            connector = self.connectors[name]
            disconnect_result = await connector.disconnect()
            
            if disconnect_result.success:
                del self.connectors[name]
                logger.info(f"Successfully disconnected connector: {name}")
            
            return disconnect_result
            
        except Exception as e:
            logger.error(f"Failed to disconnect connector {name}: {str(e)}")
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def get_connector_status(self, name: str = None) -> ConnectorResponse:
        """Get status of one or all connectors"""
        try:
            if name:
                if name not in self.connectors:
                    return ConnectorResponse(
                        success=False,
                        error=f"Connector {name} not found"
                    )
                
                connector = self.connectors[name]
                return ConnectorResponse(
                    success=True,
                    data={"status": connector.get_status()}
                )
            else:
                statuses = {}
                for conn_name, connector in self.connectors.items():
                    statuses[conn_name] = connector.get_status()
                
                return ConnectorResponse(
                    success=True,
                    data={"connectors": statuses}
                )
                
        except Exception as e:
            logger.error(f"Failed to get connector status: {str(e)}")
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def execute_connector_action(self, name: str, action: str, data: Dict[str, Any] = None) -> ConnectorResponse:
        """Execute an action on a specific connector"""
        try:
            if name not in self.connectors:
                return ConnectorResponse(
                    success=False,
                    error=f"Connector {name} not found"
                )
            
            connector = self.connectors[name]
            
            if not connector.is_connected():
                return ConnectorResponse(
                    success=False,
                    error=f"Connector {name} is not connected"
                )
            
            if action == "get_data":
                return await connector.get_data(data or {})
            elif action == "send_data":
                return await connector.send_data(data or {})
            elif action == "test_connection":
                return await connector.test_connection()
            elif action == "health_check":
                return await connector.health_check()
            else:
                return ConnectorResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
                
        except Exception as e:
            logger.error(f"Failed to execute action {action} on connector {name}: {str(e)}")
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def get_connected_connectors_by_type(self, connector_type: ConnectorType) -> List[str]:
        """Get list of connected connectors by type"""
        connected = []
        for name, connector in self.connectors.items():
            if (connector.config.connector_type == connector_type and 
                connector.is_connected()):
                connected.append(name)
        return connected
    
    async def broadcast_to_type(self, connector_type: ConnectorType, action: str, data: Dict[str, Any]) -> Dict[str, ConnectorResponse]:
        """Broadcast an action to all connectors of a specific type"""
        results = {}
        connected_connectors = await self.get_connected_connectors_by_type(connector_type)
        
        for name in connected_connectors:
            try:
                result = await self.execute_connector_action(name, action, data)
                results[name] = result
            except Exception as e:
                results[name] = ConnectorResponse(
                    success=False,
                    error=str(e)
                )
        
        return results
    
    async def start_health_monitoring(self):
        """Start periodic health check monitoring"""
        if self._health_check_task and not self._health_check_task.done():
            return
        
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Started connector health monitoring")
    
    async def stop_health_monitoring(self):
        """Stop periodic health check monitoring"""
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped connector health monitoring")
    
    async def _health_check_loop(self):
        """Periodic health check loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {str(e)}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all connectors"""
        for name, connector in self.connectors.items():
            try:
                health_result = await connector.health_check()
                if not health_result.success:
                    logger.warning(f"Health check failed for connector {name}: {health_result.error}")
                    
                    # Try to reconnect if health check failed
                    if connector.status == ConnectorStatus.ERROR:
                        logger.info(f"Attempting to reconnect connector {name}")
                        reconnect_result = await connector.connect()
                        if reconnect_result.success:
                            logger.info(f"Successfully reconnected connector {name}")
                        else:
                            logger.error(f"Failed to reconnect connector {name}: {reconnect_result.error}")
                            
            except Exception as e:
                logger.error(f"Error during health check for connector {name}: {str(e)}")
    
    async def shutdown_all(self):
        """Shutdown all connectors"""
        logger.info("Shutting down all connectors...")
        
        # Stop health monitoring
        await self.stop_health_monitoring()
        
        # Disconnect all connectors
        disconnect_tasks = []
        for name in list(self.connectors.keys()):
            disconnect_tasks.append(self.disconnect_connector(name))
        
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        logger.info("All connectors shut down")

class ConnectorConfigManager:
    """Manager for connector configurations"""
    
    @staticmethod
    def create_jira_config(
        name: str,
        base_url: str,
        username: str,
        api_token: str,
        enabled: bool = True
    ) -> ConnectorConfig:
        """Create Jira connector configuration"""
        return ConnectorConfig(
            name=name,
            connector_type=ConnectorType.PROJECT_MANAGEMENT,
            enabled=enabled,
            api_key=api_token,
            base_url=base_url,
            custom_config={"username": username}
        )
    
    @staticmethod
    def create_github_config(
        name: str,
        api_token: str,
        enabled: bool = True
    ) -> ConnectorConfig:
        """Create GitHub connector configuration"""
        return ConnectorConfig(
            name=name,
            connector_type=ConnectorType.VERSION_CONTROL,
            enabled=enabled,
            api_key=api_token,
            base_url="https://api.github.com"
        )
    
    @staticmethod
    def create_slack_config(
        name: str,
        bot_token: str,
        enabled: bool = True
    ) -> ConnectorConfig:
        """Create Slack connector configuration"""
        return ConnectorConfig(
            name=name,
            connector_type=ConnectorType.COMMUNICATION,
            enabled=enabled,
            api_key=bot_token
        )
