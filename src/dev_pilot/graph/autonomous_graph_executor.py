"""
Enhanced Autonomous Graph Executor
Handles execution of autonomous SDLC workflows with agent integration
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..state.sdlc_state import SDLCState
from ..cache.redis_cache import flush_redis_cache, save_state_to_redis, get_state_from_redis
from .autonomous_graph_builder import AutonomousGraphBuilder
import src.dev_pilot.utils.constants as const

logger = logging.getLogger(__name__)

class AutonomousGraphExecutor:
    """Executes autonomous SDLC workflows with full agent integration"""
    
    def __init__(self, llm, connector_configs: Dict[str, Dict[str, Any]] = None):
        self.llm = llm
        self.connector_configs = connector_configs or {}
        
        # Initialize autonomous graph builder
        self.graph_builder = AutonomousGraphBuilder(llm, connector_configs)
        
        # Initialize graphs
        self.autonomous_graph = None
        self.fully_autonomous_graph = None
        
        # Setup graphs
        self._setup_graphs()
    
    def _setup_graphs(self):
        """Setup both autonomous graph variants"""
        try:
            # Graph with manual override capabilities
            self.autonomous_graph = self.graph_builder.setup_autonomous_graph()
            
            # Fully autonomous graph (no interrupts)
            self.fully_autonomous_graph = self.graph_builder.setup_fully_autonomous_graph()
            
            logger.info("Autonomous graphs setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup autonomous graphs: {str(e)}")
            raise
    
    def get_thread(self, task_id: str) -> Dict[str, Any]:
        """Get thread configuration for graph execution"""
        return {"configurable": {"thread_id": task_id}}
    
    async def start_autonomous_workflow(self, project_name: str, fully_autonomous: bool = False) -> Dict[str, Any]:
        """Start autonomous SDLC workflow"""
        try:
            logger.info(f"Starting autonomous workflow for project: {project_name}")
            
            # Clear cache for new workflow
            flush_redis_cache()
            
            # Generate unique task ID
            task_id = f"autonomous-sdlc-{uuid.uuid4().hex[:8]}"
            thread = self.get_thread(task_id)
            
            # Choose graph based on autonomy level
            graph = self.fully_autonomous_graph if fully_autonomous else self.autonomous_graph
            
            # Initial state
            initial_state = {
                "project_name": project_name,
                "autonomous_mode": fully_autonomous,
                "started_at": datetime.now().isoformat(),
                "next_node": const.PROJECT_INITILIZATION
            }
            
            # Execute initial phase
            state = None
            for event in graph.stream(initial_state, thread, stream_mode="values"):
                state = event
                logger.debug(f"Autonomous workflow event: {event.get('next_node', 'unknown')}")
            
            # Save current state
            current_state = graph.get_state(thread)
            save_state_to_redis(task_id, current_state)
            
            # Get autonomous insights
            insights = await self.graph_builder.get_autonomous_insights(state)
            
            return {
                "task_id": task_id,
                "state": state,
                "autonomous_insights": insights,
                "fully_autonomous": fully_autonomous,
                "status": "initialized"
            }
            
        except Exception as e:
            logger.error(f"Failed to start autonomous workflow: {str(e)}")
            raise
    
    async def continue_autonomous_workflow(self, task_id: str, user_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """Continue autonomous workflow execution"""
        try:
            logger.info(f"Continuing autonomous workflow: {task_id}")
            
            # Get saved state
            saved_state = get_state_from_redis(task_id)
            if not saved_state:
                raise ValueError(f"No saved state found for task_id: {task_id}")
            
            # Determine if fully autonomous
            fully_autonomous = saved_state.get("autonomous_mode", False)
            graph = self.fully_autonomous_graph if fully_autonomous else self.autonomous_graph
            
            thread = self.get_thread(task_id)
            
            # Update state with user input if provided
            if user_input:
                saved_state.update(user_input)
                graph.update_state(thread, saved_state, as_node="get_user_requirements")
            
            # Continue execution
            state = None
            for event in graph.stream(None, thread, stream_mode="values"):
                state = event
                logger.debug(f"Autonomous workflow continue event: {event.get('next_node', 'unknown')}")
            
            # Save updated state
            current_state = graph.get_state(thread)
            save_state_to_redis(task_id, current_state)
            
            # Get updated insights
            insights = await self.graph_builder.get_autonomous_insights(state)
            
            return {
                "task_id": task_id,
                "state": state,
                "autonomous_insights": insights,
                "status": "continued"
            }
            
        except Exception as e:
            logger.error(f"Failed to continue autonomous workflow: {str(e)}")
            raise
    
    async def handle_autonomous_feedback(self, task_id: str, feedback: str, review_type: str) -> Dict[str, Any]:
        """Handle feedback in autonomous workflow"""
        try:
            logger.info(f"Handling autonomous feedback for {task_id}, type: {review_type}")
            
            saved_state = get_state_from_redis(task_id)
            if not saved_state:
                raise ValueError(f"No saved state found for task_id: {task_id}")
            
            # Use agent manager to handle feedback
            agent_manager = self.graph_builder.agent_manager
            updated_state = await agent_manager.handle_feedback(review_type, feedback, saved_state)
            
            # Determine graph and continue execution
            fully_autonomous = saved_state.get("autonomous_mode", False)
            graph = self.fully_autonomous_graph if fully_autonomous else self.autonomous_graph
            thread = self.get_thread(task_id)
            
            # Update feedback in state
            if review_type == const.REVIEW_USER_STORIES:
                updated_state['user_stories_review_status'] = "feedback"
                updated_state['user_stories_feedback'] = feedback
                node_name = "review_user_stories"
                updated_state['next_node'] = const.REVIEW_USER_STORIES
                
            elif review_type == const.REVIEW_DESIGN_DOCUMENTS:
                updated_state['design_documents_review_status'] = "feedback"
                updated_state['design_documents_feedback'] = feedback
                node_name = "review_design_documents"
                updated_state['next_node'] = const.REVIEW_DESIGN_DOCUMENTS
                
            elif review_type == const.REVIEW_CODE:
                updated_state['code_review_status'] = "feedback"
                updated_state['code_review_feedback'] = feedback
                node_name = "code_review"
                updated_state['next_node'] = const.REVIEW_CODE
                
            elif review_type == const.REVIEW_SECURITY_RECOMMENDATIONS:
                updated_state['security_review_status'] = "feedback"
                updated_state['security_review_comments'] = feedback
                node_name = "security_review"
                updated_state['next_node'] = const.REVIEW_SECURITY_RECOMMENDATIONS
                
            elif review_type == const.REVIEW_TEST_CASES:
                updated_state['test_case_review_status'] = "feedback"
                updated_state['test_case_review_feedback'] = feedback
                node_name = "review_test_cases"
                updated_state['next_node'] = const.REVIEW_TEST_CASES
                
            elif review_type == const.REVIEW_QA_TESTING:
                updated_state['qa_testing_status'] = "feedback"
                updated_state['qa_testing_feedback'] = feedback
                node_name = "qa_review"
                updated_state['next_node'] = const.REVIEW_QA_TESTING
            
            # Update graph state and continue
            graph.update_state(thread, updated_state, as_node=node_name)
            
            # Continue execution
            state = None
            for event in graph.stream(None, thread, stream_mode="values"):
                state = event
            
            # Save state
            current_state = graph.get_state(thread)
            save_state_to_redis(task_id, current_state)
            
            return {
                "task_id": task_id,
                "state": state,
                "feedback_processed": True,
                "status": "feedback_handled"
            }
            
        except Exception as e:
            logger.error(f"Failed to handle autonomous feedback: {str(e)}")
            raise
    
    async def approve_autonomous_stage(self, task_id: str, review_type: str) -> Dict[str, Any]:
        """Approve a stage in autonomous workflow"""
        try:
            logger.info(f"Approving autonomous stage: {review_type} for {task_id}")
            
            saved_state = get_state_from_redis(task_id)
            if not saved_state:
                raise ValueError(f"No saved state found for task_id: {task_id}")
            
            fully_autonomous = saved_state.get("autonomous_mode", False)
            graph = self.fully_autonomous_graph if fully_autonomous else self.autonomous_graph
            thread = self.get_thread(task_id)
            
            # Set approval status
            if review_type == const.REVIEW_USER_STORIES:
                saved_state['user_stories_review_status'] = "approved"
                node_name = "review_user_stories"
                saved_state['next_node'] = const.CREATE_DESIGN_DOC
                
            elif review_type == const.REVIEW_DESIGN_DOCUMENTS:
                saved_state['design_documents_review_status'] = "approved"
                node_name = "review_design_documents"
                saved_state['next_node'] = const.CODE_GENERATION
                
            elif review_type == const.REVIEW_CODE:
                saved_state['code_review_status'] = "approved"
                node_name = "code_review"
                saved_state['next_node'] = const.SECURITY_REVIEW
                
            elif review_type == const.REVIEW_SECURITY_RECOMMENDATIONS:
                saved_state['security_review_status'] = "approved"
                node_name = "security_review"
                saved_state['next_node'] = const.WRITE_TEST_CASES
                
            elif review_type == const.REVIEW_TEST_CASES:
                saved_state['test_case_review_status'] = "approved"
                node_name = "review_test_cases"
                saved_state['next_node'] = const.QA_TESTING
                
            elif review_type == const.REVIEW_QA_TESTING:
                saved_state['qa_testing_status'] = "approved"
                node_name = "qa_review"
                saved_state['next_node'] = const.DEPLOYMENT
            
            # Update and continue
            graph.update_state(thread, saved_state, as_node=node_name)
            
            state = None
            for event in graph.stream(None, thread, stream_mode="values"):
                state = event
            
            current_state = graph.get_state(thread)
            save_state_to_redis(task_id, current_state)
            
            return {
                "task_id": task_id,
                "state": state,
                "approved_stage": review_type,
                "status": "approved"
            }
            
        except Exception as e:
            logger.error(f"Failed to approve autonomous stage: {str(e)}")
            raise
    
    async def get_autonomous_status(self, task_id: str) -> Dict[str, Any]:
        """Get current status of autonomous workflow"""
        try:
            saved_state = get_state_from_redis(task_id)
            if not saved_state:
                return {"error": "Task not found", "task_id": task_id}
            
            # Get insights from agent manager
            insights = await self.graph_builder.get_autonomous_insights(saved_state)
            
            # Determine current phase
            current_phase = saved_state.get("next_node", "unknown")
            
            # Get completion percentage
            completion_percentage = self._calculate_completion_percentage(saved_state)
            
            return {
                "task_id": task_id,
                "current_phase": current_phase,
                "completion_percentage": completion_percentage,
                "autonomous_mode": saved_state.get("autonomous_mode", False),
                "autonomous_insights": insights,
                "last_updated": datetime.now().isoformat(),
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Failed to get autonomous status: {str(e)}")
            return {"error": str(e), "task_id": task_id}
    
    def _calculate_completion_percentage(self, state: SDLCState) -> float:
        """Calculate completion percentage based on current phase"""
        phase_weights = {
            const.PROJECT_INITILIZATION: 5,
            const.REQUIREMENT_COLLECTION: 10,
            const.GENERATE_USER_STORIES: 20,
            const.CREATE_DESIGN_DOC: 35,
            const.CODE_GENERATION: 50,
            const.SECURITY_REVIEW: 60,
            const.WRITE_TEST_CASES: 70,
            const.QA_TESTING: 80,
            const.DEPLOYMENT: 90,
            const.ARTIFACTS: 100
        }
        
        current_phase = state.get("next_node", const.PROJECT_INITILIZATION)
        return phase_weights.get(current_phase, 0)
    
    async def get_execution_summary(self, task_id: str) -> Dict[str, Any]:
        """Get comprehensive execution summary"""
        try:
            saved_state = get_state_from_redis(task_id)
            if not saved_state:
                return {"error": "Task not found"}
            
            # Get agent execution summary
            agent_summary = self.graph_builder.agent_manager.get_execution_summary(saved_state)
            
            # Get autonomous insights
            insights = await self.graph_builder.get_autonomous_insights(saved_state)
            
            return {
                "task_id": task_id,
                "project_name": saved_state.get("project_name", "Unknown"),
                "started_at": saved_state.get("started_at"),
                "completion_percentage": self._calculate_completion_percentage(saved_state),
                "autonomous_mode": saved_state.get("autonomous_mode", False),
                "agent_summary": agent_summary,
                "autonomous_insights": insights,
                "phases_completed": self._get_completed_phases(saved_state)
            }
            
        except Exception as e:
            logger.error(f"Failed to get execution summary: {str(e)}")
            return {"error": str(e)}
    
    def _get_completed_phases(self, state: SDLCState) -> list:
        """Get list of completed phases"""
        completed = []
        
        if "user_stories" in state:
            completed.append("User Stories Generation")
        if "design_documents" in state:
            completed.append("Design Documents")
        if "code_generated" in state:
            completed.append("Code Generation")
        if "security_recommendations" in state:
            completed.append("Security Review")
        if "test_cases" in state:
            completed.append("Test Cases")
        if "qa_testing_comments" in state:
            completed.append("QA Testing")
        if "deployment_feedback" in state:
            completed.append("Deployment")
        if "artifacts" in state:
            completed.append("Artifacts Generation")
        
        return completed
    
    async def shutdown(self):
        """Shutdown autonomous graph executor"""
        try:
            await self.graph_builder.shutdown()
            logger.info("Autonomous graph executor shut down successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def get_available_connectors(self) -> Dict[str, Any]:
        """Get available connector information"""
        try:
            connector_manager = self.graph_builder.agent_manager.connector_manager
            return {
                "available": connector_manager.get_available_connectors(),
                "status": connector_manager.get_connector_status()
            }
        except Exception as e:
            logger.error(f"Failed to get connector info: {str(e)}")
            return {"error": str(e)}
