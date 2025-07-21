"""
Enhanced Slack Connector with AI Agent Integration
Provides advanced communication capabilities for SDLC workflow notifications
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from ..base_connector import BaseConnector, ConnectorConfig, ConnectorResponse, ConnectorType, ConnectorStatus
from ..communication.slack_connector import SlackConnector

logger = logging.getLogger(__name__)

class EnhancedSlackConnector(SlackConnector):
    """Enhanced Slack connector with AI agent integration capabilities"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.workflow_channels = {
            "general": "#sdlc-updates",
            "development": "#dev-team",
            "qa": "#qa-team",
            "deployment": "#deployments",
            "alerts": "#alerts"
        }
        self.message_templates = self._initialize_message_templates()
    
    def _initialize_message_templates(self) -> Dict[str, Dict]:
        """Initialize message templates for different workflow stages"""
        return {
            "project_started": {
                "title": "🚀 New SDLC Project Started",
                "color": "good",
                "emoji": ":rocket:"
            },
            "user_stories_generated": {
                "title": "📋 User Stories Generated",
                "color": "#36a64f",
                "emoji": ":clipboard:"
            },
            "design_completed": {
                "title": "🎨 Design Documents Completed",
                "color": "#36a64f",
                "emoji": ":art:"
            },
            "code_generated": {
                "title": "💻 Code Generation Completed",
                "color": "#36a64f",
                "emoji": ":computer:"
            },
            "tests_completed": {
                "title": "✅ Testing Phase Completed",
                "color": "good",
                "emoji": ":white_check_mark:"
            },
            "deployment_ready": {
                "title": "🚀 Ready for Deployment",
                "color": "warning",
                "emoji": ":rocket:"
            },
            "deployment_success": {
                "title": "🎉 Deployment Successful",
                "color": "good",
                "emoji": ":tada:"
            },
            "deployment_failed": {
                "title": "❌ Deployment Failed",
                "color": "danger",
                "emoji": ":x:"
            },
            "review_required": {
                "title": "👀 Review Required",
                "color": "warning",
                "emoji": ":eyes:"
            },
            "error_occurred": {
                "title": "🚨 Error Occurred",
                "color": "danger",
                "emoji": ":warning:"
            }
        }
    
    async def send_workflow_notification(self, stage: str, project_name: str, details: Dict[str, Any]) -> ConnectorResponse:
        """Send structured workflow notifications"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="Slack client not connected")
            
            template = self.message_templates.get(stage, self.message_templates.get("general", {}))
            channel = details.get("channel", self.workflow_channels.get("general"))
            
            # Create rich message
            message = self._create_workflow_message(stage, project_name, details, template)
            
            response = await self.send_data({
                "channel": channel,
                "text": message["text"],
                "attachments": message.get("attachments", []),
                "blocks": message.get("blocks", [])
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending workflow notification: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    def _create_workflow_message(self, stage: str, project_name: str, details: Dict[str, Any], template: Dict) -> Dict:
        """Create structured workflow message"""
        base_text = f"{template.get('emoji', '📋')} {template.get('title', 'Workflow Update')}: {project_name}"
        
        # Create blocks for rich formatting
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{template.get('emoji', '📋')} {template.get('title', 'Workflow Update')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Project:*\\n{project_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Stage:*\\n{stage.replace('_', ' ').title()}"
                    }
                ]
            }
        ]
        
        # Add stage-specific details
        if stage == "user_stories_generated":
            blocks.append(self._create_user_stories_block(details))
        elif stage == "code_generated":
            blocks.append(self._create_code_block(details))
        elif stage == "deployment_success":
            blocks.append(self._create_deployment_block(details))
        elif stage == "review_required":
            blocks.append(self._create_review_block(details))
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"<!date^{int(datetime.now().timestamp())}^{{date_short_pretty}} at {{time}}|{datetime.now().isoformat()}>"
                }
            ]
        })
        
        return {
            "text": base_text,
            "blocks": blocks
        }
    
    def _create_user_stories_block(self, details: Dict[str, Any]) -> Dict:
        """Create block for user stories notification"""
        stories_count = details.get("stories_count", 0)
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"✅ Generated *{stories_count} user stories*\\n" +
                       f"📋 Ready for review and approval"
            }
        }
    
    def _create_code_block(self, details: Dict[str, Any]) -> Dict:
        """Create block for code generation notification"""
        files_count = details.get("files_count", 0)
        repository = details.get("repository")
        
        text = f"💻 Generated *{files_count} code files*"
        if repository:
            text += f"\\n🔗 Repository: `{repository}`"
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    
    def _create_deployment_block(self, details: Dict[str, Any]) -> Dict:
        """Create block for deployment notification"""
        url = details.get("deployment_url")
        environment = details.get("environment", "production")
        
        text = f"🚀 Successfully deployed to *{environment}*"
        if url:
            text += f"\\n🌐 <{url}|View Application>"
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    
    def _create_review_block(self, details: Dict[str, Any]) -> Dict:
        """Create block for review required notification"""
        reviewers = details.get("reviewers", [])
        review_type = details.get("review_type", "code")
        
        text = f"👀 *{review_type.title()} review* required"
        if reviewers:
            mentions = " ".join([f"<@{reviewer}>" for reviewer in reviewers])
            text += f"\\n📋 Reviewers: {mentions}"
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    
    async def send_daily_summary(self, projects_summary: List[Dict[str, Any]]) -> ConnectorResponse:
        """Send daily SDLC summary"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Daily SDLC Summary"
                    }
                }
            ]
            
            for project in projects_summary:
                blocks.extend([
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Project:* {project.get('name')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Stage:* {project.get('current_stage', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Progress:* {project.get('progress', 0)}%"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Last Update:* {project.get('last_update', 'N/A')}"
                            }
                        ]
                    }
                ])
            
            response = await self.send_data({
                "channel": self.workflow_channels["general"],
                "text": "📊 Daily SDLC Summary",
                "blocks": blocks
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def send_error_alert(self, error_details: Dict[str, Any]) -> ConnectorResponse:
        """Send error alerts to the team"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 SDLC Error Alert"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Project:* {error_details.get('project_name')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Stage:* {error_details.get('stage')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Error:* {error_details.get('error_message')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:* {error_details.get('severity', 'Medium')}"
                        }
                    ]
                }
            ]
            
            # Add action buttons if needed
            if error_details.get("action_required"):
                blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Details"
                            },
                            "url": error_details.get("details_url", "#")
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Retry Process"
                            },
                            "value": "retry_process"
                        }
                    ]
                })
            
            response = await self.send_data({
                "channel": self.workflow_channels["alerts"],
                "text": f"🚨 Error in {error_details.get('project_name')}",
                "blocks": blocks
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending error alert: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def create_project_channel(self, project_name: str, team_members: List[str] = None) -> ConnectorResponse:
        """Create a dedicated channel for the project"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="Slack client not connected")
            
            channel_name = f"proj-{project_name.lower().replace(' ', '-').replace('_', '-')}"
            
            # Create channel
            channel_data = {
                "action": "create_channel",
                "channel_data": {
                    "name": channel_name,
                    "is_private": False,
                    "topic": f"SDLC project channel for {project_name}",
                    "purpose": f"Collaboration space for {project_name} development"
                }
            }
            
            response = await self.send_data(channel_data)
            
            if response.success and team_members:
                # Invite team members
                invite_data = {
                    "action": "invite_users",
                    "channel": channel_name,
                    "users": team_members
                }
                await self.send_data(invite_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating project channel: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def send_milestone_celebration(self, milestone: str, project_name: str, details: Dict[str, Any]) -> ConnectorResponse:
        """Send celebration message for project milestones"""
        try:
            celebrations = {
                "project_completed": "🎉🎉🎉",
                "deployment_success": "🚀✨",
                "all_tests_passed": "✅🎯",
                "code_review_approved": "👍💯"
            }
            
            emoji = celebrations.get(milestone, "🎉")
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} Milestone Achieved!"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{project_name}* has reached a major milestone: *{milestone.replace('_', ' ').title()}*"
                    }
                }
            ]
            
            # Add celebration GIF or image
            if details.get("include_celebration"):
                blocks.append({
                    "type": "image",
                    "image_url": "https://media.giphy.com/media/g9582DNuQppxC/giphy.gif",
                    "alt_text": "Celebration!"
                })
            
            response = await self.send_data({
                "channel": self.workflow_channels["general"],
                "text": f"{emoji} {project_name} milestone achieved!",
                "blocks": blocks
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending milestone celebration: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
    
    async def get_team_availability(self, team_members: List[str]) -> ConnectorResponse:
        """Get team member availability for coordination"""
        try:
            if not self.client:
                return ConnectorResponse(success=False, error="Slack client not connected")
            
            availability = {}
            
            for member in team_members:
                user_data = {
                    "action": "get_user_presence",
                    "user_id": member
                }
                
                response = await self.send_data(user_data)
                if response.success:
                    availability[member] = response.data.get("presence", "unknown")
            
            return ConnectorResponse(
                success=True,
                data={
                    "team_availability": availability,
                    "available_count": len([m for m, status in availability.items() if status == "active"]),
                    "total_members": len(team_members)
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting team availability: {str(e)}")
            return ConnectorResponse(success=False, error=str(e))
