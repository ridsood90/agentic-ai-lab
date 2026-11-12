"""Single place that decides which Ollama model the agent uses.

Override per run without editing code:
    AGENT_MODEL=llama3.1:8b PYTHONPATH=src python scripts/run_evals.py
"""
import os

DEFAULT_MODEL = "qwen3:8b"
MODEL = os.environ.get("AGENT_MODEL", DEFAULT_MODEL)
