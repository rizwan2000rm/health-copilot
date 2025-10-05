# Repository Guidelines

## Project Structure & Module Organization
Health Copilot spans three workspaces. `agent/` hosts the Python FastAPI API and console UI; core logic lives in `fitness_coach.py`, prompts and references in `context/`, and cached embeddings in `agent/chroma_db/` (rebuild via `document_processor.py` if sources change). `hevy-mcp/` implements the Model Context Protocol server, with Pydantic types in `schemas/` and callable tool handlers in `tools/`. The Expo app resides in `ui/`: routed screens under `app/`, shared primitives in `components/`, data helpers in `services/`, and assets in `assets/`.

## Build, Test, and Development Commands
Install agent deps via `cd agent && pip install -r requirements.txt`. Start the API via `uvicorn main:app --reload` and launch the CLI with `python main.py`. Initialize the MCP server with `cd hevy-mcp && uv sync`, then run `uv run app.py`. For the Expo workspace run `cd ui && npm install`, followed by `npm run start` (or platform-specific variants) with `EXPO_PUBLIC_AGENT_URL` targeting the agent service. Lint React Native code through `npm run lint`.

## Coding Style & Naming Conventions
Python modules should follow PEP 8: four-space indentation, snake_case names, and async functions prefixed with verbs (`get_response`, `generate_weekly_plan`). Keep prompts and constants in dedicated modules rather than inline strings. JavaScript/TypeScript respects the Expo flat ESLint config; favor PascalCase components, camelCase utilities, and colocate screen-only hooks beneath `ui/hooks/`. Tailwind classes should group layout tokens first, then spacing, then color.

## Testing Guidelines
Automated tests are still forming; add `pytest` cases for new backend behavior and Jest or React Testing Library coverage for UI changes. Until tooling is expanded, run manual smoke tests: exercise `/chat`, `/sleep-analysis`, and `/weekly-plan` while the agent is up, and verify key screens load in Expo Go.

## Commit & Pull Request Guidelines
Commits use short Title Case subjects (`Add New Chat Key State Management`) and note intent or follow-up actions when needed. Pull requests should outline the change set, reference related issues, and include evidence of verification (lint output, server logs, or emulator screenshots when UI shifts). Mention configuration prerequisites so reviewers can replay your setup quickly.

## Configuration & Security Tips
Keep secrets in environment files ignored by Git. `HEVY_API_KEY` powers the MCP server; agent models rely on standard OpenAI or Ollama env vars; the Expo app reads public endpoints from `EXPO_PUBLIC_` variables. Avoid committing regenerated `chroma_db` content or exported health data unless explicitly anonymized.
