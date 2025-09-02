# Health Copilot

Transform your health data into an intelligent, personalized fitness co-pilot. This enables LLMs to analyze your training patterns, generate personalized workout plans, and provide data-driven fitness recommendations—all while keeping your data private and local.

## 🎯 Vision & Scope

### Primary Use Case (for now)

**Weekly Workout Planning**: Analyze your current week's workouts and automatically generate next week's workout plan

### Future Expansion

- **Health Data Integration**: Sleep data, step counts, heart rate from Apple Health and other platforms
- **Health Copilot**: Once all your workouts, stress levels, heart rate, spo2, intake/burned calories data is available for querying, copilot can do wonders for you.

## 🏗️ Architecture

This project consists of three main components:

### 1. Hevy API Server (`hevy/api/`)

- **Purpose**: RESTful API server that provides access to workout data
- **Features**:
  - SQLite database with workout and exercise data
  - CSV import functionality
  - Comprehensive workout and exercise endpoints
  - Health monitoring and logging
- **Technology**: Node.js, Express, SQLite3
- **Port**: 3000

### 2. Hevy MCP Server (`hevy/mcp/`)

- **Purpose**: Model Context Protocol (MCP) server for AI integration
- **Features**:
  - Standardized MCP interface for workout data access
  - 6 comprehensive tools for data retrieval and analysis
  - Production-grade error handling and logging
  - TypeScript implementation with validation
  - Docker support for deployment
- **Technology**: TypeScript, MCP SDK, Winston logging
- **Port**: 3001

### 3. Hevy LLM Integration (`hevy/llm/`)

- **Purpose**: LLM (Large Language Model) integration components
- **Features**:
  - Ollama integration for local AI processing
  - Interactive chat with workout data
  - AI-powered workout analysis
  - Alternative integration methods
  - Comprehensive documentation and guides
- **Technology**: Bash scripts, Ollama, Local LLMs
- **Dependencies**: MCP Server, Hevy API

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Hevy workout data (CSV format)

### 1. Start the Hevy API Server

```bash
cd hevy/api
npm install
npm start
```

### 2. Start the MCP Server

```bash
cd hevy/mcp
./setup.sh
npm start
```

### 3. Start LLM Integration (Optional)

```bash
cd hevy/llm
./scripts/ollama-integration.sh
```

## 📚 Documentation

- **[API Documentation](hevy/api/README.md)**: Complete API reference and setup guide
- **[MCP Server Documentation](hevy/mcp/README.md)**: Comprehensive MCP server guide
- **[LLM Integration Documentation](hevy/llm/README.md)**: Ollama integration and AI features
- **[Quick Start Guide](hevy/mcp/QUICKSTART.md)**: Get MCP server running in 5 minutes

## 🔧 MCP Server Tools

The MCP server provides the following tools for AI integration:

| Tool                | Description                                | Use Case                       |
| ------------------- | ------------------------------------------ | ------------------------------ |
| `get_workouts`      | Retrieve paginated workouts with filtering | Get workout history and trends |
| `get_workout_by_id` | Get specific workout with all exercises    | Detailed workout analysis      |
| `get_exercises`     | Retrieve exercises for a workout           | Exercise-specific analysis     |
| `search_exercises`  | Search exercises across all workouts       | Find specific exercises        |
| `get_workout_stats` | Comprehensive workout statistics           | Analytics and insights         |
| `health_check`      | API health status                          | Monitoring and diagnostics     |

## 🌐 Deployment

### Local Development

```bash
# Terminal 1: API Server
cd hevy/api && npm start

# Terminal 2: MCP Server
cd hevy/mcp && npm run dev
```

### Docker Deployment

```bash
cd hevy/mcp
docker-compose up -d
```

### Production

- Use the provided Dockerfile and docker-compose.yml
- Configure environment variables for production
- Set up proper logging and monitoring

## 🔍 Testing

### API Testing

```bash
cd hevy/api
node test-api.js
```

### MCP Testing

```bash
cd hevy/llm
node test-mcp.js
```

## 📊 Data Flow

```
Hevy CSV Data → SQLite Database → Hevy API → MCP Server → AI/LLM Client
```

## 🛠️ Development

### Project Structure

```
health-copilot/
├── hevy/
│   ├── api/           # REST API server
│   │   ├── api.js     # API routes
│   │   ├── index.js   # Server entry point
│   │   └── workouts.db # SQLite database
│   ├── mcp/           # MCP server
│   │   ├── src/       # TypeScript source
│   │   ├── dist/      # Compiled JavaScript
│   │   ├── scripts/   # Management scripts
│   │   └── Dockerfile # Container configuration
│   └── llm/           # LLM integration
│       ├── scripts/   # Ollama integration scripts
│       ├── docs/      # Documentation and guides
│       └── test-mcp.js # MCP testing script
└── README.md
```

### Adding New Features

1. **API Endpoints**: Add to `hevy/api/api.js`
2. **MCP Tools**: Add to `hevy/mcp/src/tools/index.ts`
3. **LLM Integration**: Add to `hevy/llm/scripts/`
4. **Data Models**: Update `hevy/mcp/src/types/index.ts`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Check the troubleshooting sections in each component's README
- Review logs for error details
- Open an issue on GitHub
- Contact the development team

---

**🎉 Ready to transform your fitness data into intelligent insights!**
