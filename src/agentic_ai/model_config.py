"""Single place that decides how the agent talks to Ollama.

Override per run without editing code:
    AGENT_MODEL=mistral:latest PYTHONPATH=src python scripts/run_evals.py
    AGENT_TIMEOUT=90 AGENT_MAX_TOKENS=512 ...
"""
import os

from ollama import Client

DEFAULT_MODEL = "qwen3:8b"
MODEL = os.environ.get("AGENT_MODEL", DEFAULT_MODEL)

# A model that never emits a stop token (a runaway loop) must not block a run
# forever. One slow or looping call then costs one run, not the whole batch.
REQUEST_TIMEOUT_S = float(os.environ.get("AGENT_TIMEOUT", "180"))
MAX_OUTPUT_TOKENS = int(os.environ.get("AGENT_MAX_TOKENS", "1024"))

# Every LLM call in the project goes through this one client.
chat = Client(timeout=REQUEST_TIMEOUT_S).chat
