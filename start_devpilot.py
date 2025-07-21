#!/usr/bin/env python3
"""
DevPilot Enterprise Startup Script
Run this script to launch the DevPilot Enterprise platform
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the DevPilot banner"""
    banner = """
    ████████╗ ███████╗██╗   ██╗██████╗ ██╗██╗      ██████╗ ████████╗
    ╚══██╔══╝ ██╔════╝██║   ██║██╔══██╗██║██║     ██╔═══██╗╚══██╔══╝
       ██║    █████╗  ██║   ██║██████╔╝██║██║     ██║   ██║   ██║   
       ██║    ██╔══╝  ╚██╗ ██╔╝██╔═══╝ ██║██║     ██║   ██║   ██║   
       ██║    ███████╗ ╚████╔╝ ██║     ██║███████╗╚██████╔╝   ██║   
       ╚═╝    ╚══════╝  ╚═══╝  ╚═╝     ╚═╝╚══════╝ ╚═════╝    ╚═╝   
                                                                      
    🚀 DevPilot Enterprise - AI-Powered SDLC Platform 🚀
    
    ✨ Features:
    • 40+ Enterprise Connectors (Jira, GitHub, Slack, AWS, etc.)
    • Advanced Security & Authentication
    • Real-time Analytics & Monitoring
    • AI-Powered SDLC Automation
    • Enterprise-grade Performance
    
    🔗 Visit: http://localhost:8502
    """
    
    print("=" * 80)
    print(banner)
    print("=" * 80)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'streamlit', 'fastapi', 'langchain', 'pandas', 'plotly', 
        'pydantic', 'jose', 'passlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def setup_environment():
    """Setup environment variables"""
    print("\n🔧 Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("""# DevPilot Enterprise Environment Configuration

# AI/LLM API Keys (Add your keys here)
GROQ_API_KEY=your-groq-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Connector API Keys (Optional - configure in UI)
JIRA_API_TOKEN=your-jira-api-token-here
GITHUB_API_TOKEN=your-github-token-here
SLACK_BOT_TOKEN=your-slack-bot-token-here

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
""")
        print("✅ Created .env file. Please add your API keys.")
    else:
        print("✅ .env file already exists.")

def start_redis():
    """Try to start Redis if available"""
    print("\n🔴 Checking Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
        return True
    except:
        print("⚠️  Redis not available. Some features may be limited.")
        print("   To enable full functionality, install and start Redis:")
        print("   • Docker: docker run -p 6379:6379 redis")
        print("   • Local: Install Redis server")
        return False

def start_application():
    """Start the DevPilot Enterprise application"""
    print("\n🚀 Starting DevPilot Enterprise...")
    print("   Opening browser at: http://localhost:8502")
    print("   Press Ctrl+C to stop the application\n")
    
    try:
        # Start the Streamlit application
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_streamlit.py",
            "--server.port", "8502",
            "--server.address", "0.0.0.0"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n\n👋 DevPilot Enterprise stopped. Thank you for using DevPilot!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("Try running: streamlit run app_streamlit.py")

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check Redis
    start_redis()
    
    print("\n🎯 Login Credentials for Demo:")
    print("   Username: admin")
    print("   Password: admin")
    print("   Or click 'Demo Mode' for quick access")
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
