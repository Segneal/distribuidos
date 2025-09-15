#!/bin/bash

# Sistema ONG Backend Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Sistema ONG Backend..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files from examples
echo "📝 Creating environment files..."
cp api-gateway/.env.example api-gateway/.env
cp services/user-service/.env.example services/user-service/.env
cp services/inventory-service/.env.example services/inventory-service/.env
cp services/events-service/.env.example services/events-service/.env

echo "✅ Environment files created. Please review and update them as needed."

# Install API Gateway dependencies
echo "📦 Installing API Gateway dependencies..."
cd api-gateway
npm install
cd ..

echo "🐳 Starting infrastructure services..."
docker-compose up -d mysql zookeeper kafka

echo "⏳ Waiting for services to be ready..."
sleep 30

echo "🏗️ Building application services..."
docker-compose build user-service inventory-service events-service api-gateway

echo "🚀 Starting application services..."
docker-compose up -d user-service inventory-service events-service api-gateway

echo "✅ Setup complete!"
echo ""
echo "🌐 Services are available at:"
echo "   - API Gateway: http://localhost:3000"
echo "   - Health Check: http://localhost:3000/health"
echo "   - MySQL: localhost:3306"
echo "   - Kafka: localhost:9092"
echo ""
echo "📚 Next steps:"
echo "   1. Review and update environment files"
echo "   2. Check service logs: docker-compose logs -f"
echo "   3. Test the API endpoints"
echo ""
echo "🛑 To stop all services: docker-compose down"