# Health Coach

Being fit and healthy is easy, and most of the time we make it too complicated that has to be, that is why I built this health coach. Health Coach help me you plan minimalistic workout routines (using Hevy as a workout tracking tool) it can also help you with sleep and steps planning.

My idea of fitness following the minimalism principle is as follows:

1. Simple Workout Routines - 45 mins strength training + 15 mins cardio
2. Sleep Optimization - 7-9 hours of sleep everyday with proper routine
3. Steps Tracking - Gradually building a habit of walking upto 10,000-12,000 steps per day
4. Nutrition (Coming Soon) - No calorie counting but focusing on better food choices. Grilled chicken over fried chicken, zero sugar drinks over sugary drinks etc

[Health Coach Demo](https://drive.google.com/file/d/1BXxQBdg-OFj2EhvZ8n32th7-qB-_yt6f/view)

## Features

- 📅 Weekly workout planning
- 🤖 AI-powered recommendations and coaching for workouts, sleep and steps
- 📚 Knowledge base with fitness minimalistic training research papers and guides
- 🏋️‍♂️ Hevy Workout Tracking and Management

## Project Overview

This project consists of following components:

1. **AI Fitness Coach Agent** (`agent/`) - The main application providing AI-powered fitness coaching
2. **Hevy MCP Server** (`hevy-mcp/`) - MCP server for integrating with Hevy workout tracking API
3. **Health Coach App** (`ui/`) - React Native application for interacting with the AI Fitness Coach Agent and Hevy MCP Server
4. **Chroma DB** (`chromadb/`) - Chroma DB for storing and querying embeddings of research content

## Prerequisites

- Python 3.13+ (for hevy-mcp) / Python 3.8+ (for agent)
- OpenAI Key or [Ollama](https://ollama.ai/) installed and running
- Hevy API key (for workout tracking features)
- [uv](https://github.com/astral-sh/uv) package manager (for hevy-mcp)

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd health-copilot
```

### 2. Configure Environment Variables

Create a `.env` file in the `agent/` directory:

#### For Hevy API Integration

```bash
echo "HEVY_API_KEY=your_hevy_api_key_here" > agent/.env
```

#### For OpenAI Integration

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > agent/.env
```

### 3. Set Up Hevy MCP Server

```bash
cd hevy-mcp

# Install dependencies using uv
uv sync
```

### 4. Set Up AI Fitness Coach Agent

The agent uses a virtual environment (`.venv` is already present):

```bash
cd agent

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Run AI Fitness Coach

```bash
# Navigate to agent directory
cd agent

# Activate virtual environment
source .venv/bin/activate

# Run the main application
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Usage

#### Standalone Hevy MCP Integration

```json
{
  "mcpServers": {
    "hevy": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/health-copilot/hevy-mcp/",
        "run",
        "app.py"
      ],
      "env": {
        "HEVY_API_KEY": "your_hevy_api_key_here"
      }
    }
  }
}
```

#### Using React Native Client:

```bash
# Navigate to agent directory
cd ui

# Install dependencies
npm install

# Start the application
EXPO_PUBLIC_AGENT_URL=http://192.168.xxx.xx:8000 npm run start
```
