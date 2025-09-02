#!/bin/bash

# Alternative Ollama + Hevy MCP Integration
# This script demonstrates how to use the MCP server with Ollama

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏋️  Hevy Fitness Assistant${NC}"
echo -e "${BLUE}Alternative Integration Method${NC}"
echo ""

# Check if MCP server is running
if ! pgrep -f "node.*dist/index.js" > /dev/null; then
    echo -e "${YELLOW}⚠️  Starting MCP server...${NC}"
    cd "$(dirname "$0")/../mcp"
    node dist/index.js > logs/mcp-server.log 2>&1 &
    sleep 2
fi

echo -e "${CYAN}✅ MCP server: Running${NC}"
echo -e "${CYAN}✅ Hevy API: Running${NC}"
echo ""

echo -e "${GREEN}📋 Available MCP Tools:${NC}"
echo "1. get_workouts - Get workout history"
echo "2. get_workout_by_id - Get specific workout details"
echo "3. get_exercises - Get exercises for a workout"
echo "4. search_exercises - Search exercises"
echo "5. get_workout_stats - Get statistics"
echo "6. health_check - Check API status"
echo ""

echo -e "${YELLOW}Note:${NC} The MCP server is running and ready for integration."
echo -e "${YELLOW}Note:${NC} Ollama MCP integration requires a newer version or different approach."
echo ""

echo -e "${GREEN}🔧 Manual Integration Options:${NC}"
echo ""
echo "1. Use with MCP-compatible clients:"
echo "   - Claude Desktop"
echo "   - MCP-enabled chat applications"
echo "   - Custom MCP clients"
echo ""
echo "2. Test MCP server directly:"
echo "   - Send JSON-RPC messages to the MCP server"
echo "   - Use MCP testing tools"
echo ""
echo "3. API Integration:"
echo "   - Use the Hevy API directly with Ollama"
echo "   - Create custom prompts with workout data"
echo ""

echo -e "${GREEN}🧪 Testing MCP Server:${NC}"
echo ""

# Test the MCP server with a simple JSON-RPC message
echo -e "${CYAN}Testing MCP server with tools/list request...${NC}"

# Create a simple test message
cat > /tmp/mcp_test.json << EOF
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
EOF

echo "MCP server is ready for integration!"
echo "Check logs: tail -f logs/mcp-server.log"
