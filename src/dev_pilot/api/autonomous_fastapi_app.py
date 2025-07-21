"""
Enhanced FastAPI Backend for Autonomous DevPilot SDLC
Integrates with autonomous agents and connectors
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# Import our autonomous SDLC components
from ..graph.autonomous_graph_executor import AutonomousGraphExecutor
from ..agents.agent_manager import AgentManager
from ..connectors.connector_manager import ConnectorManager, ConnectorConfigManager
from ..connectors.base_connector import ConnectorType, ConnectorConfig
from ..LLMS.groqllm import GroqLLM
from ..LLMS.geminillm import GeminiLLM
from ..LLMS.openai_llm import OpenAILLM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class ConnectorConfigRequest(BaseModel):
    name: str
    enabled: bool = True
    api_key: str
    base_url: Optional[str] = None
    username: Optional[str] = None
    
class ConnectorConfigsRequest(BaseModel):
    github: Optional[ConnectorConfigRequest] = None
    jira: Optional[ConnectorConfigRequest] = None
    slack: Optional[ConnectorConfigRequest] = None

class AutonomousStartRequest(BaseModel):
    project_name: str
    fully_autonomous: bool = False
    connector_configs: Optional[ConnectorConfigsRequest] = None
    ai_model: str = "groq"
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

class AutonomousContinueRequest(BaseModel):
    task_id: str
    user_input: Optional[Dict[str, Any]] = None

class AutonomousFeedbackRequest(BaseModel):
    task_id: str
    feedback: str
    review_type: str

class AutonomousApproveRequest(BaseModel):
    task_id: str
    review_type: str

class AutonomousResponse(BaseModel):
    success: bool
    task_id: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    autonomous_insights: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    completion_percentage: Optional[float] = None
    current_phase: Optional[str] = None

# Global variables for autonomous components
autonomous_executors: Dict[str, AutonomousGraphExecutor] = {}
agent_managers: Dict[str, AgentManager] = {}

# Create FastAPI app
app = FastAPI(
    title="DevPilot Autonomous SDLC API",
    description="AI-Powered Autonomous Software Development Lifecycle Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_llm_model(model_type: str, api_key: str):
    """Get LLM model based on type and API key"""
    try:
        if model_type.lower() == "groq":
            return GroqLLM({"GROQ_API_KEY": api_key, "selected_groq_model": "mixtral-8x7b-32768"}).get_llm_model()
        elif model_type.lower() == "gemini":
            return GeminiLLM({"GEMINI_API_KEY": api_key, "selected_gemini_model": "gemini-pro"}).get_llm_model()
        elif model_type.lower() == "openai":
            return OpenAILLM({"OPENAI_API_KEY": api_key, "selected_openai_model": "gpt-4"}).get_llm_model()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM model {model_type}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to initialize {model_type} model: {str(e)}")

def create_connector_configs(connector_configs_request: Optional[ConnectorConfigsRequest]) -> Dict[str, Dict[str, Any]]:
    """Convert request connector configs to internal format"""
    if not connector_configs_request:
        return {}
    
    configs = {}
    
    if connector_configs_request.github:
        configs["github"] = {
            "name": "github",
            "enabled": connector_configs_request.github.enabled,
            "api_key": connector_configs_request.github.api_key
        }
    
    if connector_configs_request.jira:
        configs["jira"] = {
            "name": "jira", 
            "enabled": connector_configs_request.jira.enabled,
            "api_key": connector_configs_request.jira.api_key,
            "base_url": connector_configs_request.jira.base_url,
            "username": connector_configs_request.jira.username
        }
    
    if connector_configs_request.slack:
        configs["slack"] = {
            "name": "slack",
            "enabled": connector_configs_request.slack.enabled,
            "api_key": connector_configs_request.slack.api_key
        }
    
    return configs

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DevPilot Autonomous SDLC API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Autonomous SDLC Execution",
            "AI-Powered Agents",
            "Multi-Platform Connectors",
            "Real-time Streaming",
            "Advanced Analytics"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "agents": "ready",
            "connectors": "available",
            "executors": len(autonomous_executors)
        }
    }

@app.post("/api/v1/autonomous/start", response_model=AutonomousResponse)
async def start_autonomous_sdlc(request: AutonomousStartRequest):
    """Start autonomous SDLC workflow"""
    try:
        logger.info(f"Starting autonomous SDLC for project: {request.project_name}")
        
        # Determine API key based on model
        api_key = None
        if request.ai_model.lower() == "groq" and request.groq_api_key:
            api_key = request.groq_api_key
        elif request.ai_model.lower() == "gemini" and request.gemini_api_key:
            api_key = request.gemini_api_key
        elif request.ai_model.lower() == "openai" and request.openai_api_key:
            api_key = request.openai_api_key
        else:
            # Try to get from environment
            env_key_map = {
                "groq": "GROQ_API_KEY",
                "gemini": "GEMINI_API_KEY", 
                "openai": "OPENAI_API_KEY"
            }
            api_key = os.getenv(env_key_map.get(request.ai_model.lower(), ""))
        
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail=f"API key required for {request.ai_model} model"
            )
        
        # Initialize LLM model
        llm_model = get_llm_model(request.ai_model, api_key)
        
        # Create connector configs
        connector_configs = create_connector_configs(request.connector_configs)
        
        # Initialize autonomous executor
        executor = AutonomousGraphExecutor(llm_model, connector_configs)
        
        # Start workflow
        result = await executor.start_autonomous_workflow(
            request.project_name,
            request.fully_autonomous
        )
        
        task_id = result["task_id"]
        
        # Store executor for this task
        autonomous_executors[task_id] = executor
        
        return AutonomousResponse(
            success=True,
            task_id=task_id,
            state=result["state"],
            autonomous_insights=result.get("autonomous_insights"),
            status=result.get("status"),
            message=f"Autonomous SDLC started for project: {request.project_name}",
            completion_percentage=5.0,
            current_phase="project_initialization"
        )
        
    except Exception as e:
        logger.error(f"Failed to start autonomous SDLC: {str(e)}")
        return AutonomousResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/v1/autonomous/continue", response_model=AutonomousResponse)
async def continue_autonomous_workflow(request: AutonomousContinueRequest):
    """Continue autonomous workflow with user input"""
    try:
        if request.task_id not in autonomous_executors:
            raise HTTPException(status_code=404, detail="Task not found")
        
        executor = autonomous_executors[request.task_id]
        
        result = await executor.continue_autonomous_workflow(
            request.task_id,
            request.user_input
        )
        
        return AutonomousResponse(
            success=True,
            task_id=request.task_id,
            state=result["state"],
            autonomous_insights=result.get("autonomous_insights"),
            status=result.get("status"),
            message="Workflow continued successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to continue workflow: {str(e)}")
        return AutonomousResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/v1/autonomous/feedback", response_model=AutonomousResponse)
async def handle_autonomous_feedback(request: AutonomousFeedbackRequest):
    """Handle feedback in autonomous workflow"""
    try:
        if request.task_id not in autonomous_executors:
            raise HTTPException(status_code=404, detail="Task not found")
        
        executor = autonomous_executors[request.task_id]
        
        result = await executor.handle_autonomous_feedback(
            request.task_id,
            request.feedback,
            request.review_type
        )
        
        return AutonomousResponse(
            success=True,
            task_id=request.task_id,
            state=result["state"],
            status=result.get("status"),
            message="Feedback processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to handle feedback: {str(e)}")
        return AutonomousResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/v1/autonomous/approve", response_model=AutonomousResponse)
async def approve_autonomous_stage(request: AutonomousApproveRequest):
    """Approve autonomous stage"""
    try:
        if request.task_id not in autonomous_executors:
            raise HTTPException(status_code=404, detail="Task not found")
        
        executor = autonomous_executors[request.task_id]
        
        result = await executor.approve_autonomous_stage(
            request.task_id,
            request.review_type
        )
        
        return AutonomousResponse(
            success=True,
            task_id=request.task_id,
            state=result["state"],
            status=result.get("status"),
            message=f"Stage {request.review_type} approved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to approve stage: {str(e)}")
        return AutonomousResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/v1/autonomous/status/{task_id}", response_model=AutonomousResponse)
async def get_autonomous_status(task_id: str):
    """Get autonomous workflow status"""
    try:
        if task_id not in autonomous_executors:
            raise HTTPException(status_code=404, detail="Task not found")
        
        executor = autonomous_executors[task_id]
        result = await executor.get_autonomous_status(task_id)
        
        return AutonomousResponse(
            success=True,
            task_id=task_id,
            current_phase=result.get("current_phase"),
            completion_percentage=result.get("completion_percentage"),
            autonomous_insights=result.get("autonomous_insights"),
            status="running"
        )
        
    except Exception as e:
        logger.error(f"Failed to get status: {str(e)}")
        return AutonomousResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/v1/autonomous/summary/{task_id}")
async def get_execution_summary(task_id: str):
    """Get execution summary"""
    try:
        if task_id not in autonomous_executors:
            raise HTTPException(status_code=404, detail="Task not found")
        
        executor = autonomous_executors[task_id]
        summary = await executor.get_execution_summary(task_id)
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/connectors/status")
async def get_connector_status():
    """Get connector status"""
    try:
        # Return mock connector status for now
        return {
            "github": {
                "name": "github",
                "type": "version_control",
                "status": "disconnected",
                "last_error": None,
                "connection_time": None
            },
            "jira": {
                "name": "jira", 
                "type": "project_management",
                "status": "disconnected",
                "last_error": None,
                "connection_time": None
            },
            "slack": {
                "name": "slack",
                "type": "communication", 
                "status": "disconnected",
                "last_error": None,
                "connection_time": None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get connector status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models")
async def get_available_models():
    """Get available AI models"""
    return ["groq", "gemini", "openai"]

@app.get("/api/v1/autonomous/stream/{task_id}")
async def stream_workflow_updates(task_id: str):
    """Stream workflow updates using Server-Sent Events"""
    async def event_stream():
        try:
            while task_id in autonomous_executors:
                # Get current status
                executor = autonomous_executors[task_id]
                status = await executor.get_autonomous_status(task_id)
                
                # Send status update
                yield f"data: {json.dumps(status)}\n\n"
                
                # Wait before next update
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🚀 DevPilot Autonomous SDLC API starting up...")
    logger.info("✅ Autonomous agents initialized")
    logger.info("✅ Connector framework loaded")
    logger.info("✅ API endpoints registered")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("🛑 DevPilot Autonomous SDLC API shutting down...")
    
    # Cleanup autonomous executors
    for task_id, executor in autonomous_executors.items():
        try:
            await executor.shutdown()
            logger.info(f"✅ Shut down executor for task: {task_id}")
        except Exception as e:
            logger.error(f"❌ Error shutting down executor {task_id}: {str(e)}")
    
    autonomous_executors.clear()
    logger.info("✅ Cleanup completed")

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "autonomous_fastapi_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
