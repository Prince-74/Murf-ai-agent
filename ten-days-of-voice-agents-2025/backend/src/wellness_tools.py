import json
import os
from datetime import datetime
from livekit.agents import function_tool, RunContext

LOG_FILE = "wellness_log.json"


def _load_json():
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def _save_json(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


@function_tool
async def save_checkin(ctx: RunContext, mood: str, energy: str, goals: list, summary: str):
    """Save today's wellness check-in."""

    history = _load_json()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "mood": mood,
        "energy": energy,
        "goals": goals,
        "summary": summary
    }

    history.append(entry)
    _save_json(history)

    return "Your wellness check-in has been saved."


@function_tool
async def load_history(ctx: RunContext):
    """Load past check-ins."""
    return _load_json()


@function_tool
async def summarize_history(ctx: RunContext):
    """Return a 1–2 sentence reference based on history."""

    history = _load_json()
    if not history:
        return "This is our first check-in together."

    last = history[-1]

    mood = last.get("mood", "unknown")
    energy = last.get("energy", "unknown")

    return f"Last time we talked, you mentioned feeling {mood} with {energy} energy."
