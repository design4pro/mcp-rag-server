#!/bin/bash

# MCP RAG Server Management Script
# Usage: ./manage_server.sh [start|stop|restart|status|logs]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/mcp-rag-server.pid"
LOG_FILE="$PROJECT_DIR/mcp-rag-server.log"

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

# Function to check if server is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Function to start server
start_server() {
    if is_running; then
        print_warning "Server is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_status "Starting MCP RAG Server..."
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Start server in background
           nohup python3 src/run_server_http.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo "$pid" > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if ps -p "$pid" > /dev/null 2>&1; then
        print_status "Server started successfully (PID: $pid)"
        print_status "Logs: $LOG_FILE"
        print_status "Health check: curl http://localhost:8001/mcp/"
        return 0
    else
        print_error "Failed to start server"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop server
stop_server() {
    if ! is_running; then
        print_warning "Server is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_status "Stopping MCP RAG Server (PID: $pid)..."
    
    # Send SIGTERM first
    kill -TERM "$pid" 2>/dev/null
    
    # Wait for graceful shutdown
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
        sleep 1
        ((count++))
    done
    
    # Force kill if still running
    if ps -p "$pid" > /dev/null 2>&1; then
        print_warning "Force killing server..."
        kill -KILL "$pid" 2>/dev/null
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    print_status "Server stopped"
}

# Function to restart server
restart_server() {
    print_status "Restarting MCP RAG Server..."
    stop_server
    sleep 2
    start_server
}

# Function to show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_status "Server is running (PID: $pid)"
        
        # Check if port is listening
        if lsof -i :8001 > /dev/null 2>&1; then
            print_status "Port 8001 is listening"
        else
            print_warning "Port 8001 is not listening"
        fi
        
        # Show recent logs
        if [ -f "$LOG_FILE" ]; then
            print_status "Recent logs:"
            tail -n 5 "$LOG_FILE"
        fi
    else
        print_warning "Server is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        print_error "Log file not found: $LOG_FILE"
    fi
}

# Function to show health
check_health() {
    if is_running; then
        print_status "Checking server health..."
        local response=$(curl -s -w "%{http_code}" http://localhost:8001/mcp/ 2>/dev/null)
        local status_code="${response: -3}"
        
        if [ "$status_code" = "406" ]; then
            print_status "Server is healthy (MCP endpoint responding)"
        else
            print_warning "Server health check failed (Status: $status_code)"
        fi
    else
        print_error "Server is not running"
    fi
}

# Main script logic
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    health)
        check_health
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|health}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the MCP RAG Server"
        echo "  stop    - Stop the MCP RAG Server"
        echo "  restart - Restart the MCP RAG Server"
        echo "  status  - Show server status"
        echo "  logs    - Show server logs (follow mode)"
        echo "  health  - Check server health"
        exit 1
        ;;
esac 