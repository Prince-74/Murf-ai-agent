# improv_state.py

class ImprovState:
    def __init__(self):
        self.player_name = None
        self.current_round = 0
        self.max_rounds = 3
        self.phase = "intro"  # intro | awaiting_improv | reacting | done

        self.rounds = []
        self.current_scenario = None

    def next_round(self):
        self.current_round += 1
