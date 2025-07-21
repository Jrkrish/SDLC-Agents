#!/usr/bin/env python3
"""
DevPilot Backend Startup Script
Enhanced to work with autonomous SDLC system
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set default environment variables if not already set
if not os.getenv("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = "demo_key_for_testing"

if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "demo_key_for_testing"

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "demo_key_for_testing"

print("🚀 Starting DevPilot Backend Server...")
print(f"📁 Project Root: {project_root}")
print(f"🔑 GROQ API Key: {'Set' if os.getenv('GROQ_API_KEY') else 'Not Set'}")
print(f"🔑 Gemini API Key: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not Set'}")
print(f"🔑 OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not Set'}")

try:
    # Import and run the FastAPI app
    print("📦 Loading FastAPI application...")
    
    # Try to import the existing FastAPI app
    from src.dev_pilot.api.fastapi_app import app
    
    print("✅ FastAPI application loaded successfully!")
    print("🌐 Starting server on http://0.0.0.0:8000")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("📖 Alternative docs at: http://localhost:8000/redoc")
    print("\n" + "="*60)
    print("🤖 DevPilot Autonomous SDLC Backend")
    print("="*60)
    
    # Run the server
    uvicorn.run(
        "src.dev_pilot.api.fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("🔧 Attempting to run with basic configuration...")
    
    # Fallback: create a minimal FastAPI app
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    fallback_app = FastAPI(
        title="DevPilot API - Fallback Mode",
        description="Basic DevPilot API running in fallback mode",
        version="1.0.0"
    )
    
    fallback_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @fallback_app.get("/")
    async def root():
        return {
            "message": "DevPilot API - Fallback Mode",
            "status": "running",
            "note": "Some features may be limited in fallback mode"
        }
    
    @fallback_app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "fallback"}
    
    print("⚠️ Running in fallback mode with limited functionality")
    uvicorn.run(fallback_app, host="0.0.0.0", port=8000)
    
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    print(f"🔍 Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
