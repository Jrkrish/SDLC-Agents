"""
Enhanced Graph Builder with Connector Integration
Extends the basic graph builder to include connector-aware nodes
"""

from typing import Dict, Any, Optional
import asyncio
from loguru import logger

from .graph_builder import GraphBuilder
from ..nodes.enhanced_coding_node import EnhancedCodingNode
from ..connectors.connector_manager import ConnectorManager
from ..connectors.agent_connector_bridge import WorkflowIntegration
from ..connectors.base_connector import ConnectorConfig, ConnectorType

class EnhancedGraphBuilder(GraphBuilder):
    """Enhanced graph builder with connector integration"""
    
    def __init__(self, model=None, enable_connectors: bool = True, connector_configs: Dict[str, ConnectorConfig] = None):
        super().__init__(model)
        self.enable_connectors = enable_connectors
        self.connector_manager = None
        self.connector_configs = connector_configs or {}
        
        if enable_connectors:
            self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize connector manager and connectors"""
        try:
            self.connector_manager = ConnectorManager()
            
            # Add default connectors if configurations are provided
            if self.connector_configs:
                self._setup_configured_connectors()
            else:
                self._setup_mock_connectors()
            
            logger.info("Connector system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize connectors: {str(e)}")
            self.enable_connectors = False
    
    def _setup_configured_connectors(self):
        """Setup connectors with provided configurations"""
        for name, config in self.connector_configs.items():
            try:
                self.connector_manager.register_connector(name, config)
                logger.info(f"Registered connector: {name}")
            except Exception as e:
                logger.warning(f"Failed to register connector {name}: {str(e)}")
    
    def _setup_mock_connectors(self):
        """Setup mock connectors for demonstration"""
        mock_configs = {
            "github": ConnectorConfig(
                name="github",
                connector_type=ConnectorType.PROJECT_MANAGEMENT,
                enabled=False,  # Disabled by default - requires API key
                custom_config={"mock": True}
            ),
            "slack": ConnectorConfig(
                name="slack", 
                connector_type=ConnectorType.COMMUNICATION,
                enabled=False,  # Disabled by default - requires API key
                custom_config={"mock": True}
            ),
            "jira": ConnectorConfig(
                name="jira",
                connector_type=ConnectorType.PROJECT_MANAGEMENT,
                enabled=False,  # Disabled by default - requires API key
                custom_config={"mock": True}
            )
        }
        
        for name, config in mock_configs.items():
            try:
                self.connector_manager.register_connector(name, config)
            except Exception as e:
                logger.warning(f"Failed to register mock connector {name}: {str(e)}")
    
    def setup_graph(self):
        """Enhanced graph setup with connector-aware nodes"""
        logger.info("Setting up enhanced graph with connector integration")
        
        # Call parent setup
        graph = super().setup_graph()
        
        if self.enable_connectors and self.connector_manager:
            # Replace coding node with enhanced version
            self._enhance_coding_node()
            
            # Add connector status monitoring
            self._add_connector_monitoring()
        
        return graph
    
    def _enhance_coding_node(self):
        """Replace coding node with enhanced connector-aware version"""
        try:
            # Create enhanced coding node
            enhanced_coding_node = EnhancedCodingNode(self.model, self.connector_manager)
            
            # Replace in workflow builder if available
            if hasattr(self, 'workflow_builder'):
                self.workflow_builder.coding_node = enhanced_coding_node
            
            logger.info("Enhanced coding node with connectors integrated")
        except Exception as e:
            logger.error(f"Failed to enhance coding node: {str(e)}")
    
    def _add_connector_monitoring(self):
        """Add connector health monitoring to the graph"""
        try:
            # This could be expanded to add monitoring nodes
            # For now, just log the status
            connected_count = len([c for c in self.connector_manager.connectors.values() 
                                 if c.is_connected()])
            total_count = len(self.connector_manager.connectors)
            
            logger.info(f"Connector status: {connected_count}/{total_count} connected")
        except Exception as e:
            logger.error(f"Error in connector monitoring: {str(e)}")
    
    async def connect_all_connectors(self) -> Dict[str, Any]:
        """Connect all configured connectors"""
        if not self.connector_manager:
            return {"status": "error", "message": "Connector manager not initialized"}
        
        results = {}
        
        for name, connector in self.connector_manager.connectors.items():
            if connector.config.enabled:
                try:
                    result = await connector.connect()
                    results[name] = {
                        "success": result.success,
                        "error": result.error,
                        "connected": connector.is_connected()
                    }
                except Exception as e:
                    results[name] = {
                        "success": False,
                        "error": str(e),
                        "connected": False
                    }
        
        return {
            "status": "completed",
            "results": results,
            "connected_count": len([r for r in results.values() if r["connected"]]),
            "total_count": len(results)
        }
    
    async def test_connector_integrations(self) -> Dict[str, Any]:
        """Test all connector integrations"""
        if not self.connector_manager:
            return {"status": "error", "message": "No connectors available"}
        
        test_results = {}
        
        for name, connector in self.connector_manager.connectors.items():
            if connector.is_connected():
                try:
                    health_check = await connector.health_check()
                    test_results[name] = {
                        "status": "healthy" if health_check.success else "unhealthy",
                        "error": health_check.error,
                        "data": health_check.data
                    }
                except Exception as e:
                    test_results[name] = {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                test_results[name] = {
                    "status": "disconnected"
                }
        
        return {
            "test_results": test_results,
            "healthy_count": len([r for r in test_results.values() if r["status"] == "healthy"]),
            "total_tested": len(test_results)
        }
    
    def get_connector_status(self) -> Dict[str, Any]:
        """Get comprehensive connector status"""
        if not self.connector_manager:
            return {
                "enabled": False,
                "message": "Connector system not enabled"
            }
        
        status = {
            "enabled": True,
            "connectors": {},
            "summary": {
                "total": 0,
                "connected": 0,
                "enabled": 0,
                "disabled": 0
            }
        }
        
        for name, connector in self.connector_manager.connectors.items():
            connector_status = connector.get_status()
            status["connectors"][name] = connector_status
            
            # Update summary
            status["summary"]["total"] += 1
            if connector_status["status"] == "connected":
                status["summary"]["connected"] += 1
            if connector_status["enabled"]:
                status["summary"]["enabled"] += 1
            else:
                status["summary"]["disabled"] += 1
        
        return status
    
    def enable_connector(self, connector_name: str, config: ConnectorConfig) -> bool:
        """Enable a specific connector"""
        if not self.connector_manager:
            logger.error("Connector manager not initialized")
            return False
        
        try:
            self.connector_manager.register_connector(connector_name, config)
            logger.info(f"Connector {connector_name} enabled successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to enable connector {connector_name}: {str(e)}")
            return False
    
    def disable_connector(self, connector_name: str) -> bool:
        """Disable a specific connector"""
        if not self.connector_manager:
            return False
        
        try:
            connector = self.connector_manager.get_connector(connector_name)
            if connector:
                connector.config.enabled = False
                asyncio.create_task(connector.disconnect())
            logger.info(f"Connector {connector_name} disabled")
            return True
        except Exception as e:
            logger.error(f"Failed to disable connector {connector_name}: {str(e)}")
            return False
    
    def get_integration_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for connector integrations"""
        recommendations = {
            "github": {
                "priority": "high",
                "benefits": [
                    "Automatic repository creation",
                    "Code commit automation", 
                    "Issue tracking integration",
                    "Release management"
                ],
                "requirements": ["GitHub API token", "Repository permissions"]
            },
            "slack": {
                "priority": "medium", 
                "benefits": [
                    "Real-time workflow notifications",
                    "Team collaboration",
                    "Error alerts",
                    "Progress tracking"
                ],
                "requirements": ["Slack workspace", "Bot token", "Channel permissions"]
            },
            "jira": {
                "priority": "medium",
                "benefits": [
                    "User story tracking",
                    "Sprint management", 
                    "Issue workflow automation",
                    "Progress reporting"
                ],
                "requirements": ["JIRA instance", "API credentials", "Project permissions"]
            },
            "aws_s3": {
                "priority": "low",
                "benefits": [
                    "Artifact storage",
                    "Backup automation",
                    "Version control for artifacts",
                    "Scalable storage"
                ],
                "requirements": ["AWS account", "S3 bucket", "IAM credentials"]
            }
        }
        
        return {
            "recommendations": recommendations,
            "next_steps": [
                "Configure high-priority connectors first",
                "Test connections before enabling automation",
                "Set up monitoring for connector health",
                "Configure team notification preferences"
            ]
        }
