#!/usr/bin/env python3
"""
Simplified DevPilot Backend for React Integration
Works with the existing React frontend
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="DevPilot SDLC API",
    description="AI-Powered Software Development Lifecycle Platform",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class SDLCRequest(BaseModel):
    project_name: str
    requirements: Optional[str] = None
    task_id: Optional[str] = None
    status: Optional[str] = None
    feedback: Optional[str] = None
    next_node: Optional[str] = None

class SDLCResponse(BaseModel):
    status: str
    message: str
    task_id: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global storage for demo (in production, use a database)
workflows: Dict[str, Dict[str, Any]] = {}

def generate_task_id() -> str:
    """Generate a unique task ID"""
    import uuid
    return f"sdlc-session-{uuid.uuid4().hex[:8]}"

def create_mock_user_stories(requirements: str) -> list:
    """Create mock user stories based on requirements"""
    return [
        {
            "id": 1,
            "title": "User Authentication System",
            "description": f"As a user, I want to be able to register and login to access {requirements}",
            "priority": 1,
            "acceptance_criteria": "Given a new user, when they provide valid registration details, then they should be able to create an account and login"
        },
        {
            "id": 2,
            "title": "Main Feature Implementation",
            "description": f"As a user, I want to use the main features described in: {requirements}",
            "priority": 1,
            "acceptance_criteria": "Given an authenticated user, when they access the main features, then they should work as described in requirements"
        },
        {
            "id": 3,
            "title": "User Dashboard",
            "description": "As a user, I want to have a dashboard to manage my activities",
            "priority": 2,
            "acceptance_criteria": "Given an authenticated user, when they access the dashboard, then they can see and manage their data"
        }
    ]

def create_mock_design_docs() -> Dict[str, str]:
    """Create mock design documents"""
    return {
        "functional": """
# Functional Design Document

## Overview
This document outlines the functional requirements and design for the DevPilot SDLC project.

## User Journey
1. User Registration/Authentication
2. Project Setup
3. Feature Usage
4. Data Management

## Business Rules
- All users must be authenticated
- Data validation at all input points
- Audit trail for all operations

## Integration Requirements
- REST API endpoints
- Database integration
- Third-party service connections
        """,
        "technical": """
# Technical Design Document

## System Architecture
- Frontend: React TypeScript
- Backend: FastAPI Python
- Database: PostgreSQL
- Caching: Redis

## API Design
- RESTful endpoints
- JWT authentication
- Rate limiting
- Error handling

## Database Schema
- Users table
- Projects table
- Activities table
- Audit logs

## Security Considerations
- HTTPS encryption
- Input validation
- SQL injection prevention
- XSS protection
        """
    }

def create_mock_code() -> str:
    """Create mock generated code"""
    return """
# Generated FastAPI Application

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Generated Application")
security = HTTPBearer()

class User(BaseModel):
    id: int
    username: str
    email: str

class Project(BaseModel):
    id: int
    name: str
    description: str
    user_id: int

@app.get("/users", response_model=List[User])
async def get_users():
    # Implementation here
    return []

@app.post("/projects", response_model=Project)
async def create_project(project: Project):
    # Implementation here
    return project

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    """

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DevPilot SDLC API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_workflows": len(workflows)
    }

@app.post("/api/v1/sdlc/start", response_model=SDLCResponse)
async def start_sdlc(request: SDLCRequest):
    """Start SDLC workflow"""
    try:
        task_id = generate_task_id()
        
        # Initialize workflow state
        workflows[task_id] = {
            "project_name": request.project_name,
            "created_at": datetime.now().isoformat(),
            "current_step": "project_initialization",
            "status": "active"
        }
        
        return SDLCResponse(
            status="success",
            message=f"SDLC process started for project: {request.project_name}",
            task_id=task_id,
            state={
                "project_name": request.project_name,
                "next_node": "requirement_collection",
                "progress": 10
            }
        )
        
    except Exception as e:
        return SDLCResponse(
            status="error",
            message="Failed to start SDLC process",
            error=str(e)
        )

@app.post("/api/v1/sdlc/user_stories", response_model=SDLCResponse)
async def generate_user_stories(request: SDLCRequest):
    """Generate user stories"""
    try:
        if request.task_id not in workflows:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        user_stories = create_mock_user_stories(request.requirements or "the application")
        
        # Update workflow state
        workflows[request.task_id].update({
            "user_stories": {"user_stories": user_stories},
            "requirements": request.requirements,
            "current_step": "user_stories_generated"
        })
        
        return SDLCResponse(
            status="success",
            message="User stories generated successfully",
            task_id=request.task_id,
            state={
                "user_stories": {"user_stories": user_stories},
                "requirements": request.requirements,
                "next_node": "review_user_stories",
                "progress": 25
            }
        )
        
    except Exception as e:
        return SDLCResponse(
            status="error",
            message="Failed to generate user stories",
            error=str(e)
        )

@app.post("/api/v1/sdlc/progress_flow", response_model=SDLCResponse)
async def progress_flow(request: SDLCRequest):
    """Progress to next step in the workflow"""
    try:
        if request.task_id not in workflows:
            raise HTTPException(status_code=404, detail="Task not found")
        
        workflow = workflows[request.task_id]
        current_step = workflow.get("current_step", "")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Determine next step and generate appropriate content
        if "user_stories" in current_step or request.next_node == "create_design_documents":
            # Generate design documents
            design_docs = create_mock_design_docs()
            workflow.update({
                "design_documents": design_docs,
                "current_step": "design_documents_generated"
            })
            
            return SDLCResponse(
                status="success",
                message="Design documents generated successfully",
                task_id=request.task_id,
                state={
                    **workflow,
                    "design_documents": design_docs,
                    "next_node": "review_design_documents",
                    "progress": 40
                }
            )
            
        elif "design" in current_step or request.next_node == "generate_code":
            # Generate code
            generated_code = create_mock_code()
            workflow.update({
                "code_generated": generated_code,
                "current_step": "code_generated"
            })
            
            return SDLCResponse(
                status="success",
                message="Code generated successfully",
                task_id=request.task_id,
                state={
                    **workflow,
                    "code_generated": generated_code,
                    "next_node": "code_review",
                    "progress": 60
                }
            )
            
        elif "code" in current_step:
            # Security review
            security_recommendations = """
# Security Analysis Report

## Identified Issues
1. **Authentication**: Implement JWT token validation
2. **Input Validation**: Add proper input sanitization
3. **HTTPS**: Ensure all communications use HTTPS
4. **Database**: Use parameterized queries to prevent SQL injection

## Recommendations
- Implement rate limiting
- Add CORS configuration
- Use environment variables for secrets
- Add logging and monitoring

## Risk Assessment
- **High Priority**: Authentication and input validation
- **Medium Priority**: HTTPS and database security
- **Low Priority**: Additional monitoring features
            """
            
            workflow.update({
                "security_recommendations": security_recommendations,
                "current_step": "security_reviewed"
            })
            
            return SDLCResponse(
                status="success",
                message="Security review completed",
                task_id=request.task_id,
                state={
                    **workflow,
                    "security_recommendations": security_recommendations,
                    "next_node": "write_test_cases",
                    "progress": 75
                }
            )
            
        else:
            # Default progression
            workflow.update({
                "current_step": "deployment_ready",
                "deployment_feedback": "Application ready for deployment with Docker containerization"
            })
            
            return SDLCResponse(
                status="success",
                message="Workflow progressed successfully",
                task_id=request.task_id,
                state={
                    **workflow,
                    "next_node": "deployment",
                    "progress": 90
                }
            )
            
    except Exception as e:
        return SDLCResponse(
            status="error",
            message="Failed to progress workflow",
            error=str(e)
        )

@app.get("/api/v1/sdlc/status/{task_id}")
async def get_workflow_status(task_id: str):
    """Get workflow status"""
    if task_id not in workflows:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        "status": "active",
        "workflow": workflows[task_id]
    }

if __name__ == "__main__":
    print("🚀 Starting DevPilot Backend Server...")
    print("🌐 Server will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔧 Compatible with React frontend on port 3000")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
