"""
AI Fitness Coach - Entry Points

Provides both a console UI entry point and a FastAPI server for UI integration.
"""

import asyncio
import os
from typing import Optional, List
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


# --- Sleep Analysis Route ---


class SleepDaySummary(BaseModel):
    date: str
    steps: int
    active_kcal: float
    basal_kcal: float
    sleep_minutes: float
    sleep_start: Optional[str] = None
    sleep_end: Optional[str] = None
    sleep_source: Optional[str] = None  # "asleep" | "in_bed"


class SleepAnalysisRequest(BaseModel):
    days: List[SleepDaySummary]


@app.post("/sleep-analysis", response_model=ChatResponse)
async def sleep_analysis(req: SleepAnalysisRequest):
    if _coach is None:
        return ChatResponse(text="Agent not initialized")

    # Prepare a concise but structured prompt for the model (no training context)
    header = (
        "You are a sleep coach. Analyze the user's last 30 non zero sleep data points."
        "Identify patterns (duration trends, consistency/bedtime windows, weekend variability, outliers). "
        "Provide 3-5 prioritized, concrete recommendations to improve duration and quality. "
        "Use the data fields: date, sleep_minutes, sleep_start, sleep_end, sleep_source, steps, active_kcal, basal_kcal. "
    )

    # Validate input and filter to non-zero sleep; take the most recent 30 entries
    if not req.days or len(req.days) == 0:
        return ChatResponse(
            text=(
                "No sleep data provided. Please send at least 1 day with non-zero sleep_minutes."
            )
        )
    days_nonzero = [d for d in req.days if (d.sleep_minutes or 0) > 0]
    if not days_nonzero:
        return ChatResponse(
            text=(
                "No non-zero sleep data found in the request. Ensure sleep_minutes > 0 for the last 30 days."
            )
        )
    days_sorted = sorted(days_nonzero, key=lambda d: d.date)
    if len(days_sorted) > 30:
        days_sorted = days_sorted[-30:]

    # Render a compact table-like section for context
    lines = []
    for d in days_sorted:
        line = (
            f"{d.date} | sleep_min={round(d.sleep_minutes)} | "
            f"start={d.sleep_start or ''} | end={d.sleep_end or ''} | src={d.sleep_source or ''} | "
            f"steps={d.steps} | active_kcal={round(d.active_kcal)} | basal_kcal={round(d.basal_kcal)}"
        )
        lines.append(line)

    prompt = (
        f"{header}\n\nDATA (oldest→newest):\n"
        + "\n".join(lines)
        + "\n\nReturn a short analysis followed by a numbered list of recommendations."
    )

    # Bypass RAG/agent to avoid injecting unrelated research context
    reply = await _coach.get_direct_response(prompt)
    return ChatResponse(text=reply)


@app.get("/stats")
async def stats():
    if _coach is None:
        return {"initialized": False}
    return {"initialized": _initialized, **_coach.get_stats()}


# --- Step Analysis Route ---


class StepDaySummary(BaseModel):
    date: str
    steps: int
    active_kcal: float
    basal_kcal: float


class StepAnalysisRequest(BaseModel):
    days: List[StepDaySummary]


@app.post("/steps-analysis", response_model=ChatResponse)
async def steps_analysis(req: StepAnalysisRequest):
    if _coach is None:
        return ChatResponse(text="Agent not initialized")

    if not req.days:
        return ChatResponse(
            text="No step data provided. Please send at least 1 day with recorded steps."
        )

    header = (
        "You are a walking coach. Analyze the user's last 30 days of step data. "
        "Surface consistency trends, weekday vs. weekend differences, and any outliers. "
        "Suggest 3-5 realistic recommendations that focus on building a sustainable daily habit around 6,000 steps, "
        "favoring steady routines over occasional 10,000+ days."
    )

    days_nonzero = [d for d in req.days if (d.steps or 0) > 0]
    if not days_nonzero:
        return ChatResponse(
            text="No step counts above zero were found. Import recent activity and try again."
        )

    days_sorted = sorted(days_nonzero, key=lambda d: d.date)
    recent = days_sorted[-30:]

    lines = []
    for d in recent:
        line = (
            f"{d.date} | steps={d.steps} | "
            f"active_kcal={round(d.active_kcal)} | basal_kcal={round(d.basal_kcal)}"
        )
        lines.append(line)

    prompt = (
        f"{header}\n\nDATA (oldest→newest):\n"
        + "\n".join(lines)
        + "\n\nReturn a short analysis followed by a numbered list of habit-focused recommendations."
    )

    reply = await _coach.get_direct_response(prompt)
    return ChatResponse(text=reply)


if __name__ == "__main__":
    # If run directly, start console UI
    asyncio.run(main())
