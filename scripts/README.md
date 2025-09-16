# Sistema ONG Backend - Deployment Scripts

This directory contains scripts to automate deployment, testing, and management of the Sistema ONG Backend.

## Available Scripts

### Deployment Scripts

#### `deploy.sh` / `deploy.bat`
Automates the complete deployment of the system.

**Usage:**
```bash
# Linux/Mac
./scripts/deploy.sh [clean|quick]

# Windows
scripts\deploy.bat
```

**Options:**
- `clean`: Performs clean deployment with system prune
- `quick`: Quick deployment without rebuild (Linux only)

**What it does:**
1. Checks system requirements (Docker, Docker Compose)
2. Sets up environment variables
3. Cleans up existing containers
4. Builds all services
5. Starts infrastructure (MySQL, Kafka, Zookeeper)
6. Starts microservices (User, Inventory, Events)
7. Starts API Gateway
8. Performs health checks
9. Shows deployment status

#### `stop.sh` / `stop.bat`
Stops all services gracefully.

**Usage:**
```bash
# Linux/Mac
./scripts/stop.sh [clean]

# Windows
scripts\stop.bat [clean]
```

**Options:**
- `clean`: Also cleans up resources (networks, orphaned containers)

### Testing Scripts

#### `test.sh` / `test.bat`
Runs comprehensive test suite.

**Usage:**
```bash
# Linux/Mac
./scripts/test.sh [unit|integration|kafka|postman|all]

# Windows
scripts\test.bat
```

**Test Types:**
- `unit`: Unit tests for all services
- `integration`: API endpoint integration tests
- `kafka`: Kafka connectivity and topic tests
- `postman`: Postman collection tests (requires Newman)
- `all`: All test types (default)

**What it tests:**
1. Service health checks
2. Unit tests for all microservices
3. API Gateway functionality
4. Kafka integration
5. Database connectivity
6. gRPC service communication

### Maintenance Scripts

#### `reset.sh`
Completely resets the environment (Linux/Mac only).

**Usage:**
```bash
./scripts/reset.sh [--force] [--deep] [--force-deep]
```

**Options:**
- `--force`: Skip confirmation prompt
- `--deep`: Perform deep cleanup including system prune
- `--force-deep`: Force deep cleanup without confirmation

**What it does:**
1. Stops all containers
2. Removes containers and volumes
3. Removes images
4. Cleans up networks
5. Removes test results and temporary files
6. Optional: System-wide Docker cleanup

## Prerequisites

### System Requirements
- Docker 20.10+
- Docker Compose 2.0+
- curl (for health checks)
- jq (optional, for JSON formatting)

### For Postman Tests
- Newman CLI: `npm install -g newman`

### For Linux/Mac Scripts
- Bash shell
- Standard Unix utilities (grep, awk, etc.)

## Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit environment variables:**
   ```bash
   # Required changes
   JWT_SECRET=your_secure_jwt_secret_minimum_32_characters
   MYSQL_ROOT_PASSWORD=your_secure_root_password
   DB_PASSWORD=your_secure_db_password
   
   # Optional changes
   ORGANIZATION_ID=your-organization-id
   NODE_ENV=production  # for production deployment
   ```

## Quick Start

### First Time Setup
```bash
# 1. Clone repository and navigate to project
cd sistema-ong-backend

# 2. Copy and edit environment file
cp .env.example .env
# Edit .env with your configuration

# 3. Deploy the system
./scripts/deploy.sh

# 4. Run tests to verify deployment
./scripts/test.sh
```

### Daily Development Workflow
```bash
# Start services
./scripts/deploy.sh quick

# Run tests
./scripts/test.sh

# Stop services
./scripts/stop.sh

# Reset environment (if needed)
./scripts/reset.sh
```

## Service URLs

After successful deployment:

- **API Gateway:** http://localhost:3000
- **API Documentation:** http://localhost:3000/api-docs
- **Health Check:** http://localhost:3000/health
- **MySQL:** localhost:3306
- **Kafka:** localhost:9092

### gRPC Services
- **User Service:** localhost:50051
- **Inventory Service:** localhost:50052
- **Events Service:** localhost:50053

## Troubleshooting

### Common Issues

#### Services won't start
```bash
# Check Docker daemon
docker info

# Check logs
docker-compose logs [service-name]

# Reset environment
./scripts/reset.sh --force
./scripts/deploy.sh
```

#### Port conflicts
```bash
# Check what's using the ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :3306
netstat -tulpn | grep :9092

# Stop conflicting services or change ports in docker-compose.yml
```

#### Database connection issues
```bash
# Check MySQL logs
docker-compose logs mysql

# Verify database initialization
docker-compose exec mysql mysql -u ong_user -p ong_sistema -e "SHOW TABLES;"
```

#### Kafka issues
```bash
# Check Kafka logs
docker-compose logs kafka

# List topics
docker-compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

# Reset Kafka data
./scripts/reset.sh
./scripts/deploy.sh
```

### Health Checks

#### Manual Health Checks
```bash
# API Gateway
curl http://localhost:3000/health

# Database
docker-compose exec mysql mysqladmin ping -h localhost

# Kafka
docker-compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list
```

#### Service Status
```bash
# All services
docker-compose ps

# Specific service logs
docker-compose logs -f [service-name]

# Resource usage
docker stats
```

## Script Customization

### Adding Custom Tests
Edit `test.sh` and add your test functions:

```bash
run_custom_tests() {
    log_info "Running custom tests..."
    # Add your test logic here
}
```

### Modifying Deployment
Edit `deploy.sh` to customize the deployment process:

```bash
# Add custom initialization steps
custom_setup() {
    log_info "Running custom setup..."
    # Add your setup logic here
}
```

### Environment-Specific Configuration
Create environment-specific scripts:

```bash
# scripts/deploy-production.sh
export NODE_ENV=production
export JWT_SECRET=$(cat /etc/secrets/jwt-secret)
./scripts/deploy.sh
```

## Security Considerations

1. **Never commit .env files** with real credentials
2. **Change default passwords** in production
3. **Use strong JWT secrets** (minimum 32 characters)
4. **Limit network exposure** in production
5. **Regular security updates** for base images
6. **Monitor logs** for suspicious activity

## Performance Tuning

### Resource Limits
Add resource limits to docker-compose.yml:

```yaml
services:
  api-gateway:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

### Database Optimization
Tune MySQL configuration for your workload:

```yaml
mysql:
  environment:
    - MYSQL_INNODB_BUFFER_POOL_SIZE=256M
    - MYSQL_MAX_CONNECTIONS=100
```

### Kafka Optimization
Adjust Kafka settings for your message volume:

```yaml
kafka:
  environment:
    - KAFKA_NUM_PARTITIONS=3
    - KAFKA_DEFAULT_REPLICATION_FACTOR=1
```

## Monitoring and Logging

### Log Management
```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f api-gateway

# Save logs to file
docker-compose logs > system-logs-$(date +%Y%m%d).log
```

### Monitoring Setup
Consider adding monitoring tools:

- **Prometheus + Grafana** for metrics
- **ELK Stack** for log aggregation
- **Jaeger** for distributed tracing

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec mysql mysqldump -u root -p ong_sistema > backup-$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T mysql mysql -u root -p ong_sistema < backup-20240115.sql
```

### Volume Backup
```bash
# Backup volumes
docker run --rm -v sistema-ong-backend_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql-backup-$(date +%Y%m%d).tar.gz /data
```

## Contributing

When adding new scripts:

1. Follow the existing naming convention
2. Add proper error handling
3. Include logging with appropriate levels
4. Update this README
5. Test on both Linux and Windows (if applicable)
6. Add usage examples