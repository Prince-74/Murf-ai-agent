import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    tokenize,
)

from livekit.plugins import murf, google, deepgram, noise_cancellation

# tools (async) — implemented in sdr_tools_extended.py
from sdr_tools_extended import (
    find_faq_answer,
    collect_lead_field,
    finalize_lead,
    list_slots,
    book_slot,
    generate_crm_notes,
    infer_persona,
    draft_followup_email,
    find_returning,
)

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# Simple persona -> voice map. We use one session-level default voice.
PERSONA_VOICE = {
    "default": {"voice": "en-US-matthew", "style": "Conversation"},
    "developer": {"voice": "en-US-isha", "style": "Conversational"},
    "product_manager": {"voice": "en-US-alicia", "style": "Conversation"},
    "founder": {"voice": "en-US-matthew", "style": "Conversation"},
}


class SDRAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are an SDR for Amazon. Greet warmly, ask what they need, answer FAQ-based questions using the company content, collect lead fields, offer meeting times, and summarize.
Behavior notes:
- Keep responses concise but friendly (not extremely short).
- Use tools to answer FAQs and store data (do not invent facts).
- Ask clarifying questions if important lead fields are missing.
- When the user indicates the call is finished, finalize the lead and produce a short summary.
""",
            tools=[
                find_faq_answer,
                collect_lead_field,
                finalize_lead,
                list_slots,
                book_slot,
                generate_crm_notes,
                infer_persona,
                draft_followup_email,
                find_returning,
            ],
        )


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    # Choose a safe default voice for the session
    tts_conf = PERSONA_VOICE["default"]

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice=tts_conf["voice"],
            style=tts_conf["style"],
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
        ),
        # Windows-friendly: no ONNX turn detector / VAD
        turn_detection=None,
        vad=None,
        preemptive_generation=True,
    )

    # Start the agent session and connect to the room
    await session.start(
        agent=SDRAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Connect and let the framework handle tool invocation (LLM will call tools)
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
