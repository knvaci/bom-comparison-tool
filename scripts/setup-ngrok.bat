@echo off
echo 🌐 Setting up ngrok tunnel for BOM Comparison Tool...
echo.

REM Check if ngrok is installed
where ngrok >nul 2>&1
if errorlevel 1 (
    echo ❌ ngrok is not installed. 
    echo 📥 Please download and install ngrok from: https://ngrok.com/download
    echo.
    echo After installation:
    echo 1. Sign up at https://ngrok.com
    echo 2. Get your authtoken from the dashboard
    echo 3. Run: ngrok config add-authtoken YOUR_TOKEN
    echo 4. Run this script again
    pause
    exit /b 1
)

echo ✅ ngrok found! Starting tunnel...
echo.

REM Start ngrok tunnel
echo 🚀 Creating secure tunnel to localhost:80...
echo.
echo 📧 Share the https://xxxxx.ngrok.app URL with your employees
echo ⚠️  Keep this window open while employees are testing
echo.

ngrok http 80