import streamlit as st
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Set page config early
st.set_page_config(
    page_title="SDLC Agents - AI-Powered Development",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check if running on Hugging Face Spaces
IS_HF_SPACE = os.getenv('SPACE_ID') is not None

if IS_HF_SPACE:
    # Show Hugging Face Spaces info
    st.sidebar.info("""
    🚀 **Running on Hugging Face Spaces**
    
    This is a demo version with core AI features.
    For full enterprise features, deploy on your infrastructure.
    """)

try:
    # Import and load the main app
    from src.dev_pilot.ui.streamlit_ui.streamlit_app import load_app
    load_app()
except Exception as e:
    st.error(f"""
    🚨 **Application Error**
    
    There was an issue loading the application: {str(e)}
    
    This might be due to missing dependencies or configuration issues.
    Please check the requirements and try again.
    """)
    
    # Show basic info as fallback
    st.header("SDLC Agents - AI-Powered Software Development")
    st.write("""
    This application helps automate the Software Development Lifecycle using AI agents.
    
    **Features:**
    - Automated User Story Generation
    - Design Document Creation  
    - AI-Powered Code Generation
    - Test Case Generation
    - Deployment Analysis
    
    **To use this application:**
    1. Select your preferred LLM provider
    2. Enter your API key
    3. Input project requirements
    4. Let AI agents handle the rest!
    """)
