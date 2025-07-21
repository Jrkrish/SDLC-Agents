"""
Enhanced Coding Node with Connector Integration
Extends the basic coding node with connector-based automation
"""

from typing import Dict, Any, Optional
import asyncio
from loguru import logger

from .coding_node import CodingNode
from ..state.sdlc_state import SDLCState
from ..connectors.agent_connector_bridge import AgentConnectorBridge, AgentAction, WorkflowIntegration
from ..connectors.connector_manager import ConnectorManager

class EnhancedCodingNode(CodingNode):
    """Enhanced coding node with connector integration"""
    
    def __init__(self, model, connector_manager: ConnectorManager = None):
        super().__init__(model)
        self.connector_manager = connector_manager
        self.agent_bridge = None
        
        if connector_manager:
            integration_config = WorkflowIntegration(
                auto_create_repos=True,
                auto_notify=True,
                backup_artifacts=True
            )
            self.agent_bridge = AgentConnectorBridge(connector_manager, integration_config)
    
    def generate_code(self, state: SDLCState):
        """Enhanced code generation with connector integration"""
        logger.info("----- Generating code with connector integration ----")
        
        # Call parent method for code generation
        result = super().generate_code(state)
        
        # If connectors are available, integrate with external services
        if self.agent_bridge:
            try:
                # Run connector integrations asynchronously
                asyncio.create_task(self._handle_code_generation_integrations(state, result))
            except Exception as e:
                logger.warning(f"Connector integration failed: {str(e)}")
        
        return result
    
    async def _handle_code_generation_integrations(self, state: SDLCState, code_result: Dict[str, Any]):
        """Handle connector integrations after code generation"""
        try:
            project_name = state.get("project_name", "sdlc-project")
            
            # 1. Create repository if auto-create is enabled
            if self.agent_bridge.integration_config.auto_create_repos:
                repo_response = await self.agent_bridge.execute_agent_action(
                    AgentAction.CREATE_REPOSITORY,
                    {
                        "private": True,
                        "language": "Python",
                        "description": f"AI-generated SDLC project: {project_name}"
                    },
                    state
                )
                
                if repo_response.success:
                    logger.info(f"Repository created: {repo_response.data.get('repository', {}).get('name')}")
                    
                    # 2. Commit the generated code
                    if state.get("repository"):
                        commit_response = await self.agent_bridge.execute_agent_action(
                            AgentAction.COMMIT_CODE,
                            {
                                "repository_name": state["repository"]["name"],
                                "branch": "main"
                            },
                            state
                        )
                        
                        if commit_response.success:
                            logger.info("Code committed successfully")
                        else:
                            logger.warning(f"Code commit failed: {commit_response.error}")
            
            # 3. Send notification about code generation
            if self.agent_bridge.integration_config.auto_notify:
                notification_response = await self.agent_bridge.execute_agent_action(
                    AgentAction.SEND_NOTIFICATION,
                    {
                        "stage": "code_generated",
                        "channel": "#dev-team",
                        "files_count": len(self._parse_generated_files(code_result.get("code_generated", "")))
                    },
                    state
                )
                
                if notification_response.success:
                    logger.info("Code generation notification sent")
            
            # 4. Create GitHub issues for any code review comments
            if code_result.get("code_review_comments") and state.get("repository"):
                await self._create_code_review_issues(state, code_result["code_review_comments"])
        
        except Exception as e:
            logger.error(f"Error in code generation integrations: {str(e)}")
    
    async def _create_code_review_issues(self, state: SDLCState, review_comments: str):
        """Create GitHub issues for code review comments"""
        try:
            github_connector = self.connector_manager.get_connector("github")
            if not github_connector or not github_connector.is_connected():
                return
            
            repository = state.get("repository", {}).get("full_name")
            if not repository:
                return
            
            # Parse review comments into actionable items
            issues = self._parse_review_comments_to_issues(review_comments)
            
            for issue in issues:
                issue_data = {
                    "action": "create_issue",
                    "repository": repository,
                    "issue_data": {
                        "title": f"Code Review: {issue['title']}",
                        "body": issue['description'],
                        "labels": ["code-review", "enhancement", "auto-generated"]
                    }
                }
                
                response = await github_connector.send_data(issue_data)
                if response.success:
                    logger.info(f"Created code review issue: {issue['title']}")
        
        except Exception as e:
            logger.error(f"Error creating code review issues: {str(e)}")
    
    def _parse_review_comments_to_issues(self, review_comments: str) -> list:
        """Parse review comments into actionable GitHub issues"""
        issues = []
        
        # Simple parsing - in production, this would be more sophisticated
        lines = review_comments.split('\n')
        current_issue = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for action items or recommendations
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'improve', 'consider', 'should']):
                if current_issue:
                    issues.append(current_issue)
                
                current_issue = {
                    "title": line[:50] + "..." if len(line) > 50 else line,
                    "description": f"Code review recommendation:\\n\\n{line}\\n\\nGenerated from automated code review."
                }
            elif current_issue and line:
                current_issue["description"] += f"\\n{line}"
        
        if current_issue:
            issues.append(current_issue)
        
        return issues[:5]  # Limit to 5 issues to avoid spam
    
    def _parse_generated_files(self, code_generated: str) -> list:
        """Parse generated code into file list"""
        files = []
        lines = code_generated.split('\\n')
        
        for line in lines:
            if line.strip().startswith('# File:') or line.strip().startswith('##'):
                filename = line.replace('# File:', '').replace('##', '').strip()
                if filename:
                    files.append(filename)
        
        return files if files else ["main.py"]  # Default if no files detected
    
    def deployment(self, state: SDLCState):
        """Enhanced deployment with connector integration"""
        logger.info("----- Enhanced deployment with connectors ----")
        
        # Call parent deployment method
        result = super().deployment(state)
        
        # Add connector integrations
        if self.agent_bridge:
            try:
                asyncio.create_task(self._handle_deployment_integrations(state, result))
            except Exception as e:
                logger.warning(f"Deployment connector integration failed: {str(e)}")
        
        return result
    
    async def _handle_deployment_integrations(self, state: SDLCState, deployment_result: Dict[str, Any]):
        """Handle connector integrations during deployment"""
        try:
            # 1. Store artifacts in cloud storage
            if self.agent_bridge.integration_config.backup_artifacts:
                artifacts_response = await self.agent_bridge.execute_agent_action(
                    AgentAction.STORE_ARTIFACTS,
                    {"bucket": "sdlc-deployment-artifacts"},
                    state
                )
                
                if artifacts_response.success:
                    logger.info("Deployment artifacts stored successfully")
            
            # 2. Create GitHub release if deployment successful
            if deployment_result.get("deployment_status") == "ready" and state.get("repository"):
                release_response = await self._create_deployment_release(state, deployment_result)
                if release_response and release_response.success:
                    logger.info("GitHub release created for deployment")
            
            # 3. Send deployment notification
            if self.agent_bridge.integration_config.auto_notify:
                status = deployment_result.get("deployment_status", "unknown")
                stage = "deployment_success" if status == "ready" else "deployment_failed"
                
                notification_response = await self.agent_bridge.execute_agent_action(
                    AgentAction.SEND_NOTIFICATION,
                    {
                        "stage": stage,
                        "channel": "#deployments",
                        "deployment_status": status,
                        "environment": "staging"
                    },
                    state
                )
                
                if notification_response.success:
                    logger.info("Deployment notification sent")
            
            # 4. Update project management system
            await self._update_project_management(state, deployment_result)
        
        except Exception as e:
            logger.error(f"Error in deployment integrations: {str(e)}")
    
    async def _create_deployment_release(self, state: SDLCState, deployment_result: Dict[str, Any]):
        """Create a GitHub release for the deployment"""
        try:
            github_connector = self.connector_manager.get_connector("github")
            if not github_connector or not github_connector.is_connected():
                return None
            
            repository = state.get("repository", {}).get("full_name")
            if not repository:
                return None
            
            # Generate version number (simple incrementing)
            version = f"1.0.{int(datetime.now().timestamp()) % 10000}"
            
            # Create release notes from deployment feedback
            deployment_feedback = deployment_result.get("deployment_feedback", "")
            release_notes = f"""# Release {version}

## Deployment Analysis
{deployment_feedback[:500]}...

## Features
- AI-generated codebase
- Automated testing
- Security review completed
- Production-ready deployment

Generated automatically by SDLC AI Agent.
"""
            
            release_data = {
                "action": "create_release",
                "repository": repository,
                "release_data": {
                    "tag_name": f"v{version}",
                    "name": f"Release {version}",
                    "body": release_notes,
                    "draft": False,
                    "prerelease": False
                }
            }
            
            return await github_connector.send_data(release_data)
        
        except Exception as e:
            logger.error(f"Error creating deployment release: {str(e)}")
            return None
    
    async def _update_project_management(self, state: SDLCState, deployment_result: Dict[str, Any]):
        """Update project management system with deployment status"""
        try:
            # Update JIRA tickets if available
            jira_connector = self.connector_manager.get_connector("jira")
            if jira_connector and jira_connector.is_connected():
                tickets = state.get("jira_tickets", [])
                
                for ticket in tickets:
                    update_data = {
                        "action": "update_issue",
                        "issue_key": ticket.get("key"),
                        "update_data": {
                            "fields": {
                                "status": {"name": "Done"},
                                "resolution": {"name": "Fixed"}
                            },
                            "comment": f"Automatically resolved - deployment completed with status: {deployment_result.get('deployment_status')}"
                        }
                    }
                    
                    response = await jira_connector.send_data(update_data)
                    if response.success:
                        logger.info(f"Updated JIRA ticket: {ticket.get('key')}")
        
        except Exception as e:
            logger.error(f"Error updating project management: {str(e)}")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all connector integrations"""
        if not self.agent_bridge:
            return {"status": "no_connectors", "message": "No connector integration available"}
        
        return await self.agent_bridge.get_integration_status()
    
    def enable_connector_integration(self, connector_manager: ConnectorManager, config: WorkflowIntegration = None):
        """Enable connector integration if not already enabled"""
        if not self.agent_bridge:
            self.connector_manager = connector_manager
            integration_config = config or WorkflowIntegration(
                auto_create_repos=True,
                auto_notify=True,
                backup_artifacts=True
            )
            self.agent_bridge = AgentConnectorBridge(connector_manager, integration_config)
            logger.info("Connector integration enabled for CodingNode")
