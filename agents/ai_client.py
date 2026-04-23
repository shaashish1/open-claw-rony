from __future__ import annotations
"""
ITGYANI AI Client — Azure Foundry wrapper
All agents use this instead of OpenRouter or direct OpenAI.

Models:
  - claude-sonnet-4-6  → fast, smart (default for most tasks)
  - claude-opus-4-6    → heavy reasoning (strategy, scoring)
  - gpt-4o             → fallback / multi-modal
  - gpt-4o-transcribe  → audio transcription
  - gpt-4o-mini-tts    → text to speech

Rate limits: 130K TPM (Claude), 250K TPM (GPT-4o)
"""
import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional

FOUNDRY_KEY = os.getenv("AZURE_FOUNDRY_KEY", "")
ANTHROPIC_ENDPOINT = "https://ai-sambhatt3210ai899661109114.services.ai.azure.com/anthropic/v1/messages"
COGSVCS_ENDPOINT   = "https://ai-sambhatt3210ai899661109114.cognitiveservices.azure.com"

DEFAULT_MODEL = "claude-sonnet-4-6"
OPUS_MODEL    = "claude-opus-4-6"
GPT4O_MODEL   = "gpt-4o"


def chat(
    prompt: str,
    system: str = "You are RONY, the AI COO of ITGYANI. Be concise and action-focused.",
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Single-turn chat via Azure Foundry Claude."""
    return chat_messages(
        messages=[{"role": "user", "content": prompt}],
        system=system,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


def chat_messages(
    messages: List[Dict],
    system: str = "You are RONY, the AI COO of ITGYANI. Be concise and action-focused.",
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Multi-turn chat via Azure Foundry Claude."""
    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system,
        "messages": messages,
    }).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": FOUNDRY_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["content"][0]["text"]


def chat_opus(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    """Heavy reasoning tasks — use Opus sparingly."""
    return chat(prompt, system=system or "You are a strategic business analyst.", model=OPUS_MODEL, max_tokens=max_tokens)


def json_chat(prompt: str, system: str = "", model: str = DEFAULT_MODEL) -> dict:
    """Chat and parse JSON response."""
    sys = system or "Respond only with valid JSON, no markdown, no explanation."
    raw = chat(prompt, system=sys, model=model, max_tokens=2048, temperature=0.2)
    # Strip markdown code fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


if __name__ == "__main__":
    result = chat("Confirm you are online. Reply in exactly 5 words.")
    print(f"Azure Foundry test: {result}")
