"""
Span reconciliation for converting consensus entities to ground truth format.

Adapted from SyGra tasks.pii_data.entity_recovery for standalone use.
"""

import logging
import re
import unicodedata
from collections import Counter
from typing import Optional

from src.span_utils import (
    _is_cjk_char,
    greedy_search,
    is_boundary_blocked_left,
    is_boundary_blocked_right,
    passes_boundary_check,
    remove_overlaps,
)

logger = logging.getLogger(__name__)

# Mapping of real escape characters to their literal two-char representations
_ESCAPE_CHAR_TO_LITERAL = {'\n': '\\n', '\t': '\\t', '\r': '\\r'}
_LITERAL_TO_ESCAPE_CHAR = {v: k for k, v in _ESCAPE_CHAR_TO_LITERAL.items()}


# ---------------------------------------------------------------------------
# Helper function for standalone use
# ---------------------------------------------------------------------------

def reconcile_consensus_to_spans(
    text: str,
    consensus_entities: dict,
    consensus_metadata: Optional[dict] = None,
    greedy_mode: str = "single_occ",
) -> list:
    """
    Convert consensus entities to ground truth spans.
    
    This is a simplified version that only handles consensus entities
    (no marker spans or string-match spans like in full SyGra pipeline).
    
    Args:
        text: Original text
        consensus_entities: {entity_type: [entity_objects]} from consensus
        consensus_metadata: Metadata from consensus engine
        greedy_mode: 'single_occ' (default) matches one occurrence per
            prediction; 'multiple_occ' matches all occurrences in text.
        
    Returns:
        List of gt_entities with format:
        [{start, end, type, text, source: "consensus"}, ...]
    """
    return reconcile_spans(
        marker_spans=[],
        string_match_spans=[],
        consensus_entities=consensus_entities,
        clean_text=text,
        consensus_metadata=consensus_metadata,
        greedy_mode=greedy_mode,
    )


# ---------------------------------------------------------------------------
# S8a: String-match sweep
# ---------------------------------------------------------------------------

_CJK_SCRIPTS = {"CJK", "Hangul", "Hiragana", "Katakana"}


def string_match_sweep(
    clean_text: str,
    existing_spans: list[dict],
    entity_spec: list[dict],
    generated_entity_values: Optional[list[dict]] = None,
    language_script: str = "Latin",
) -> list[dict]:
    """
    Find entity values that appear in clean_text but are not covered by
    existing_spans.

    Collects candidate values from:
      1. entity_spec patterns' faker_values and forced_values
      2. generated_entity_values (from LLM ENTITIES: section)
      3. text of existing_spans (catch repeated mentions)

    Returns list of new spans (may be empty). Each span has:
      {start, end, type, text, source: "string_match"}
    """
    if not clean_text:
        return []

    # Normalize text for matching
    norm_text = unicodedata.normalize("NFC", clean_text)

    # Build set of already-covered character ranges
    covered = set()
    for s in existing_spans:
        for i in range(s["start"], s["end"]):
            covered.add(i)

    # Collect (entity_type, value) candidates
    candidates: list[tuple[str, str]] = []

    # From entity_spec
    if entity_spec:
        for entry in entity_spec:
            etype = entry["type"]
            # Faker values
            for v in entry.get("faker_values", []):
                if v:
                    candidates.append((etype, v))
            # Forced values (ambiguous mode)
            for v in entry.get("forced_values", []):
                if v:
                    candidates.append((etype, v))

    # From generated_entity_values (LLM-declared entities)
    if generated_entity_values:
        for ev in generated_entity_values:
            if ev.get("type") and ev.get("value"):
                candidates.append((ev["type"], ev["value"]))

    # From existing spans (catch repeated mentions)
    for s in existing_spans:
        candidates.append((s["type"], s["text"]))

    # Deduplicate candidates
    seen_candidates: set[tuple[str, str]] = set()
    unique_candidates: list[tuple[str, str]] = []
    for c in candidates:
        key = (c[0], c[1].strip())
        if key not in seen_candidates and len(key[1]) >= 3:
            seen_candidates.add(key)
            unique_candidates.append(key)

    # Sort by value length descending (prefer longer matches first)
    unique_candidates.sort(key=lambda x: len(x[1]), reverse=True)

    new_spans: list[dict] = []

    for etype, value in unique_candidates:
        value_norm = unicodedata.normalize("NFC", value.strip())
        if not value_norm:
            continue

        # Find all occurrences in text using word-boundary-aware search
        pattern = re.escape(value_norm)
        for match in re.finditer(pattern, norm_text):
            start, end = match.start(), match.end()

            # Skip if any character in this range is already covered
            if any(i in covered for i in range(start, end)):
                continue

            # Word boundary check: avoid matching inside a larger word.
            # For CJK scripts, skip this check — CJK has no whitespace word boundaries.
            skip_boundary = language_script in _CJK_SCRIPTS
            if not skip_boundary:
                if start > 0 and norm_text[start - 1].isalnum() and not _is_cjk_char(norm_text[start - 1]):
                    continue
                if end < len(norm_text) and norm_text[end].isalnum() and not _is_cjk_char(norm_text[end]):
                    continue

            new_spans.append({
                "start": start,
                "end": end,
                "type": etype,
                "text": norm_text[start:end],
                "source": "string_match",
            })

            # Mark these characters as covered
            for i in range(start, end):
                covered.add(i)

    return new_spans


# ---------------------------------------------------------------------------
# Escape-sequence-aware context matching (multi-level)
# ---------------------------------------------------------------------------

def _build_context_variants(context_norm: str) -> list[tuple[str, str]]:
    """
    Return (label, variant) pairs for multi-level context matching.

    LLM-produced contexts are typically *clean* (contain real whitespace
    characters like ``\\n``), whereas the original text may store them as
    literal two-char escape sequences (``\\`` + ``n``).  We therefore
    try increasingly relaxed normalizations:

    Level 1 – exact context (no transformation).
    Level 2 – real escape chars (``\\n``, ``\\t``, ``\\r``) replaced
              with their literal two-char representations so they can
              match original text that was not unescaped.
    Level 3 – reverse: literal two-char sequences collapsed to real
              escape chars (handles the opposite direction).
    """
    variants: list[tuple[str, str]] = [("exact", context_norm)]

    # Level 2: real escape chars → literal two-char sequences
    escaped = context_norm
    for real_char, lit_seq in _ESCAPE_CHAR_TO_LITERAL.items():
        escaped = escaped.replace(real_char, lit_seq)
    if escaped != context_norm:
        variants.append(("escape_to_literal", escaped))

    # Level 3: literal two-char sequences → real escape chars
    unescaped = context_norm
    for lit_seq, real_char in _LITERAL_TO_ESCAPE_CHAR.items():
        unescaped = unescaped.replace(lit_seq, real_char)
    if unescaped != context_norm and unescaped != escaped:
        variants.append(("literal_to_escape", unescaped))

    return variants


def _find_entity_via_context(
    context_norm: str,
    norm_text: str,
    value_norm: str,
) -> list[tuple[int, int]]:
    """
    Locate *value_norm* inside *norm_text* using a multi-level context
    search.

    **Level 1** – try matching the exact *context_norm* in *norm_text*.
    **Level 2** – if Level 1 fails, convert real escape characters in
                  the context (``\\n`` → ``\\`` + ``n``) and retry.  This
                  covers the common case where an LLM returns clean text
                  but the original content has literal escape sequences.
    **Level 3** – reverse conversion (literal → real) for the opposite
                  mismatch direction.

    Returns a list of ``(start, end)`` tuples for all context occurrences
    found in the text, or an empty list when no match is found.
    """
    entity_pattern = re.escape(value_norm)
    results: list[tuple[int, int]] = []

    # Pass 1: case-sensitive matching
    for level_label, ctx_variant in _build_context_variants(context_norm):
        context_pattern = re.escape(ctx_variant)
        for context_match in re.finditer(context_pattern, norm_text):
            context_start = context_match.start()
            context_text = context_match.group()

            # Find ALL entity positions within the matched context
            for entity_match in re.finditer(entity_pattern, context_text):
                start = context_start + entity_match.start()
                end = context_start + entity_match.end()
                if level_label != "exact":
                    logger.debug(
                        "Context matched at level '%s' for entity '%s' "
                        "(exact context not found in text)",
                        level_label, value_norm,
                    )
                results.append((start, end))

        if results:
            break  # found at this level, but still try case-insensitive below

    # Pass 2: augment with case-insensitive matches (new positions only)
    result_set = set(results)
    for level_label, ctx_variant in _build_context_variants(context_norm):
        context_pattern = re.escape(ctx_variant)
        for context_match in re.finditer(context_pattern, norm_text, re.IGNORECASE):
            context_start = context_match.start()
            context_text = context_match.group()

            for entity_match in re.finditer(entity_pattern, context_text, re.IGNORECASE):
                start = context_start + entity_match.start()
                end = context_start + entity_match.end()
                if (start, end) not in result_set:
                    logger.debug(
                        "Context matched via case-insensitive fallback at level '%s' "
                        "for entity '%s'",
                        level_label, value_norm,
                    )
                    results.append((start, end))
                    result_set.add((start, end))

        if result_set:
            return results

    logger.debug(
        "Context match failed at all levels for entity '%s'",
        value_norm,
    )
    return []


# ---------------------------------------------------------------------------
# Boundary helpers  (delegated to span_utils)
# ---------------------------------------------------------------------------

_is_boundary_blocked_left = is_boundary_blocked_left
_is_boundary_blocked_right = is_boundary_blocked_right
_passes_boundary_check = passes_boundary_check


# ---------------------------------------------------------------------------
# S8c: Span reconciliation
# ---------------------------------------------------------------------------

def reconcile_spans(
    marker_spans: list[dict],
    string_match_spans: list[dict],
    consensus_entities: dict[str, list[str]],
    clean_text: str,
    consensus_metadata: Optional[dict] = None,
    greedy_mode: str = "single_occ",
) -> list[dict]:
    """
    Merge spans from all sources into a single deduplicated list.

    Two-phase index calculation:
      Phase 1 — try context-based matching for every prediction.
      Phase 2 — for predictions where context failed or was absent,
                fall back to greedy string matching (longest first,
                with occurrence tracking for duplicates).

    Boundary rules:
      '@' always blocks.  '.' blocks only when connecting two
      alphanumeric characters (domain-like), NOT sentence-ending.

    Args:
        marker_spans: spans from S8 marker extraction
        string_match_spans: spans from S8a string-match sweep
        consensus_entities: {entity_type: [values]} from S8b consensus
        clean_text: the clean text to search for consensus entity positions
        consensus_metadata: optional metadata from consensus engine
        greedy_mode: 'single_occ' (default) matches one occurrence per
            prediction; 'multiple_occ' matches all occurrences in text.

    Returns:
        Merged, deduplicated span list sorted by start position.
        Each span has: {start, end, type, text, source}
    """
    norm_text = unicodedata.normalize("NFC", clean_text) if clean_text else ""

    # Start with marker spans (add source tag if not present)
    all_spans: list[dict] = []
    for s in marker_spans:
        span = dict(s)
        span.setdefault("source", "marker")
        all_spans.append(span)

    # Add string-match spans
    for s in string_match_spans:
        all_spans.append(dict(s))

    # Build covered ranges from existing spans
    covered = set()
    for s in all_spans:
        for i in range(s["start"], s["end"]):
            covered.add(i)

    # Resolve consensus entities to spans
    if consensus_entities and norm_text:
        # Get agreement details for type conflict resolution
        agreement_details = {}
        if consensus_metadata:
            agreement_details = consensus_metadata.get(
                "entity_agreement_details", {}
            )

        # ── Flatten all predictions ──────────────────────────────
        all_predictions = []
        for etype, values in consensus_entities.items():
            for v in values:
                if isinstance(v, dict):
                    value = v.get("text", "")
                    pre_start = v.get("start")
                    pre_end = v.get("end")
                    context = v.get("context", "")
                else:
                    value = str(v)
                    pre_start = None
                    pre_end = None
                    context = ""

                value_norm = unicodedata.normalize("NFC", value.strip())
                if not value_norm:
                    continue

                all_predictions.append({
                    "etype": etype,
                    "value": value,
                    "value_norm": value_norm,
                    "pre_start": pre_start,
                    "pre_end": pre_end,
                    "context": context,
                    "original": v,
                })

        # Sort longest first so longer entities claim positions before shorter ones
        all_predictions.sort(key=lambda x: len(x["value_norm"]), reverse=True)

        # ── Phase 1: Context-based matching ──────────────────────
        # Try context for every prediction first.  Collect resolved
        # spans and a list of failures to hand to Phase 2.
        resolved: list[tuple] = []   # (etype, start, end, value)
        failed: list[dict] = []      # prediction dicts
        context_covered: set[int] = set()  # positions claimed by context matches

        for pred in all_predictions:
            # Pre-calculated positions — use directly
            if pred["pre_start"] is not None and pred["pre_end"] is not None:
                resolved.append((
                    pred["etype"], pred["pre_start"],
                    pred["pre_end"], pred["value"],
                ))
                for i in range(pred["pre_start"], pred["pre_end"]):
                    context_covered.add(i)
                continue

            # Try context-based matching
            if pred["context"]:
                context_norm = unicodedata.normalize("NFC", pred["context"])
                matches = _find_entity_via_context(
                    context_norm, norm_text, pred["value_norm"]
                )
                if matches:
                    # Find the first match not already claimed
                    placed = False
                    for s, e in matches:
                        if not _passes_boundary_check(norm_text, s, e):
                            continue
                        if not any(i in context_covered for i in range(s, e)):
                            resolved.append((pred["etype"], s, e, pred["value"]))
                            for i in range(s, e):
                                context_covered.add(i)
                            placed = True
                            break
                    if placed:
                        continue

            # Context missing or malformed — fall through to Phase 2
            failed.append(pred)

        # ── Phase 2: Greedy string match for failures ────────────
        # Positions already claimed (existing spans + Phase 1 results)
        greedy_covered = set(covered)
        for _, s, e, _ in resolved:
            for i in range(s, e):
                greedy_covered.add(i)

        greedy_spans = greedy_search(
            norm_text, failed, covered=greedy_covered, mode=greedy_mode,
        )
        for gs in greedy_spans:
            resolved.append((gs["type"], gs["start"], gs["end"], gs["text"]))

        # ── Phase 3: Apply boundary checks & merge ───────────────
        for etype, start, end, value in resolved:
            # Boundary check (context-resolved spans may still land
            # inside emails / domains — reject those)
            if not _passes_boundary_check(norm_text, start, end):
                continue

            # Check overlap with existing spans
            overlap_span = _find_overlapping_span(all_spans, start, end)

            if overlap_span is not None:
                # Type conflict: consensus wins if types disagree
                if overlap_span["type"] != etype:
                    match_len = end - start
                    span_len = (
                        overlap_span["end"] - overlap_span["start"]
                    )
                    if span_len > 0 and match_len > 0:
                        min_ratio = min(
                            match_len / span_len, span_len / match_len
                        )
                    else:
                        min_ratio = 0.0

                    if min_ratio >= 0.8:
                        n_agreed = _get_agreement_count(
                            agreement_details, etype, value
                        )
                        if n_agreed >= 2:
                            overlap_span["type"] = etype
                            overlap_span["source"] = "consensus_override"
                continue

            # No overlap — check if fully uncovered
            if any(i in covered for i in range(start, end)):
                continue

            all_spans.append({
                "start": start,
                "end": end,
                "type": etype,
                "text": norm_text[start:end],
                "source": "consensus",
            })
            for i in range(start, end):
                covered.add(i)

    # Sort by start position
    all_spans.sort(key=lambda s: s["start"])

    # Remove any remaining overlaps (keep earlier/longer span)
    final_spans = _remove_overlaps(all_spans)

    return final_spans


def _find_overlapping_span(
    spans: list[dict], start: int, end: int
) -> Optional[dict]:
    """Find an existing span that overlaps with [start, end)."""
    for s in spans:
        if s["start"] < end and s["end"] > start:
            return s
    return None


def _get_agreement_count(
    agreement_details: dict, entity_type: str, value: str
) -> int:
    """Get number of models that agreed on this entity type + value."""
    type_details = agreement_details.get(entity_type, {})
    for entity_key, info in type_details.items():
        if entity_key.lower() == value.lower():
            return len(info.get("agreed_models", []))
    return 0


_remove_overlaps = remove_overlaps


# ---------------------------------------------------------------------------
# Per-model span extraction + span-level merge
# ---------------------------------------------------------------------------

def extract_single_model_spans(
    text: str,
    parsed_entities: dict[str, list],
) -> list[dict]:
    """
    Convert ONE model's parsed entities to character-level spans.

    Uses two-phase approach:
      Phase 1 — context-based matching (if entity has context).
      Phase 2 — greedy string matching for the rest (longest first,
                with occurrence tracking for duplicates).

    Boundary rules apply: '@' always blocks, '.' blocks when
    connecting two alphanumeric characters (domain-like).

    Args:
        text: Original input text.
        parsed_entities: {entity_type: [entity_objects]}
            Each entity_object is either:
              - a plain string: "nikhil"
              - a dict: {"text": "nikhil", "context": "call nikhil."}

    Returns:
        List of {start, end, type, text, source} dicts sorted by start.
        Spans with start == -1 means entity text was not found.
    """
    if not text or not parsed_entities:
        return []

    norm_text = unicodedata.normalize("NFC", text) if text else ""

    # ── Flatten all entities ──────────────────────────────────
    all_entities = []
    for etype, values in parsed_entities.items():
        for v in values:
            if isinstance(v, dict):
                value = v.get("text", "")
                context = v.get("context", "")
            else:
                value = str(v)
                context = ""

            value_norm = unicodedata.normalize("NFC", value.strip())
            if not value_norm:
                continue

            all_entities.append({
                "etype": etype,
                "value": value,
                "value_norm": value_norm,
                "context": context,
            })

    # Sort longest first so longer entities claim positions before shorter ones
    all_entities.sort(key=lambda x: len(x["value_norm"]), reverse=True)

    # ── Phase 1: Context-based matching ──────────────────────
    resolved: list[dict] = []   # {etype, start, end, text}
    failed: list[dict] = []     # entity dicts
    context_covered: set[int] = set()  # positions claimed by context matches

    for ent in all_entities:
        if ent["context"]:
            context_norm = unicodedata.normalize("NFC", ent["context"])
            matches = _find_entity_via_context(
                context_norm, norm_text, ent["value_norm"]
            )
            if matches:
                # Find the first match not already claimed
                placed = False
                for s, e in matches:
                    if not _passes_boundary_check(norm_text, s, e):
                        continue
                    if any(i in context_covered for i in range(s, e)):
                        continue
                    resolved.append({
                        "start": s, "end": e,
                        "type": ent["etype"],
                        "text": norm_text[s:e],
                        "source": "context",
                    })
                    for i in range(s, e):
                        context_covered.add(i)
                    placed = True
                    break
                if placed:
                    continue

        # Context failed/missing → Phase 2
        failed.append(ent)

    # ── Phase 2: Greedy string match ─────────────────────────
    # Positions already claimed by Phase 1
    greedy_covered: set[int] = set()
    for sp in resolved:
        for i in range(sp["start"], sp["end"]):
            greedy_covered.add(i)

    greedy_spans = greedy_search(
        norm_text, failed, covered=greedy_covered, mode="single_occ",
    )
    resolved.extend(greedy_spans)

    # Sort and deduplicate
    resolved.sort(key=lambda x: x["start"])
    return _remove_overlaps(resolved)


def merge_model_spans(
    span_lists: list[list[dict]],
    min_agreement: int = 2,
    match_mode: str = "overlap",
    position_tolerance: int = 2,
    text_similarity_threshold: float = 0.8,
) -> list[dict]:
    """
    Merge spans from multiple models using span-level voting.

    Spans of the same type are clustered according to *match_mode*:
      - ``exact``:   only identical (start, end) boundaries match.
      - ``overlap``: overlapping spans match if text similarity ≥
                     *text_similarity_threshold* (default).
      - ``fuzzy``:   overlap matching **plus** non-overlapping spans
                     with gap ≤ *position_tolerance*.

    A cluster is kept if it contains spans from at least
    *min_agreement* distinct models; the longest span in the
    cluster becomes the canonical output.

    Args:
        span_lists: List of per-model span lists.
            Each span is {start, end, type, text, ...}.
        min_agreement: Minimum number of models that must agree
            for a span to be kept.
        match_mode: One of 'exact', 'overlap', 'fuzzy'.
        position_tolerance: Maximum character gap for non-overlapping
            spans (only used when match_mode='fuzzy').
        text_similarity_threshold: Minimum ratio of the shorter
            text contained in the longer text (0.0–1.0).  Used
            by 'overlap' and 'fuzzy' modes.

    Returns:
        Merged, deduplicated span list sorted by start position.
    """
    # Tag every span with its model index
    tagged: list[tuple[int, dict]] = []
    for model_idx, spans in enumerate(span_lists):
        for sp in spans:
            tagged.append((model_idx, sp))

    # Group by entity type
    by_type: dict[str, list[tuple[int, dict]]] = {}
    for model_idx, sp in tagged:
        etype = sp["type"]
        if etype not in by_type:
            by_type[etype] = []
        by_type[etype].append((model_idx, sp))

    agreed: list[dict] = []

    for etype, pairs in by_type.items():
        # Build clusters: each cluster = list of (model_idx, span)
        clusters: list[list[tuple[int, dict]]] = []

        for model_idx, sp in pairs:
            matched_cluster = None
            for cluster in clusters:
                for _, cluster_sp in cluster:
                    if _spans_match(
                        sp, cluster_sp,
                        match_mode=match_mode,
                        position_tolerance=position_tolerance,
                        text_similarity_threshold=text_similarity_threshold,
                    ):
                        matched_cluster = cluster
                        break
                if matched_cluster is not None:
                    break

            if matched_cluster is not None:
                matched_cluster.append((model_idx, sp))
            else:
                clusters.append([(model_idx, sp)])

        # Vote on each cluster
        for cluster in clusters:
            unique_models = set(m for m, _ in cluster)
            if len(unique_models) >= min_agreement:
                # Canonical = longest span in the cluster
                best_sp = max(
                    (sp for _, sp in cluster),
                    key=lambda s: s["end"] - s["start"],
                )
                out = dict(best_sp)
                out["agreement"] = len(unique_models)
                out["source"] = "span_consensus"
                agreed.append(out)

    agreed.sort(key=lambda x: x["start"])
    return _remove_overlaps(agreed)


def _spans_match(
    s1: dict,
    s2: dict,
    match_mode: str = "overlap",
    position_tolerance: int = 2,
    text_similarity_threshold: float = 0.8,
) -> bool:
    """
    Check if two spans refer to the same occurrence.

    Rules (cumulative by mode):
      exact:   1. Identical (start, end) → match.
      overlap: 1 + 2. Overlapping spans → match if text similarity ≥ threshold.
      fuzzy:   1 + 2 + 3. Non-overlapping gap ≤ position_tolerance → match
               if text similarity ≥ threshold.
    """
    start1, end1 = s1["start"], s1["end"]
    start2, end2 = s2["start"], s2["end"]

    # Rule 1: exact same boundaries → always match (all modes)
    if start1 == start2 and end1 == end2:
        return True

    if match_mode == "exact":
        return False

    # Rule 2: overlapping spans → check text similarity (overlap + fuzzy)
    overlapping = start1 < end2 and start2 < end1
    if overlapping:
        containment = _shorter_text_containment(s1["text"], s2["text"])
        return containment >= text_similarity_threshold

    # Rule 3: non-overlapping gap within tolerance (fuzzy only)
    if match_mode == "fuzzy" and position_tolerance > 0:
        gap = max(0, max(start1, start2) - min(end1, end2))
        if gap <= position_tolerance:
            containment = _shorter_text_containment(s1["text"], s2["text"])
            return containment >= text_similarity_threshold

    return False


def _shorter_text_containment(text1: str, text2: str) -> float:
    """
    Return the fraction of the shorter text contained in the longer text.

    E.g. "Danish Sha" vs "Danish Shah" → 10/11 ≈ 0.91
    """
    if not text1 or not text2:
        return 0.0
    shorter, longer = (text1, text2) if len(text1) <= len(text2) else (text2, text1)
    if longer.find(shorter) != -1:
        return 1.0
    # Character-level overlap ratio
    common = sum(1 for c in shorter if c in longer)
    return common / len(longer)
