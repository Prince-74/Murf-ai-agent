import logging
from dotenv import load_dotenv

from improv_state import ImprovState

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    RoomInputOptions,
    cli,
    tokenize,
)

from livekit.plugins import murf, google, deepgram

logger = logging.getLogger("improv-agent")
load_dotenv(".env.local")


SCENARIOS = [
    "You are a Martian barista telling a customer their latte has become a wormhole.",
    "You are a time-traveling tour guide explaining smartphones to someone from the year 1800.",
    "You are a shopkeeper trying to convince a customer that the cursed object they returned is actually perfectly safe.",
    "You are a waiter explaining that their meal escaped the kitchen and is running loose.",
]


class ImprovAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
You are the energetic host of a TV improv show **Improv Battle**.
High energy, witty, comedic, but respectful.

GAME RULES:
- Introduce yourself.
- Ask the player for their name (if unknown).
- Run 3 improv rounds.
- For each round:
   1. Announce the scenario.
   2. Ask the player to act it out.
   3. React with mixed tones (funny, supportive, teasing).
- After 3 rounds, give a closing summary.

GAME STATE RULES:
- Never break character.
- Never reveal internal state.
- Do not call tools (there are no tools).
- Always end your turn with: “What do you do next?”
""",
        )

        self.state = ImprovState()

    async def on_user_message(self, msg, ctx):
        user_text = msg.text.strip()

        # 1. intro -> ask name
        if self.state.phase == "intro":
            self.state.player_name = user_text
            self.state.phase = "awaiting_improv"
            return f"Great to meet you, {self.state.player_name}! Welcome to **Improv Battle**. Let’s start Round 1! {self.start_scenario()}"

        # 2. awaiting_improv -> react
        if self.state.phase == "awaiting_improv":
            self.state.phase = "reacting"
            return self.react_to_scene(user_text)

        # 3. reacting -> move to next round or finish
        if self.state.phase == "reacting":
            return self.move_to_next_round()

    def start_scenario(self):
        scenario = SCENARIOS[self.state.current_round]
        self.state.current_scenario = scenario
        return f"Your scenario is: {scenario}. Begin your improv! What do you do next?"

    def react_to_scene(self, player_response):
        reactions = [
            "That was wild!",
            "Interesting choice of delivery!",
            "Unexpected but entertaining!",
            "You really committed to that!",
        ]
        import random

        reaction = random.choice(reactions)

        self.state.rounds.append(
            {
                "scenario": self.state.current_scenario,
                "player_response": player_response,
                "host_reaction": reaction,
            }
        )

        return f"{reaction} Ready for the next step?"

    def move_to_next_round(self):
        self.state.next_round()

        if self.state.current_round >= self.state.max_rounds:
            self.state.phase = "done"
            return self.final_summary()

        self.state.phase = "awaiting_improv"
        return f"Great! Round {self.state.current_round + 1} begins now! {self.start_scenario()}"

    def final_summary(self):
        summary = f"That's a wrap, {self.state.player_name}! You completed {self.state.max_rounds} rounds of Improv Battle."
        return summary + " Thanks for playing!"


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
        agent=ImprovAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
