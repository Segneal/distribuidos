@echo off
REM Sistema ONG Backend Setup Script for Windows
REM This script sets up the development environment

echo 🚀 Setting up Sistema ONG Backend...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create environment files from examples
echo 📝 Creating environment files...
copy api-gateway\.env.example api-gateway\.env
copy services\user-service\.env.example services\user-service\.env
copy services\inventory-service\.env.example services\inventory-service\.env
copy services\events-service\.env.example services\events-service\.env

echo ✅ Environment files created. Please review and update them as needed.

REM Install API Gateway dependencies
echo 📦 Installing API Gateway dependencies...
cd api-gateway
call npm install
cd ..

echo 🐳 Starting infrastructure services...
docker-compose up -d mysql zookeeper kafka

echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

echo 🏗️ Building application services...
docker-compose build user-service inventory-service events-service api-gateway

echo 🚀 Starting application services...
docker-compose up -d user-service inventory-service events-service api-gateway

echo ✅ Setup complete!
echo.
echo 🌐 Services are available at:
echo    - API Gateway: http://localhost:3000
echo    - Health Check: http://localhost:3000/health
echo    - MySQL: localhost:3306
echo    - Kafka: localhost:9092
echo.
echo 📚 Next steps:
echo    1. Review and update environment files
echo    2. Check service logs: docker-compose logs -f
echo    3. Test the API endpoints
echo.
echo 🛑 To stop all services: docker-compose down

pause