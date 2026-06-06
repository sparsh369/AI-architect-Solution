"""
Shared LLM plumbing for every agent.

Design goals:
  * One place that knows how to talk to the LLM (LangChain + OpenAI GPT-4o).
  * Graceful DEMO MODE: if no OPENAI_API_KEY is set we never crash — agents
    fall back to a built-in heuristic generator so the workshop demo always
    produces a full blueprint, online or offline.
  * Robust JSON handling: LLMs sometimes wrap JSON in ```json fences or add
    stray prose; `parse_json` digs the object out reliably.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def llm_available() -> bool:
    """True when a real OpenAI key is configured."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(key) and not key.lower().startswith("your")


def get_llm(temperature: Optional[float] = None):
    """
    Return a configured LangChain ChatOpenAI client, or None in demo mode.

    Imported lazily so the project still imports cleanly even if the optional
    AI dependencies are missing.
    """
    if not llm_available():
        return None

    from langchain_openai import ChatOpenAI

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    temp = temperature if temperature is not None else float(
        os.getenv("OPENAI_TEMPERATURE", "0.2")
    )
    return ChatOpenAI(model=model, temperature=temp)


def parse_json(raw: str) -> dict:
    """
    Extract the first JSON object from an LLM response.

    Handles ```json fenced blocks, leading/trailing prose, and minor noise.
    Raises ValueError if nothing parseable is found.
    """
    if raw is None:
        raise ValueError("Empty LLM response")

    text = raw.strip()

    # Strip ``` / ```json fences if present.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    # Fast path.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: grab the outermost {...} block.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        return json.loads(candidate)

    raise ValueError("No JSON object found in LLM response")


def run_llm_json(system_prompt: str, user_prompt: str,
                 temperature: Optional[float] = None) -> Optional[dict]:
    """
    Call the LLM with a system + user prompt and return parsed JSON.

    Returns None (signalling the caller to use its demo fallback) if the LLM
    is unavailable or the call fails for any reason.
    """
    llm = get_llm(temperature)
    if llm is None:
        return None

    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        response = llm.invoke(
            [SystemMessage(content=system_prompt),
             HumanMessage(content=user_prompt)]
        )
        return parse_json(response.content)
    except Exception as exc:  # network error, rate limit, bad JSON, etc.
        print(f"[base] LLM call failed, using demo fallback: {exc}")
        return None
