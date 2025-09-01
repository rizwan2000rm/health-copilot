#!/bin/bash

echo "🏋️  Starting Health Copilot - Hevy Workout API..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start the server
echo "🚀 Starting the API server..."
echo "   The API will be available at: http://localhost:3000"
echo "   Health check: http://localhost:3000/health"
echo "   API docs: http://localhost:3000/api"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start
