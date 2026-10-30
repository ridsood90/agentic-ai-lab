import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "conversations.db"

class ConversationStore:

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(DB_PATH) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    message_json TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    session_id TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    summarized_turns INTEGER NOT NULL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS travel_states (
                    session_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL
                )
            """)

    def save(self, session_id:str, message:dict):
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                "INSERT INTO messages (session_id, message_json) VALUES (?, ?)",
                (session_id, json.dumps(message))
            )

    def load(self, session_id:str) -> list:
        with sqlite3.connect(DB_PATH) as connection:
            rows = connection.execute(
                """
                SELECT message_json
                FROM messages
                WHERE session_id = ?
                ORDER BY id
                """,
                (session_id,)
            ).fetchall()

        return [json.loads(row[0]) for row in rows]

    def save_summary(
        self,
        session_id: str,
        summary: str,
        summarized_turns: int
    ):
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """
                INSERT INTO conversation_summaries
                    (session_id, summary, summarized_turns)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id)
                DO UPDATE SET
                    summary = excluded.summary,
                    summarized_turns = excluded.summarized_turns
                """,
                (session_id, summary, summarized_turns)
            )

    def load_summary(self, session_id: str):
        with sqlite3.connect(DB_PATH) as connection:
            row = connection.execute(
                """
                SELECT summary, summarized_turns
                FROM conversation_summaries
                WHERE session_id = ?
                """,
                (session_id,)
            ).fetchone()

        return row if row else("", 0)

    def save_state(self, session_id: str, state):
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """
                INSERT INTO travel_states (session_id, state_json)
                VALUES (?, ?)
                ON CONFLICT(session_id)
                DO UPDATE SET state_json=excluded.state_json
                """,
                (session_id, state.model_dump_json())
            )

    def load_state(self, session_id:str):
        with sqlite3.connect(DB_PATH) as connection:
            row = connection.execute(
                """
                SELECT state_json
                FROM travel_states
                WHERE session_id = ?
                """,
                (session_id,)
            ).fetchone()

        return row[0] if row else None