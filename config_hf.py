"""
Configuration file for Hugging Face Spaces deployment.
Handles missing dependencies gracefully for demo purposes.
"""

import os
import streamlit as st

# Default configuration for HF Spaces
class HFConfig:
    def __init__(self):
        self.demo_mode = True
        self.enable_connectors = False
        
    def check_dependencies(self):
        """Check which dependencies are available"""
        available_deps = {}
        
        # Check core dependencies
        try:
            import langchain
            available_deps['langchain'] = True
        except ImportError:
            available_deps['langchain'] = False
            
        try:
            import langgraph
            available_deps['langgraph'] = True
        except ImportError:
            available_deps['langgraph'] = False
            
        # Check connector dependencies
        try:
            import boto3
            available_deps['aws'] = True
        except ImportError:
            available_deps['aws'] = False
            
        try:
            import github3
            available_deps['github'] = True
        except ImportError:
            available_deps['github'] = False
            
        return available_deps
    
    def show_demo_notice(self):
        """Show demo mode notice"""
        st.info("""
        🌟 **Welcome to SDLC Agents Demo!**
        
        This is a demonstration version running on Hugging Face Spaces with essential features enabled.
        
        **Available in Demo:**
        - AI-powered user story generation
        - Design document creation
        - Code generation with multiple LLMs
        - Basic workflow management
        
        **For Full Enterprise Features:**
        - Deploy on your own infrastructure
        - Enable enterprise connectors (GitHub, Slack, Jira)
        - Full database and caching support
        - Advanced security features
        
        💡 Get started by entering your API key in the sidebar!
        """)
        
    def get_demo_requirements(self):
        """Return demo project requirements"""
        return [
            "Build a task management web application",
            "Users should be able to create, edit, and delete tasks",
            "Tasks should have priority levels and due dates", 
            "Include user authentication and authorization",
            "Provide dashboard with task analytics",
            "Support team collaboration features",
            "Mobile-responsive design",
            "Export tasks to PDF/CSV formats"
        ]

# Global config instance
hf_config = HFConfig()
