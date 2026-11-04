from ollama import chat
import time
import uuid

from agentic_ai.tools.flight_tool import search_flights
from agentic_ai.tools.hotel_tool import search_hotels
from agentic_ai.memory.conversation_store import ConversationStore
from agentic_ai.memory.context_manager import ContextManager
from agentic_ai.memory.conversation_summarizer import ConversationSummarizer
from agentic_ai.memory.travel_state import TravelState
from agentic_ai.memory.state_extractor import StateExtractor
from agentic_ai.tools.tool_executor import ToolExecutor
from agentic_ai.observability.logger import get_logger

TOOLS = {
    "search_flights": search_flights,
    "search_hotels": search_hotels
}

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are a travel assistant. "
        "Use tools to search for flights and hotels. "
        "Ask questions when required information is missing. "
        "All tool results are mock data. "
        "Never invent prices or availability."
    )
}

class TravelAgent:
    def __init__(self, session_id: str, chat_client: None):
        self.session_id = session_id
        self.chat_client = chat_client or chat
        self.store = ConversationStore()
        self.context_manager = ContextManager(max_turns=2)
        self.summarizer = ConversationSummarizer()
        self.summary, self.summarized_turns = (
            self.store.load_summary(session_id)
        )
        self.state_extractor = StateExtractor()
        saved_state = self.store.load_state(session_id)
        self.state = (
            TravelState.model_validate_json(saved_state)
            if saved_state
            else TravelState()
        )
        self.tool_executor = ToolExecutor()
        self.logger = get_logger("TravelAgent")

        history = self.store.load(session_id)
        self.messages = [SYSTEM_MESSAGE] + history

    def add_message(self, message):
        if hasattr(message, "model_dump"):
            message = message.model_dump(exclude_none=True)

        message.pop("thinking", None)
        self.messages.append(message)
        self.store.save(self.session_id, message)

    def ask(self, user_request: str) -> str:
        trace_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        self.logger.info(
            "trace_id=%s session_id=%s event=request_started",
            trace_id,
            self.session_id
        )

        self.add_message({
            "role": "user",
            "content": user_request
        })
        self.update_summary()

        update = self.state_extractor.extract(
            user_request, 
            self.state
        )

        self.state.apply_update(update)

        self.store.save_state(
            self.session_id, 
            self.state
        )
        self.logger.debug(
            "trace_id=%s session_id=%s event=state saved state=%s",
            trace_id,
            self.session_id,
            self.state
        )
        
        for _ in range(5):
            turns = self.context_manager.split_turns(self.messages)
            recent_turns = turns[self.summarized_turns:]
            recent_messages = [
                message
                for turn in recent_turns
                for message in turn
            ]
            context = self.context_manager.build_context([SYSTEM_MESSAGE] + recent_messages)

            if self.summary:
                context.insert(1, {
                    "role": "system",
                    "content": (
                        "Relevant memory from earlier conversation:\n"
                        + self.summary
                    )
                })

            self.logger.debug(
                "trace_id=%s event=context_built sqlite_history_messages=%d llm_context_messages=%d",
                trace_id,
                len(self.messages),
                len(context)
            )

            context.insert(1, {
                "role": "system",
                "content": (
                    "Current structured travel state:\n"
                    + self.state.model_dump_json()
                    +"\nUse this state as the current known travel information."
                )
            })

            llm_start = time.perf_counter()

            response = self.chat_client(
                model="qwen3:8b",
                messages=context,
                tools=list(TOOLS.values()),
                think=False,
                options={"num_ctx": 8192}
            )

            llm_duration = time.perf_counter() - llm_start

            self.logger.info(
                "trace_id=%s event=llm_completed duration_ms=%.2f",
                trace_id,
                llm_duration * 1000
            )

            self.add_message(response.message)
            
            if not response.message.tool_calls:
                total_duration = time.perf_counter() - start_time

                self.logger.info(
                    "trace_id=%s event=request_completed duration=%.2f",
                    trace_id,
                    total_duration * 1000
                )

                return response.message.content or ""

            for tool_call in response.message.tool_calls:
                name = tool_call.function.name
                arguments = tool_call.function.arguments

                tool_start = time.perf_counter()

                result = self.tool_executor.execute(
                    name,
                    arguments
                )

                tool_duration = time.perf_counter() - tool_start

                self.logger.info(
                    "trace_id=%s event=tool_completed "
                    "tool=%s success=%s duration_ms=%.2f",
                    trace_id,
                    name,
                    result.success,
                    tool_duration * 1000
                )

                self.add_message({
                    "role": "tool",
                    "tool_name": name,
                    "content": result.model_dump_json()
                })

        self.logger.warning(
            "trace_id=%s event=max_iterations_reached",
            trace_id
        )

        return "Agent stopped: maximum iterations reached."

    def update_summary(self):

        turns = self.context_manager.split_turns(self.messages)
        completed_turns = turns[:-1]
        cutoff = max(
            0,
            len(completed_turns) - self.context_manager.max_turns
        )

        if cutoff <= self.summarized_turns:
            return

        new_turns = completed_turns[self.summarized_turns:cutoff]

        messages_to_summarize = [
            message
            for turn in new_turns
            for message in turn
        ]

        new_summary = self.summarizer.summarize(
            self.summary,
            messages_to_summarize
        )

        self.store.save_summary(
            self.session_id,
            new_summary,
            cutoff
        )

        self.summary = new_summary
        self.summarized_turns = cutoff 