#!/bin/bash

# Hevy Workout Analysis with Ollama
# This script demonstrates how to use Ollama with your workout data

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏋️  Hevy Workout Analysis with Ollama${NC}"
echo ""

# Check if Hevy API is running
if ! curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Hevy API server is not running on port 3000${NC}"
    echo "Please start it first: cd ../api && npm start"
    exit 1
fi

echo -e "${CYAN}✅ Hevy API: Running${NC}"

# Get recent workout data
echo -e "${BLUE}📊 Fetching your recent workout data...${NC}"
WORKOUT_DATA=$(curl -s http://localhost:3000/api/workouts | jq -c '.workouts[0:5]')

if [ "$WORKOUT_DATA" = "null" ] || [ -z "$WORKOUT_DATA" ]; then
    echo -e "${YELLOW}⚠️  No workout data found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found workout data${NC}"
echo ""

# Create analysis prompt
PROMPT="You are a fitness expert and personal trainer. Analyze this workout data and provide insights:

$WORKOUT_DATA

Please provide:
1. Training pattern analysis (frequency, consistency, variety)
2. Exercise selection observations
3. Progress indicators
4. Recommendations for improvement
5. Suggestions for next week's training

Be specific and actionable in your advice."

echo -e "${CYAN}🤖 Sending to Ollama for analysis...${NC}"
echo ""

# Run with Ollama
ollama run llama3.2:3b "$PROMPT"
