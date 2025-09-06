# Health Copilot

An AI-powered fitness coaching application that combines intelligent workout guidance with workout tracking through MCP (Model Context Protocol) integration with Hevy API.

## Project Overview

This project consists of two main components:

1. **AI Fitness Coach Agent** (`agent/`) - The main application providing AI-powered fitness coaching
2. **Hevy MCP Server** (`hevy-mcp/`) - MCP server for integrating with Hevy workout tracking API

## Features

- 🤖 AI-powered fitness coaching using Ollama (llama3.2:3b)
- 📚 Knowledge base with fitness research papers and guides
- 🏋️‍♂️ Workout tracking and management via Hevy API
- 🔧 MCP tool integration for enhanced functionality
- 📊 Workout history and analytics
- 📅 Weekly workout planning

## Prerequisites

- Python 3.13+ (for hevy-mcp) / Python 3.8+ (for agent)
- [Ollama](https://ollama.ai/) installed and running
- [uv](https://github.com/astral-sh/uv) package manager (for hevy-mcp)
- Hevy API key (optional, for workout tracking features)

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd health-copilot
```

### 2. Set Up AI Fitness Coach Agent

The agent uses a virtual environment (`.venv` is already present):

```bash
# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
cd agent
pip install -r requirements.txt
```

### 3. Set Up Hevy MCP Server

```bash
cd hevy-mcp

# Install dependencies using uv
uv sync
```

### 4. Configure Environment Variables

#### For Hevy API Integration

Create a `.env` file in the `agent/` directory to enable workout tracking features:

```bash
echo "HEVY_API_KEY=your_hevy_api_key_here" > agent/.env
```

#### For Claude Desktop Integration

Update the MCP configuration in `hevy-mcp/claude-desktop-config.json`:

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

### 5. Start Ollama

Make sure Ollama is running with the required model:

```bash
ollama serve
ollama pull llama3.2:3b
```

## Running the Application

### Run AI Fitness Coach

```bash
# Activate virtual environment
source .venv/bin/activate

# Navigate to agent directory
cd agent

# Run the main application
python3 main.py
```

### Run Hevy MCP Server

```bash
cd hevy-mcp
uv run app.py
```

## Usage

Once the application is running, you can:

### Available Commands

- `help` - Show available commands
- `stats` - Display system statistics
- `workouts` - Show workout history (requires Hevy API)
- `summary` - Show workout summary (requires Hevy API)
- `create workout` - Create a new workout (requires Hevy API)
- `weekly plan` - Generate personalized weekly plan
- `quit`/`exit`/`q` - Exit the application
