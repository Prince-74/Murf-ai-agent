# backend/src/agent.py
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

# tools (async): functions in food_tools.py
from food_tools import (
    list_catalog,
    find_item,
    add_to_cart,
    remove_from_cart,
    update_quantity,
    get_cart,
    save_order,
    list_recipes,
    add_recipe_items_to_cart,
)

logger = logging.getLogger("day7-agent")
load_dotenv(".env.local")


class FoodAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""
You are a friendly food & grocery ordering assistant for 'QuickBite'.
Behave conversationally but concisely.
Key behaviors:
- Offer help, list catalog, add/remove items, update quantities.
- Ask clarifying questions when quantity or item is missing.
- For "ingredients for X", map to recipes and add multiple items.
- When user says "place my order" or "that's all", confirm the final cart and call save_order(customer_name).
Keep replies short and clear.
""",
            tools=[
                list_catalog,
                find_item,
                add_to_cart,
                remove_from_cart,
                update_quantity,
                get_cart,
                save_order,
                list_recipes,
                add_recipe_items_to_cart,
            ],
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
        agent=FoodAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
