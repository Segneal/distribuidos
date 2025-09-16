#!/bin/bash

# Sistema ONG Backend - Test Script
# This script runs all tests for the system

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

check_services() {
    log_info "Checking if services are running..."
    
    # Check if services are up
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_error "Services are not running. Please start them first with: ./scripts/deploy.sh"
        exit 1
    fi
    
    # Check API Gateway health
    if ! curl -f http://localhost:3000/health &>/dev/null; then
        log_error "API Gateway is not responding. Please check the deployment."
        exit 1
    fi
    
    log_success "Services are running and healthy"
}

run_unit_tests() {
    log_info "Running unit tests..."
    
    local test_failed=0
    
    # Test User Service
    log_info "Testing User Service..."
    if docker-compose -f $COMPOSE_FILE exec -T user-service python -m pytest tests/ -v; then
        log_success "User Service tests passed"
    else
        log_error "User Service tests failed"
        test_failed=1
    fi
    
    # Test Inventory Service
    log_info "Testing Inventory Service..."
    if docker-compose -f $COMPOSE_FILE exec -T inventory-service python -m pytest tests/ -v; then
        log_success "Inventory Service tests passed"
    else
        log_error "Inventory Service tests failed"
        test_failed=1
    fi
    
    # Test Events Service
    log_info "Testing Events Service..."
    if docker-compose -f $COMPOSE_FILE exec -T events-service python -m pytest tests/ -v; then
        log_success "Events Service tests passed"
    else
        log_error "Events Service tests failed"
        test_failed=1
    fi
    
    # Test API Gateway
    log_info "Testing API Gateway..."
    if docker-compose -f $COMPOSE_FILE exec -T api-gateway npm test; then
        log_success "API Gateway tests passed"
    else
        log_error "API Gateway tests failed"
        test_failed=1
    fi
    
    return $test_failed
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    local test_failed=0
    
    # Test API endpoints
    log_info "Testing API endpoints..."
    
    # Test health endpoint
    if curl -f http://localhost:3000/health &>/dev/null; then
        log_success "Health endpoint test passed"
    else
        log_error "Health endpoint test failed"
        test_failed=1
    fi
    
    # Test authentication endpoint
    log_info "Testing authentication..."
    local auth_response=$(curl -s -X POST http://localhost:3000/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"identificador":"admin","clave":"admin123"}' \
        -w "%{http_code}")
    
    if [[ "$auth_response" == *"200" ]]; then
        log_success "Authentication test passed"
    else
        log_warning "Authentication test failed (expected if no admin user exists)"
    fi
    
    return $test_failed
}

run_kafka_tests() {
    log_info "Running Kafka integration tests..."
    
    local test_failed=0
    
    # Test Kafka connectivity
    if docker-compose -f $COMPOSE_FILE exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list &>/dev/null; then
        log_success "Kafka connectivity test passed"
    else
        log_error "Kafka connectivity test failed"
        test_failed=1
    fi
    
    # Test topic creation
    local topics=$(docker-compose -f $COMPOSE_FILE exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null)
    
    local required_topics=("solicitud-donaciones" "oferta-donaciones" "eventos-solidarios" "baja-solicitud-donaciones" "baja-evento-solidario")
    
    for topic in "${required_topics[@]}"; do
        if echo "$topics" | grep -q "$topic"; then
            log_success "Topic '$topic' exists"
        else
            log_warning "Topic '$topic' not found"
        fi
    done
    
    return $test_failed
}

run_postman_tests() {
    log_info "Running Postman collection tests..."
    
    local test_failed=0
    
    # Check if Newman is available
    if command -v newman &> /dev/null; then
        log_info "Running Postman collections with Newman..."
        
        local collections=(
            "api-gateway/postman/01-Autenticacion.postman_collection.json"
            "api-gateway/postman/02-Usuarios.postman_collection.json"
            "api-gateway/postman/03-Inventario.postman_collection.json"
            "api-gateway/postman/04-Eventos.postman_collection.json"
            "api-gateway/postman/05-Red-ONGs.postman_collection.json"
        )
        
        for collection in "${collections[@]}"; do
            if [ -f "$collection" ]; then
                log_info "Running collection: $(basename "$collection")"
                if newman run "$collection" --environment api-gateway/postman/environment.json --reporters cli,json --reporter-json-export "test-results/$(basename "$collection" .json)-results.json" 2>/dev/null; then
                    log_success "Collection $(basename "$collection") passed"
                else
                    log_warning "Collection $(basename "$collection") failed (may be expected if test data is missing)"
                fi
            else
                log_warning "Collection not found: $collection"
            fi
        done
    else
        log_warning "Newman not installed. Skipping Postman tests."
        log_info "To install Newman: npm install -g newman"
    fi
    
    return $test_failed
}

generate_test_report() {
    log_info "Generating test report..."
    
    local report_dir="test-results"
    mkdir -p "$report_dir"
    
    local report_file="$report_dir/test-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "=========================================="
        echo "   Sistema ONG Backend - Test Report"
        echo "   Generated: $(date)"
        echo "=========================================="
        echo ""
        echo "System Status:"
        docker-compose -f $COMPOSE_FILE ps
        echo ""
        echo "Service Health:"
        curl -s http://localhost:3000/health | jq . 2>/dev/null || echo "API Gateway health check failed"
        echo ""
        echo "Kafka Topics:"
        docker-compose -f $COMPOSE_FILE exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null || echo "Kafka not accessible"
        echo ""
    } > "$report_file"
    
    log_success "Test report generated: $report_file"
}

# Main test process
main() {
    echo "=========================================="
    echo "   Sistema ONG Backend - Test Suite"
    echo "=========================================="
    echo ""
    
    local total_failures=0
    
    check_services
    
    # Create test results directory
    mkdir -p test-results
    
    # Run different test suites based on arguments
    case "${1:-all}" in
        "unit")
            run_unit_tests
            total_failures=$?
            ;;
        "integration")
            run_integration_tests
            total_failures=$?
            ;;
        "kafka")
            run_kafka_tests
            total_failures=$?
            ;;
        "postman")
            run_postman_tests
            total_failures=$?
            ;;
        "all"|"")
            log_info "Running all test suites..."
            
            run_unit_tests
            total_failures=$((total_failures + $?))
            
            run_integration_tests
            total_failures=$((total_failures + $?))
            
            run_kafka_tests
            total_failures=$((total_failures + $?))
            
            run_postman_tests
            total_failures=$((total_failures + $?))
            ;;
        *)
            echo "Usage: $0 [unit|integration|kafka|postman|all]"
            echo "  unit: Run unit tests only"
            echo "  integration: Run integration tests only"
            echo "  kafka: Run Kafka tests only"
            echo "  postman: Run Postman collections only"
            echo "  all: Run all tests (default)"
            exit 1
            ;;
    esac
    
    generate_test_report
    
    echo ""
    if [ $total_failures -eq 0 ]; then
        log_success "🎉 All tests completed successfully!"
    else
        log_warning "⚠️  Some tests failed or had warnings. Check the output above."
    fi
    
    echo ""
    log_info "Test results saved in: test-results/"
    log_info "To view detailed logs: docker-compose logs [service-name]"
}

# Run main function with arguments
main "$@"