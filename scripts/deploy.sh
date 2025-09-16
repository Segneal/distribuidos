#!/bin/bash

# Sistema ONG Backend - Deployment Script
# This script automates the deployment of the complete system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "System requirements check passed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "Please edit .env file with your configuration before running again."
            log_warning "Especially change JWT_SECRET and database passwords!"
            exit 1
        else
            log_error ".env.example file not found. Cannot create environment file."
            exit 1
        fi
    fi
    
    log_success "Environment setup completed"
}

cleanup_containers() {
    log_info "Cleaning up existing containers..."
    
    # Stop and remove existing containers
    docker-compose -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true
    
    # Remove unused volumes (optional, commented out for safety)
    # docker volume prune -f
    
    log_success "Cleanup completed"
}

build_services() {
    log_info "Building services..."
    
    # Build all services
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    log_success "Services built successfully"
}

start_infrastructure() {
    log_info "Starting infrastructure services..."
    
    # Start database and message broker first
    docker-compose -f $COMPOSE_FILE up -d mysql zookeeper kafka
    
    # Wait for services to be ready
    log_info "Waiting for infrastructure services to be ready..."
    sleep 30
    
    # Check if MySQL is ready
    local retries=0
    local max_retries=30
    while [ $retries -lt $max_retries ]; do
        if docker-compose -f $COMPOSE_FILE exec -T mysql mysqladmin ping -h localhost --silent; then
            log_success "MySQL is ready"
            break
        fi
        log_info "Waiting for MySQL... ($((retries + 1))/$max_retries)"
        sleep 5
        retries=$((retries + 1))
    done
    
    if [ $retries -eq $max_retries ]; then
        log_error "MySQL failed to start within expected time"
        exit 1
    fi
    
    # Check if Kafka is ready
    retries=0
    while [ $retries -lt $max_retries ]; do
        if docker-compose -f $COMPOSE_FILE exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list &>/dev/null; then
            log_success "Kafka is ready"
            break
        fi
        log_info "Waiting for Kafka... ($((retries + 1))/$max_retries)"
        sleep 5
        retries=$((retries + 1))
    done
    
    if [ $retries -eq $max_retries ]; then
        log_error "Kafka failed to start within expected time"
        exit 1
    fi
    
    log_success "Infrastructure services are ready"
}

start_microservices() {
    log_info "Starting microservices..."
    
    # Start gRPC services
    docker-compose -f $COMPOSE_FILE up -d user-service inventory-service events-service
    
    # Wait for services to be ready
    log_info "Waiting for microservices to be ready..."
    sleep 20
    
    log_success "Microservices started"
}

start_api_gateway() {
    log_info "Starting API Gateway..."
    
    # Start API Gateway
    docker-compose -f $COMPOSE_FILE up -d api-gateway
    
    # Wait for API Gateway to be ready
    log_info "Waiting for API Gateway to be ready..."
    sleep 15
    
    # Check if API Gateway is responding
    local retries=0
    local max_retries=20
    while [ $retries -lt $max_retries ]; do
        if curl -f http://localhost:3000/health &>/dev/null; then
            log_success "API Gateway is ready"
            break
        fi
        log_info "Waiting for API Gateway... ($((retries + 1))/$max_retries)"
        sleep 3
        retries=$((retries + 1))
    done
    
    if [ $retries -eq $max_retries ]; then
        log_error "API Gateway failed to start within expected time"
        exit 1
    fi
}

show_status() {
    log_info "Deployment Status:"
    echo ""
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    log_info "Service URLs:"
    echo "  🌐 API Gateway: http://localhost:3000"
    echo "  📚 API Documentation: http://localhost:3000/api-docs"
    echo "  🏥 Health Check: http://localhost:3000/health"
    echo "  🗄️  MySQL: localhost:3306"
    echo "  📨 Kafka: localhost:9092"
    echo ""
    log_info "gRPC Services:"
    echo "  👥 User Service: localhost:50051"
    echo "  📦 Inventory Service: localhost:50052"
    echo "  🎯 Events Service: localhost:50053"
}

# Main deployment process
main() {
    echo "=========================================="
    echo "   Sistema ONG Backend - Deployment"
    echo "=========================================="
    echo ""
    
    check_requirements
    setup_environment
    cleanup_containers
    build_services
    start_infrastructure
    start_microservices
    start_api_gateway
    
    echo ""
    log_success "🎉 Deployment completed successfully!"
    echo ""
    show_status
    
    echo ""
    log_info "To stop all services, run: ./scripts/stop.sh"
    log_info "To view logs, run: docker-compose logs -f [service-name]"
    log_info "To run tests, run: ./scripts/test.sh"
}

# Handle script arguments
case "${1:-}" in
    "clean")
        log_info "Performing clean deployment..."
        cleanup_containers
        docker system prune -f
        main
        ;;
    "quick")
        log_info "Performing quick deployment (no rebuild)..."
        check_requirements
        setup_environment
        docker-compose -f $COMPOSE_FILE up -d
        show_status
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [clean|quick]"
        echo "  clean: Clean deployment with system prune"
        echo "  quick: Quick deployment without rebuild"
        exit 1
        ;;
esac