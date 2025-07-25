#!/bin/bash

# MCP RAG Server - Service Startup Script
# This script helps start all required services for the RAG server

set -e

echo "🚀 Starting MCP RAG Server Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if Qdrant is already running
check_qdrant() {
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        print_success "Qdrant is already running on http://localhost:6333"
        return 0
    else
        return 1
    fi
}

# Start Qdrant
start_qdrant() {
    print_status "Starting Qdrant vector database..."
    
    if check_qdrant; then
        print_warning "Qdrant is already running"
        return 0
    fi
    
    # Check if Qdrant container is already running
    if docker ps --format "table {{.Names}}" | grep -q "qdrant"; then
        print_success "Qdrant container is already running"
        return 0
    fi
    
    # Start Qdrant in detached mode
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v qdrant_storage:/qdrant/storage \
        qdrant/qdrant
    
    # Wait for Qdrant to be ready
    print_status "Waiting for Qdrant to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:6333/health > /dev/null 2>&1; then
            print_success "Qdrant is ready on http://localhost:6333"
            return 0
        fi
        sleep 1
    done
    
    print_error "Qdrant failed to start within 30 seconds"
    exit 1
}

# Check environment configuration
check_env() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env file not found. Creating from .env.example..."
            cp .env.example .env
            print_warning "Please edit .env file with your Gemini API key before starting the server"
        else
            print_error ".env.example not found. Please create a .env file with your configuration."
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

# Test connections
test_connections() {
    print_status "Testing service connections..."
    
    if command -v python3 &> /dev/null; then
        python3 test_connections.py
    elif command -v python &> /dev/null; then
        python test_connections.py
    else
        print_error "Python not found. Please install Python 3.9+"
        exit 1
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  MCP RAG Server - Service Startup"
    echo "=========================================="
    echo
    
    # Check prerequisites
    check_docker
    check_env
    
    # Start services
    start_qdrant
    
    echo
    print_success "All services started successfully!"
    echo
    
    # Test connections
    test_connections
    
    echo
    echo "=========================================="
    print_success "Services are ready!"
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your Gemini API key"
    echo "2. Start the RAG server: python run_server.py"
    echo "3. Or test connections: python test_connections.py"
    echo "=========================================="
}

# Run main function
main "$@" 