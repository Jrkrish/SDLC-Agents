"""
Base autonomous agent class for DevPilot SDLC system
Implements vibeocoder-like intelligence for autonomous decision making
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pydantic import BaseModel, Field

from ..connectors.connector_manager import ConnectorManager
from ..connectors.base_connector import ConnectorType
from ..state.sdlc_state import SDLCState

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Enum for different agent roles"""
    PROJECT_MANAGER = "project_manager"
    BUSINESS_ANALYST = "business_analyst"
    SOFTWARE_ARCHITECT = "software_architect"
    DEVELOPER = "developer"
    SECURITY_EXPERT = "security_expert"
    QA_ENGINEER = "qa_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    PRODUCT_OWNER = "product_owner"

class AgentAction(BaseModel):
    """Represents an action taken by an agent"""
    action_type: str
    target: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    connector_involved: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)
    estimated_duration: Optional[int] = None  # in minutes
    dependencies: List[str] = Field(default_factory=list)

class AgentDecision(BaseModel):
    """Represents a decision made by an agent"""
    decision_id: str
    agent_role: AgentRole
    context: Dict[str, Any]
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    actions: List[AgentAction]
    timestamp: datetime = Field(default_factory=datetime.now)

class BaseAgent(ABC):
    """Base class for all autonomous agents"""
    
    def __init__(self, 
                 role: AgentRole,
                 llm,
                 connector_manager: ConnectorManager,
                 name: str = None):
        self.role = role
        self.name = name or f"{role.value}_agent"
        self.llm = llm
        self.connector_manager = connector_manager
        self.memory: List[AgentDecision] = []
        self.active = True
        self.capabilities: List[str] = []
        
    @abstractmethod
    async def analyze(self, state: SDLCState, context: Dict[str, Any]) -> AgentDecision:
        """Analyze the current state and make decisions"""
        pass
    
    @abstractmethod
    async def execute_action(self, action: AgentAction, state: SDLCState) -> Dict[str, Any]:
        """Execute a specific action"""
        pass
    
    async def autonomous_work(self, state: SDLCState, context: Dict[str, Any] = None) -> SDLCState:
        """Perform autonomous work on the current state"""
        try:
            # Analyze current situation
            decision = await self.analyze(state, context or {})
            
            # Store decision in memory
            self.memory.append(decision)
            
            # Execute actions
            results = {}
            for action in decision.actions:
                try:
                    result = await self.execute_action(action, state)
                    results[action.action_type] = result
                    
                    # Update state if action modifies it
                    if 'updated_state' in result:
                        state.update(result['updated_state'])
                        
                except Exception as e:
                    logger.error(f"Action {action.action_type} failed: {str(e)}")
                    results[action.action_type] = {"error": str(e)}
            
            # Store execution results
            decision.context['execution_results'] = results
            
            return state
            
        except Exception as e:
            logger.error(f"Agent {self.name} autonomous work failed: {str(e)}")
            raise
    
    async def collaborate(self, other_agents: List['BaseAgent'], state: SDLCState) -> Dict[str, Any]:
        """Collaborate with other agents"""
        collaboration_results = {}
        
        for agent in other_agents:
            if agent.role != self.role and agent.active:
                try:
                    # Get other agent's perspective
                    other_decision = await agent.analyze(state, {"collaborating_with": self.role})
                    
                    # Find common actions or complementary capabilities
                    synergies = self._find_synergies(other_decision)
                    collaboration_results[agent.name] = {
                        "synergies": synergies,
                        "decision": other_decision
                    }
                    
                except Exception as e:
                    logger.warning(f"Collaboration with {agent.name} failed: {str(e)}")
        
        return collaboration_results
    
    def _find_synergies(self, other_decision: AgentDecision) -> List[str]:
        """Find potential synergies with another agent's decision"""
        synergies = []
        
        # Simple synergy detection based on action types
        my_latest_decision = self.memory[-1] if self.memory else None
        if my_latest_decision:
            my_actions = {action.action_type for action in my_latest_decision.actions}
            other_actions = {action.action_type for action in other_decision.actions}
            
            # Find complementary actions
            common_actions = my_actions.intersection(other_actions)
            if common_actions:
                synergies.append(f"Common actions: {', '.join(common_actions)}")
        
        return synergies
    
    async def get_connector_insights(self, connector_types: List[ConnectorType]) -> Dict[str, Any]:
        """Get insights from connected external systems"""
        insights = {}
        
        for conn_type in connector_types:
            connected_connectors = await self.connector_manager.get_connected_connectors_by_type(conn_type)
            
            for connector_name in connected_connectors:
                try:
                    # Get relevant data from connector
                    result = await self.connector_manager.execute_connector_action(
                        connector_name, 
                        "get_data",
                        self._get_connector_query(conn_type)
                    )
                    
                    if result.success:
                        insights[connector_name] = result.data
                    
                except Exception as e:
                    logger.warning(f"Failed to get insights from {connector_name}: {str(e)}")
        
        return insights
    
    def _get_connector_query(self, conn_type: ConnectorType) -> Dict[str, Any]:
        """Get appropriate query parameters for connector type"""
        queries = {
            ConnectorType.PROJECT_MANAGEMENT: {"action": "get_issues"},
            ConnectorType.VERSION_CONTROL: {"action": "get_repositories"},
            ConnectorType.COMMUNICATION: {"action": "get_channels"},
            ConnectorType.DATABASE: {"action": "get_metrics"},
            ConnectorType.MONITORING: {"action": "get_health_status"}
        }
        return queries.get(conn_type, {"action": "get_data"})
    
    async def notify_progress(self, message: str, details: Dict[str, Any] = None):
        """Notify stakeholders about progress"""
        try:
            # Send notifications via Slack if available
            comm_connectors = await self.connector_manager.get_connected_connectors_by_type(
                ConnectorType.COMMUNICATION
            )
            
            for connector_name in comm_connectors:
                await self.connector_manager.execute_connector_action(
                    connector_name,
                    "send_data",
                    {
                        "action": "send_message",
                        "channel": "general",  # Should be configurable
                        "text": f"🤖 {self.role.value}: {message}",
                        "details": details
                    }
                )
                
        except Exception as e:
            logger.warning(f"Failed to send progress notification: {str(e)}")
    
    def get_memory_context(self, limit: int = 5) -> Dict[str, Any]:
        """Get recent memory context for decision making"""
        recent_decisions = self.memory[-limit:] if self.memory else []
        
        return {
            "recent_decisions": [
                {
                    "decision_id": d.decision_id,
                    "reasoning": d.reasoning,
                    "confidence": d.confidence,
                    "actions_taken": len(d.actions),
                    "timestamp": d.timestamp
                }
                for d in recent_decisions
            ],
            "total_decisions": len(self.memory),
            "capabilities": self.capabilities
        }
