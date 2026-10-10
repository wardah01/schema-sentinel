#!/usr/bin/env python3
"""Schema Sentinel: review a SQL schema with a local open-weight model (via Ollama)."""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b"
SKILL_PATH = Path(__file__).parent / "skills" / "sql-schema-review" / "SKILL.md"


def load_instructions() -> str:
    """Read the skill file and strip the YAML frontmatter."""
    text = SKILL_PATH.read_text(encoding="utf-8")
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()


def review(schema_sql: str) -> str:
    payload = {
        "model": MODEL,
        "stream": False,
        "think": False,  # skip Qwen3's slow reasoning mode on CPU
        "options": {"temperature": 0.2, "num_ctx": 4096},
        "messages": [
            {"role": "system", "content": load_instructions()},
            {"role": "user", "content": f"/no_think\nReview this schema:\n\n{schema_sql}"},
        ],
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            return json.loads(resp.read())["message"]["content"]
    except urllib.error.URLError:
        sys.exit("Could not reach Ollama at localhost:11434. Is it running?")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python sentinel.py path/to/schema.sql")
    schema = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(f"Reviewing {sys.argv[1]} with {MODEL} (this can take a minute on CPU)...\n")
    print(review(schema))


if __name__ == "__main__":
    main()