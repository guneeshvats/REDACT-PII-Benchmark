"""
Reusable span utilities for greedy search and boundary checking.

These utilities are decoupled from the reconciliation pipeline so that
postprocessing scripts can import and reuse them independently.
"""

import logging
import re
import unicodedata
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CJK helpers
# ---------------------------------------------------------------------------

def _is_cjk_char(ch: str) -> bool:
    """Check if a character belongs to a CJK script."""
    try:
        name = unicodedata.name(ch, "")
        return any(s in name for s in ("CJK", "HANGUL", "HIRAGANA", "KATAKANA"))
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Boundary checking utilities
# ---------------------------------------------------------------------------

def is_boundary_blocked_left(norm_text: str, start: int) -> bool:
    """Check if the character to the left of *start* should block a match.

    Alphanumeric always blocks.  '@' always blocks.
    '.' blocks only when it sits between two alphanumeric characters
    (e.g. 'google.com') — a sentence-ending period ('old.') does NOT block.
    """
    if start <= 0:
        return False
    ch = norm_text[start - 1]
    if ch.isalnum():
        return True
    if ch == '@':
        return True
    if ch == '.' and start >= 2 and norm_text[start - 2].isalnum():
        return True
    return False


def is_boundary_blocked_right(norm_text: str, end: int) -> bool:
    """Check if the character to the right of *end* should block a match.

    Alphanumeric always blocks.  '@' always blocks.
    '.' blocks only when followed by another alphanumeric character
    (e.g. 'google.com') — a sentence-ending period ('old.') does NOT block.
    """
    if end >= len(norm_text):
        return False
    ch = norm_text[end]
    if ch.isalnum():
        return True
    if ch == '@':
        return True
    if ch == '.' and end + 1 < len(norm_text) and norm_text[end + 1].isalnum():
        return True
    return False


def passes_boundary_check(norm_text: str, start: int, end: int) -> bool:
    """Return True if the span at [start, end) passes boundary checks.

    Blocks matches that land inside emails / domains / larger words,
    with a CJK exemption (CJK has no whitespace word boundaries).
    """
    if is_boundary_blocked_left(norm_text, start):
        if not (start > 0 and _is_cjk_char(norm_text[start - 1])):
            return False
    if is_boundary_blocked_right(norm_text, end):
        if not (end < len(norm_text) and _is_cjk_char(norm_text[end])):
            return False
    return True


# ---------------------------------------------------------------------------
# Overlap removal
# ---------------------------------------------------------------------------

def remove_overlaps(sorted_spans: list[dict]) -> list[dict]:
    """Remove overlapping spans, keeping the earlier one (or longer if same start)."""
    if not sorted_spans:
        return []
    result = [sorted_spans[0]]
    for s in sorted_spans[1:]:
        prev = result[-1]
        if s["start"] >= prev["end"]:
            result.append(s)
        else:
            # Overlap: keep the longer one
            if (s["end"] - s["start"]) > (prev["end"] - prev["start"]):
                result[-1] = s
    return result


# ---------------------------------------------------------------------------
# Greedy search
# ---------------------------------------------------------------------------

def greedy_search(
    norm_text: str,
    predictions: list[dict],
    covered: Optional[set[int]] = None,
    mode: str = "single_occ",
) -> list[dict]:
    """
    Find entity positions in text using greedy string matching.

    Supports two modes:
      - **single_occ**: Each prediction claims the next unclaimed
        occurrence of its text.  If a model predicts "Danish Shah"
        twice, exactly two occurrences are claimed (1st → 1st
        available, 2nd → 2nd available).
      - **multiple_occ**: Predictions are deduplicated to unique
        (entity_type, value) pairs, and ALL unclaimed occurrences
        in the text are returned for each unique pair.

    Longest entities are processed first to prevent shorter
    substrings from stealing positions.

    Args:
        norm_text: NFC-normalized text to search in.
        predictions: List of dicts, each with:
            - ``etype`` (str): entity type
            - ``value_norm`` (str): NFC-normalized entity text to find
            - ``value`` (str): original entity text (for output)
        covered: Set of character positions already claimed.
            These positions will not be matched.  Updated in-place.
        mode: ``"single_occ"`` or ``"multiple_occ"``.

    Returns:
        List of span dicts ``{start, end, type, text, source}``,
        sorted by start position.
    """
    if not norm_text or not predictions:
        return []

    if covered is None:
        covered = set()

    # Work on a copy so the caller's set is not mutated unexpectedly
    greedy_covered = set(covered)

    # Sort longest-first so longer entities claim positions first
    sorted_preds = sorted(
        predictions, key=lambda x: len(x["value_norm"]), reverse=True
    )

    if mode == "multiple_occ":
        return _greedy_multiple_occ(norm_text, sorted_preds, greedy_covered)
    else:
        return _greedy_single_occ(norm_text, sorted_preds, greedy_covered)


def _greedy_single_occ(
    norm_text: str,
    sorted_preds: list[dict],
    greedy_covered: set[int],
) -> list[dict]:
    """
    Single-occurrence mode: each prediction claims exactly one
    position via an occurrence tracker.

    If "Danish Shah" appears 3 times in predictions, at most 3
    occurrences in the text are claimed (one per prediction).
    """
    resolved: list[dict] = []

    for pred in sorted_preds:
        value_norm = pred["value_norm"]
        available = _find_available_positions(
            norm_text, value_norm, greedy_covered
        )

        if available:
            s, e = available[0]
            resolved.append({
                "start": s,
                "end": e,
                "type": pred["etype"],
                "text": norm_text[s:e],
                "source": "greedy",
            })
            for i in range(s, e):
                greedy_covered.add(i)

    resolved.sort(key=lambda x: x["start"])
    return resolved


def _greedy_multiple_occ(
    norm_text: str,
    sorted_preds: list[dict],
    greedy_covered: set[int],
) -> list[dict]:
    """
    Multiple-occurrence mode: predictions are deduplicated to
    unique (etype, value_norm) pairs, and ALL unclaimed occurrences
    in the text are returned for each pair.

    If "Danish Shah" appears 3 times in text but only 2 predictions
    exist, all 3 occurrences are still returned.
    """
    # Deduplicate to unique (etype, value_norm)
    seen: set[tuple[str, str]] = set()
    unique_preds: list[dict] = []
    for pred in sorted_preds:
        key = (pred["etype"], pred["value_norm"])
        if key not in seen:
            seen.add(key)
            unique_preds.append(pred)

    resolved: list[dict] = []

    for pred in unique_preds:
        value_norm = pred["value_norm"]
        available = _find_available_positions(
            norm_text, value_norm, greedy_covered
        )

        for s, e in available:
            resolved.append({
                "start": s,
                "end": e,
                "type": pred["etype"],
                "text": norm_text[s:e],
                "source": "greedy",
            })
            for i in range(s, e):
                greedy_covered.add(i)

    resolved.sort(key=lambda x: x["start"])
    return resolved


def _find_available_positions(
    norm_text: str,
    value_norm: str,
    covered: set[int],
) -> list[tuple[int, int]]:
    """
    Find all positions of *value_norm* in *norm_text* that pass
    boundary checks and are not covered.

    Tries case-sensitive first, falls back to case-insensitive.

    Returns:
        List of (start, end) tuples, in order of appearance.
    """
    pattern = re.escape(value_norm)

    # Case-sensitive first
    all_positions = [
        (m.start(), m.end())
        for m in re.finditer(pattern, norm_text)
    ]
    # Case-insensitive fallback
    if not all_positions:
        all_positions = [
            (m.start(), m.end())
            for m in re.finditer(pattern, norm_text, re.IGNORECASE)
        ]

    available = []
    for s, e in all_positions:
        if not passes_boundary_check(norm_text, s, e):
            continue
        if any(i in covered for i in range(s, e)):
            continue
        available.append((s, e))

    return available
