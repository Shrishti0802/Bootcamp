import argparse
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from models import Triage

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
MODEL = os.getenv("MODEL")


def load_prompt(version: str) -> str:
    path = Path(__file__).parent / "prompts" / f"{version}.txt"
    return path.read_text(encoding="utf-8")


def ask(messages: list) -> str:
    resp = client.chat.completions.create(model=MODEL, messages=messages, temperature=0)
    return resp.choices[0].message.content or ""


def parse(text: str) -> Triage:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON found in reply")
    return Triage.model_validate(json.loads(match.group(0)))


def triage(complaint: str, version: str = "v1"):
    messages = [
        {"role": "system", "content": load_prompt(version)},
        {"role": "user", "content": f"<complaint>{complaint}</complaint>"},
    ]
    reply = ask(messages)
    try:
        return parse(reply)
    except ValueError as err:  # covers bad JSON and Pydantic errors
        messages += [
            {"role": "assistant", "content": reply},
            {"role": "user", "content": f"Your JSON was invalid: {err}. Reply again with ONLY the corrected JSON."},
        ]
        reply = ask(messages)
        try:
            return parse(reply)
        except ValueError:
            return None  # failed twice


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("complaint")
    ap.add_argument("--prompt", default="v1")
    args = ap.parse_args()
    result = triage(args.complaint, args.prompt)
    print(result.model_dump_json(indent=2) if result else "Invalid output after retry")