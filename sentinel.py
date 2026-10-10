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

# The model can only answer in this shape, so it cannot ramble or narrate.
REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["High", "Medium", "Low"]},
                    "location": {"type": "string"},
                    "problem": {"type": "string"},
                    "fix": {"type": "string"},
                },
                "required": ["severity", "location", "problem", "fix"],
            },
        },
        "top_fixes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["issues", "top_fixes"],
}

TASK = (
    "/no_think\n"
    "Review the SQL schema below. Report only issues actually present in it. "
    "Return JSON only. At most 10 issues, most severe first. "
    "'location' is like table.column. 'problem' and 'fix' are each ONE short sentence. "
    "'top_fixes' lists the 3 most important fixes, one short sentence each.\n\n"
)

SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def load_instructions() -> str:
    """Read the skill file and strip the YAML frontmatter."""
    text = SKILL_PATH.read_text(encoding="utf-8")
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text.strip()


def get_review(schema_sql: str) -> str:
    """Ask the local model for a structured review; show progress while it works."""
    payload = {
        "model": MODEL,
        "stream": True,
        "think": False,  # skip Qwen3's slow reasoning mode on CPU
        "format": REPORT_SCHEMA,
        "options": {"temperature": 0.2, "num_ctx": 4096, "num_predict": 1200},
        "messages": [
            {"role": "system", "content": load_instructions()},
            {"role": "user", "content": TASK + schema_sql},
        ],
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    raw, tokens = "", 0
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            for line in resp:
                if not line.strip():
                    continue
                chunk = json.loads(line)
                raw += chunk.get("message", {}).get("content", "")
                tokens += 1
                print(f"\rReviewing... {tokens} tokens generated", end="", flush=True)
                if chunk.get("done"):
                    break
    except urllib.error.URLError:
        sys.exit("\nCould not reach Ollama at localhost:11434. Is it running?")
    print("\r" + " " * 50 + "\r", end="")
    return raw


def render(raw: str) -> None:
    """Turn the model's JSON into a clean, readable report."""
    try:
        report = json.loads(raw)
    except json.JSONDecodeError:
        print("The model's output was cut off or malformed. Raw output:\n")
        print(raw)
        return

    issues = sorted(
        report.get("issues", []),
        key=lambda i: SEVERITY_ORDER.get(i.get("severity"), 3),
    )
    print(f"Schema Sentinel found {len(issues)} issue(s)\n")
    for n, issue in enumerate(issues, 1):
        print(f"{n}. [{str(issue.get('severity', '?')).upper()}] {issue.get('location', '')}")
        print(f"   Problem: {issue.get('problem', '')}")
        print(f"   Fix:     {issue.get('fix', '')}\n")

    top = report.get("top_fixes", [])
    if top:
        print("Top fixes:")
        for n, fix in enumerate(top, 1):
            print(f"  {n}. {fix}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: python sentinel.py path/to/schema.sql")
    schema = Path(sys.argv[1]).read_text(encoding="utf-8")
    print(f"Reviewing {sys.argv[1]} with {MODEL} (CPU-only, this can take a few minutes)...\n")
    render(get_review(schema))


if __name__ == "__main__":
    main()