import logging
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
)

# Windows-safe plugins only
from livekit.plugins import murf, google, deepgram, noise_cancellation

# Load environment
logger = logging.getLogger("agent")
load_dotenv(".env.local")

# -------------------------
# IMPORT TOOLS (Day-2 logic)
# -------------------------
from coffee_tools import update_order, is_order_complete, save_order


# =========================================================
#   ASSISTANT CLASS — BARISTA + GREETING LOGIC
# =========================================================
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are a friendly barista at **Cafe Coffee Day** (CCD).

Start EVERY conversation with:
"Hi! Welcome to Cafe Coffee Day! What can I get started for you today?"

Your job:
1. Take the user's coffee order.
2. Ask questions until ALL fields are filled:
   - drinkType
   - size
   - milk
   - extras
   - name

3. Use the tools EXACTLY as needed:
   - Call update_order when user provides any detail.
   - Call is_order_complete to check if the order is finished.
   - When complete, call save_order, then read back the full order, and say:
     "Your order is ready. Thank you!"

Rules:
- Keep responses short and natural.
- Never guess — always ask for missing details.
- Do NOT fill fields unless user says them.
- Confirm unclear details.
""",
            tools=[update_order, is_order_complete, save_order]
        )


# =========================================================
#   ENTRYPOINT — PIPELINE SETUP (Windows Friendly)
# =========================================================
async def entrypoint(ctx: JobContext):

    ctx.log_context_fields = {"room": ctx.room.name}

    # Voice agent session
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
        ),

        # Disable broken-on-Windows features
        turn_detection=None,
        vad=None,

        preemptive_generation=True,
    )

    # Metrics
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics(ev):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        logger.info(f"Usage summary: {usage_collector.get_summary()}")

    ctx.add_shutdown_callback(log_usage)

    # Start assistant
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Connect to the room
    await ctx.connect()


# =========================================================
#   MAIN ENTRY
# =========================================================
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
