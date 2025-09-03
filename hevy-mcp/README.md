<!-- https://api.hevyapp.com/docs/#/ -->

My ToDo List for the MVP

- [ ] Implement get_workouts -> /v1/workouts
  - [ ] Connect to Claude and Ollama
  - [ ] Test and see if the workouts are fetched properly
- [ ] Implement get_routines -> /v1/routines
  - [ ] Test and see if the routines are fetched properly
- [ ] Implement create_routine -> v1/routines (POST)
  - [ ] Test and see if the routine is created properly
- [ ] Implement update_routine -> v1/routines/{routineId}
  - [ ] Test and see if the routines are updated properly

## Configuration

Set `HEVY_API_KEY` in your MCP client configuration so it is available in the server process environment. The server reads `HEVY_API_KEY` from `os.environ` and, if present, sends `Authorization: Bearer <key>` on requests.
