# Hevy MCP Server

A production-grade Model Context Protocol (MCP) server that provides access to Hevy workout tracking data through a standardized interface.

## Features

- **Comprehensive Workout Data Access**: Retrieve workouts, exercises, and statistics
- **Advanced Filtering**: Search and filter by date ranges, exercise types, and more
- **Production Ready**: Built with TypeScript, comprehensive error handling, and logging
- **MCP Standard Compliant**: Follows the Model Context Protocol specification
- **Robust Error Handling**: Graceful error handling with detailed logging
- **Input Validation**: Zod-based schema validation for all inputs
- **Health Monitoring**: Built-in health checks and connection testing

## Prerequisites

- Node.js 18+ 
- Hevy API server running (see parent directory)
- TypeScript 5.0+

## Installation

1. Navigate to the MCP server directory:
```bash
cd hevy/mcp
```

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

## Configuration

Copy the environment file and configure your settings:

```bash
cp env.example .env
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_NAME` | Name of the MCP server | `hevy-mcp-server` |
| `MCP_SERVER_VERSION` | Version of the MCP server | `1.0.0` |
| `HEVY_API_BASE_URL` | Base URL for Hevy API | `http://localhost:3000/api` |
| `HEVY_API_TIMEOUT` | API request timeout (ms) | `30000` |
| `LOG_LEVEL` | Logging level | `info` |
| `LOG_FILE_PATH` | Path to log file | `./logs/mcp-server.log` |
| `PORT` | MCP server port | `3001` |
| `HOST` | MCP server host | `localhost` |

## Usage

### Development Mode

```bash
npm run dev
```

### Production Mode

```bash
npm run build
npm start
```

### Watch Mode

```bash
npm run watch
```

## Available Tools

### 1. `get_workouts`
Retrieve a paginated list of workouts with optional filtering.

**Parameters:**
- `page` (number): Page number for pagination (default: 1)
- `limit` (number): Number of workouts per page (default: 20, max: 100)
- `search` (string): Search term to filter workouts by title or description
- `start_date` (string): Start date filter (ISO format: YYYY-MM-DD)
- `end_date` (string): End date filter (ISO format: YYYY-MM-DD)

### 2. `get_workout_by_id`
Retrieve a specific workout by ID with all its exercises.

**Parameters:**
- `id` (number): The unique identifier of the workout

### 3. `get_exercises`
Retrieve all exercises for a specific workout.

**Parameters:**
- `workout_id` (number): The ID of the workout to get exercises for

### 4. `search_exercises`
Search for exercises by title across all workouts.

**Parameters:**
- `query` (string): Search query for exercise titles
- `limit` (number): Maximum number of results to return (default: 20, max: 100)

### 5. `get_workout_stats`
Retrieve comprehensive workout statistics and analytics.

**Parameters:**
- `start_date` (string): Start date for statistics (ISO format: YYYY-MM-DD)
- `end_date` (string): End date for statistics (ISO format: YYYY-MM-DD)

### 6. `health_check`
Check the health status of the Hevy API.

**Parameters:** None

## API Integration

The MCP server integrates with the Hevy API to provide:

- **Workout Management**: Create, read, and analyze workout sessions
- **Exercise Tracking**: Detailed exercise data with sets, reps, weights, and more
- **Analytics**: Comprehensive workout statistics and trends
- **Search & Filtering**: Advanced search capabilities across workouts and exercises

## Error Handling

The server implements comprehensive error handling:

- **Validation Errors**: Input validation using Zod schemas
- **API Errors**: Proper handling of HTTP errors from the Hevy API
- **Network Errors**: Timeout and connection error handling
- **Graceful Degradation**: Continues operation even when API is unavailable

## Logging

Comprehensive logging using Winston:

- **File Logging**: Rotating log files with size limits
- **Error Logging**: Separate error log file
- **Structured Logging**: JSON format for production, colored for development
- **Context Tracking**: Request context and error details

## Development

### Project Structure

```
src/
├── config/          # Configuration management
├── services/        # Business logic and API integration
├── tools/           # MCP tool definitions and handlers
├── types/           # TypeScript type definitions
└── utils/           # Utility functions and helpers
```

### Building

```bash
npm run build
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
```

### Formatting

```bash
npm run format
```

## Production Deployment

### Docker Support

The server can be containerized for production deployment:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 3001
CMD ["npm", "start"]
```

### Environment Configuration

Ensure all environment variables are properly set in production:

```bash
export NODE_ENV=production
export LOG_LEVEL=warn
export HEVY_API_BASE_URL=https://your-api-domain.com/api
```

### Monitoring

- **Health Checks**: Built-in health check endpoint
- **Log Aggregation**: Structured logs for log aggregation systems
- **Error Tracking**: Comprehensive error logging for monitoring
- **Performance Metrics**: Request/response logging for performance analysis

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Verify Hevy API server is running
   - Check `HEVY_API_BASE_URL` configuration
   - Ensure network connectivity

2. **Validation Errors**
   - Check input parameter formats
   - Verify date formats (YYYY-MM-DD)
   - Ensure numeric values are within valid ranges

3. **Logging Issues**
   - Verify log directory permissions
   - Check `LOG_LEVEL` configuration
   - Ensure disk space is available

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=debug
npm run dev
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue on GitHub
4. Contact the development team

## Changelog

### v1.0.0
- Initial release
- Complete MCP server implementation
- Integration with Hevy API
- Comprehensive error handling and logging
- Production-ready architecture
