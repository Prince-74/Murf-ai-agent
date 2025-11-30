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

from livekit.plugins import murf, google, deepgram

from commerce_tools import list_products, create_order, last_order

logger = logging.getLogger("ecommerce-agent")
load_dotenv(".env.local")


class EcommerceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are a voice shopping assistant following an ACP-inspired flow.

You MUST:
- Use list_products for showing catalog items.
- Use create_order to place orders.
- Use last_order to read back previous purchases.

Never guess product details.
Always confirm before placing an order.
""",
            tools=[list_products, create_order, last_order],
        )


async def entrypoint(ctx: JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
        ),
    )

    await session.start(
        agent=EcommerceAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
