#!/bin/bash

# Hevy MCP Server Startup Script
# This script handles the startup process for the MCP server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/mcp-server.pid"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

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

# Function to check if server is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            # Remove stale PID file
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Function to start the server
start_server() {
    print_status "Starting Hevy MCP Server..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed or not in PATH"
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        exit 1
    fi
    
    # Navigate to project directory
    cd "$PROJECT_DIR"
    
    # Check if dependencies are installed
    if [ ! -d "node_modules" ]; then
        print_status "Installing dependencies..."
        npm install
    fi
    
    # Check if build is needed
    if [ ! -d "dist" ] || [ "src" -nt "dist" ]; then
        print_status "Building project..."
        npm run build
    fi
    
    # Start the server
    print_status "Launching MCP server..."
    nohup npm start > "$LOG_DIR/startup.log" 2>&1 &
    SERVER_PID=$!
    
    # Save PID
    echo "$SERVER_PID" > "$PID_FILE"
    
    # Wait a moment for server to start
    sleep 2
    
    # Check if server started successfully
    if ps -p "$SERVER_PID" > /dev/null 2>&1; then
        print_success "MCP Server started successfully with PID: $SERVER_PID"
        print_status "Logs are being written to: $LOG_DIR/"
        print_status "PID file: $PID_FILE"
    else
        print_error "Failed to start MCP Server"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Function to stop the server
stop_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_status "Stopping MCP Server (PID: $PID)..."
            kill "$PID"
            
            # Wait for process to terminate
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                print_warning "Force killing server process..."
                kill -9 "$PID"
            fi
            
            rm -f "$PID_FILE"
            print_success "MCP Server stopped"
        else
            print_warning "Server not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "No PID file found - server may not be running"
    fi
}

# Function to restart the server
restart_server() {
    print_status "Restarting MCP Server..."
    stop_server
    sleep 2
    start_server
}

# Function to show server status
show_status() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        print_success "MCP Server is running (PID: $PID)"
        
        # Show process info
        ps -p "$PID" -o pid,ppid,cmd,etime,pcpu,pmem
        
        # Show recent logs
        if [ -f "$LOG_DIR/mcp-server.log" ]; then
            print_status "Recent log entries:"
            tail -n 5 "$LOG_DIR/mcp-server.log"
        fi
    else
        print_warning "MCP Server is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_DIR/mcp-server.log" ]; then
        print_status "Showing MCP Server logs:"
        tail -f "$LOG_DIR/mcp-server.log"
    else
        print_warning "No log file found"
    fi
}

# Function to show help
show_help() {
    echo "Hevy MCP Server Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the MCP server"
    echo "  stop      Stop the MCP server"
    echo "  restart   Restart the MCP server"
    echo "  status    Show server status"
    echo "  logs      Show server logs (follow mode)"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start the server"
    echo "  $0 status     # Check server status"
    echo "  $0 logs       # Follow server logs"
}

# Main script logic
case "${1:-start}" in
    start)
        if check_running; then
            print_warning "MCP Server is already running"
            show_status
        else
            start_server
        fi
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
