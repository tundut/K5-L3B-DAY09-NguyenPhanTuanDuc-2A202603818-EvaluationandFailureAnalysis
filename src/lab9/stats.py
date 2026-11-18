"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import comb, isfinite

import numpy as np
from scipy.stats import bootstrap

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge) or not human:
        raise ValueError("labels must have equal, nonzero length")
    if any(x not in {"PASS", "FAIL"} for x in [*human, *judge]):
        raise ValueError("labels must be PASS or FAIL")
    out = dict(tp=0, fp=0, fn=0, tn=0)
    for h, j in zip(human, judge):
        out[("tp" if h == POS else "fp") if j == POS else ("fn" if h == POS else "tn")] += 1
    return out


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    m = confusion(human, judge)
    return (m["tp"] / (m["tp"] + m["fp"]) if m["tp"] + m["fp"] else 0.0,
            m["tp"] / (m["tp"] + m["fn"]) if m["tp"] + m["fn"] else 0.0)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    m = confusion(human, judge)
    n = len(human)
    po = (m["tp"] + m["tn"]) / n
    pe = ((m["tp"] + m["fn"]) * (m["tp"] + m["fp"]) +
          (m["tn"] + m["fp"]) * (m["tn"] + m["fn"])) / n**2
    if pe == 1:
        raise ValueError("kappa undefined")
    return (po - pe) / (1 - pe)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    if any(not isfinite(x) or not 0 <= x <= 1 for x in (observed_rate, sensitivity, specificity)):
        raise ValueError("rates must lie in [0, 1]")
    denominator = sensitivity + specificity - 1
    if denominator <= 0:
        raise ValueError("judge must be informative")
    return min(1.0, max(0.0, (observed_rate + specificity - 1) / denominator))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.ndim != 1 or b.ndim != 1 or len(a) != len(b) or not len(a):
        raise ValueError("paired samples must be nonempty vectors of equal length")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("samples must be finite")
    if not 0 < confidence < 1 or n_resamples < 1:
        raise ValueError("invalid bootstrap configuration")
    delta = float(np.mean(a - b))
    if len(a) == 1 or np.all(a - b == (a - b)[0]):
        return delta, delta, delta
    result = bootstrap((a, b), lambda x, y, axis: np.mean(x - y, axis=axis),
                       paired=True, method="percentile", n_resamples=n_resamples,
                       confidence_level=confidence, rng=np.random.default_rng(rng))
    return delta, float(result.confidence_interval.low), float(result.confidence_interval.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    _validate_counts(n, c, k)
    return 1 - comb(n - c, k) / comb(n, k) if n - c >= k else 1.0


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    _validate_counts(n, c, k)
    return comb(c, k) / comb(n, k) if c >= k else 0.0


def _validate_counts(n: int, c: int, k: int) -> None:
    if any(type(x) is not int for x in (n, c, k)) or not (n >= 1 and 0 <= c <= n and 1 <= k <= n):
        raise ValueError("require integer n >= 1, 0 <= c <= n, 1 <= k <= n")
