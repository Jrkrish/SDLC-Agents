"""
Agent-Connector Bridge
This module provides integration between AI agents and external connectors
for automated SDLC workflow management
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
import asyncio
import logging
from datetime import datetime
from pydantic import BaseModel, Field

from .connector_manager import ConnectorManager
from .base_connector import ConnectorType, ConnectorResponse
from ..state.sdlc_state import SDLCState
from ..utils.constants import *

logger = logging.getLogger(__name__)

class AgentAction(Enum):
    """Types of actions agents can perform through connectors"""
    CREATE_REPOSITORY = "create_repository"
    CREATE_BRANCH = "create_branch"
    COMMIT_CODE = "commit_code"
    CREATE_PULL_REQUEST = "create_pull_request"
    CREATE_JIRA_TICKET = "create_jira_ticket"
    UPDATE_JIRA_TICKET = "update_jira_ticket"
    SEND_NOTIFICATION = "send_notification"
    STORE_ARTIFACTS = "store_artifacts"
    DEPLOY_APPLICATION = "deploy_application"
    CREATE_DATABASE = "create_database"
    SETUP_MONITORING = "setup_monitoring"
    GENERATE_DOCUMENTATION = "generate_documentation"
    SCHEDULE_MEETING = "schedule_meeting"
    CREATE_TEST_ENVIRONMENT = "create_test_environment"
    BACKUP_DATA = "backup_data"

class WorkflowIntegration(BaseModel):
    """Configuration for workflow integration with connectors"""
    enabled: bool = True
    auto_create_repos: bool = False
    auto_create_tickets: bool = False
    auto_deploy: bool = False
    auto_notify: bool = True
    backup_artifacts: bool = True
    integration_points: List[str] = Field(default_factory=list)

class AgentConnectorBridge:
    """Bridge between AI agents and external connectors"""
    
    def __init__(self, connector_manager: ConnectorManager, integration_config: WorkflowIntegration = None):
        self.connector_manager = connector_manager
        self.integration_config = integration_config or WorkflowIntegration()
        self.workflow_history: List[Dict[str, Any]] = []
        
    async def execute_agent_action(self, action: AgentAction, context: Dict[str, Any], state: SDLCState) -> ConnectorResponse:
        """Execute an agent action through appropriate connectors"""
        try:
            logger.info(f"Executing agent action: {action.value}")
            
            # Route action to appropriate connector
            if action == AgentAction.CREATE_REPOSITORY:
                return await self._create_repository(context, state)
            elif action == AgentAction.COMMIT_CODE:
                return await self._commit_code(context, state)
            elif action == AgentAction.CREATE_JIRA_TICKET:
                return await self._create_jira_ticket(context, state)
            elif action == AgentAction.SEND_NOTIFICATION:
                return await self._send_notification(context, state)
            elif action == AgentAction.STORE_ARTIFACTS:
                return await self._store_artifacts(context, state)
            elif action == AgentAction.DEPLOY_APPLICATION:
                return await self._deploy_application(context, state)
            else:
                return ConnectorResponse(
                    success=False,
                    error=f"Action {action.value} not implemented"
                )
                
        except Exception as e:
            logger.error(f"Error executing agent action {action.value}: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def _create_repository(self, context: Dict[str, Any], state: SDLCState) -> ConnectorResponse:
        """Create a new repository using GitHub connector"""
        github_connector = self.connector_manager.get_connector("github")
        if not github_connector or not github_connector.is_connected():
            return ConnectorResponse(success=False, error="GitHub connector not available")
        
        project_name = state.get("project_name", "sdlc-project")
        description = f"Auto-generated repository for {project_name}"
        
        # Create repository
        repo_data = {
            "name": project_name.lower().replace(" ", "-"),
            "description": description,
            "private": context.get("private", True),
            "auto_init": True,
            "gitignore_template": context.get("language", "Python")
        }
        
        response = await github_connector.send_data(repo_data)
        
        if response.success:
            # Update state with repository information
            state["repository"] = {
                "url": response.data.get("clone_url"),
                "name": response.data.get("name"),
                "created_at": datetime.now().isoformat()
            }
            
            # Log workflow action
            self._log_workflow_action("repository_created", {
                "repository_name": repo_data["name"],
                "connector": "github"
            })
        
        return response
    
    async def _commit_code(self, context: Dict[str, Any], state: SDLCState) -> ConnectorResponse:
        """Commit generated code to repository"""
        github_connector = self.connector_manager.get_connector("github")
        if not github_connector or not github_connector.is_connected():
            return ConnectorResponse(success=False, error="GitHub connector not available")
        
        code_generated = state.get("code_generated", "")
        if not code_generated:
            return ConnectorResponse(success=False, error="No code available to commit")
        
        # Parse code into files
        files = self._parse_code_into_files(code_generated)
        
        commit_data = {
            "repository": context.get("repository_name"),
            "branch": context.get("branch", "main"),
            "message": f"Auto-generated code for {state.get('project_name', 'project')}",
            "files": files
        }
        
        response = await github_connector.send_data(commit_data)
        
        if response.success:
            state["code_committed"] = True
            state["commit_hash"] = response.data.get("sha")
            
            self._log_workflow_action("code_committed", {
                "repository": context.get("repository_name"),
                "files_count": len(files)
            })
        
        return response
    
    async def _create_jira_ticket(self, context: Dict[str, Any], state: SDLCState) -> ConnectorResponse:
        """Create JIRA tickets for user stories"""
        jira_connector = self.connector_manager.get_connector("jira")
        if not jira_connector or not jira_connector.is_connected():
            return ConnectorResponse(success=False, error="JIRA connector not available")
        
        user_stories = state.get("user_stories")
        if not user_stories:
            return ConnectorResponse(success=False, error="No user stories available")
        
        tickets = []
        project_key = context.get("project_key", "PROJ")
        
        # Create tickets for each user story
        for story in user_stories.user_stories:
            ticket_data = {
                "project": {"key": project_key},
                "summary": story.title,
                "description": f"{story.description}\n\nAcceptance Criteria:\n{story.acceptance_criteria}",
                "issuetype": {"name": "Story"},
                "priority": {"name": self._map_priority(story.priority)},
                "labels": ["auto-generated", "sdlc-agent"]
            }
            
            response = await jira_connector.send_data(ticket_data)
            if response.success:
                tickets.append(response.data)
        
        if tickets:
            state["jira_tickets"] = tickets
            self._log_workflow_action("jira_tickets_created", {
                "count": len(tickets),
                "project_key": project_key
            })
        
        return ConnectorResponse(success=True, data={"tickets": tickets})
    
    async def _send_notification(self, context: Dict[str, Any], state: SDLCState) -> ConnectorResponse:
        """Send notifications through Slack connector"""
        slack_connector = self.connector_manager.get_connector("slack")
        if not slack_connector or not slack_connector.is_connected():
            return ConnectorResponse(success=False, error="Slack connector not available")
        
        stage = context.get("stage", "unknown")
        project_name = state.get("project_name", "Project")
        
        message = self._generate_notification_message(stage, project_name, context)
        
        notification_data = {
            "channel": context.get("channel", "#sdlc-updates"),
            "text": message,
            "attachments": self._create_notification_attachments(stage, state)
        }
        
        response = await slack_connector.send_data(notification_data)
        
        if response.success:
            self._log_workflow_action("notification_sent", {
                "stage": stage,
                "channel": notification_data["channel"]
            })
        
        return response
    
    async def _store_artifacts(self, context: Dict[str, Any], state: SDLCState) -> ConnectorResponse:
        """Store artifacts in cloud storage"""
        s3_connector = self.connector_manager.get_connector("aws_s3")
        if not s3_connector or not s3_connector.is_connected():
            return ConnectorResponse(success=False, error="S3 connector not available")
        
        artifacts = state.get("artifacts", {})
        if not artifacts:
            return ConnectorResponse(success=False, error="No artifacts to store")
        
        project_name = state.get("project_name", "project")
        bucket_name = context.get("bucket", "sdlc-artifacts")
        
        uploaded_files = []
        
        for artifact_name, artifact_path in artifacts.items():
            if artifact_path:
                try:
                    with open(artifact_path, "rb") as f:
                        file_content = f.read()
                    
                    s3_key = f"{project_name}/{artifact_name.lower()}.md"
                    
                    upload_data = {
                        "bucket": bucket_name,
                        "key": s3_key,
                        "body": file_content,
                        "content_type": "text/markdown"
                    }
                    
                    response = await s3_connector.send_data(upload_data)
                    if response.success:
                        uploaded_files.append({
                            "name": artifact_name,
                            "s3_key": s3_key,
                            "url": response.data.get("url")
                        })
                
                except Exception as e:
                    logger.error(f"Error uploading {artifact_name}: {str(e)}")
        
        if uploaded_files:
            state["artifacts_stored"] = uploaded_files
            self._log_workflow_action("artifacts_stored", {
                "count": len(uploaded_files),
                "bucket": bucket_name
            })
        
        return ConnectorResponse(success=True, data={"uploaded_files": uploaded_files})
    
    async def _deploy_application(self, context: Dict[str, Any], state: SDLCState) -> ConnectorResponse:
        """Deploy application using appropriate connector"""
        # This would integrate with deployment connectors like AWS, Azure, GCP
        deployment_connector = self.connector_manager.get_connector(context.get("platform", "aws"))
        if not deployment_connector:
            return ConnectorResponse(success=False, error="Deployment connector not available")
        
        code_generated = state.get("code_generated", "")
        if not code_generated:
            return ConnectorResponse(success=False, error="No code available to deploy")
        
        deployment_data = {
            "project_name": state.get("project_name"),
            "code": code_generated,
            "environment": context.get("environment", "staging"),
            "configuration": context.get("config", {})
        }
        
        response = await deployment_connector.send_data(deployment_data)
        
        if response.success:
            state["deployed"] = True
            state["deployment_url"] = response.data.get("url")
            
            self._log_workflow_action("application_deployed", {
                "platform": context.get("platform"),
                "environment": context.get("environment")
            })
        
        return response
    
    def _parse_code_into_files(self, code_generated: str) -> List[Dict[str, str]]:
        """Parse generated code into individual files"""
        files = []
        current_file = None
        current_content = []
        
        lines = code_generated.split('\n')
        
        for line in lines:
            if line.strip().startswith('# File:') or line.strip().startswith('##'):
                # Save previous file
                if current_file and current_content:
                    files.append({
                        "path": current_file,
                        "content": '\n'.join(current_content)
                    })
                
                # Start new file
                current_file = line.replace('# File:', '').replace('##', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            files.append({
                "path": current_file,
                "content": '\n'.join(current_content)
            })
        
        # If no files detected, create a default main.py
        if not files and code_generated.strip():
            files.append({
                "path": "main.py",
                "content": code_generated
            })
        
        return files
    
    def _map_priority(self, priority: int) -> str:
        """Map numeric priority to JIRA priority names"""
        priority_map = {1: "Highest", 2: "High", 3: "Medium", 4: "Low"}
        return priority_map.get(priority, "Medium")
    
    def _generate_notification_message(self, stage: str, project_name: str, context: Dict[str, Any]) -> str:
        """Generate notification message based on stage"""
        stage_messages = {
            "user_stories_approved": f"✅ User stories approved for {project_name}",
            "design_completed": f"📐 Design documents completed for {project_name}",
            "code_generated": f"💻 Code generation completed for {project_name}",
            "tests_passed": f"✅ All tests passed for {project_name}",
            "deployment_ready": f"🚀 {project_name} is ready for deployment",
            "deployment_completed": f"🎉 {project_name} has been successfully deployed"
        }
        
        return stage_messages.get(stage, f"📋 Update for {project_name}: {stage}")
    
    def _create_notification_attachments(self, stage: str, state: SDLCState) -> List[Dict[str, Any]]:
        """Create rich attachments for notifications"""
        attachments = []
        
        if stage == "code_generated":
            attachments.append({
                "color": "good",
                "fields": [
                    {"title": "Project", "value": state.get("project_name"), "short": True},
                    {"title": "Files Generated", "value": "Multiple Python files", "short": True}
                ]
            })
        
        return attachments
    
    def _log_workflow_action(self, action: str, details: Dict[str, Any]):
        """Log workflow actions for audit trail"""
        self.workflow_history.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all connector integrations"""
        connected_connectors = []
        failed_connectors = []
        
        for name, connector in self.connector_manager.connectors.items():
            status = connector.get_status()
            if status["status"] == "connected":
                connected_connectors.append(name)
            else:
                failed_connectors.append(name)
        
        return {
            "connected_count": len(connected_connectors),
            "failed_count": len(failed_connectors),
            "connected_connectors": connected_connectors,
            "failed_connectors": failed_connectors,
            "workflow_history": self.workflow_history[-10:],  # Last 10 actions
            "integration_config": self.integration_config.dict()
        }
    
    async def execute_workflow_stage_integration(self, stage: str, state: SDLCState) -> List[ConnectorResponse]:
        """Execute connector integrations for a specific workflow stage"""
        responses = []
        
        try:
            if stage == GENERATE_USER_STORIES and self.integration_config.auto_create_tickets:
                response = await self.execute_agent_action(
                    AgentAction.CREATE_JIRA_TICKET,
                    {"project_key": "SDLC"},
                    state
                )
                responses.append(response)
            
            elif stage == CODE_GENERATION:
                if self.integration_config.auto_create_repos:
                    response = await self.execute_agent_action(
                        AgentAction.CREATE_REPOSITORY,
                        {"private": True, "language": "Python"},
                        state
                    )
                    responses.append(response)
                
                # Always commit code if repository exists
                if state.get("repository"):
                    response = await self.execute_agent_action(
                        AgentAction.COMMIT_CODE,
                        {"repository_name": state["repository"]["name"]},
                        state
                    )
                    responses.append(response)
            
            elif stage == DEPLOYMENT:
                if self.integration_config.backup_artifacts:
                    response = await self.execute_agent_action(
                        AgentAction.STORE_ARTIFACTS,
                        {"bucket": "sdlc-artifacts"},
                        state
                    )
                    responses.append(response)
                
                if self.integration_config.auto_deploy:
                    response = await self.execute_agent_action(
                        AgentAction.DEPLOY_APPLICATION,
                        {"platform": "aws", "environment": "staging"},
                        state
                    )
                    responses.append(response)
            
            # Send notifications for all stages if enabled
            if self.integration_config.auto_notify:
                response = await self.execute_agent_action(
                    AgentAction.SEND_NOTIFICATION,
                    {"stage": stage, "channel": "#sdlc-updates"},
                    state
                )
                responses.append(response)
        
        except Exception as e:
            logger.error(f"Error in workflow stage integration for {stage}: {str(e)}")
            responses.append(ConnectorResponse(success=False, error=str(e)))
        
        return responses
