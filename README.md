# Health Copilot

Transform your health data into an intelligent, personalized fitness co‑pilot. Analyze training patterns, generate personalized workout plans, and get data‑driven recommendations — all while keeping your data private and local.

## 🎯 Scope

- Weekly workout planning from your historical data
- Local, privacy‑preserving processing

## 🏗️ Components

1. Hevy API Server (`hevy/api/`)

- Node.js + Express + SQLite
- Imports `hevy/api/workouts.csv` on first run into `hevy/api/workouts.db`
- Exposes REST endpoints under `/api`

2. Hevy MCP Server (`hevy/mcp/`)

- TypeScript MCP server for AI tools
- Tools: `get_workouts`, `get_workout_by_id`, `get_exercises`, `search_exercises`, `get_workout_stats`, `health_check`

3. LLM Integration (`hevy/llm/`)

- Single entrypoint script: `scripts/ollama-integration.sh`
- Local LLM workflows integrating with the MCP server

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Hevy workout CSV at `hevy/api/workouts.csv`

### 1) Start API Server

```bash
cd hevy/api
npm install
npm start
```

Starts on `http://localhost:3000`:

- Health: `http://localhost:3000/health`
- API base: `http://localhost:3000/api`

### 2) Start MCP Server

```bash
cd hevy/mcp
npm install
npm run build
npm start
```

Dev mode (hot reload):

```bash
cd hevy/mcp
npm install
npm run dev
```

### 3) LLM Integration (optional)

```bash
cd hevy/llm
./scripts/ollama-integration.sh
```

## 📚 API Endpoints

- GET `/api/workouts` — list workouts with pagination and filters
- GET `/api/workouts/:id` — workout details + exercises
- POST `/api/workouts` — create workout (optional nested exercises)
- PUT `/api/workouts/:id` — update workout
- DELETE `/api/workouts/:id` — delete workout (and exercises)
- GET `/api/exercises` — list exercises with filters
- GET `/api/exercises/:id` — exercise details
- POST `/api/exercises` — add exercise
- PUT `/api/exercises/:id` — update exercise
- DELETE `/api/exercises/:id` — delete exercise
- GET `/api/stats?period=week|month|year|all` — aggregate stats
- GET `/api/search?q=...&type=all|workouts|exercises` — search
- GET `/api/export?format=json|csv` — export data

## 🔧 MCP Tools

- `get_workouts` — paginated workouts with filters
- `get_workout_by_id` — workout + exercises
- `get_exercises` — exercises with filters
- `search_exercises` — search across workouts/exercises
- `get_workout_stats` — aggregate statistics
- `health_check` — API health status

## 🌐 Development & Deployment

### Local development

```bash
# Terminal 1: API
cd hevy/api && npm install && npm start

# Terminal 2: MCP (dev)
cd hevy/mcp && npm install && npm run dev
```

### Docker (MCP)

```bash
cd hevy/mcp
docker-compose up -d
```

## 📁 Structure

```
health-copilot/
├── hevy/
│   ├── api/           # REST API server
│   │   ├── api.js     # API routes
│   │   ├── index.js   # Server entry
│   │   ├── workouts.csv # Source CSV (imported on first run)
│   │   └── workouts.db # SQLite database
│   ├── mcp/           # MCP server
│   │   ├── src/       # TypeScript source
│   │   ├── dist/      # Compiled JavaScript
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── llm/           # LLM integration
│       ├── scripts/
│       │   └── ollama-integration.sh
│       └── test-mcp.js
├── test-api.js        # API test script
└── README.md
```

## 🛠️ Extending

- API endpoints: edit `hevy/api/api.js`
- MCP tools: edit `hevy/mcp/src/tools/index.ts`
- LLM integration: extend `hevy/llm/scripts/ollama-integration.sh`
- Types/models: edit `hevy/mcp/src/types/index.ts`

## 📄 License

MIT
