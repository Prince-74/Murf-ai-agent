import logging
import json
import os
from datetime import datetime
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
    RunContext
)

# No VAD or turn detection (Windows workaround)
from livekit.plugins import murf, google, deepgram, noise_cancellation

logger = logging.getLogger("agent")
load_dotenv(".env.local")

WELLNESS_FILE = "wellness_log.json"


# -------------------------------
# JSON UTILITIES
# -------------------------------
def load_history():
    if not os.path.exists(WELLNESS_FILE):
        return []
    try:
        with open(WELLNESS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_history_entry(entry):
    history = load_history()
    history.append(entry)
    with open(WELLNESS_FILE, "w") as f:
        json.dump(history, f, indent=2)


# -------------------------------
# TOOLS
# -------------------------------
@function_tool
async def save_checkin(
    context: RunContext,
    mood: str,
    energy: str,
    stress: str,
    goals: list[str],
    summary: str
):
    """
    Saves a wellness check-in to the JSON log.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "mood": mood,
        "energy": energy,
        "stress": stress,
        "goals": goals,
        "summary": summary,
    }
    save_history_entry(entry)
    return "saved"


@function_tool
async def read_last_checkin(context: RunContext):
    """
    Returns the last entry in wellness_log.json.
    """
    history = load_history()
    if len(history) == 0:
        return "none"
    return history[-1]


# -------------------------------
# AGENT
# -------------------------------
class WellnessAgent(Agent):
    def __init__(self):
        last = load_history()[-1] if len(load_history()) else None

        previous_ref = ""
        if last:
            previous_ref = (
                f"Yesterday you reported mood {last['mood']}, "
                f"energy {last['energy']}, stress {last['stress']}. "
                f"Use this as conversational reference, but don't rely on it too strongly."
            )

        super().__init__(
            instructions=f"""
You are a calm, grounded Health & Wellness voice companion.

Your job:
1. Ask about today's mood, energy, stress.
2. Ask for 1–3 simple goals.
3. Give small, realistic, supportive advice.
4. Create a brief recap.
5. Call save_checkin tool with:
   - mood
   - energy
   - stress
   - goals
   - summary

Avoid medical, diagnostic or clinical claims.

Reference the previous day like this:
"{previous_ref}"
            """,
            tools=[save_checkin, read_last_checkin],
        )


# -------------------------------
# ENTRYPOINT
# -------------------------------
async def entrypoint(ctx: JobContext):

    ctx.log_context_fields = {"room": ctx.room.name}

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
        ),
        turn_detection=None,
        vad=None,
        preemptive_generation=True,
    )

    usage = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _m(ev):
        usage.collect(ev.metrics)

    await session.start(
        agent=WellnessAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
