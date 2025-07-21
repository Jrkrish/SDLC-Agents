"""
Autonomous Nodes with Agent Integration
These nodes work with the AgentManager to provide autonomous SDLC execution
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from ..state.sdlc_state import SDLCState, UserStoryList
from ..agents.agent_manager import AgentManager
from .project_requirement_node import ProjectRequirementNode
from .design_document_node import DesingDocumentNode
from .coding_node import CodingNode
from .markdown_node import MarkdownArtifactsNode
import src.dev_pilot.utils.constants as const

logger = logging.getLogger(__name__)

class AutonomousProjectNode:
    """Autonomous project management node with agent integration"""
    
    def __init__(self, llm, agent_manager: AgentManager):
        self.llm = llm
        self.agent_manager = agent_manager
        self.base_node = ProjectRequirementNode(llm)
    
    async def initialize_project(self, state: SDLCState) -> SDLCState:
        """Initialize project with autonomous agents"""
        try:
            logger.info("Starting autonomous project initialization")
            
            # Execute autonomous agent work for project initialization
            updated_state = await self.agent_manager.execute_phase(
                const.PROJECT_INITILIZATION, 
                state,
                {"initialization": True}
            )
            
            # Set up project infrastructure autonomously
            project_name = updated_state.get("project_name", "")
            if project_name:
                # Agents will handle repository creation, channel setup, etc.
                logger.info(f"Project '{project_name}' initialized autonomously")
            
            updated_state["next_node"] = const.REQUIREMENT_COLLECTION
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous project initialization failed: {str(e)}")
            return state
    
    async def get_user_requirements(self, state: SDLCState) -> SDLCState:
        """Get user requirements with agent assistance"""
        try:
            # Agents can analyze and suggest requirements
            updated_state = await self.agent_manager.execute_phase(
                const.REQUIREMENT_COLLECTION,
                state,
                {"requirements_gathering": True}
            )
            
            return updated_state
            
        except Exception as e:
            logger.error(f"Requirements gathering failed: {str(e)}")
            return state
    
    async def generate_user_stories(self, state: SDLCState) -> SDLCState:
        """Generate user stories with autonomous business analyst"""
        try:
            logger.info("Starting autonomous user story generation")
            
            # Execute autonomous business analyst work
            updated_state = await self.agent_manager.execute_phase(
                const.GENERATE_USER_STORIES,
                state,
                {"story_generation": True}
            )
            
            # If agents didn't generate stories, use base implementation
            if "user_stories" not in updated_state or not updated_state["user_stories"]:
                updated_state = self.base_node.generate_user_stories(updated_state)
            
            logger.info("Autonomous user story generation completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous user story generation failed: {str(e)}")
            # Fallback to base implementation
            return self.base_node.generate_user_stories(state)
    
    async def review_user_stories(self, state: SDLCState) -> SDLCState:
        """Review user stories with autonomous agents"""
        try:
            # Agents can perform autonomous review
            insights = await self.agent_manager.get_autonomous_recommendations(state)
            
            # Store autonomous review insights
            state["autonomous_review"] = {
                "user_stories": insights,
                "timestamp": datetime.now().isoformat(),
                "auto_reviewed": True
            }
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous user stories review failed: {str(e)}")
            return state
    
    async def revise_user_stories(self, state: SDLCState) -> SDLCState:
        """Revise user stories based on autonomous feedback"""
        try:
            # Handle feedback autonomously
            feedback = state.get("user_stories_feedback", "")
            if feedback:
                updated_state = await self.agent_manager.handle_feedback(
                    const.GENERATE_USER_STORIES, feedback, state
                )
                return updated_state
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous user stories revision failed: {str(e)}")
            return state
    
    def autonomous_user_stories_router(self, state: SDLCState) -> str:
        """Autonomous routing for user stories review"""
        # Check if autonomous review is available
        autonomous_review = state.get("autonomous_review", {})
        if autonomous_review.get("auto_reviewed"):
            # Agent can auto-approve based on quality metrics
            confidence_threshold = 0.8
            
            # Get agent recommendations
            try:
                recommendations = state.get("agent_execution_log", {}).get(const.GENERATE_USER_STORIES, {})
                if recommendations:
                    # Check if business analyst has high confidence
                    ba_results = recommendations.get("business_analyst_agent", {})
                    if ba_results.get("completed") and not ba_results.get("error"):
                        return "autonomous_approve"
            except:
                pass
        
        # Default behavior
        return state.get("user_stories_review_status", "approved")


class AutonomousDesignNode:
    """Autonomous design node with software architect integration"""
    
    def __init__(self, llm, agent_manager: AgentManager):
        self.llm = llm
        self.agent_manager = agent_manager
        self.base_node = DesingDocumentNode(llm)
    
    async def create_design_documents(self, state: SDLCState) -> SDLCState:
        """Create design documents with autonomous software architect"""
        try:
            logger.info("Starting autonomous design document creation")
            
            # Execute autonomous software architect work
            updated_state = await self.agent_manager.execute_phase(
                const.CREATE_DESIGN_DOC,
                state,
                {"design_creation": True}
            )
            
            # If agents didn't create designs, use base implementation
            if "design_documents" not in updated_state:
                updated_state = self.base_node.create_design_documents(updated_state)
            
            logger.info("Autonomous design document creation completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous design creation failed: {str(e)}")
            return self.base_node.create_design_documents(state)
    
    async def review_design_documents(self, state: SDLCState) -> SDLCState:
        """Review design documents autonomously"""
        try:
            insights = await self.agent_manager.get_autonomous_recommendations(state)
            
            state["autonomous_design_review"] = {
                "insights": insights,
                "timestamp": datetime.now().isoformat(),
                "auto_reviewed": True
            }
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous design review failed: {str(e)}")
            return state
    
    async def revise_design_documents(self, state: SDLCState) -> SDLCState:
        """Revise design documents based on autonomous feedback"""
        try:
            feedback = state.get("design_documents_feedback", "")
            if feedback:
                updated_state = await self.agent_manager.handle_feedback(
                    const.CREATE_DESIGN_DOC, feedback, state
                )
                return updated_state
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous design revision failed: {str(e)}")
            return state
    
    def autonomous_design_documents_router(self, state: SDLCState) -> str:
        """Autonomous routing for design documents review"""
        autonomous_review = state.get("autonomous_design_review", {})
        if autonomous_review.get("auto_reviewed"):
            # Check architect agent confidence
            try:
                recommendations = state.get("agent_execution_log", {}).get(const.CREATE_DESIGN_DOC, {})
                if recommendations:
                    arch_results = recommendations.get("software_architect_agent", {})
                    if arch_results.get("completed") and not arch_results.get("error"):
                        return "autonomous_approve"
            except:
                pass
        
        return state.get("design_documents_review_status", "approved")


class AutonomousCodingNode:
    """Autonomous coding node with developer, security, QA, and DevOps agents"""
    
    def __init__(self, llm, agent_manager: AgentManager):
        self.llm = llm
        self.agent_manager = agent_manager
        self.base_node = CodingNode(llm)
    
    async def generate_code(self, state: SDLCState) -> SDLCState:
        """Generate code with autonomous developer agent"""
        try:
            logger.info("Starting autonomous code generation")
            
            updated_state = await self.agent_manager.execute_phase(
                const.CODE_GENERATION,
                state,
                {"code_generation": True}
            )
            
            # Fallback if agents didn't generate code
            if "code_generated" not in updated_state:
                updated_state = self.base_node.generate_code(updated_state)
            
            logger.info("Autonomous code generation completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous code generation failed: {str(e)}")
            return self.base_node.generate_code(state)
    
    async def code_review(self, state: SDLCState) -> SDLCState:
        """Perform autonomous code review"""
        try:
            insights = await self.agent_manager.get_autonomous_recommendations(state)
            
            state["autonomous_code_review"] = {
                "insights": insights,
                "timestamp": datetime.now().isoformat(),
                "auto_reviewed": True
            }
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous code review failed: {str(e)}")
            return state
    
    async def fix_code(self, state: SDLCState) -> SDLCState:
        """Fix code based on autonomous feedback"""
        try:
            feedback = state.get("code_review_feedback", "")
            if feedback:
                updated_state = await self.agent_manager.handle_feedback(
                    const.CODE_GENERATION, feedback, state
                )
                return updated_state
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous code fixing failed: {str(e)}")
            return state
    
    async def security_review_recommendations(self, state: SDLCState) -> SDLCState:
        """Generate security recommendations with autonomous security expert"""
        try:
            logger.info("Starting autonomous security analysis")
            
            updated_state = await self.agent_manager.execute_phase(
                const.SECURITY_REVIEW,
                state,
                {"security_analysis": True}
            )
            
            if "security_recommendations" not in updated_state:
                updated_state = self.base_node.security_review_recommendations(updated_state)
            
            logger.info("Autonomous security analysis completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous security analysis failed: {str(e)}")
            return self.base_node.security_review_recommendations(state)
    
    async def security_review(self, state: SDLCState) -> SDLCState:
        """Perform autonomous security review"""
        try:
            insights = await self.agent_manager.get_autonomous_recommendations(state)
            
            state["autonomous_security_review"] = {
                "insights": insights,
                "timestamp": datetime.now().isoformat(),
                "auto_reviewed": True
            }
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous security review failed: {str(e)}")
            return state
    
    async def fix_code_after_security_review(self, state: SDLCState) -> SDLCState:
        """Fix code after security review"""
        try:
            feedback = state.get("security_review_comments", "")
            if feedback:
                updated_state = await self.agent_manager.handle_feedback(
                    const.SECURITY_REVIEW, feedback, state
                )
                return updated_state
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous security fix failed: {str(e)}")
            return state
    
    async def write_test_cases(self, state: SDLCState) -> SDLCState:
        """Write test cases with autonomous QA engineer"""
        try:
            logger.info("Starting autonomous test case generation")
            
            updated_state = await self.agent_manager.execute_phase(
                const.WRITE_TEST_CASES,
                state,
                {"test_case_generation": True}
            )
            
            if "test_cases" not in updated_state:
                updated_state = self.base_node.write_test_cases(updated_state)
            
            logger.info("Autonomous test case generation completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous test case generation failed: {str(e)}")
            return self.base_node.write_test_cases(state)
    
    async def review_test_cases(self, state: SDLCState) -> SDLCState:
        """Review test cases autonomously"""
        try:
            insights = await self.agent_manager.get_autonomous_recommendations(state)
            
            state["autonomous_test_review"] = {
                "insights": insights,
                "timestamp": datetime.now().isoformat(),
                "auto_reviewed": True
            }
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous test review failed: {str(e)}")
            return state
    
    async def revise_test_cases(self, state: SDLCState) -> SDLCState:
        """Revise test cases based on autonomous feedback"""
        try:
            feedback = state.get("test_case_review_feedback", "")
            if feedback:
                updated_state = await self.agent_manager.handle_feedback(
                    const.WRITE_TEST_CASES, feedback, state
                )
                return updated_state
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous test case revision failed: {str(e)}")
            return state
    
    async def qa_testing(self, state: SDLCState) -> SDLCState:
        """Perform QA testing with autonomous QA engineer"""
        try:
            logger.info("Starting autonomous QA testing")
            
            updated_state = await self.agent_manager.execute_phase(
                const.QA_TESTING,
                state,
                {"qa_testing": True}
            )
            
            if "qa_testing_comments" not in updated_state:
                updated_state = self.base_node.qa_testing(updated_state)
            
            logger.info("Autonomous QA testing completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous QA testing failed: {str(e)}")
            return self.base_node.qa_testing(state)
    
    async def qa_review(self, state: SDLCState) -> SDLCState:
        """Perform autonomous QA review"""
        try:
            insights = await self.agent_manager.get_autonomous_recommendations(state)
            
            state["autonomous_qa_review"] = {
                "insights": insights,
                "timestamp": datetime.now().isoformat(),
                "auto_reviewed": True
            }
            
            return state
            
        except Exception as e:
            logger.error(f"Autonomous QA review failed: {str(e)}")
            return state
    
    async def deployment(self, state: SDLCState) -> SDLCState:
        """Perform deployment with autonomous DevOps engineer"""
        try:
            logger.info("Starting autonomous deployment")
            
            updated_state = await self.agent_manager.execute_phase(
                const.DEPLOYMENT,
                state,
                {"deployment": True}
            )
            
            if "deployment_feedback" not in updated_state:
                updated_state = self.base_node.deployment(updated_state)
            
            logger.info("Autonomous deployment completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous deployment failed: {str(e)}")
            return self.base_node.deployment(state)
    
    def autonomous_code_review_router(self, state: SDLCState) -> str:
        """Autonomous routing for code review"""
        autonomous_review = state.get("autonomous_code_review", {})
        if autonomous_review.get("auto_reviewed"):
            return "autonomous_approve"
        return state.get("code_review_status", "approved")
    
    def autonomous_security_review_router(self, state: SDLCState) -> str:
        """Autonomous routing for security review"""
        autonomous_review = state.get("autonomous_security_review", {})
        if autonomous_review.get("auto_reviewed"):
            return "autonomous_approve"
        return state.get("security_review_status", "approved")
    
    def autonomous_test_cases_router(self, state: SDLCState) -> str:
        """Autonomous routing for test cases review"""
        autonomous_review = state.get("autonomous_test_review", {})
        if autonomous_review.get("auto_reviewed"):
            return "autonomous_approve"
        return state.get("test_case_review_status", "approved")
    
    def autonomous_qa_review_router(self, state: SDLCState) -> str:
        """Autonomous routing for QA review"""
        autonomous_review = state.get("autonomous_qa_review", {})
        if autonomous_review.get("auto_reviewed"):
            return "autonomous_approve"
        return state.get("qa_testing_status", "approved")


class AutonomousArtifactsNode:
    """Autonomous artifacts generation node"""
    
    def __init__(self, llm, agent_manager: AgentManager):
        self.llm = llm
        self.agent_manager = agent_manager
        self.base_node = MarkdownArtifactsNode()
    
    async def generate_artifacts(self, state: SDLCState) -> SDLCState:
        """Generate artifacts with autonomous agents insights"""
        try:
            logger.info("Starting autonomous artifacts generation")
            
            # Get execution summary from agent manager
            execution_summary = self.agent_manager.get_execution_summary(state)
            
            # Add autonomous execution data to state
            state["autonomous_execution_summary"] = execution_summary
            
            # Generate base artifacts
            updated_state = self.base_node.generate_markdown_artifacts(state)
            
            # Enhance with autonomous insights
            if "artifacts" in updated_state:
                artifacts = updated_state["artifacts"]
                
                # Add autonomous execution report
                autonomous_report = self._generate_autonomous_report(execution_summary)
                artifacts["autonomous_execution_report"] = autonomous_report
            
            logger.info("Autonomous artifacts generation completed")
            return updated_state
            
        except Exception as e:
            logger.error(f"Autonomous artifacts generation failed: {str(e)}")
            return self.base_node.generate_markdown_artifacts(state)
    
    def _generate_autonomous_report(self, execution_summary: Dict[str, Any]) -> str:
        """Generate autonomous execution report"""
        report = f"""
# Autonomous SDLC Execution Report

## Summary
- **Total Phases Executed**: {execution_summary.get('total_phases_executed', 0)}
- **Total Agent Actions**: {execution_summary.get('total_agents_executed', 0)}
- **Success Rate**: {execution_summary.get('success_rate', 0):.2%}
- **Active Agents**: {execution_summary.get('active_agents', 0)}

## Agent Performance
{self._format_agent_status(execution_summary.get('agent_status', {}))}

## Cross-Phase Coordination
- **Coordination Events**: {execution_summary.get('cross_phase_coordinations', 0)}

## Generated on: {datetime.now().isoformat()}
        """
        
        return report
    
    def _format_agent_status(self, agent_status: Dict[str, Any]) -> str:
        """Format agent status for report"""
        if not agent_status:
            return "No agent status available."
        
        formatted = ""
        for agent_name, status in agent_status.items():
            formatted += f"""
### {agent_name.replace('_', ' ').title()}
- **Active**: {status.get('active', False)}
- **Decisions Made**: {status.get('decisions_made', 0)}
- **Capabilities**: {', '.join(status.get('capabilities', []))}
- **Last Activity**: {status.get('last_activity', 'N/A')}
"""
        
        return formatted
