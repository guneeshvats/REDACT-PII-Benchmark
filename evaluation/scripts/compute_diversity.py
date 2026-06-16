"""
Family C — Diversity metrics.

Implements the methodology §6.3 diversity family + a few literature
favorites:

  C1  Entity-type entropy (Shannon).
  C2  Distinct-1, Distinct-2, Distinct-3 (Li et al., 2016).
  C3  Self-BLEU-3, Self-BLEU-4 (Zhu et al., 2018).
       Lower = more diverse. Target Self-BLEU-3 ≤ 0.35.
  C4  ROUGE-L intra-stratum mean (Self-Instruct, Wang et al., 2023).
       Target ≤ 0.70.
  C5  Type-Token Ratio (Tweedie & Baayen, 1998).
  C6  Vendi Score (Friedman & Dieng, 2023).
       Cardinality-based diversity, generalizes Distinct-n.
  C7  SBERT semantic diversity (Gao et al., EMNLP 2021).
       Mean pairwise cosine distance over sentence embeddings.
  C8  Pattern density per record — novel framing for PII benchmarks.
       Mean unique target_pattern_ids covered per record-bucket.

Computed corpus-wide AND per-language for the most informative metrics.

Dependencies (install once):
    pip install nltk sentence-transformers numpy scikit-learn
    python -c "import nltk; nltk.download('punkt_tab')"

Usage:
    python compute_diversity.py corpus.json --out diversity_report.json [--sample 2000]

For corpora >5k records, set --sample 2000 to avoid O(n^2) blowup on Self-BLEU
and SBERT pairwise.
"""

import json
import argparse
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# C1 — Entity-type Shannon entropy
# ---------------------------------------------------------------------------

def shannon_entropy(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c == 0:
            continue
        p = c / total
        h -= p * math.log2(p)
    return h


# ---------------------------------------------------------------------------
# C2 — Distinct-n (Li et al., NAACL 2016)
# ---------------------------------------------------------------------------

def tokenize_simple(text: str) -> list[str]:
    """Whitespace + punctuation tokenizer. Multilingual-safe (no language-specific rules)."""
    import re
    text = text.lower()
    tokens = re.findall(r"\w+", text, flags=re.UNICODE)
    return tokens


def ngrams(tokens: list[str], n: int):
    for i in range(len(tokens) - n + 1):
        yield tuple(tokens[i : i + n])


def compute_distinct_n(texts: list[str], n: int) -> float:
    """Distinct-n = unique n-grams / total n-grams across the corpus."""
    total = 0
    seen = set()
    for t in texts:
        toks = tokenize_simple(t)
        for ng in ngrams(toks, n):
            total += 1
            seen.add(ng)
    return len(seen) / total if total else 0.0


# ---------------------------------------------------------------------------
# C3 — Self-BLEU (Zhu et al., SIGIR 2018)
# ---------------------------------------------------------------------------

def compute_self_bleu(texts: list[str], n: int = 3, sample: int = 500) -> float:
    """
    Self-BLEU-n. For each text, BLEU against the rest of the corpus as
    references. Mean across the sample.

    O(sample^2) — capped via `sample` arg.
    """
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    except ImportError:
        return float("nan")

    if len(texts) < 2:
        return 0.0

    rng = random.Random(0)
    sampled = rng.sample(texts, min(sample, len(texts)))
    smooth = SmoothingFunction().method1
    weights = tuple([1.0 / n] * n)

    scores = []
    for i, t in enumerate(sampled):
        hyp = tokenize_simple(t)
        if len(hyp) < n:
            continue
        refs = [tokenize_simple(s) for j, s in enumerate(sampled) if j != i]
        refs = [r for r in refs if len(r) >= n]
        if not refs:
            continue
        score = sentence_bleu(refs, hyp, weights=weights, smoothing_function=smooth)
        scores.append(score)

    return sum(scores) / len(scores) if scores else 0.0


# ---------------------------------------------------------------------------
# C4 — ROUGE-L intra-stratum (Self-Instruct, Wang et al., ACL 2023)
# ---------------------------------------------------------------------------

def lcs_length(a: list[str], b: list[str]) -> int:
    """Length of longest common subsequence."""
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0
    dp = [0] * (n + 1)
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            tmp = dp[j]
            if a[i - 1] == b[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = tmp
    return dp[n]


def rouge_l(a: list[str], b: list[str]) -> float:
    """ROUGE-L F1 between two token sequences."""
    if not a or not b:
        return 0.0
    lcs = lcs_length(a, b)
    if lcs == 0:
        return 0.0
    p = lcs / len(b)
    r = lcs / len(a)
    return 2 * p * r / (p + r)


def compute_rouge_l_pairs(texts: list[str], sample: int = 300) -> float:
    """Mean pairwise ROUGE-L over a sample."""
    rng = random.Random(1)
    sampled = rng.sample(texts, min(sample, len(texts)))
    toks = [tokenize_simple(t) for t in sampled]
    scores = []
    for i in range(len(toks)):
        for j in range(i + 1, len(toks)):
            scores.append(rouge_l(toks[i], toks[j]))
    return sum(scores) / len(scores) if scores else 0.0


# ---------------------------------------------------------------------------
# C5 — Type-Token Ratio
# ---------------------------------------------------------------------------

def compute_ttr(texts: list[str]) -> float:
    types = set()
    tokens = 0
    for t in texts:
        toks = tokenize_simple(t)
        tokens += len(toks)
        types.update(toks)
    return len(types) / tokens if tokens else 0.0


# ---------------------------------------------------------------------------
# C6 — Vendi Score (Friedman & Dieng, 2023)
# ---------------------------------------------------------------------------

def compute_vendi(embeddings) -> float:
    """
    Vendi Score = exp(entropy of eigenvalues of normalized kernel matrix).
    Implements eq. 1 from Friedman & Dieng 2023.
    """
    try:
        import numpy as np
    except ImportError:
        return float("nan")

    if embeddings is None or len(embeddings) < 2:
        return 0.0

    X = np.asarray(embeddings)
    # Normalize each row (unit length) so kernel = cosine similarity
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    Xn = X / norms

    # Kernel matrix K = X X^T (cosine similarity), scale to trace = 1
    n = Xn.shape[0]
    K = (Xn @ Xn.T) / n

    # Compute eigenvalues (symmetric -> use eigh)
    eigs = np.linalg.eigvalsh(K)
    eigs = np.clip(eigs, 1e-12, None)
    eigs = eigs / eigs.sum()

    H = -np.sum(eigs * np.log(eigs))
    return float(np.exp(H))


# ---------------------------------------------------------------------------
# C7 — SBERT semantic diversity (mean pairwise cosine distance)
# ---------------------------------------------------------------------------

def compute_sbert_diversity(embeddings) -> float:
    """Mean pairwise cosine *distance* (= 1 - cosine similarity) across embeddings."""
    try:
        import numpy as np
    except ImportError:
        return float("nan")

    if embeddings is None or len(embeddings) < 2:
        return 0.0

    X = np.asarray(embeddings)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    Xn = X / norms

    n = Xn.shape[0]
    K = Xn @ Xn.T  # cosine similarity
    iu = np.triu_indices(n, k=1)
    mean_sim = K[iu].mean()
    return float(1.0 - mean_sim)


# ---------------------------------------------------------------------------
# Embeddings helper (loaded once, optional)
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str], model_name: str = "all-MiniLM-L6-v2"):
    """Returns embeddings array, or None if sentence-transformers unavailable."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("WARN: sentence-transformers not installed; skipping Vendi + SBERT diversity.")
        return None
    model = SentenceTransformer(model_name)
    return model.encode(texts, batch_size=64, show_progress_bar=False, convert_to_numpy=True)


# ---------------------------------------------------------------------------
# C8 — Pattern density per record-bucket (novel)
# ---------------------------------------------------------------------------

def compute_pattern_density(records: list[dict]) -> dict:
    """
    For each (language, entity_type) bucket, count unique target_pattern_ids
    actually exercised. Returns:
        {language: {entity_type: n_unique_patterns_used}}
    Plus a global summary.
    """
    bucket = defaultdict(lambda: defaultdict(set))
    global_patterns = set()
    for r in records:
        lang = r.get("axes", {}).get("language", "?")
        et = r.get("target_entity_type", "?")
        pid = r.get("target_pattern_id")
        if pid:
            bucket[lang][et].add(pid)
            global_patterns.add(pid)

    out = {
        "global_unique_patterns_used": len(global_patterns),
        "per_language_summary": {
            lang: {
                "n_entity_types": len(d),
                "n_unique_patterns": sum(len(s) for s in d.values()),
            }
            for lang, d in bucket.items()
        },
    }
    return out


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("corpus_path")
    p.add_argument("--out", default="diversity_report.json")
    p.add_argument("--sample", type=int, default=500,
                   help="Sample size for O(n^2) metrics (Self-BLEU, ROUGE-L, SBERT pairwise)")
    p.add_argument("--no-embeddings", action="store_true",
                   help="Skip SBERT embeddings (Vendi, C7). Use if sentence-transformers not installed.")
    args = p.parse_args()

    with open(args.corpus_path) as f:
        records = json.load(f)

    texts = [r.get("text", "") for r in records if r.get("text")]
    n = len(texts)
    print(f"Loaded {n:,} records with non-empty text")

    # Entity-type entropy (C1)
    print("[C1] Computing entity-type entropy...")
    et_counts = Counter()
    for r in records:
        for e in r.get("entities", []):
            et_counts[e.get("entity_type", "?")] += 1
    H_entity = shannon_entropy(et_counts)
    H_max = math.log2(len(et_counts)) if et_counts else 0
    print(f"    Shannon entropy = {H_entity:.3f} bits (max possible = {H_max:.3f})")

    # Distinct-n (C2)
    print("[C2] Computing Distinct-1/2/3...")
    d1 = compute_distinct_n(texts, 1)
    d2 = compute_distinct_n(texts, 2)
    d3 = compute_distinct_n(texts, 3)
    print(f"    Distinct-1={d1:.4f}  Distinct-2={d2:.4f}  Distinct-3={d3:.4f}")

    # Self-BLEU (C3)
    print(f"[C3] Computing Self-BLEU on sample of {args.sample}...")
    sb3 = compute_self_bleu(texts, n=3, sample=args.sample)
    sb4 = compute_self_bleu(texts, n=4, sample=args.sample)
    print(f"    Self-BLEU-3={sb3:.4f}  Self-BLEU-4={sb4:.4f}  (lower = more diverse)")

    # ROUGE-L pairwise (C4)
    print(f"[C4] Computing ROUGE-L pairwise on sample of {min(args.sample, 300)}...")
    rouge_l_mean = compute_rouge_l_pairs(texts, sample=min(args.sample, 300))
    print(f"    Mean ROUGE-L = {rouge_l_mean:.4f}")

    # TTR (C5)
    print("[C5] Computing Type-Token Ratio...")
    ttr = compute_ttr(texts)
    print(f"    TTR = {ttr:.4f}")

    # SBERT embeddings (one pass, used for C6 + C7)
    vendi = None
    sbert_div = None
    if not args.no_embeddings:
        print(f"[C6+C7] Embedding sample of {args.sample} with SBERT...")
        rng = random.Random(2)
        sample_texts = rng.sample(texts, min(args.sample, len(texts)))
        emb = embed_texts(sample_texts)
        if emb is not None:
            print("    Computing Vendi Score...")
            vendi = compute_vendi(emb)
            print(f"    Vendi Score = {vendi:.3f}")
            print("    Computing SBERT mean pairwise distance...")
            sbert_div = compute_sbert_diversity(emb)
            print(f"    SBERT diversity = {sbert_div:.4f}")

    # Pattern density (C8)
    print("[C8] Computing pattern density...")
    pat_dens = compute_pattern_density(records)
    print(f"    Unique target_pattern_ids exercised: {pat_dens['global_unique_patterns_used']}")

    report = {
        "n_records": n,
        "sample_size_used": args.sample,
        "C1_entity_type_shannon_entropy": round(H_entity, 4),
        "C1_max_possible_entropy": round(H_max, 4),
        "C1_normalized_entropy": round(H_entity / H_max, 4) if H_max else 0,
        "C2_distinct_1": round(d1, 4),
        "C2_distinct_2": round(d2, 4),
        "C2_distinct_3": round(d3, 4),
        "C3_self_bleu_3": round(sb3, 4),
        "C3_self_bleu_4": round(sb4, 4),
        "C4_rouge_l_pairs_mean": round(rouge_l_mean, 4),
        "C5_ttr": round(ttr, 4),
        "C6_vendi_score": round(vendi, 3) if vendi is not None else None,
        "C7_sbert_semantic_diversity": round(sbert_div, 4) if sbert_div is not None else None,
        "C8_pattern_density": pat_dens,
        "_targets": {
            "C1_target": ">= 4.0 bits",
            "C3_self_bleu_3_target": "<= 0.35",
            "C4_rouge_l_target": "<= 0.70",
        },
    }

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to: {args.out}")


if __name__ == "__main__":
    main()
