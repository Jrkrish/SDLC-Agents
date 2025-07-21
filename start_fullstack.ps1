# DevPilot Full Stack Startup Script
# This script starts both the FastAPI backend and React frontend

Write-Host "Starting DevPilot Full Stack Application..." -ForegroundColor Green

# Check if required environment variables are set
if (-not $env:GROQ_API_KEY -and -not $env:GEMINI_API_KEY) {
    Write-Host "Warning: Neither GROQ_API_KEY nor GEMINI_API_KEY environment variables are set." -ForegroundColor Yellow
    Write-Host "Please set at least one of these API keys to use the application." -ForegroundColor Yellow
}

# Start FastAPI backend in a new PowerShell window
Write-Host "Starting FastAPI backend..." -ForegroundColor Blue
Start-Process -FilePath "powershell.exe" -ArgumentList "-Command", "cd 'C:\Saample sdlc\DevPilot'; python app_api.py" -WindowStyle Normal

# Wait a moment for the backend to start
Start-Sleep -Seconds 3

# Start React frontend in a new PowerShell window
Write-Host "Starting React frontend..." -ForegroundColor Blue
Start-Process -FilePath "powershell.exe" -ArgumentList "-Command", "cd 'C:\Saample sdlc\DevPilot\frontend'; npm start" -WindowStyle Normal

Write-Host "Both services are starting..." -ForegroundColor Green
Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`nPress Ctrl+C to stop this script (services will continue running in separate windows)" -ForegroundColor Yellow
Write-Host "To stop services, close the PowerShell windows or use Ctrl+C in each window" -ForegroundColor Yellow

# Keep the script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "Script terminated." -ForegroundColor Red
}
