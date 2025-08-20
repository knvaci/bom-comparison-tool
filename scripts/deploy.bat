@echo off
echo 🚀 Starting BOM Comparison Tool deployment...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Stop existing containers if running
echo 🛑 Stopping existing containers...
docker-compose down 2>nul

REM Build containers
echo 🔨 Building containers...
docker-compose build --no-cache

REM Start services
echo 🚀 Starting services...
docker-compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check service status
echo 🔍 Checking service status...
docker-compose ps

echo.
echo 🎉 Deployment complete!
echo 📊 BOM Comparison Tool is now available at: http://localhost
echo.
echo 🔧 Management commands:
echo   View logs:     docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart:       docker-compose restart
echo.
echo 📁 Data is persisted in Docker volumes
echo 📝 Logs are available in ./logs/nginx/

pause