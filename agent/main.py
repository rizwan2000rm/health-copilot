"""
AI Fitness Coach - Entry Points

Provides both a console UI entry point and a FastAPI server for UI integration.
"""

import asyncio
import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ui import AsyncConsoleUI
from fitness_coach import FitnessCoach


async def main():
    """Main application entry point for console UI."""
    ui = AsyncConsoleUI()
    await ui.run_async()


# FastAPI app for mobile UI integration
app = FastAPI(title="Health Copilot Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_coach: Optional[FitnessCoach] = None
_initialized = False


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    text: str


@app.on_event("startup")
async def startup_event():
    global _coach, _initialized
    _coach = FitnessCoach(model_name=os.getenv("AGENT_MODEL", "gpt-5-nano"))
    # Setup KB (sync)
    context_dir = os.path.join(os.path.dirname(__file__), "context")
    if os.path.exists(context_dir):
        _coach.setup_knowledge_base(context_dir)
    # Initialize MCP agent in background to avoid blocking startup
    async def init_agent_bg():
        try:
            await _coach.setup_agent()
        except Exception as _:
            pass
    asyncio.create_task(init_agent_bg())
    _initialized = True


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if _coach is None:
        return ChatResponse(text="Agent not initialized")
    reply = await _coach.get_response(req.prompt)
    return ChatResponse(text=reply)


@app.get("/chat")
async def chat_get(prompt: str = "Hello!"):
    if _coach is None:
        return {"text": "Agent not initialized"}
    reply = await _coach.get_response(prompt)
    return {"text": reply}


@app.post("/weekly-plan", response_model=ChatResponse)
async def weekly_plan():
    if _coach is None:
        return ChatResponse(text="Agent not initialized")
    reply = await _coach.generate_weekly_plan()
    return ChatResponse(text=reply)


@app.get("/stats")
async def stats():
    if _coach is None:
        return {"initialized": False}
    return {"initialized": _initialized, **_coach.get_stats()}


if __name__ == "__main__":
    # If run directly, start console UI
    asyncio.run(main())