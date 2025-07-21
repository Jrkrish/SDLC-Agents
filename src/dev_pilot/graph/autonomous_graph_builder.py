"""
Enhanced Autonomous Graph Builder with Agent Integration
Combines LangGraph with autonomous agents for complete SDLC automation
"""

import asyncio
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables.graph import MermaidDrawMethod

from ..state.sdlc_state import SDLCState
from ..agents.agent_manager import AgentManager
from ..nodes.autonomous_nodes import AutonomousProjectNode, AutonomousDesignNode, AutonomousCodingNode, AutonomousArtifactsNode
import src.dev_pilot.utils.constants as const
import logging

logger = logging.getLogger(__name__)

class AutonomousGraphBuilder:
    """Enhanced graph builder with autonomous agent integration"""
    
    def __init__(self, llm, connector_configs: Dict[str, Dict[str, Any]] = None):
        self.llm = llm
        self.connector_configs = connector_configs or {}
        self.graph_builder = StateGraph(SDLCState)
        self.memory = MemorySaver()
        
        # Initialize agent manager
        self.agent_manager = AgentManager(self.llm, self.connector_configs)
        
        # Initialize autonomous nodes with agent manager
        self.project_node = AutonomousProjectNode(self.llm, self.agent_manager)
        self.design_node = AutonomousDesignNode(self.llm, self.agent_manager)
        self.coding_node = AutonomousCodingNode(self.llm, self.agent_manager)
        self.artifacts_node = AutonomousArtifactsNode(self.llm, self.agent_manager)
    
    def build_autonomous_sdlc_graph(self):
        """Build the complete autonomous SDLC graph"""
        
        # Add all nodes with autonomous capabilities
        self._add_project_nodes()
        self._add_design_nodes()
        self._add_coding_nodes()
        self._add_testing_nodes()
        self._add_deployment_nodes()
        self._add_artifacts_nodes()
        
        # Add edges with autonomous routing
        self._add_autonomous_edges()
        
        logger.info("Built complete autonomous SDLC graph with agent integration")
    
    def _add_project_nodes(self):
        """Add project initialization and requirements nodes"""
        self.graph_builder.add_node("initialize_project", self.project_node.initialize_project)
        self.graph_builder.add_node("get_user_requirements", self.project_node.get_user_requirements)
        self.graph_builder.add_node("generate_user_stories", self.project_node.generate_user_stories)
        self.graph_builder.add_node("review_user_stories", self.project_node.review_user_stories)
        self.graph_builder.add_node("revise_user_stories", self.project_node.revise_user_stories)
    
    def _add_design_nodes(self):
        """Add design document nodes"""
        self.graph_builder.add_node("create_design_documents", self.design_node.create_design_documents)
        self.graph_builder.add_node("review_design_documents", self.design_node.review_design_documents)
        self.graph_builder.add_node("revise_design_documents", self.design_node.revise_design_documents)
    
    def _add_coding_nodes(self):
        """Add coding and security nodes"""
        self.graph_builder.add_node("generate_code", self.coding_node.generate_code)
        self.graph_builder.add_node("code_review", self.coding_node.code_review)
        self.graph_builder.add_node("fix_code", self.coding_node.fix_code)
        
        self.graph_builder.add_node("security_review_recommendations", self.coding_node.security_review_recommendations)
        self.graph_builder.add_node("security_review", self.coding_node.security_review)
        self.graph_builder.add_node("fix_code_after_security_review", self.coding_node.fix_code_after_security_review)
    
    def _add_testing_nodes(self):
        """Add testing nodes"""
        self.graph_builder.add_node("write_test_cases", self.coding_node.write_test_cases)
        self.graph_builder.add_node("review_test_cases", self.coding_node.review_test_cases)
        self.graph_builder.add_node("revise_test_cases", self.coding_node.revise_test_cases)
        
        self.graph_builder.add_node("qa_testing", self.coding_node.qa_testing)
        self.graph_builder.add_node("qa_review", self.coding_node.qa_review)
    
    def _add_deployment_nodes(self):
        """Add deployment nodes"""
        self.graph_builder.add_node("deployment", self.coding_node.deployment)
    
    def _add_artifacts_nodes(self):
        """Add artifacts generation node"""
        self.graph_builder.add_node("download_artifacts", self.artifacts_node.generate_artifacts)
    
    def _add_autonomous_edges(self):
        """Add edges with autonomous decision making"""
        
        # Start with project initialization
        self.graph_builder.add_edge(START, "initialize_project")
        self.graph_builder.add_edge("initialize_project", "get_user_requirements")
        self.graph_builder.add_edge("get_user_requirements", "generate_user_stories")
        self.graph_builder.add_edge("generate_user_stories", "review_user_stories")
        
        # User stories review flow with autonomous decisions
        self.graph_builder.add_conditional_edges(
            "review_user_stories",
            self.project_node.autonomous_user_stories_router,
            {
                "approved": "create_design_documents",
                "feedback": "revise_user_stories",
                "autonomous_approve": "create_design_documents"  # Agent can auto-approve
            }
        )
        self.graph_builder.add_edge("revise_user_stories", "generate_user_stories")
        
        # Design documents flow with autonomous decisions
        self.graph_builder.add_edge("create_design_documents", "review_design_documents")
        self.graph_builder.add_conditional_edges(
            "review_design_documents",
            self.design_node.autonomous_design_documents_router,
            {
                "approved": "generate_code",
                "feedback": "revise_design_documents",
                "autonomous_approve": "generate_code"
            }
        )
        self.graph_builder.add_edge("revise_design_documents", "create_design_documents")
        
        # Code generation flow with autonomous decisions
        self.graph_builder.add_edge("generate_code", "code_review")
        self.graph_builder.add_conditional_edges(
            "code_review",
            self.coding_node.autonomous_code_review_router,
            {
                "approved": "security_review_recommendations",
                "feedback": "fix_code",
                "autonomous_approve": "security_review_recommendations"
            }
        )
        self.graph_builder.add_edge("fix_code", "generate_code")
        
        # Security review flow with autonomous decisions
        self.graph_builder.add_edge("security_review_recommendations", "security_review")
        self.graph_builder.add_conditional_edges(
            "security_review",
            self.coding_node.autonomous_security_review_router,
            {
                "approved": "write_test_cases",
                "feedback": "fix_code_after_security_review",
                "autonomous_approve": "write_test_cases"
            }
        )
        self.graph_builder.add_edge("fix_code_after_security_review", "generate_code")
        
        # Testing flow with autonomous decisions
        self.graph_builder.add_edge("write_test_cases", "review_test_cases")
        self.graph_builder.add_conditional_edges(
            "review_test_cases",
            self.coding_node.autonomous_test_cases_router,
            {
                "approved": "qa_testing",
                "feedback": "revise_test_cases",
                "autonomous_approve": "qa_testing"
            }
        )
        self.graph_builder.add_edge("revise_test_cases", "write_test_cases")
        
        # QA testing flow with autonomous decisions
        self.graph_builder.add_edge("qa_testing", "qa_review")
        self.graph_builder.add_conditional_edges(
            "qa_review",
            self.coding_node.autonomous_qa_review_router,
            {
                "approved": "deployment",
                "feedback": "generate_code",
                "autonomous_approve": "deployment"
            }
        )
        
        # Deployment and completion
        self.graph_builder.add_edge("deployment", "download_artifacts")
        self.graph_builder.add_edge("download_artifacts", END)
    
    def setup_autonomous_graph(self):
        """Setup the complete autonomous graph with interrupts for manual override"""
        
        self.build_autonomous_sdlc_graph()
        
        # Create graph with autonomous capabilities but allow manual interrupts
        graph = self.graph_builder.compile(
            interrupt_before=[
                # Optional manual checkpoints - agents can bypass these
                'get_user_requirements',
                'review_user_stories', 
                'review_design_documents',
                'code_review',
                'security_review',
                'review_test_cases',
                'qa_review'
            ],
            checkpointer=self.memory
        )
        
        # Save graph visualization
        self.save_autonomous_graph_image(graph)
        
        return graph
    
    def setup_fully_autonomous_graph(self):
        """Setup completely autonomous graph with no manual interrupts"""
        
        self.build_autonomous_sdlc_graph()
        
        # Create fully autonomous graph
        graph = self.graph_builder.compile(checkpointer=self.memory)
        
        logger.info("Created fully autonomous SDLC graph - no manual intervention required")
        
        return graph
    
    def save_autonomous_graph_image(self, graph):
        """Save autonomous graph visualization"""
        try:
            img_data = graph.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API
            )
            
            graph_path = "autonomous_workflow_graph.png"
            with open(graph_path, "wb") as f:
                f.write(img_data)
            
            logger.info(f"Saved autonomous graph visualization to {graph_path}")
            
        except Exception as e:
            logger.warning(f"Could not save graph image: {str(e)}")
    
    async def get_autonomous_insights(self, state: SDLCState) -> Dict[str, Any]:
        """Get insights from autonomous agents"""
        try:
            recommendations = await self.agent_manager.get_autonomous_recommendations(state)
            execution_summary = self.agent_manager.get_execution_summary(state)
            agent_status = self.agent_manager.get_agent_status()
            
            return {
                "autonomous_recommendations": recommendations,
                "execution_summary": execution_summary,
                "agent_status": agent_status,
                "connector_health": await self._get_connector_health()
            }
        except Exception as e:
            logger.error(f"Error getting autonomous insights: {str(e)}")
            return {}
    
    async def _get_connector_health(self) -> Dict[str, Any]:
        """Get health status of all connectors"""
        try:
            result = await self.agent_manager.connector_manager.get_connector_status()
            return result.data if result.success else {"error": result.error}
        except Exception as e:
            return {"error": str(e)}
    
    async def shutdown(self):
        """Shutdown autonomous graph and agent manager"""
        await self.agent_manager.shutdown()
        logger.info("Autonomous graph builder shut down")
