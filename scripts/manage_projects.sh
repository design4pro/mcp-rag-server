#!/bin/bash

# MCP RAG Server Multi-Project Management Script
# This script helps manage multiple project configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configurations
PROJECTS=("web-dev" "mobile" "acme")
PORTS=(8001 8002 8003)
QDANT_PORTS=(6333 6334 6336)

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show usage
show_usage() {
    echo "MCP RAG Server Multi-Project Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [PROJECT]"
    echo ""
    echo "Commands:"
    echo "  start [PROJECT]     Start a specific project or all projects"
    echo "  stop [PROJECT]      Stop a specific project or all projects"
    echo "  restart [PROJECT]   Restart a specific project or all projects"
    echo "  status [PROJECT]    Show status of a specific project or all projects"
    echo "  logs [PROJECT]      Show logs for a specific project"
    echo "  build [PROJECT]     Build a specific project or all projects"
    echo "  rebuild [PROJECT]   Rebuild a specific project or all projects"
    echo "  cleanup [PROJECT]   Clean up a specific project or all projects"
    echo "  list                List all available projects"
    echo "  config [PROJECT]    Show configuration for a specific project"
    echo ""
    echo "Projects:"
    echo "  web-dev             Web Development Project (Port 8001)"
    echo "  mobile              Mobile App Project (Port 8002)"
    echo "  acme                Acme Corp Client Project (Port 8003)"
    echo "  all                 All projects"
    echo ""
    echo "Examples:"
    echo "  $0 start web-dev    Start web development project"
    echo "  $0 start all        Start all projects"
    echo "  $0 status           Show status of all projects"
    echo "  $0 logs web-dev     Show logs for web development project"
}

# Function to get project index
get_project_index() {
    local project=$1
    for i in "${!PROJECTS[@]}"; do
        if [[ "${PROJECTS[$i]}" == "$project" ]]; then
            echo $i
            return 0
        fi
    done
    return 1
}

# Function to get compose file path
get_compose_file() {
    local project=$1
    echo "docker/docker-compose.${project}.yml"
}

# Function to check if project is running
is_project_running() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    if docker-compose -f "$compose_file" ps --services --filter "status=running" | grep -q "mcp-rag-server"; then
        return 0
    else
        return 1
    fi
}

# Function to start a project
start_project() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    print_info "Starting $project project..."
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    # Check if project is already running
    if is_project_running "$project"; then
        print_warning "$project project is already running"
        return 0
    fi
    
    # Start the project
    docker-compose -f "$compose_file" up -d
    
    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    if is_project_running "$project"; then
        print_success "$project project started successfully"
    else
        print_error "Failed to start $project project"
        return 1
    fi
}

# Function to stop a project
stop_project() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    print_info "Stopping $project project..."
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    docker-compose -f "$compose_file" down
    print_success "$project project stopped"
}

# Function to restart a project
restart_project() {
    local project=$1
    
    print_info "Restarting $project project..."
    stop_project "$project"
    sleep 2
    start_project "$project"
}

# Function to show project status
show_project_status() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    echo ""
    print_info "Status for $project project:"
    echo "=================================="
    docker-compose -f "$compose_file" ps
    echo ""
}

# Function to show project logs
show_project_logs() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    print_info "Logs for $project project:"
    echo "=================================="
    docker-compose -f "$compose_file" logs --tail=50 -f
}

# Function to build a project
build_project() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    print_info "Building $project project..."
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    docker-compose -f "$compose_file" build
    print_success "$project project built successfully"
}

# Function to rebuild a project
rebuild_project() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    print_info "Rebuilding $project project..."
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    # Stop the project first
    stop_project "$project"
    
    # Remove images and rebuild
    docker-compose -f "$compose_file" down --rmi all --volumes
    docker-compose -f "$compose_file" build --no-cache
    
    print_success "$project project rebuilt successfully"
}

# Function to cleanup a project
cleanup_project() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    print_info "Cleaning up $project project..."
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    docker-compose -f "$compose_file" down --rmi all --volumes
    print_success "$project project cleaned up"
}

# Function to show project configuration
show_project_config() {
    local project=$1
    local compose_file=$(get_compose_file $project)
    
    if [ ! -f "$compose_file" ]; then
        print_error "Compose file not found: $compose_file"
        return 1
    fi
    
    print_info "Configuration for $project project:"
    echo "=========================================="
    
    # Extract and display key configuration
    echo "Project: $project"
    echo "Compose file: $compose_file"
    
    # Get port mapping
    local port_index=$(get_project_index "$project")
    if [ $? -eq 0 ]; then
        echo "Port: ${PORTS[$port_index]}"
        echo "Qdrant Port: ${QDANT_PORTS[$port_index]}"
    fi
    
    # Extract environment variables
    echo ""
    echo "Key Environment Variables:"
    echo "-------------------------"
    grep -E "MCP_COLLECTION|MCP_PROJECT_NAMESPACE|MCP_USER_ID" "$compose_file" | sed 's/^[[:space:]]*- //'
    
    echo ""
}

# Function to list all projects
list_projects() {
    echo "Available Projects:"
    echo "=================="
    
    for i in "${!PROJECTS[@]}"; do
        local project="${PROJECTS[$i]}"
        local port="${PORTS[$i]}"
        local qdrant_port="${QDANT_PORTS[$i]}"
        local compose_file=$(get_compose_file "$project")
        
        echo -n "• $project (Port: $port, Qdrant: $qdrant_port)"
        
        if [ -f "$compose_file" ]; then
            echo -n " [Config: ✅]"
        else
            echo -n " [Config: ❌]"
        fi
        
        if is_project_running "$project"; then
            echo " [Status: 🟢 Running]"
        else
            echo " [Status: 🔴 Stopped]"
        fi
    done
    
    echo ""
    echo "Commands:"
    echo "  $0 start [PROJECT]     - Start a project"
    echo "  $0 stop [PROJECT]      - Stop a project"
    echo "  $0 status [PROJECT]    - Show project status"
    echo "  $0 config [PROJECT]    - Show project configuration"
}

# Main script logic
main() {
    local command=$1
    local project=$2
    
    # Check if command is provided
    if [ -z "$command" ]; then
        show_usage
        exit 1
    fi
    
    # Handle list command
    if [ "$command" = "list" ]; then
        list_projects
        exit 0
    fi
    
    # Handle help command
    if [ "$command" = "help" ] || [ "$command" = "--help" ] || [ "$command" = "-h" ]; then
        show_usage
        exit 0
    fi
    
    # Check if project is provided
    if [ -z "$project" ]; then
        print_error "Project name is required for command: $command"
        echo ""
        show_usage
        exit 1
    fi
    
    # Handle "all" projects
    if [ "$project" = "all" ]; then
        for p in "${PROJECTS[@]}"; do
            case "$command" in
                start)
                    start_project "$p"
                    ;;
                stop)
                    stop_project "$p"
                    ;;
                restart)
                    restart_project "$p"
                    ;;
                status)
                    show_project_status "$p"
                    ;;
                build)
                    build_project "$p"
                    ;;
                rebuild)
                    rebuild_project "$p"
                    ;;
                cleanup)
                    cleanup_project "$p"
                    ;;
                *)
                    print_error "Unknown command: $command"
                    show_usage
                    exit 1
                    ;;
            esac
        done
        exit 0
    fi
    
    # Check if project exists
    if ! get_project_index "$project" > /dev/null; then
        print_error "Unknown project: $project"
        echo ""
        echo "Available projects:"
        for p in "${PROJECTS[@]}"; do
            echo "  • $p"
        done
        exit 1
    fi
    
    # Execute command for specific project
    case "$command" in
        start)
            start_project "$project"
            ;;
        stop)
            stop_project "$project"
            ;;
        restart)
            restart_project "$project"
            ;;
        status)
            show_project_status "$project"
            ;;
        logs)
            show_project_logs "$project"
            ;;
        build)
            build_project "$project"
            ;;
        rebuild)
            rebuild_project "$project"
            ;;
        cleanup)
            cleanup_project "$project"
            ;;
        config)
            show_project_config "$project"
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 