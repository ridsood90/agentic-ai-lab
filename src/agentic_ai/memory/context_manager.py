class ContextManager:

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns

    def build_context(self, messages: list) -> list:

        system_messages = []
        turns = []
        current_turn = []

        for message in messages:

            if message["role"] == "system":
                system_messages.append(message)
                continue

            if message["role"] == "user":
                if current_turn:
                    turns.append(current_turn)
                current_turn = [message]

            else:
                current_turn.append(message)

        if current_turn:
            turns.append(current_turn)

        recent_turns = turns[-self.max_turns:]

        context = system_messages.copy()

        for turn in recent_turns:
            context.extend(turn)

        return context

    def split_turns(self, messages: list) -> list:
        turns = []
        current_turn = []

        for message in messages:
            if message["role"] == "system":
                continue

            if message["role"] == "user":
                if current_turn:
                    turns.append(current_turn)

                current_turn = [message]
            elif current_turn:
                current_turn.append(message)

        if current_turn:
            turns.append(current_turn)

        return turns