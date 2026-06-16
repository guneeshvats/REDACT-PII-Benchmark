"""
Family K — Synthetic-Real Ranking Correlation.

The validity test for the benchmark (Kiela et al., NeurIPS 2021).
If detectors ranked by F1 on our synthetic corpus rank the same way on real
TAB data, our benchmark is a valid proxy. If not, the benchmark has limited
external validity.

Inputs:
    - One or more synthetic F1 reports (from compute_stratified_f1.py) for
      different detectors on the synthetic corpus
    - One or more real F1 reports (same detectors run against TAB)

Metrics:
    K1  Kendall's τ      — rank correlation between synthetic and real
    K2  Spearman's ρ     — alt rank correlation
    K3  Mean abs F1 delta — average |F1_synthetic - F1_real|
    K4  Bootstrap 95% CI on K1 — over detector resampling

Threshold (methodology §6.11): K1 >= 0.70 point estimate (necessary but not
sufficient evidence — frame honestly with CI).

Usage:
    python compute_kendall_tau.py \\
        --synthetic synth_presidio.json synth_gliner.json synth_gpt.json synth_claude.json \\
        --real real_presidio.json real_gliner.json real_gpt.json real_claude.json \\
        --out kendall_tau_report.json
"""

import json
import argparse
import random
from itertools import combinations
from pathlib import Path


def kendall_tau(a: list, b: list) -> float:
    """Kendall's τ between two rankings. O(n^2) — fine for n <= 20."""
    n = len(a)
    if n < 2:
        return 0.0
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            sign_a = (a[i] - a[j])
            sign_b = (b[i] - b[j])
            if sign_a * sign_b > 0:
                concordant += 1
            elif sign_a * sign_b < 0:
                discordant += 1
    total_pairs = n * (n - 1) / 2
    return (concordant - discordant) / total_pairs if total_pairs else 0.0


def spearman_rho(a: list, b: list) -> float:
    """Spearman's ρ via rank correlation."""
    n = len(a)
    if n < 2:
        return 0.0
    ranks_a = {v: i for i, v in enumerate(sorted(a))}
    ranks_b = {v: i for i, v in enumerate(sorted(b))}
    ra = [ranks_a[v] for v in a]
    rb = [ranks_b[v] for v in b]
    n_pairs = n
    d_sq_sum = sum((ra[i] - rb[i]) ** 2 for i in range(n_pairs))
    return 1 - 6 * d_sq_sum / (n_pairs * (n_pairs ** 2 - 1))


def bootstrap_kendall(a: list, b: list, n_bootstrap: int = 1000, seed: int = 0):
    """Bootstrap CI for Kendall's τ over detector resampling."""
    rng = random.Random(seed)
    n = len(a)
    if n < 3:
        return None
    taus = []
    for _ in range(n_bootstrap):
        idxs = [rng.randint(0, n - 1) for _ in range(n)]
        sa = [a[i] for i in idxs]
        sb = [b[i] for i in idxs]
        try:
            t = kendall_tau(sa, sb)
            taus.append(t)
        except Exception:
            pass
    taus.sort()
    lo = taus[int(0.025 * len(taus))]
    hi = taus[int(0.975 * len(taus))]
    mean = sum(taus) / len(taus)
    return {"mean": round(mean, 4), "ci_95_lo": round(lo, 4), "ci_95_hi": round(hi, 4)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--synthetic", nargs="+", required=True,
                   help="F1 report files from synthetic corpus, one per detector")
    p.add_argument("--real", nargs="+", required=True,
                   help="F1 report files from real corpus (TAB), one per detector")
    p.add_argument("--out", default="kendall_tau_report.json")
    p.add_argument("--bootstrap", type=int, default=1000)
    args = p.parse_args()

    if len(args.synthetic) != len(args.real):
        raise ValueError("Need same number of synthetic and real reports")

    # Load F1 scores per detector
    synth_f1s = []
    real_f1s = []
    detector_names = []

    for sp, rp in zip(args.synthetic, args.real):
        with open(sp) as f:
            s = json.load(f)
        with open(rp) as f:
            r = json.load(f)
        det = s.get("detector", Path(sp).stem)
        detector_names.append(det)
        synth_f1s.append(s["overall"]["f1"])
        real_f1s.append(r["overall"]["f1"])

    print("Detectors:", detector_names)
    print("Synthetic F1:", [round(f, 3) for f in synth_f1s])
    print("Real F1:     ", [round(f, 3) for f in real_f1s])

    if len(synth_f1s) < 2:
        print("Not enough detectors for ranking correlation. Need >= 2.")
        return

    # K1 — Kendall's τ
    tau = kendall_tau(synth_f1s, real_f1s)

    # K2 — Spearman's ρ
    rho = spearman_rho(synth_f1s, real_f1s)

    # K3 — Mean absolute delta
    abs_deltas = [abs(s - r) for s, r in zip(synth_f1s, real_f1s)]
    mean_abs_delta = sum(abs_deltas) / len(abs_deltas)

    # K4 — Bootstrap CI on Kendall's τ
    bs = bootstrap_kendall(synth_f1s, real_f1s, args.bootstrap)

    report = {
        "detectors": detector_names,
        "synthetic_f1": [round(f, 4) for f in synth_f1s],
        "real_f1": [round(f, 4) for f in real_f1s],
        "K1_kendall_tau": round(tau, 4),
        "K2_spearman_rho": round(rho, 4),
        "K3_mean_abs_f1_delta": round(mean_abs_delta, 4),
        "K4_bootstrap_95_ci": bs,
        "n_detectors": len(synth_f1s),
        "thresholds": {
            "K1_target": "point estimate >= 0.70",
            "K3_target": "<= 0.10",
        },
        "framing_note": (
            "At small n (typically 4-5 detectors), the bootstrap CI is wide. "
            "Frame as 'necessary but not sufficient' evidence per Kiela 2021. "
            "Report both point estimate and CI in the paper."
        ),
    }

    print(f"\nK1 Kendall's τ:       {tau:.3f}")
    print(f"K2 Spearman's ρ:      {rho:.3f}")
    print(f"K3 mean |ΔF1|:        {mean_abs_delta:.3f}")
    if bs:
        print(f"K4 bootstrap 95% CI:  [{bs['ci_95_lo']:.3f}, {bs['ci_95_hi']:.3f}]")

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport: {args.out}")


if __name__ == "__main__":
    main()
