"""
Autonomous Agent Manager for DevPilot SDLC
Coordinates all agents throughout the SDLC process with LangGraph integration
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentRole
from .specialized_agents import (
    ProjectManagerAgent, BusinessAnalystAgent, SoftwareArchitectAgent,
    DeveloperAgent, SecurityExpertAgent, QAEngineerAgent, DevOpsEngineerAgent
)
from ..connectors.connector_manager import ConnectorManager, ConnectorConfigManager
from ..connectors.base_connector import ConnectorType, ConnectorConfig
from ..state.sdlc_state import SDLCState
import src.dev_pilot.utils.constants as const

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages all autonomous agents and their coordination"""
    
    def __init__(self, llm, connector_configs: Dict[str, Dict[str, Any]] = None):
        self.llm = llm
        self.connector_manager = ConnectorManager()
        self.agents: Dict[AgentRole, BaseAgent] = {}
        self.active_agents: List[BaseAgent] = []
        self.phase_agent_mapping = self._create_phase_mapping()
        
        # Initialize agents
        self._initialize_agents()
        
        # Initialize connectors if configs provided
        if connector_configs:
            asyncio.create_task(self._initialize_connectors(connector_configs))
    
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        self.agents = {
            AgentRole.PROJECT_MANAGER: ProjectManagerAgent(self.llm, self.connector_manager),
            AgentRole.BUSINESS_ANALYST: BusinessAnalystAgent(self.llm, self.connector_manager),
            AgentRole.SOFTWARE_ARCHITECT: SoftwareArchitectAgent(self.llm, self.connector_manager),
            AgentRole.DEVELOPER: DeveloperAgent(self.llm, self.connector_manager),
            AgentRole.SECURITY_EXPERT: SecurityExpertAgent(self.llm, self.connector_manager),
            AgentRole.QA_ENGINEER: QAEngineerAgent(self.llm, self.connector_manager),
            AgentRole.DEVOPS_ENGINEER: DevOpsEngineerAgent(self.llm, self.connector_manager)
        }
        
        # All agents are active by default
        self.active_agents = list(self.agents.values())
        
        logger.info(f"Initialized {len(self.agents)} autonomous agents")
    
    def _create_phase_mapping(self) -> Dict[str, List[AgentRole]]:
        """Map SDLC phases to responsible agents"""
        return {
            const.PROJECT_INITILIZATION: [AgentRole.PROJECT_MANAGER],
            const.REQUIREMENT_COLLECTION: [AgentRole.PROJECT_MANAGER, AgentRole.BUSINESS_ANALYST],
            const.GENERATE_USER_STORIES: [AgentRole.BUSINESS_ANALYST],
            const.CREATE_DESIGN_DOC: [AgentRole.SOFTWARE_ARCHITECT, AgentRole.BUSINESS_ANALYST],
            const.CODE_GENERATION: [AgentRole.DEVELOPER, AgentRole.SOFTWARE_ARCHITECT],
            const.SECURITY_REVIEW: [AgentRole.SECURITY_EXPERT, AgentRole.DEVELOPER],
            const.WRITE_TEST_CASES: [AgentRole.QA_ENGINEER, AgentRole.DEVELOPER],
            const.QA_TESTING: [AgentRole.QA_ENGINEER],
            const.DEPLOYMENT: [AgentRole.DEVOPS_ENGINEER, AgentRole.DEVELOPER],
        }
    
    async def _initialize_connectors(self, connector_configs: Dict[str, Dict[str, Any]]):
        """Initialize connectors based on configuration"""
        try:
            for connector_name, config in connector_configs.items():
                if config.get("enabled", False):
                    connector_config = self._create_connector_config(connector_name, config)
                    result = await self.connector_manager.initialize_connector(
                        connector_name, connector_config
                    )
                    if result.success:
                        logger.info(f"Successfully initialized connector: {connector_name}")
                    else:
                        logger.error(f"Failed to initialize connector {connector_name}: {result.error}")
        except Exception as e:
            logger.error(f"Error initializing connectors: {str(e)}")
    
    def _create_connector_config(self, name: str, config: Dict[str, Any]) -> ConnectorConfig:
        """Create connector configuration"""
        if name == "github":
            return ConnectorConfigManager.create_github_config(
                name, config["api_key"], config.get("enabled", True)
            )
        elif name == "jira":
            return ConnectorConfigManager.create_jira_config(
                name, config["base_url"], config["username"], 
                config["api_key"], config.get("enabled", True)
            )
        elif name == "slack":
            return ConnectorConfigManager.create_slack_config(
                name, config["api_key"], config.get("enabled", True)
            )
        else:
            return ConnectorConfig(
                name=name,
                connector_type=ConnectorType.PROJECT_MANAGEMENT,
                enabled=config.get("enabled", True),
                api_key=config.get("api_key"),
                base_url=config.get("base_url")
            )
    
    async def execute_phase(self, phase: str, state: SDLCState, context: Dict[str, Any] = None) -> SDLCState:
        """Execute autonomous work for a specific SDLC phase"""
        try:
            logger.info(f"Starting autonomous execution for phase: {phase}")
            
            # Get agents responsible for this phase
            responsible_agents = self._get_phase_agents(phase)
            
            if not responsible_agents:
                logger.warning(f"No agents assigned to phase: {phase}")
                return state
            
            # Execute agents in sequence with collaboration
            updated_state = state
            execution_results = {}
            
            for agent in responsible_agents:
                try:
                    logger.info(f"Agent {agent.name} starting autonomous work for {phase}")
                    
                    # Agent performs autonomous analysis and execution
                    updated_state = await agent.autonomous_work(updated_state, context or {})
                    
                    # Get collaboration insights from other agents
                    other_agents = [a for a in responsible_agents if a != agent]
                    if other_agents:
                        collaboration_results = await agent.collaborate(other_agents, updated_state)
                        execution_results[agent.name] = {
                            "completed": True,
                            "collaboration": collaboration_results
                        }
                    
                    logger.info(f"Agent {agent.name} completed work for {phase}")
                    
                except Exception as e:
                    logger.error(f"Agent {agent.name} failed in phase {phase}: {str(e)}")
                    execution_results[agent.name] = {
                        "completed": False,
                        "error": str(e)
                    }
            
            # Store execution results in state
            if "agent_execution_log" not in updated_state:
                updated_state["agent_execution_log"] = {}
            updated_state["agent_execution_log"][phase] = execution_results
            
            logger.info(f"Completed autonomous execution for phase: {phase}")
            return updated_state
            
        except Exception as e:
            logger.error(f"Error in autonomous phase execution {phase}: {str(e)}")
            raise
    
    def _get_phase_agents(self, phase: str) -> List[BaseAgent]:
        """Get active agents for a specific phase"""
        agent_roles = self.phase_agent_mapping.get(phase, [])
        return [self.agents[role] for role in agent_roles if role in self.agents and self.agents[role].active]
    
    async def coordinate_cross_phase_work(self, current_phase: str, next_phase: str, state: SDLCState) -> SDLCState:
        """Coordinate work between phases"""
        try:
            current_agents = self._get_phase_agents(current_phase)
            next_agents = self._get_phase_agents(next_phase)
            
            # Cross-phase collaboration
            coordination_results = {}
            
            for current_agent in current_agents:
                for next_agent in next_agents:
                    if current_agent.role != next_agent.role:
                        try:
                            # Current agent provides insights to next agent
                            handoff_context = {
                                "phase_transition": f"{current_phase} -> {next_phase}",
                                "previous_work": current_agent.get_memory_context(),
                                "recommendations": f"Insights from {current_agent.role.value}"
                            }
                            
                            coordination_results[f"{current_agent.name}_to_{next_agent.name}"] = handoff_context
                            
                        except Exception as e:
                            logger.warning(f"Cross-phase coordination failed: {str(e)}")
            
            # Store coordination results
            if "cross_phase_coordination" not in state:
                state["cross_phase_coordination"] = {}
            state["cross_phase_coordination"][f"{current_phase}_to_{next_phase}"] = coordination_results
            
            return state
            
        except Exception as e:
            logger.error(f"Error in cross-phase coordination: {str(e)}")
            return state
    
    async def get_autonomous_recommendations(self, state: SDLCState) -> Dict[str, Any]:
        """Get autonomous recommendations from all agents"""
        recommendations = {}
        
        for role, agent in self.agents.items():
            try:
                if agent.active and agent.memory:
                    latest_decision = agent.memory[-1]
                    recommendations[role.value] = {
                        "reasoning": latest_decision.reasoning,
                        "confidence": latest_decision.confidence,
                        "suggested_actions": len(latest_decision.actions),
                        "timestamp": latest_decision.timestamp.isoformat()
                    }
            except Exception as e:
                logger.warning(f"Failed to get recommendations from {role.value}: {str(e)}")
        
        return recommendations
    
    async def handle_feedback(self, phase: str, feedback: str, state: SDLCState) -> SDLCState:
        """Handle feedback and trigger agent adaptations"""
        try:
            responsible_agents = self._get_phase_agents(phase)
            
            for agent in responsible_agents:
                # Agent analyzes feedback and adapts
                feedback_context = {
                    "feedback": feedback,
                    "phase": phase,
                    "adaptation_required": True
                }
                
                adapted_state = await agent.autonomous_work(state, feedback_context)
                state.update(adapted_state)
            
            return state
            
        except Exception as e:
            logger.error(f"Error handling feedback: {str(e)}")
            return state
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {}
        
        for role, agent in self.agents.items():
            status[role.value] = {
                "active": agent.active,
                "decisions_made": len(agent.memory),
                "capabilities": agent.capabilities,
                "last_activity": agent.memory[-1].timestamp.isoformat() if agent.memory else None
            }
        
        return status
    
    async def shutdown(self):
        """Shutdown agent manager and all connectors"""
        try:
            # Deactivate all agents
            for agent in self.agents.values():
                agent.active = False
            
            # Shutdown connector manager
            await self.connector_manager.shutdown_all()
            
            logger.info("Agent manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def get_execution_summary(self, state: SDLCState) -> Dict[str, Any]:
        """Get summary of autonomous execution"""
        execution_log = state.get("agent_execution_log", {})
        coordination_log = state.get("cross_phase_coordination", {})
        
        total_agents_executed = sum(
            len(phase_results) for phase_results in execution_log.values()
        )
        
        successful_executions = sum(
            sum(1 for result in phase_results.values() if result.get("completed", False))
            for phase_results in execution_log.values()
        )
        
        return {
            "total_phases_executed": len(execution_log),
            "total_agents_executed": total_agents_executed,
            "successful_executions": successful_executions,
            "success_rate": successful_executions / total_agents_executed if total_agents_executed > 0 else 0,
            "cross_phase_coordinations": len(coordination_log),
            "active_agents": len([a for a in self.agents.values() if a.active]),
            "agent_status": self.get_agent_status()
        }
