"""Judge-the-judge: calibrate a replayed LLM judge against human labels.

    python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5

Default backend is REPLAY (the judge verdicts are stored in the CSV, zero key).
Floors (lecture S6): kappa >= 0.6, precision >= 0.8, recall >= 0.7.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats

FLOORS = {"kappa": 0.6, "precision": 0.8, "recall": 0.7}


def calibrate(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    human = [r["human"].strip().upper() for r in rows]
    judge = [r["judge"].strip().upper() for r in rows]
    p, r = stats.precision_recall(human, judge)
    try:
        k = stats.cohen_kappa(human, judge)
    except ValueError:
        k = float("nan")
    cm = stats.confusion(human, judge)
    spec = cm["tn"] / (cm["tn"] + cm["fp"]) if cm["tn"] + cm["fp"] else 0.0
    obs = (cm["tp"] + cm["fp"]) / len(rows)
    # With a missing class or a non-informative judge, the replay cannot
    # estimate a corrected prevalence. Still report the calibration verdict.
    corrected = None
    if cm["tp"] + cm["fn"] and cm["tn"] + cm["fp"] and r + spec > 1:
        corrected = round(stats.rogan_gladen(obs, r, spec), 3)
    res = {"n": len(rows), "precision": round(p, 3), "recall": round(r, 3), "kappa": round(k, 3),
           "confusion": cm, "observed_fail_rate": round(obs, 3),
           "corrected_fail_rate": corrected,
           "disagreements": [x for x, h, j in zip(rows, human, judge) if h != j]}
    res["passed"] = (k >= FLOORS["kappa"] and p >= FLOORS["precision"] and r >= FLOORS["recall"])   # nan compares False -> fails
    return res


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.judge")
    ap.add_argument("--csv", required=True)
    ap.add_argument("--audit", type=int, default=0, help="print N disagreements to audit by hand")
    args = ap.parse_args(argv)
    res = calibrate(Path(args.csv))
    print(f"n={res['n']} P={res['precision']} R={res['recall']} kappa={res['kappa']} {res['confusion']}")
    corrected = res["corrected_fail_rate"]
    print(f"fail rate observed {res['observed_fail_rate']} -> corrected {corrected if corrected is not None else 'N/A'}")
    for row in res["disagreements"][: args.audit]:
        print(f"  {row['item_id']} human={row['human']} judge={row['judge']} | {row['reply'][:90]}")
    print("PASS floors" if res["passed"] else "FAIL floors", FLOORS)
    return 0 if res["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
