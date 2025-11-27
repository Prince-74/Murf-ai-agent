import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent, AgentSession, JobContext,
    RoomInputOptions, WorkerOptions, cli, tokenize
)

from livekit.plugins import murf, google, deepgram, noise_cancellation

from fraud_tools import load_case, verify_answer, update_case_status

logger = logging.getLogger("fraud-agent")
load_dotenv(".env.local")


class FraudAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are a fraud-alert representative and your name is Alex from **SecureBank**.
Be calm, professional, and concise.

FLOW:
1. Ask for customer's name.
2. Call load_case(name). If not_found → politely end.
3. Ask stored verification question.
4. Call verify_answer(name, answer).
   - If False → say cannot proceed → end call.
   - If True → continue.
5. Read suspicious transaction details.
6. Ask: “Did you make this transaction? Yes or No?”
7. If YES → update_case_status(..., "confirmed_safe")
8. If NO  → update_case_status(..., "confirmed_fraud")
9. End call.

RULES:
- Never ask for PIN, password, or full card number.
- Use only tool data.
""",
            tools=[load_case, verify_answer, update_case_status],
        )


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
        vad=None,
        turn_detection=None,
        preemptive_generation=True,
    )

    await session.start(
        agent=FraudAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
