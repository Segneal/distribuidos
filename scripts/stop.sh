#!/bin/bash

# Sistema ONG Backend - Stop Script
# This script stops all services gracefully

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"

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

stop_services() {
    log_info "Stopping all services..."
    
    # Stop all services gracefully
    docker-compose -f $COMPOSE_FILE down
    
    log_success "All services stopped"
}

cleanup_resources() {
    log_info "Cleaning up resources..."
    
    # Remove orphaned containers
    docker-compose -f $COMPOSE_FILE down --remove-orphans
    
    # Remove unused networks
    docker network prune -f
    
    log_success "Resources cleaned up"
}

show_status() {
    log_info "Current status:"
    docker-compose -f $COMPOSE_FILE ps
}

# Main stop process
main() {
    echo "=========================================="
    echo "   Sistema ONG Backend - Stop Services"
    echo "=========================================="
    echo ""
    
    stop_services
    
    if [ "${1:-}" = "clean" ]; then
        cleanup_resources
    fi
    
    echo ""
    log_success "🛑 Services stopped successfully!"
    echo ""
    show_status
    
    echo ""
    log_info "To start services again, run: ./scripts/deploy.sh"
}

# Handle script arguments
case "${1:-}" in
    "clean")
        log_info "Stopping services with cleanup..."
        main clean
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [clean]"
        echo "  clean: Stop services and clean up resources"
        exit 1
        ;;
esac