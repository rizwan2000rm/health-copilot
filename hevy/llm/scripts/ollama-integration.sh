#!/bin/bash

# Ollama + Hevy MCP Server Integration Script
# This script starts Ollama with the Hevy MCP server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER_PATH="$(dirname "$SCRIPT_DIR")/../mcp/dist/index.js"
OLLAMA_MODEL="llama3.2:3b"
OLLAMA_HOST="http://localhost:11434"

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  Ollama + Hevy MCP Integration${NC}"
    echo -e "${PURPLE}================================${NC}"
    echo ""
}

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

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        print_error "Ollama is not installed. Please install it first:"
        print_status "  brew install ollama"
        exit 1
    fi
    
    print_success "Ollama found ✓"
    
    # Check if MCP server exists
    if [ ! -f "$MCP_SERVER_PATH" ]; then
        print_error "MCP server not found at: $MCP_SERVER_PATH"
        print_status "Please build the MCP server first:"
        print_status "  npm run build"
        exit 1
    fi
    
    print_success "MCP server found ✓"
    
    # Check if Hevy API is running
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        print_success "Hevy API server is running ✓"
    else
        print_warning "Hevy API server is not running on port 3000"
        print_status "Please start the Hevy API server first:"
        print_status "  cd ../api && npm start"
    fi
}

# Start Ollama service
start_ollama() {
    print_step "Starting Ollama service..."
    
    # Check if Ollama is already running
    if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
        print_success "Ollama is already running ✓"
    else
        print_status "Starting Ollama service..."
        brew services start ollama
        
        # Wait for Ollama to start
        for i in {1..10}; do
            if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
                print_success "Ollama started successfully ✓"
                break
            fi
            sleep 1
        done
        
        if [ $i -eq 10 ]; then
            print_error "Failed to start Ollama"
            exit 1
        fi
    fi
}

# Check if model is available
check_model() {
    print_step "Checking model availability..."
    
    if ollama list | grep -q "$OLLAMA_MODEL"; then
        print_success "Model $OLLAMA_MODEL is available ✓"
    else
        print_warning "Model $OLLAMA_MODEL not found"
        print_status "Pulling model..."
        ollama pull "$OLLAMA_MODEL"
        print_success "Model pulled successfully ✓"
    fi
}

# Start MCP server
start_mcp_server() {
    print_step "Starting MCP server..."
    
    # Check if MCP server is already running
    if pgrep -f "node.*dist/index.js" > /dev/null; then
        print_success "MCP server is already running ✓"
    else
        print_status "Starting MCP server..."
        cd "$(dirname "$SCRIPT_DIR")/../mcp"
        nohup node dist/index.js > logs/ollama-integration.log 2>&1 &
        MCP_PID=$!
        
        # Wait for MCP server to start
        sleep 3
        
        # Check if process is still running
        if ps -p "$MCP_PID" > /dev/null 2>&1; then
            print_success "MCP server started with PID: $MCP_PID ✓"
        else
            print_error "Failed to start MCP server"
            print_status "Check logs: tail -f logs/ollama-integration.log"
            exit 1
        fi
    fi
}

# Test integration
test_integration() {
    print_step "Testing integration..."
    
    # Test Ollama API
    if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
        print_success "Ollama API is accessible ✓"
    else
        print_error "Ollama API is not accessible"
        exit 1
    fi
    
    # Test MCP server
    if pgrep -f "node.*dist/index.js" > /dev/null; then
        print_success "MCP server is running ✓"
    else
        print_error "MCP server is not running"
        exit 1
    fi
}

# Show usage instructions
show_usage() {
    print_step "Integration complete! Here's how to use it:"
    echo ""
    echo -e "${GREEN}1.${NC} Chat with Ollama using the MCP server:"
    echo -e "   ${CYAN}ollama run $OLLAMA_MODEL --mcp-server $MCP_SERVER_PATH${NC}"
    echo ""
    echo -e "${GREEN}2.${NC} Or use the provided chat script:"
    echo -e "   ${CYAN}./scripts/chat.sh${NC}"
    echo ""
    echo -e "${GREEN}3.${NC} Example conversation:"
    echo -e "   ${CYAN}User:${NC} Show me my recent workouts"
    echo -e "   ${CYAN}User:${NC} What exercises did I do last week?"
    echo -e "   ${CYAN}User:${NC} Give me workout statistics for this month"
    echo ""
    echo -e "${GREEN}4.${NC} Check logs:"
    echo -e "   ${CYAN}tail -f logs/ollama-integration.log${NC}"
    echo ""
    echo -e "${YELLOW}Note:${NC} The MCP server provides access to your Hevy workout data"
    echo ""
}

# Main function
main() {
    print_header
    
    check_prerequisites
    echo ""
    
    start_ollama
    echo ""
    
    check_model
    echo ""
    
    start_mcp_server
    echo ""
    
    test_integration
    echo ""
    
    show_usage
}

# Run main function
main "$@"
