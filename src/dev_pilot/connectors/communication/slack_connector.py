import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

from ..base_connector import BaseConnector, ConnectorConfig, ConnectorResponse, ConnectorType, ConnectorStatus

logger = logging.getLogger(__name__)

class SlackConnector(BaseConnector):
    """Slack integration connector for team communication"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.client: Optional[WebClient] = None
        self.bot_info: Optional[Dict] = None
        
    async def connect(self) -> ConnectorResponse:
        """Connect to Slack"""
        try:
            self.status = ConnectorStatus.AUTHENTICATING
            
            # Initialize Slack client
            self.client = WebClient(token=self.config.api_key)
            
            # Test connection by getting bot info
            auth_response = await asyncio.to_thread(self.client.auth_test)
            self.bot_info = {
                "user_id": auth_response["user_id"],
                "team": auth_response["team"],
                "user": auth_response["user"],
                "team_id": auth_response["team_id"]
            }
            
            self.status = ConnectorStatus.CONNECTED
            self.connection_time = datetime.now()
            
            return ConnectorResponse(
                success=True,
                data={
                    "bot_info": self.bot_info,
                    "connected_at": self.connection_time
                }
            )
            
        except SlackApiError as e:
            self.status = ConnectorStatus.ERROR
            self.last_error = str(e)
            logger.error(f"Failed to connect to Slack: {str(e)}")
            
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def disconnect(self) -> ConnectorResponse:
        """Disconnect from Slack"""
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
        """Test Slack connection"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not initialized"
                )
            
            # Test by getting bot info
            auth_response = await asyncio.to_thread(self.client.auth_test)
            
            return ConnectorResponse(
                success=True,
                data={"auth_test": auth_response.data}
            )
            
        except SlackApiError as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def get_data(self, params: Dict[str, Any]) -> ConnectorResponse:
        """Get data from Slack based on parameters"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not connected"
                )
            
            action = params.get("action", "get_channels")
            
            if action == "get_channels":
                channels_response = await asyncio.to_thread(
                    self.client.conversations_list,
                    types="public_channel,private_channel"
                )
                
                channels = []
                for channel in channels_response["channels"]:
                    channels.append({
                        "id": channel["id"],
                        "name": channel["name"],
                        "is_private": channel["is_private"],
                        "is_archived": channel["is_archived"],
                        "num_members": channel.get("num_members", 0),
                        "topic": channel.get("topic", {}).get("value", ""),
                        "purpose": channel.get("purpose", {}).get("value", "")
                    })
                
                return ConnectorResponse(
                    success=True,
                    data={"channels": channels}
                )
                
            elif action == "get_users":
                users_response = await asyncio.to_thread(self.client.users_list)
                
                users = []
                for user in users_response["members"]:
                    if not user.get("deleted", False) and not user.get("is_bot", False):
                        users.append({
                            "id": user["id"],
                            "name": user.get("name", ""),
                            "real_name": user.get("real_name", ""),
                            "email": user.get("profile", {}).get("email", ""),
                            "is_admin": user.get("is_admin", False),
                            "is_owner": user.get("is_owner", False),
                            "status": user.get("profile", {}).get("status_text", "")
                        })
                
                return ConnectorResponse(
                    success=True,
                    data={"users": users}
                )
                
            elif action == "get_messages":
                channel_id = params.get("channel_id")
                if not channel_id:
                    return ConnectorResponse(
                        success=False,
                        error="Channel ID is required"
                    )
                
                history_response = await asyncio.to_thread(
                    self.client.conversations_history,
                    channel=channel_id,
                    limit=params.get("limit", 100)
                )
                
                messages = []
                for message in history_response["messages"]:
                    messages.append({
                        "ts": message["ts"],
                        "user": message.get("user", ""),
                        "text": message.get("text", ""),
                        "type": message.get("type", ""),
                        "subtype": message.get("subtype", "")
                    })
                
                return ConnectorResponse(
                    success=True,
                    data={"messages": messages}
                )
                
            else:
                return ConnectorResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
                
        except SlackApiError as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def send_data(self, data: Dict[str, Any]) -> ConnectorResponse:
        """Send data to Slack (send messages, create channels, etc.)"""
        try:
            if not self.client:
                return ConnectorResponse(
                    success=False,
                    error="Client not connected"
                )
            
            action = data.get("action", "send_message")
            
            if action == "send_message":
                channel = data.get("channel")
                text = data.get("text", "")
                
                if not channel:
                    return ConnectorResponse(
                        success=False,
                        error="Channel is required"
                    )
                
                response = await asyncio.to_thread(
                    self.client.chat_postMessage,
                    channel=channel,
                    text=text,
                    blocks=data.get("blocks"),
                    attachments=data.get("attachments")
                )
                
                return ConnectorResponse(
                    success=True,
                    data={
                        "message": {
                            "ts": response["ts"],
                            "channel": response["channel"],
                            "text": text
                        }
                    }
                )
                
            elif action == "create_channel":
                channel_name = data.get("channel_name")
                is_private = data.get("is_private", False)
                
                if not channel_name:
                    return ConnectorResponse(
                        success=False,
                        error="Channel name is required"
                    )
                
                response = await asyncio.to_thread(
                    self.client.conversations_create,
                    name=channel_name,
                    is_private=is_private
                )
                
                return ConnectorResponse(
                    success=True,
                    data={"created_channel": response["channel"]}
                )
                
            elif action == "invite_to_channel":
                channel_id = data.get("channel_id")
                user_ids = data.get("user_ids", [])
                
                if not channel_id or not user_ids:
                    return ConnectorResponse(
                        success=False,
                        error="Channel ID and user IDs are required"
                    )
                
                response = await asyncio.to_thread(
                    self.client.conversations_invite,
                    channel=channel_id,
                    users=",".join(user_ids)
                )
                
                return ConnectorResponse(
                    success=True,
                    data={"invited_users": user_ids}
                )
                
            else:
                return ConnectorResponse(
                    success=False,
                    error=f"Unknown action: {action}"
                )
                
        except SlackApiError as e:
            return ConnectorResponse(
                success=False,
                error=str(e)
            )
    
    async def notify_sdlc_progress(self, channel: str, project_name: str, stage: str, details: Dict[str, Any]) -> ConnectorResponse:
        """Send SDLC progress notification to Slack"""
        
        stage_emojis = {
            "project_initialization": "🚀",
            "user_stories": "📝",
            "design_documents": "📋",
            "code_generation": "💻",
            "security_review": "🔒",
            "testing": "🧪",
            "deployment": "🚀",
            "completed": "✅"
        }
        
        emoji = stage_emojis.get(stage.lower(), "📋")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} DevPilot SDLC Update"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Project:* {project_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Stage:* {stage.replace('_', ' ').title()}"
                    }
                ]
            }
        ]
        
        if details:
            detail_text = "\n".join([f"• {k}: {v}" for k, v in details.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{detail_text}"
                }
            })
        
        return await self.send_data({
            "action": "send_message",
            "channel": channel,
            "text": f"DevPilot SDLC Update for {project_name}",
            "blocks": blocks
        })
    
    async def create_project_channel(self, project_name: str, team_members: List[str] = None) -> ConnectorResponse:
        """Create a dedicated channel for the project"""
        channel_name = f"devpilot-{project_name.lower().replace(' ', '-')}"
        
        # Create channel
        create_result = await self.send_data({
            "action": "create_channel",
            "channel_name": channel_name,
            "is_private": False
        })
        
        if not create_result.success:
            return create_result
        
        channel_id = create_result.data["created_channel"]["id"]
        
        # Invite team members if provided
        if team_members:
            invite_result = await self.send_data({
                "action": "invite_to_channel",
                "channel_id": channel_id,
                "user_ids": team_members
            })
            
            if not invite_result.success:
                logger.warning(f"Failed to invite members to channel: {invite_result.error}")
        
        # Send welcome message
        welcome_message = f"""
🎉 Welcome to the DevPilot project channel for *{project_name}*!

This channel will be used for:
• SDLC progress updates
• Automated notifications from DevPilot
• Team collaboration and discussions
• Code review alerts
• Deployment notifications

Let's build something amazing together! 🚀
"""
        
        await self.send_data({
            "action": "send_message",
            "channel": channel_id,
            "text": welcome_message
        })
        
        return ConnectorResponse(
            success=True,
            data={
                "channel": create_result.data["created_channel"],
                "invited_members": team_members or []
            }
        )
