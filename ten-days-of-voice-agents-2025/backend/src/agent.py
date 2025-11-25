# backend/src/agent.py
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
)

# Plugins
from livekit.plugins import murf, google, deepgram, noise_cancellation

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# --- CONFIG / FILE PATHS ---
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
SHARED_DIR = os.path.normpath(os.path.join(BASE_DIR, "shared-data"))
CONTENT_PATH = os.path.join(SHARED_DIR, "day4_tutor_content.json")
STATE_PATH = os.path.join(SHARED_DIR, "tutor_state.json")

# Voice mapping for modes (Option B)
VOICE_MAP = {
    "learn": "Matthew",     # Murf voice id for learn
    "quiz": "Isha",         # Murf voice id for quiz
    "teach_back": "Alicia", # Murf voice id for teach_back
}

# Globals (set at runtime)
CURRENT_SESSION: Optional[AgentSession] = None
CURRENT_MODE: str = "learn"  # default


# ----------------- Utility helpers -----------------
def ensure_shared_files():
    os.makedirs(SHARED_DIR, exist_ok=True)
    # ensure tutor state file exists
    if not os.path.exists(STATE_PATH):
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({"mode": CURRENT_MODE, "history": []}, f, indent=2)


def load_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("File not found: %s", path)
        return None
    except Exception as e:
        logger.exception("Failed to load JSON %s: %s", path, e)
        return None


def save_json(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            return True
    except Exception as e:
        logger.exception("Failed to save JSON %s: %s", path, e)
        return False


# ----------------- Tools (async, no ctx) -----------------
@function_tool
async def list_concepts() -> Dict:
    """
    Return the list of available concepts (IDs and titles).
    Called by LLM when it needs the catalog.
    """
    data = load_json(CONTENT_PATH)
    if not data:
        return {"error": "content_not_found"}
    concepts = data.get("concepts") if isinstance(data, dict) else data
    # Normalize: return id + title list
    return {"concepts": [{"id": c["id"], "title": c.get("title", "")} for c in concepts]}


@function_tool
async def get_concept(concept_id: str) -> Dict:
    """
    Return full concept object for a given id.
    """
    data = load_json(CONTENT_PATH)
    if not data:
        return {"error": "content_not_found"}
    concepts = data.get("concepts") if isinstance(data, dict) else data
    for c in concepts:
        if c.get("id") == concept_id:
            return {"concept": c}
    return {"error": "not_found"}


@function_tool
async def evaluate_teach_back(concept_summary: str, user_explanation: str) -> Dict:
    """
    Very simple qualitative evaluator for teach_back mode.
    Returns a score and short feedback.
    """
    # Basic heuristic
    score = 50
    tokens = concept_summary.lower().split()[:6]
    if any(t in user_explanation.lower() for t in tokens):
        score = 80
    feedback = (
        "Good explanation — you covered key ideas."
        if score > 60
        else "Try referencing the core idea more directly and use simple examples."
    )
    return {"score": score, "feedback": feedback}


@function_tool
async def get_mode() -> Dict:
    """
    Return current mode from tutor_state.json.
    """
    st = load_json(STATE_PATH)
    if not st:
        return {"mode": CURRENT_MODE}
    return {"mode": st.get("mode", CURRENT_MODE)}


@function_tool
async def set_mode(mode: str) -> Dict:
    """
    Set the learning mode (learn/quiz/teach_back) and switch TTS voice accordingly.
    This function mutates tutor_state.json and tries to update CURRENT_SESSION.tts.
    """
    global CURRENT_MODE, CURRENT_SESSION
    if mode not in ["learn", "quiz", "teach_back"]:
        return {"error": "invalid_mode"}

    # Update persistent state
    st = load_json(STATE_PATH)
    if not isinstance(st, dict):
        st = {}
    st["mode"] = mode
    save_json(STATE_PATH, st)

    CURRENT_MODE = mode

    # Update session TTS voice (if session available)
    if CURRENT_SESSION is not None:
        # map mode -> voice id
        voice_id = VOICE_MAP.get(mode, VOICE_MAP["learn"])
        try:
            # create new TTS instance with chosen voice
            # Keep same style and other defaults
            CURRENT_SESSION.tts = murf.TTS(voice=voice_id, style="Conversation", tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2))
            logger.info("Switched TTS voice to %s for mode %s", voice_id, mode)
        except Exception:
            logger.exception("Failed to switch TTS voice in session")

    return {"mode": mode}


@function_tool
async def save_session_checkin(entry: Dict) -> Dict:
    """
    Save check-in / session results into tutor_state.json history.
    Expects `entry` to contain keys like: mood, energy, stress, goals (list), summary.
    The agent can call this at the end of a successful check-in.
    """
    st = load_json(STATE_PATH)
    if not isinstance(st, dict):
        st = {}
    history = st.get("history", [])
    entry = entry.copy()
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    history.append(entry)
    st["history"] = history
    success = save_json(STATE_PATH, st)
    return {"saved": bool(success), "entry": entry if success else None}


# ----------------- Agent & Entrypoint -----------------
class TutorAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are an active-recall tutor. Ask the user which mode they want: "
                "'learn', 'quiz', or 'teach_back'. Use the tools provided to list concepts, "
                "fetch concept details, evaluate teach-back answers, save check-ins, "
                "and change modes. Keep replies concise and conversational."
            ),
            # Tools are registered here so the LLM sees them as callable functions
            tools=[list_concepts, get_concept, evaluate_teach_back, get_mode, set_mode, save_session_checkin],
        )


async def entrypoint(ctx: JobContext):
    global CURRENT_SESSION, CURRENT_MODE

    ensure_shared_files()

    # Create AgentSession with default voice mapped to current mode
    default_voice = VOICE_MAP.get(CURRENT_MODE, "Matthew")
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice=default_voice,
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
        ),
        turn_detection=None,
        vad=None,
        preemptive_generation=True,
    )

    # set current session global so set_mode tool can update TTS at runtime
    CURRENT_SESSION = session

    # usage/metrics
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics(ev):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        logger.info("Usage summary: %s", usage_collector.get_summary())

    ctx.add_shutdown_callback(log_usage)

    # Start session with TutorAgent
    await session.start(
        agent=TutorAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    # Quick greeting when a job starts (agent voice will use session.tts)
    # Use the LLM to produce the greeting or call TTS directly: here we allow LLM flow.
    # Connect and run
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    