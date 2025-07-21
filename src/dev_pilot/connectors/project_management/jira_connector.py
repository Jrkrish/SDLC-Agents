import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from atlassian import Jira
import logging

from ..base_connector import BaseConnector, ConnectorConfig, ConnectorResponse, ConnectorType, ConnectorStatus

logger = logging.getLogger(__name__)

class JiraConnector(BaseConnector):
    """Jira integration connector for project management"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.client: Optional[Jira] = None
        self.server_info: Optional[Dict] = None
        
    async def connect(self) -> ConnectorResponse:
        """Connect to Jira instance"""
        try:
            self.status = ConnectorStatus.AUTHENTICATING
            
            # Initialize Jira client
            self.client = Jira(
                url=self.config.base_url,
                username=self.config.custom_config.get("username"),
                password=self.config.api_key,  # API token
                timeout=self.config.timeout
            )
            
            # Test connection by getting server info
            self.server_info = await asyncio.to_thread(self.client.server_info)
            
            self.status = ConnectorStatus.CONNECTED
            self.connection_time = datetime.now()
            
            return ConnectorResponse(
                success=True,
                data={
                    "server_info": self.server_info,
                    "connected_at": self.connection_time
                }
            )
            
        except Exception as e:
            self.status = ConnectorStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to Jira: {str(e)}")
            
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def disconnect(self) -> ConnectorResponse:
        """Disconnect from Jira"""
        try:
            self.client = None
            self.status = ConnectorStatus.DISCONNECTED
            self.connection_time = None
            
            return ConnectorResponse(success=True)
            
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def test_connection(self) -> ConnectorResponse:
        """Test Jira connection"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not initialized"
                )
            
            # Test by fetching current user info
            user_info = await asyncio.to_thread(self.client.myself)
            
            return ConnectorResponse(
                success=True,
                data={"user_info": user_info}
            )
            
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def get_data(self, params: Dict[str, Any]) -> ConnectorResponse:
        """Get data from Jira based on parameters"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not connected"
                )
            
            action = params.get("action", "get_issues")
            
            if action == "get_issues":
                jql = params.get("jql", "project = {} ORDER BY created DESC".format(
                    params.get("project_key", "")
                ))
                max_results = params.get("max_results", 50)
                
                issues = await asyncio.to_thread(
                    self.client.jql,
                    jql,
                    limit=max_results
                )
                
                return ConnectorResponse(
                    success=True,
                    data={"issues": issues}
                )
                
            elif action == "get_projects":
                projects = await asyncio.to_thread(self.client.projects)
                return ConnectorResponse(
                    success=True,
                    data={"projects": projects}
                )
                
            elif action == "get_issue":
                issue_key = params.get("issue_key")
                if not issue_key:
                    return ConnectorResponse(
                        success=False,
                        error="Issue key is required"
                    )
                
                issue = await asyncio.to_thread(self.client.issue, issue_key)
                return ConnectorResponse(
                    success=True,
                    data={"issue": issue}
                )
                
            else:
                return ConnectorResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
                
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def send_data(self, data: Dict[str, Any]) -> ConnectorResponse:
        """Send data to Jira (create/update issues, etc.)"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not connected"
                )
            
            action = data.get("action", "create_issue")
            
            if action == "create_issue":
                issue_data = data.get("issue_data", {})
                
                # Create issue
                new_issue = await asyncio.to_thread(
                    self.client.create_issue,
                    fields=issue_data
                )
                
                return ConnectorResponse(
                    success=True,
                    data={"created_issue": new_issue}
                )
                
            elif action == "update_issue":
                issue_key = data.get("issue_key")
                update_data = data.get("update_data", {})
                
                if not issue_key:
                    return ConnectorResponse(
                        success=False,
                        error="Issue key is required"
                    )
                
                await asyncio.to_thread(
                    self.client.update_issue_field,
                    issue_key,
                    update_data
                )
                
                return ConnectorResponse(
                    success=True,
                    data={"updated_issue": issue_key}
                )
                
            elif action == "add_comment":
                issue_key = data.get("issue_key")
                comment_body = data.get("comment")
                
                if not issue_key or not comment_body:
                    return ConnectorResponse(
                        success=False,
                        error="Issue key and comment are required"
                    )
                
                comment = await asyncio.to_thread(
                    self.client.issue_add_comment,
                    issue_key,
                    comment_body
                )
                
                return ConnectorResponse(
                    success=True,
                    data={"comment": comment}
                )
                
            else:
                return ConnectorResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
                
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def create_user_story(self, story_data: Dict[str, Any]) -> ConnectorResponse:
        """Create a user story in Jira"""
        issue_data = {
            "project": {"key": story_data.get("project_key")},
            "summary": story_data.get("title", ""),
            "description": story_data.get("description", ""),
            "issuetype": {"name": "Story"},
            "priority": {"name": story_data.get("priority", "Medium")},
            "customfield_10016": story_data.get("acceptance_criteria", "")  # Story Points or custom field
        }
        
        return await self.send_data({
            "action": "create_issue",
            "issue_data": issue_data
        })
    
    async def sync_user_stories(self, user_stories: List[Dict[str, Any]], project_key: str) -> ConnectorResponse:
        """Sync multiple user stories to Jira"""
        try:
            created_issues = []
            
            for story in user_stories:
                story_data = {
                    "project_key": project_key,
                    "title": story.get("title", ""),
                    "description": story.get("description", ""),
                    "priority": story.get("priority", "Medium"),
                    "acceptance_criteria": story.get("acceptance_criteria", "")
                }
                
                result = await self.create_user_story(story_data)
                if result.success:
                    created_issues.append(result.data.get("created_issue"))
                else:
                    logger.warning(f"Failed to create story '{story.get('title')}': {result.error}")
            
            return ConnectorResponse(
                success=True,
                data={
                    "created_issues": created_issues,
                    "total_created": len(created_issues),
                    "total_requested": len(user_stories)
                }
            )
            
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
