#!/bin/bash

# Hevy Fitness Chat Script
# Interactive chat with Ollama using Hevy workout data

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER_PATH="$(dirname "$SCRIPT_DIR")/../mcp/dist/index.js"
OLLAMA_MODEL="llama3.2:3b"

echo -e "${GREEN}🏋️  Hevy Fitness Assistant${NC}"
echo -e "${BLUE}Chat with your workout data using Ollama + MCP${NC}"
echo ""

# Check if MCP server is running
if ! pgrep -f "node.*dist/index.js" > /dev/null; then
    echo -e "${YELLOW}⚠️  MCP server is not running. Starting it...${NC}"
    cd "$(dirname "$SCRIPT_DIR")/../mcp"
    nohup node dist/index.js > logs/chat.log 2>&1 &
    sleep 2
fi

# Check if Hevy API is running
if ! curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Hevy API server is not running on port 3000${NC}"
    echo "Please start it first: cd ../api && npm start"
    exit 1
fi

echo -e "${CYAN}✅ MCP server: Running${NC}"
echo -e "${CYAN}✅ Hevy API: Running${NC}"
echo -e "${CYAN}✅ Ollama model: $OLLAMA_MODEL${NC}"
echo ""

echo -e "${GREEN}💬 Starting chat session...${NC}"
echo -e "${YELLOW}Type 'quit' to exit${NC}"
echo ""

# Try starting Ollama with MCP server. If unsupported, fall back to manual mode.
if ollama run "$OLLAMA_MODEL" --mcp-server "$MCP_SERVER_PATH"; then
    exit 0
else
    echo -e "${YELLOW}⚠️  Ollama does not support --mcp-server on your version.${NC}"
    echo -e "${BLUE}Switching to manual chat mode using Hevy API context...${NC}"
    echo ""

    # Manual chat loop with Hevy API context
    while true; do
        echo -ne "${GREEN}You:${NC} "
        IFS= read -r USER_INPUT
        if [ "$USER_INPUT" = "quit" ] || [ "$USER_INPUT" = "exit" ]; then
            echo -e "${CYAN}👋 Exiting chat.${NC}"
            break
        fi

        # Fetch recent workouts as context (uses jq if available)
        if command -v jq >/dev/null 2>&1; then
            WORKOUT_CTX=$(curl -s http://localhost:3000/api/workouts | jq -c '.workouts[0:5]')
        else
            WORKOUT_CTX=$(curl -s http://localhost:3000/api/workouts)
        fi

        PROMPT="You are a fitness assistant. Use the following recent workout data as context to help the user. Be concise and actionable.\n\nRecentWorkouts: ${WORKOUT_CTX}\n\nUser: ${USER_INPUT}"

        echo -e "${CYAN}🤖 Assistant:${NC}"
        ollama run "$OLLAMA_MODEL" "$PROMPT"
        echo ""
    done
fi
