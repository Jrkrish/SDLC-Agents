@echo off
echo.
echo ================================================================================
echo.
echo     🚀 DevPilot Enterprise - AI-Powered SDLC Platform 🚀
echo.
echo     ✨ Features:
echo     • 40+ Enterprise Connectors (Jira, GitHub, Slack, AWS, etc.)
echo     • Advanced Security ^& Authentication  
echo     • Real-time Analytics ^& Monitoring
echo     • AI-Powered SDLC Automation
echo     • Enterprise-grade Performance
echo.
echo     🔗 Visit: http://localhost:8503
echo.
echo ================================================================================
echo.

echo 🚀 Starting DevPilot Enterprise...
echo    Opening browser at: http://localhost:8503
echo    Press Ctrl+C to stop the application
echo.

echo 🎯 Login Credentials for Demo:
echo    Username: admin
echo    Password: admin
echo    Or click 'Demo Mode' for quick access
echo.

streamlit run app_streamlit.py --server.port 8503

pause
