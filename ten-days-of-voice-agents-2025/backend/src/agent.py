# agent.py
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

from game_tools import (
    start_new_game,
    get_game_state,
    update_location,
    add_to_inventory,
    log_story_event,
)

logger = logging.getLogger("game-master")
load_dotenv(".env.local")


class GameMaster(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are a Sci-Fi Game Master running an adventure on Mars.
Tone: cinematic, dramatic, immersive.

Rules:
- Describe scenes vividly.
- End every response with: “What do you do next?”
- Use tools ONLY when needed (new game, state, inventory, logs).
- Never break character.
""",
            tools=[
                start_new_game,
                get_game_state,
                update_location,
                add_to_inventory,
                log_story_event,
            ],
        )


async def entrypoint(ctx: JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Narration",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2)
        ),
        vad=None,
        turn_detection=None,
        preemptive_generation=True
    )

    await session.start(
        agent=GameMaster(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
