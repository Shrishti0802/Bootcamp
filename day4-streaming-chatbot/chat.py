import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

load_dotenv()

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
# Free models cost $0, so we log what the call WOULD cost at reference prices
# (USD per million tokens). Update these to match a paid model if you like.
PRICE_IN, PRICE_OUT = 0.10, 0.50
USD_TO_INR = 88.0   # placeholder: update to today's rate
MAX_TURNS = 10      # stop condition so we never loop forever
MAX_TOKENS = 500    # cap on each reply's length
LOG_FILE = Path("cost_log.csv")
SYSTEM_PROMPT = "You are a friendly, concise assistant. Keep answers under 120 words."


def estimate_cost(input_tokens: int, output_tokens: int) -> tuple[float, float]:
    usd = (input_tokens * PRICE_IN + output_tokens * PRICE_OUT) / 1_000_000
    return usd, usd * USD_TO_INR


def log_call(input_tokens: int, output_tokens: int, usd: float, inr: float) -> None:
    new_file = not LOG_FILE.exists()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["timestamp", "model", "input_tokens", "output_tokens", "cost_usd", "cost_inr"])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            MODEL, input_tokens, output_tokens, f"{usd:.6f}", f"{inr:.4f}",
        ])


def is_retryable(exc: BaseException) -> bool:
    """Retry on 429 (rate limit), 5xx (server trouble) and network errors."""
    if isinstance(exc, (openai.RateLimitError, openai.APIConnectionError)):
        return True
    return isinstance(exc, openai.APIStatusError) and exc.status_code >= 500


@retry(
    retry=retry_if_exception(is_retryable),
    wait=wait_exponential(multiplier=1, min=1, max=20),  # waits 1s, 2s, 4s, 8s...
    stop=stop_after_attempt(5),
    reraise=True,
    before_sleep=lambda rs: print(f"\n[temporary error, retrying in {rs.next_action.sleep:.0f}s...]"),
)
def stream_reply(client: OpenAI, messages: list[dict]) -> tuple[str, int, int]:
    chunks: list[str] = []
    usage = None
    stream = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        stream=True,
        stream_options={"include_usage": True},  # ask for token counts at the end
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            print(text, end="", flush=True)  # show words as they arrive
            chunks.append(text)
        if chunk.usage:
            usage = chunk.usage
    print()
    in_tok = usage.prompt_tokens if usage else 0
    out_tok = usage.completion_tokens if usage else 0
    return "".join(chunks), in_tok, out_tok


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not os.getenv("OPENROUTER_API_KEY"):
        sys.exit("OPENROUTER_API_KEY not found. Put it in .env (see .env.example).")
    if MODEL.startswith("PASTE"):
        sys.exit("Set MODEL at the top of chat.py to a real model ID from openrouter.ai.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        max_retries=0,  # we handle retries ourselves with tenacity
    )
    messages: list[dict] = []
    session_usd = 0.0
    turns = 0

    print(f"Chatting with {MODEL}. Type 'quit' to stop (max {MAX_TURNS} turns).")
    while turns < MAX_TURNS:
        try:
            user_text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_text.lower() in {"quit", "exit"}:
            break
        if not user_text:
            continue

        messages.append({"role": "user", "content": user_text})
        print("\nAssistant: ", end="", flush=True)
        try:
            reply, in_tok, out_tok = stream_reply(client, messages)
        except openai.APIError as exc:
            print(f"\n[API error: {exc}]")
            messages.pop()  # remove the failed question so history stays valid
            continue

        messages.append({"role": "assistant", "content": reply})
        usd, inr = estimate_cost(in_tok, out_tok)
        log_call(in_tok, out_tok, usd, inr)
        session_usd += usd
        turns += 1
        print(f"[in {in_tok} | out {out_tok} | est ${usd:.6f} | INR {inr:.4f} | session ${session_usd:.6f}]")

    print(f"\nDone. {turns} turns, estimated cost about ${session_usd:.6f}. Log: {LOG_FILE}")


if __name__ == "__main__":
    main()