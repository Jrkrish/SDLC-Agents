import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from github3 import GitHub
from github3.exceptions import GitHubError
import base64
import json
import logging

from ..base_connector import BaseConnector, ConnectorConfig, ConnectorResponse, ConnectorType, ConnectorStatus

logger = logging.getLogger(__name__)

class GitHubConnector(BaseConnector):
    """Enhanced GitHub integration connector for AI agent interactions"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.client: Optional[GitHub] = None
        self.user_info: Optional[Dict] = None
        self.organization: Optional[str] = None
        
    async def connect(self) -> ConnectorResponse:
        """Connect to GitHub"""
        try:
            self.status = ConnectorStatus.AUTHENTICATING
            
            # Initialize GitHub client
            self.client = GitHub(token=self.config.api_key)
            
            # Test connection by getting user info
            user = await asyncio.to_thread(self.client.me)
            self.user_info = {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "company": user.company,
                "location": user.location
            }
            
            self.status = ConnectorStatus.CONNECTED
            self.connection_time = datetime.now()
            
            return ConnectorResponse(
                success=True,
                data={
                    "user_info": self.user_info,
                    "connected_at": self.connection_time
                }
            )
            
        except Exception as e:
            self.status = ConnectorStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to GitHub: {str(e)}")
            
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def disconnect(self) -> ConnectorResponse:
        """Disconnect from GitHub"""
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
        """Test GitHub connection"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not initialized"
                )
            
            # Test by fetching rate limit info
            rate_limit = await asyncio.to_thread(self.client.rate_limit)
            
            return ConnectorResponse(
                success=True,
                data={
                    "rate_limit": {
                        "remaining": rate_limit["resources"]["core"]["remaining"],
                        "limit": rate_limit["resources"]["core"]["limit"],
                        "reset": rate_limit["resources"]["core"]["reset"]
                    }
                }
            )
            
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def get_data(self, params: Dict[str, Any]) -> ConnectorResponse:
        """Get data from GitHub based on parameters"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not connected"
                )
            
            action = params.get("action", "get_repositories")
            
            if action == "get_repositories":
                repos = []
                user = await asyncio.to_thread(self.client.me)
                for repo in user.repositories():
                    repos.append({
                        "name": repo.name,
                        "full_name": repo.full_name,
                        "description": repo.description,
                        "private": repo.private,
                        "language": repo.language,
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count
                    })
                    
                return ConnectorResponse(
                    success=True,
                    data={"repositories": repos}
                )
                
            elif action == "get_repository":
                repo_name = params.get("repository")
                if not repo_name:
                    return ConnectorResponse(
                        success=False,
                        error="Repository name is required"
                    )
                
                repo = await asyncio.to_thread(self.client.repository, *repo_name.split("/"))
                repo_data = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "open_issues": repo.open_issues_count,
                    "default_branch": repo.default_branch
                }
                
                return ConnectorResponse(
                    success=True,
                    data={"repository": repo_data}
                )
                
            elif action == "get_issues":
                repo_name = params.get("repository")
                if not repo_name:
                    return ConnectorResponse(
                        success=False,
                        error="Repository name is required"
                    )
                
                repo = await asyncio.to_thread(self.client.repository, *repo_name.split("/"))
                issues = []
                
                for issue in repo.issues():
                    if not issue.pull_request:  # Exclude pull requests
                        issues.append({
                            "number": issue.number,
                            "title": issue.title,
                            "body": issue.body,
                            "state": issue.state,
                            "created_at": issue.created_at.isoformat(),
                            "updated_at": issue.updated_at.isoformat(),
                            "assignee": issue.assignee.login if issue.assignee else None,
                            "labels": [label.name for label in issue.labels()]
                        })
                
                return ConnectorResponse(
                    success=True,
                    data={"issues": issues}
                )
                
            elif action == "get_pull_requests":
                repo_name = params.get("repository")
                if not repo_name:
                    return ConnectorResponse(
                        success=False,
                        error="Repository name is required"
                    )
                
                repo = await asyncio.to_thread(self.client.repository, *repo_name.split("/"))
                prs = []
                
                for pr in repo.pull_requests():
                    prs.append({
                        "number": pr.number,
                        "title": pr.title,
                        "body": pr.body,
                        "state": pr.state,
                        "created_at": pr.created_at.isoformat(),
                        "updated_at": pr.updated_at.isoformat(),
                        "head": pr.head.ref,
                        "base": pr.base.ref,
                        "mergeable": pr.mergeable
                    })
                
                return ConnectorResponse(
                    success=True,
                    data={"pull_requests": prs}
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
        """Send data to GitHub (create issues, repos, etc.)"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not connected"
                )
            
            action = data.get("action", "create_issue")
            
            if action == "create_repository":
                repo_data = data.get("repository_data", {})
                
                new_repo = await asyncio.to_thread(
                    self.client.create_repository,
                    name=repo_data.get("name"),
                    description=repo_data.get("description", ""),
                    private=repo_data.get("private", False),
                    has_issues=repo_data.get("has_issues", True),
                    has_projects=repo_data.get("has_projects", True),
                    has_wiki=repo_data.get("has_wiki", True)
                )
                
                return ConnectorResponse(
                    success=True,
                    data={"created_repository": new_repo.full_name}
                )
                
            elif action == "create_issue":
                repo_name = data.get("repository")
                issue_data = data.get("issue_data", {})
                
                if not repo_name:
                    return ConnectorResponse(
                        success=False,
                        error="Repository name is required"
                    )
                
                repo = await asyncio.to_thread(self.client.repository, *repo_name.split("/"))
                
                new_issue = await asyncio.to_thread(
                    repo.create_issue,
                    title=issue_data.get("title", ""),
                    body=issue_data.get("body", ""),
                    assignee=issue_data.get("assignee"),
                    labels=issue_data.get("labels", [])
                )
                
                return ConnectorResponse(
                    success=True,
                    data={
                        "created_issue": {
                            "number": new_issue.number,
                            "title": new_issue.title,
                            "url": new_issue.html_url
                        }
                    }
                )
                
            elif action == "create_pull_request":
                repo_name = data.get("repository")
                pr_data = data.get("pull_request_data", {})
                
                if not repo_name:
                    return ConnectorResponse(
                        success=False,
                        error="Repository name is required"
                    )
                
                repo = await asyncio.to_thread(self.client.repository, *repo_name.split("/"))
                
                new_pr = await asyncio.to_thread(
                    repo.create_pull,
                    title=pr_data.get("title", ""),
                    body=pr_data.get("body", ""),
                    head=pr_data.get("head"),
                    base=pr_data.get("base", "main")
                )
                
                return ConnectorResponse(
                    success=True,
                    data={
                        "created_pull_request": {
                            "number": new_pr.number,
                            "title": new_pr.title,
                            "url": new_pr.html_url
                        }
                    }
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
    
    async def create_project_repository(self, project_data: Dict[str, Any]) -> ConnectorResponse:
        """Create a new repository for the project"""
        repo_data = {
            "name": project_data.get("name", "").replace(" ", "-").lower(),
            "description": project_data.get("description", ""),
            "private": project_data.get("private", False),
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True
        }
        
        return await self.send_data({
            "action": "create_repository",
            "repository_data": repo_data
        })
    
    async def sync_user_stories_as_issues(self, user_stories: List[Dict[str, Any]], repository: str) -> ConnectorResponse:
        """Sync user stories as GitHub issues"""
        try:
            created_issues = []
            
            for story in user_stories:
                issue_data = {
                    "title": f"User Story: {story.get('title', '')}",
                    "body": f"""
## Description
{story.get('description', '')}

## Acceptance Criteria
{story.get('acceptance_criteria', '')}

## Priority
{story.get('priority', 'Medium')}
""",
                    "labels": ["user-story", f"priority-{story.get('priority', 'medium').lower()}"]
                }
                
                result = await self.send_data({
                    "action": "create_issue",
                    "repository": repository,
                    "issue_data": issue_data
                })
                
                if result.success:
                    created_issues.append(result.data.get("created_issue"))
                else:
                    logger.warning(f"Failed to create issue for story '{story.get('title')}': {result.error}")
            
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
