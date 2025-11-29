# game_tools.py
import json
import os
from datetime import datetime
from livekit.agents import function_tool, RunContext

BASE = os.path.join(os.path.dirname(__file__), "..", "shared-data")
STATE_PATH = os.path.join(BASE, "game_state.json")


def _load():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def _save(data):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@function_tool
def start_new_game(ctx: RunContext, player_name: str):
    state = {
        "player_name": player_name,
        "location": "outpost_gamma",
        "inventory": [],
        "story_log": [],
        "started_at": datetime.utcnow().isoformat(),
    }
    _save(state)
    return {"started": True, "player_name": player_name}


@function_tool
def get_game_state(ctx: RunContext):
    return _load()


@function_tool
def update_location(ctx: RunContext, new_location: str):
    state = _load()
    state["location"] = new_location
    _save(state)
    return {"updated": True, "location": new_location}


@function_tool
def add_to_inventory(ctx: RunContext, item: str):
    state = _load()
    inv = state.get("inventory", [])
    inv.append(item)
    state["inventory"] = inv
    _save(state)
    return {"inventory": inv}


@function_tool
def log_story_event(ctx: RunContext, event: str):
    state = _load()
    log = state.get("story_log", [])
    log.append(event)
    state["story_log"] = log
    _save(state)
    return {"logged": event}
