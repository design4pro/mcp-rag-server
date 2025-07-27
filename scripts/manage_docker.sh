#!/bin/bash

# MCP RAG Server Docker Management Script
# This script provides easy management of the MCP RAG Server Docker services

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "[INFO] Loaded environment variables from .env file"
else
    echo "[WARNING] .env file not found. Using default environment variables."
fi

# Default values
COMPOSE_FILE="docker/docker-compose.yml"
PROJECT_NAME="mcp-rag"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
}

# Function to start services
start_services() {
    print_header "Starting MCP RAG Server services..."
    check_docker
    check_docker_compose
    
    # Use --env-file to explicitly load .env file
    docker-compose -f "$COMPOSE_FILE" --env-file .env up -d
    
    if [ $? -eq 0 ]; then
        print_status "Services started successfully"
        print_status "Waiting for services to be ready..."
        sleep 5
        show_status
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Function to stop services
stop_services() {
    print_header "Stopping MCP RAG Server services..."
    docker-compose -f "$COMPOSE_FILE" down
    
    if [ $? -eq 0 ]; then
        print_status "Services stopped successfully"
    else
        print_error "Failed to stop services"
        exit 1
    fi
}

# Function to restart services
restart_services() {
    print_header "Restarting MCP RAG Server services..."
    stop_services
    sleep 2
    start_services
}

# Function to show service status
show_status() {
    print_header "Service status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    print_header "Health checks:"
    
    # Check Qdrant health
    if docker-compose -f "$COMPOSE_FILE" ps qdrant | grep -q "healthy"; then
        print_status "✅ Qdrant is healthy"
    else
        print_warning "❌ Qdrant health check failed"
    fi
    
    # Check MCP RAG Server health
    if docker-compose -f "$COMPOSE_FILE" ps mcp-rag-server | grep -q "healthy"; then
        print_status "✅ MCP RAG Server is healthy"
    else
        print_warning "❌ MCP RAG Server health check failed"
    fi
}

# Function to show logs
show_logs() {
    print_header "Showing logs for all services..."
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Function to show logs for a specific service
show_service_logs() {
    local service_name=$1
    if [ -z "$service_name" ]; then
        print_error "Please specify a service name (e.g., qdrant, mcp-rag-server)"
        exit 1
    fi
    
    print_header "Showing logs for $service_name..."
    docker-compose -f "$COMPOSE_FILE" logs -f "$service_name"
}

# Function to build Docker image
build_image() {
    print_header "Building Docker image..."
    docker-compose -f "$COMPOSE_FILE" build
    
    if [ $? -eq 0 ]; then
        print_status "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to rebuild Docker image from scratch
rebuild_image() {
    print_header "Rebuilding Docker image from scratch..."
    
    # Stop services if running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_warning "Stopping running services..."
        stop_services
    fi
    
    # Remove existing image
    print_status "Removing existing Docker image..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    if [ $? -eq 0 ]; then
        print_status "Docker image rebuilt successfully"
        
        # Ask if user wants to start services
        read -p "Do you want to start the services now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            start_services
        fi
    else
        print_error "Failed to rebuild Docker image"
        exit 1
    fi
}

# Function to clean up Docker resources
cleanup() {
    print_header "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (optional)
    read -p "Do you want to remove unused volumes? This will delete all data! (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
        print_warning "All data has been removed!"
    fi
    
    print_status "Cleanup completed"
}

# Function to show environment information
show_env() {
    print_header "Environment Information:"
    echo "Project Name: $PROJECT_NAME"
    echo "Compose File: $COMPOSE_FILE"
    echo "Docker Version: $(docker --version)"
    echo "Docker Compose Version: $(docker-compose --version)"
    
    print_header "Key Environment Variables:"
    echo "MCP_GEMINI_API_KEY: ${MCP_GEMINI_API_KEY:0:10}..."  # Show first 10 chars
    echo "MCP_SERVER_PORT: ${MCP_SERVER_PORT:-8000}"
    echo "MCP_COLLECTION: ${MCP_COLLECTION:-not set}"
    echo "MCP_PROJECT_NAMESPACE: ${MCP_PROJECT_NAMESPACE:-not set}"
    echo "MCP_USER_ID: ${MCP_USER_ID:-default}"
}

# Function to show volume information
show_volumes() {
    print_header "Volume Information:"
    
    # List all volumes
    docker volume ls | grep "$PROJECT_NAME" || echo "No volumes found"
    
    # Show volume details
    print_header "Volume Details:"
    for volume in $(docker volume ls -q | grep "$PROJECT_NAME"); do
        echo "📁 $volume"
        echo "   Size: $(docker run --rm -v $volume:/data alpine du -sh /data 2>/dev/null || echo 'unknown')"
        
        # Check for specific files
        if [[ $volume == *"mem0"* ]]; then
            echo "   Contains: $(docker run --rm -v $volume:/data alpine find /data -type f | wc -l) files, $(docker run --rm -v $volume:/data alpine find /data -type d | wc -l) directories"
            if docker run --rm -v $volume:/data alpine test -f /data/memories.json; then
                echo "   📄 memories.json exists"
            fi
        elif [[ $volume == *"qdrant"* ]]; then
            echo "   Contains: $(docker run --rm -v $volume:/data alpine find /data -type f | wc -l) files, $(docker run --rm -v $volume:/data alpine find /data -type d | wc -l) directories"
            echo "   🗄️  Qdrant collections exist"
        fi
        echo ""
    done
}

# Function to show help
show_help() {
    echo "MCP RAG Server Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Start all services"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  status          Show service status and health checks"
    echo "  logs            Show logs for all services"
    echo "  logs-service    Show logs for a specific service (e.g., qdrant, mcp-rag-server)"
    echo "  build           Build Docker image (with cache)"
    echo "  rebuild         Rebuild Docker image from scratch (no cache)"
    echo "  cleanup         Clean up Docker resources (containers, images, volumes)"
    echo "  env             Show environment information"
    echo "  volumes         Show volume information and data"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 logs-service qdrant      # Show Qdrant logs"
    echo "  $0 rebuild                  # Rebuild image from scratch"
    echo ""
}

# Main script logic
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    logs-service)
        show_service_logs "$2"
        ;;
    build)
        build_image
        ;;
    rebuild)
        rebuild_image
        ;;
    cleanup)
        cleanup
        ;;
    env)
        show_env
        ;;
    volumes)
        show_volumes
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 