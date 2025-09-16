#!/bin/bash

# Sistema ONG Backend - Reset Script
# This script completely resets the environment

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

confirm_reset() {
    echo ""
    log_warning "⚠️  This will completely reset the environment:"
    echo "   - Stop all containers"
    echo "   - Remove all containers and volumes"
    echo "   - Remove all images"
    echo "   - Clean up networks"
    echo "   - Remove test results"
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Reset cancelled"
        exit 0
    fi
}

stop_services() {
    log_info "Stopping all services..."
    
    docker-compose -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true
    
    log_success "Services stopped"
}

remove_containers() {
    log_info "Removing containers..."
    
    # Remove all project containers
    docker-compose -f $COMPOSE_FILE down --volumes --remove-orphans 2>/dev/null || true
    
    # Remove any remaining containers with our prefix
    docker ps -a --filter "name=ong-" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
    
    log_success "Containers removed"
}

remove_images() {
    log_info "Removing images..."
    
    # Remove project images
    docker images --filter "reference=*ong*" --format "{{.ID}}" | xargs -r docker rmi -f 2>/dev/null || true
    
    # Remove dangling images
    docker image prune -f 2>/dev/null || true
    
    log_success "Images removed"
}

remove_volumes() {
    log_info "Removing volumes..."
    
    # Remove project volumes
    docker volume ls --filter "name=sistema-ong-backend" --format "{{.Name}}" | xargs -r docker volume rm 2>/dev/null || true
    
    # Remove dangling volumes
    docker volume prune -f 2>/dev/null || true
    
    log_success "Volumes removed"
}

cleanup_networks() {
    log_info "Cleaning up networks..."
    
    # Remove unused networks
    docker network prune -f 2>/dev/null || true
    
    log_success "Networks cleaned up"
}

cleanup_files() {
    log_info "Cleaning up local files..."
    
    # Remove test results
    rm -rf test-results/ 2>/dev/null || true
    
    # Remove log files
    rm -rf logs/ 2>/dev/null || true
    
    # Remove temporary files
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Local files cleaned up"
}

system_cleanup() {
    log_info "Performing system cleanup..."
    
    # Clean up Docker system
    docker system prune -af --volumes 2>/dev/null || true
    
    log_success "System cleanup completed"
}

show_status() {
    log_info "Current Docker status:"
    echo ""
    echo "Containers:"
    docker ps -a --filter "name=ong-" 2>/dev/null || echo "No containers found"
    echo ""
    echo "Images:"
    docker images --filter "reference=*ong*" 2>/dev/null || echo "No images found"
    echo ""
    echo "Volumes:"
    docker volume ls --filter "name=sistema-ong-backend" 2>/dev/null || echo "No volumes found"
    echo ""
    echo "Networks:"
    docker network ls --filter "name=sistema-ong-backend" 2>/dev/null || echo "No networks found"
}

# Main reset process
main() {
    echo "=========================================="
    echo "   Sistema ONG Backend - Reset Environment"
    echo "=========================================="
    
    if [ "${1:-}" != "--force" ]; then
        confirm_reset
    fi
    
    echo ""
    log_info "Starting reset process..."
    
    stop_services
    remove_containers
    remove_volumes
    remove_images
    cleanup_networks
    cleanup_files
    
    if [ "${1:-}" = "--deep" ] || [ "${2:-}" = "--deep" ]; then
        system_cleanup
    fi
    
    echo ""
    log_success "🧹 Environment reset completed!"
    echo ""
    show_status
    
    echo ""
    log_info "To start fresh, run: ./scripts/deploy.sh"
    log_info "To see what was cleaned up, check the output above"
}

# Handle script arguments
case "${1:-}" in
    "--force")
        log_info "Forcing reset without confirmation..."
        main --force
        ;;
    "--deep")
        log_info "Performing deep reset with system cleanup..."
        main --deep
        ;;
    "--force-deep")
        log_info "Forcing deep reset without confirmation..."
        main --force --deep
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [--force] [--deep] [--force-deep]"
        echo "  --force: Skip confirmation prompt"
        echo "  --deep: Perform deep cleanup including system prune"
        echo "  --force-deep: Force deep cleanup without confirmation"
        exit 1
        ;;
esac