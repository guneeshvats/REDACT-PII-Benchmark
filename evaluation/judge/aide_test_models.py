#!/usr/bin/env python3
"""
aide_test_models.py — Sanity check for AIDE model access (v2)

Verifies all 4 models respond with valid content (not just non-error).
Handles per-vendor parameter quirks:
  - gpt-5.2 uses max_completion_tokens (not max_tokens)
  - gemini-2.5-pro needs higher token budget for internal reasoning
  - claude-sonnet-4-6 in AIDE returns content via output.message.content[0].text

Run this FIRST. All 4 should print non-empty "OK". If anything is empty
or shows MAX_TOKENS, stop and fix before the expensive runs.
"""

import json
import sys

try:
    from aide import AIDE
except ImportError:
    print("ERROR: 'aide' package not found. Run on AIDE.")
    sys.exit(1)

aide = AIDE()

MODELS = [
    ("gpt-5.2",            "openai",    "judge"),
    ("claude-sonnet-4-6",  "anthropic", "judge"),
    ("gemini-2.5-pro",     "google",    "judge"),
    ("gpt-4.1",            "openai",    "detector"),
]

TEST_PROMPT = "Reply with just the word OK and nothing else."


def make_payload(model: str, vendor: str, prompt: str):
    """Per-vendor payload — accounts for parameter and tokenization quirks."""
    if vendor == "google":
        return {
            "contents": {
                "role": "user",
                "parts": [{"text": prompt}]
            },
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": 2000,
            }
        }
    if model == "gpt-5.2":
        return {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ],
            "max_completion_tokens": 2000,
        }
    return {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ],
        "temperature": 0.0,
        "max_tokens": 100,
    }


def extract_content(response, vendor):
    """Vendor-aware content extraction."""
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            return response

    if not isinstance(response, dict):
        return None

    # AIDE-wrapped Anthropic shape (Bedrock-style): output.message.content[0].text
    if "output" in response and isinstance(response["output"], dict):
        output = response["output"]
        msg = output.get("message", {})
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and "text" in block:
                        return block["text"]
            elif isinstance(content, str):
                return content

    # OpenAI shape
    if "choices" in response:
        choices = response.get("choices", [])
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                msg = first.get("message")
                if isinstance(msg, dict):
                    content = msg.get("content")
                    if isinstance(content, str):
                        return content
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                return block.get("text", "")
                if first.get("text"):
                    return first["text"]

    # Direct Anthropic shape
    if "content" in response:
        content = response["content"]
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        return block.get("text", "")
                    if "text" in block:
                        return block["text"]

    # Gemini shape
    if "candidates" in response:
        cands = response.get("candidates", [])
        if isinstance(cands, list) and cands:
            first = cands[0]
            if isinstance(first, dict):
                gcontent = first.get("content", {})
                if isinstance(gcontent, dict):
                    parts = gcontent.get("parts", [])
                    if isinstance(parts, list) and parts:
                        text = parts[0].get("text", "")
                        if text:
                            return text

    if "text" in response:
        return response["text"]

    return None


def main():
    print("=" * 70)
    print("AIDE MODEL ACCESS TEST v2")
    print("=" * 70)
    print()

    results = []
    for model, vendor, role in MODELS:
        print(f"Testing: {model} ({vendor}, {role})")
        try:
            payload = make_payload(model, vendor, TEST_PROMPT)
            response = aide.call_llm(model=model, payload=payload)
            content = extract_content(response, vendor)

            print(f"  EXTRACTED CONTENT: {content!r}")
            print(f"  RAW (first 400 chars): {str(response)[:400]}")

            if content and content.strip():
                results.append({"model": model, "ok": True, "content": content.strip()})
                print("  STATUS: OK")
            else:
                results.append({"model": model, "ok": False, "reason": "empty content"})
                print("  STATUS: EMPTY (fix payload/parser)")
            print()
        except Exception as e:
            print(f"  ERROR: {e}")
            print()
            results.append({"model": model, "ok": False, "reason": str(e)[:200]})

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for r in results:
        status = "OK " if r["ok"] else "FAIL"
        extra = r.get("content", r.get("reason", ""))
        print(f"  [{status}] {r['model']} -> {extra[:80]}")
    print()
    all_ok = all(r["ok"] for r in results)
    if all_ok:
        print("All 4 models returned content. Safe to run aide_geval.py and aide_llm_detectors.py.")
    else:
        print("Some models failed. Do NOT run the expensive scripts yet.")
        sys.exit(1)


if __name__ == "__main__":
    main()
