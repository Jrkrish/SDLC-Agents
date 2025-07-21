#!/usr/bin/env python3
"""
Simple DevPilot FastAPI Backend
A minimal working version to get started quickly
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
import uuid
import json

app = FastAPI(
    title="DevPilot API - Simple Backend",
    description="AI-powered SDLC API (Simplified Version)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class SDLCRequest(BaseModel):
    project_name: Optional[str] = None
    requirements: Optional[Union[str, list[str]]] = None
    task_id: Optional[str] = None
    next_node: Optional[str] = None
    status: Optional[str] = None
    feedback: Optional[str] = None

class SDLCResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory storage (for demonstration)
project_states = {}

@app.get("/")
async def root():
    return {
        "message": "Welcome to DevPilot API - Simple Backend",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "status": "running"
    }

@app.post("/api/v1/sdlc/start", response_model=SDLCResponse)
async def start_sdlc(request: SDLCRequest):
    try:
        # Generate task ID
        task_id = f"sdlc-session-{uuid.uuid4().hex[:8]}"
        
        # Create mock project state
        state = {
            "project_name": request.project_name,
            "current_step": "requirements_gathering",
            "status": "initialized",
            "created_at": "2025-01-19T16:00:00Z",
            "steps_completed": ["project_initialization"],
            "next_steps": ["requirements_analysis", "user_stories_creation"],
            "progress": 10
        }
        
        # Store in memory
        project_states[task_id] = state
        
        return SDLCResponse(
            status="success",
            message=f"SDLC process started successfully for project: {request.project_name}",
            task_id=task_id,
            state=state
        )
    except Exception as e:
        return SDLCResponse(
            status="error",
            message="Failed to start SDLC process",
            error=str(e)
        )

@app.post("/api/v1/sdlc/user_stories", response_model=SDLCResponse)
async def generate_user_stories(request: SDLCRequest):
    try:
        if not request.task_id or request.task_id not in project_states:
            raise HTTPException(status_code=404, detail="Task ID not found")
        
        # Get existing state
        state = project_states[request.task_id].copy()
        
        # Mock user stories generation
        requirements = request.requirements if isinstance(request.requirements, str) else str(request.requirements)
        
        user_stories = [
            f"As a user, I want to {requirements[:50]}... so that I can achieve my goals",
            "As an admin, I want to manage the system configuration",
            "As a developer, I want to integrate with external APIs",
            "As a stakeholder, I want to view project progress and reports"
        ]
        
        # Update state
        state.update({
            "current_step": "user_stories_review",
            "requirements": requirements,
            "user_stories": user_stories,
            "steps_completed": ["project_initialization", "requirements_analysis"],
            "next_steps": ["design_document_creation", "system_architecture"],
            "progress": 25
        })
        
        project_states[request.task_id] = state
        
        return SDLCResponse(
            status="success",
            message="User stories generated successfully",
            task_id=request.task_id,
            state=state
        )
    except Exception as e:
        return SDLCResponse(
            status="error",
            message="Failed to generate user stories",
            error=str(e)
        )

@app.post("/api/v1/sdlc/progress_flow", response_model=SDLCResponse)
async def progress_flow(request: SDLCRequest):
    try:
        if not request.task_id or request.task_id not in project_states:
            raise HTTPException(status_code=404, detail="Task ID not found")
        
        state = project_states[request.task_id].copy()
        
        # Mock progress based on current step
        current_progress = state.get("progress", 0)
        new_progress = min(current_progress + 15, 100)
        
        # Simulate different steps
        step_mapping = {
            "user_stories_review": {
                "step": "design_document_creation",
                "completed": ["project_initialization", "requirements_analysis", "user_stories_creation"],
                "next": ["system_design", "database_design"]
            },
            "design_document_creation": {
                "step": "code_implementation",
                "completed": ["project_initialization", "requirements_analysis", "user_stories_creation", "system_design"],
                "next": ["coding", "unit_testing"]
            },
            "code_implementation": {
                "step": "security_analysis",
                "completed": ["project_initialization", "requirements_analysis", "user_stories_creation", "system_design", "coding"],
                "next": ["security_review", "vulnerability_assessment"]
            }
        }
        
        current_step = state.get("current_step", "user_stories_review")
        next_step_info = step_mapping.get(current_step, {
            "step": "deployment",
            "completed": ["project_initialization", "requirements_analysis", "user_stories_creation", "system_design", "coding", "testing"],
            "next": ["deployment", "monitoring"]
        })
        
        # Add mock outputs based on step
        if "design" in next_step_info["step"]:
            state["design_document"] = "## System Architecture\n\n1. Frontend: React with Material-UI\n2. Backend: FastAPI with Python\n3. Database: PostgreSQL\n4. Deployment: Docker containers"
        elif "code" in next_step_info["step"]:
            state["code_generated"] = "Generated code files:\n- app.py (FastAPI backend)\n- components/Dashboard.tsx (React frontend)\n- models/User.py (Database models)"
        elif "security" in next_step_info["step"]:
            state["security_report"] = "Security Analysis:\n✓ Input validation implemented\n✓ Authentication middleware active\n⚠ Rate limiting recommended\n✓ HTTPS configuration ready"
        
        # Update state
        state.update({
            "current_step": next_step_info["step"],
            "steps_completed": next_step_info["completed"],
            "next_steps": next_step_info["next"],
            "progress": new_progress,
            "feedback_received": request.feedback if request.feedback else "No feedback provided",
            "last_updated": "2025-01-19T16:30:00Z"
        })
        
        project_states[request.task_id] = state
        
        return SDLCResponse(
            status="success",
            message=f"Flow progressed successfully to {next_step_info['step']}",
            task_id=request.task_id,
            state=state
        )
    except Exception as e:
        return SDLCResponse(
            status="error",
            message="Failed to progress flow",
            error=str(e)
        )

@app.get("/api/v1/sdlc/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in project_states:
        raise HTTPException(status_code=404, detail="Task ID not found")
    
    return {
        "task_id": task_id,
        "state": project_states[task_id]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting DevPilot Simple Backend...")
    print("📋 API Documentation: http://localhost:8001/docs")
    print("🔄 Frontend should connect to: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
