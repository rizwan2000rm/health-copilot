#!/bin/bash

# Hevy MCP Server Setup Script
# This script sets up the complete MCP server environment

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
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
HEVY_API_DIR="$PROJECT_DIR/api"

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  Hevy MCP Server Setup${NC}"
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

# Check system requirements
check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        print_status "Visit: https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_success "Node.js $(node --version) ✓"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    print_success "npm $(npm --version) ✓"
    
    # Check if Hevy API is running
    print_status "Checking Hevy API server..."
    if curl -s http://localhost:3000/health > /dev/null 2>&1; then
        print_success "Hevy API server is running ✓"
    else
        print_warning "Hevy API server is not running on port 3000"
        print_status "Please start the Hevy API server first:"
        print_status "  cd $HEVY_API_DIR && npm start"
        print_status "Continuing with setup..."
    fi
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    
    cd "$SCRIPT_DIR"
    
    if [ ! -f "package.json" ]; then
        print_error "package.json not found in current directory"
        exit 1
    fi
    
    print_status "Installing npm packages..."
    npm install
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully ✓"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Build the project
build_project() {
    print_step "Building the project..."
    
    cd "$SCRIPT_DIR"
    
    print_status "Running TypeScript build..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Project built successfully ✓"
    else
        print_error "Build failed"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_step "Creating necessary directories..."
    
    cd "$SCRIPT_DIR"
    
    # Create logs directory
    if [ ! -d "logs" ]; then
        mkdir -p logs
        print_success "Created logs directory ✓"
    else
        print_status "Logs directory already exists ✓"
    fi
    
    # Create dist directory if it doesn't exist
    if [ ! -d "dist" ]; then
        mkdir -p dist
        print_status "Created dist directory ✓"
    fi
}

# Set up environment
setup_environment() {
    print_step "Setting up environment..."
    
    cd "$SCRIPT_DIR"
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            print_status "Creating .env file from template..."
            cp env.example .env
            print_success "Created .env file ✓"
            print_warning "Please review and update .env file with your configuration"
        else
            print_warning "No env.example file found. Please create .env manually."
        fi
    else
        print_status ".env file already exists ✓"
    fi
    
    # Make scripts executable
    if [ -f "scripts/start.sh" ]; then
        chmod +x scripts/start.sh
        print_success "Made start script executable ✓"
    fi
}

# Test the setup
test_setup() {
    print_step "Testing the setup..."
    
    cd "$SCRIPT_DIR"
    
    # Test if the server can start
    print_status "Testing server startup..."
    
    # Start server in background
    timeout 10s npm start > logs/setup-test.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 3
    
    # Check if server is running
    if ps -p "$SERVER_PID" > /dev/null 2>&1; then
        print_success "Server started successfully ✓"
        
        # Stop the test server
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
        
        print_success "Server stopped successfully ✓"
    else
        print_warning "Server startup test inconclusive - check logs/setup-test.log"
    fi
}

# Show next steps
show_next_steps() {
    print_step "Setup complete! Here are your next steps:"
    echo ""
    echo -e "${GREEN}1.${NC} Start the MCP server:"
    echo -e "   ${CYAN}cd $SCRIPT_DIR${NC}"
    echo -e "   ${CYAN}npm start${NC}"
    echo ""
    echo -e "${GREEN}2.${NC} Or use the management script:"
    echo -e "   ${CYAN}./scripts/start.sh start${NC}"
    echo ""
    echo -e "${GREEN}3.${NC} Check server status:"
    echo -e "   ${CYAN}./scripts/start.sh status${NC}"
    echo ""
    echo -e "${GREEN}4.${NC} View logs:"
    echo -e "   ${CYAN}./scripts/start.sh logs${NC}"
    echo ""
    echo -e "${GREEN}5.${NC} Test the server:"
    echo -e "   ${CYAN}node test-mcp.js${NC}"
    echo ""
    echo -e "${GREEN}6.${NC} For production deployment:"
    echo -e "   ${CYAN}docker-compose up -d${NC}"
    echo ""
    echo -e "${YELLOW}Note:${NC} Make sure the Hevy API server is running on port 3000"
    echo ""
}

# Main setup function
main() {
    print_header
    
    print_status "Setting up Hevy MCP Server..."
    print_status "Project directory: $SCRIPT_DIR"
    print_status "Hevy API directory: $HEVY_API_DIR"
    echo ""
    
    check_requirements
    echo ""
    
    create_directories
    echo ""
    
    install_dependencies
    echo ""
    
    build_project
    echo ""
    
    setup_environment
    echo ""
    
    test_setup
    echo ""
    
    show_next_steps
}

# Run setup
main "$@"
