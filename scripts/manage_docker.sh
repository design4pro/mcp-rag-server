#!/bin/bash

# MCP RAG Server Docker Management Script
# Usage: ./manage_docker.sh [start|stop|restart|status|logs|build]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to build Docker image
build_image() {
    print_status "Building MCP RAG Server Docker image..."
    cd "$PROJECT_DIR/docker"
    
    if docker build -t mcp-rag-server .; then
        print_status "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to start services
start_services() {
    print_status "Starting MCP RAG Server with Docker Compose..."
    cd "$PROJECT_DIR/docker"
    
    # Check if services are already running
    if docker-compose ps | grep -q "Up"; then
        print_warning "Services are already running"
        return 1
    fi
    
    # Start services
    if docker-compose up -d; then
        print_status "Services started successfully"
        print_status "Waiting for services to be ready..."
        
        # Wait for services to be healthy
        local count=0
        while [ $count -lt 30 ]; do
            if docker-compose ps | grep -q "healthy"; then
                print_status "All services are healthy"
                show_status
                return 0
            fi
            sleep 2
            ((count++))
        done
        
        print_warning "Services may not be fully ready yet"
        show_status
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping MCP RAG Server services..."
    cd "$PROJECT_DIR/docker"
    
    if docker-compose down; then
        print_status "Services stopped successfully"
    else
        print_error "Failed to stop services"
        exit 1
    fi
}

# Function to restart services
restart_services() {
    print_status "Restarting MCP RAG Server services..."
    stop_services
    sleep 2
    start_services
}

# Function to show status
show_status() {
    print_status "Service status:"
    cd "$PROJECT_DIR/docker"
    docker-compose ps
    
    echo ""
    print_status "Health checks:"
    
    # Check Qdrant
    if curl -s http://localhost:6333/ > /dev/null 2>&1; then
        print_status "✅ Qdrant is healthy"
    else
        print_warning "❌ Qdrant is not responding"
    fi
    
    # Check MCP RAG Server
    local response=$(curl -s -w "%{http_code}" http://localhost:8001/mcp 2>/dev/null)
    local status_code="${response: -3}"
    
    if [ "$status_code" = "406" ]; then
        print_status "✅ MCP RAG Server is healthy (MCP endpoint responding)"
    else
        print_warning "❌ MCP RAG Server health check failed (Status: $status_code)"
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing logs (press Ctrl+C to exit)..."
    cd "$PROJECT_DIR/docker"
    docker-compose logs -f
}

# Function to show specific service logs
show_service_logs() {
    local service="${2:-mcp-rag-server}"
    print_status "Showing logs for $service (press Ctrl+C to exit)..."
    cd "$PROJECT_DIR/docker"
    docker-compose logs -f "$service"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    cd "$PROJECT_DIR/docker"
    
    # Stop and remove containers
    docker-compose down
    
    # Remove volumes (optional - uncomment if you want to clear data)
    # docker-compose down -v
    
    # Remove images
    docker rmi mcp-rag-server 2>/dev/null || true
    
    print_status "Cleanup completed"
}

# Function to show environment info
show_env() {
    print_status "Environment information:"
    echo "Project directory: $PROJECT_DIR"
    echo "Docker Compose file: $PROJECT_DIR/docker/docker-compose.yml"
    echo "Dockerfile: $PROJECT_DIR/docker/Dockerfile"
    echo ""
    
    if [ -f "$PROJECT_DIR/.env" ]; then
        print_status "Environment variables:"
        grep -E "^(GEMINI_API_KEY|QDRANT_URL|MEM0_|FASTMCP_|LOG_LEVEL)=" "$PROJECT_DIR/.env" | sed 's/=.*/=***/'
    else
        print_warning ".env file not found"
    fi
}

# Main script logic
case "${1:-}" in
    start)
        check_docker
        start_services
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        restart_services
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs
        ;;
    logs-service)
        check_docker
        show_service_logs "$@"
        ;;
    build)
        check_docker
        build_image
        ;;
    cleanup)
        check_docker
        cleanup
        ;;
    env)
        show_env
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|logs-service|build|cleanup|env}"
        echo ""
        echo "Commands:"
        echo "  start        - Start the MCP RAG Server with Docker Compose"
        echo "  stop         - Stop the MCP RAG Server services"
        echo "  restart      - Restart the MCP RAG Server services"
        echo "  status       - Show service status and health checks"
        echo "  logs         - Show logs from all services (follow mode)"
        echo "  logs-service - Show logs from specific service (e.g., logs-service qdrant)"
        echo "  build        - Build the Docker image"
        echo "  cleanup      - Clean up Docker resources (containers, images)"
        echo "  env          - Show environment information"
        echo ""
        echo "Examples:"
        echo "  $0 start                    # Start all services"
        echo "  $0 logs-service mcp-rag-server  # Show MCP server logs"
        echo "  $0 logs-service qdrant      # Show Qdrant logs"
        exit 1
        ;;
esac 