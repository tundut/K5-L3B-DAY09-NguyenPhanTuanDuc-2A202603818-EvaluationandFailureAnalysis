"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter

from lab9.graders import GRADERS
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    for label, report in (("PR", pr), ("baseline", base)):
        rows, manifest = report.get("rows", []), report.get("manifest", {})
        seeds = manifest.get("seeds", [])
        pairs = [(r.get("item_id"), r.get("seed")) for r in rows]
        if len(rows) != manifest.get("items", 0) * len(seeds):
            problems.append(f"{label}: wrong row count")
        if len(set(pairs)) != len(pairs):
            problems.append(f"{label}: duplicate item/seed")
        ids = {r.get("item_id") for r in rows}
        if len(ids) != manifest.get("items") or len(set(seeds)) != len(seeds):
            problems.append(f"{label}: inconsistent manifest")
        if set(pairs) != {(i, seed) for i in ids for seed in seeds}:
            problems.append(f"{label}: incomplete item x seed coverage")
        if report.get("evaluator_failures"):
            problems.append(f"{label}: evaluator failures")
        for mid, value in report.get("metrics", {}).items():
            if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
                problems.append(f"{label}: nonfinite metric {mid}")
        for m in spec["metrics"]:
            mid = m["id"]
            if report.get("metrics", {}).get(mid) is None:
                problems.append(f"{label}: missing metric {mid}")
            if mid in GRADERS or any(mid in row for row in rows):
                if any(not isinstance(r.get(mid), (int, float)) or not math.isfinite(r[mid]) for r in rows):
                    problems.append(f"{label}: missing/nonfinite row metric {mid}")
    key = lambda r: (r.get("item_id"), r.get("seed"))
    if Counter(key(r) for r in pr["rows"]) != Counter(key(r) for r in base["rows"]):
        problems.append("item/seed coverage differs from baseline")
    tags = {key(r): set(r.get("slices") or []) for r in base["rows"]}
    if any(set(r.get("slices") or []) != tags.get(key(r), set()) for r in pr["rows"]):
        problems.append("slice tags differ from baseline")
    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        def ratchet(old_entries, new_entries, entry_key, nested):
            current = {entry_key(m): m for m in new_entries}
            for old in old_entries:
                name = entry_key(old)
                new = current.get(name)
                if new is None:
                    problems.append(f"ratchet: removed {name}")
                    continue
                if old.get("blocking") and not new.get("blocking"):
                    problems.append(f"ratchet: nonblocking {name}")
                ot, nt = (old.get("threshold", {}), new.get("threshold", {})) if nested else (old, new)
                for threshold in ("min", "max", "max_increase", "no_significant_drop"):
                    if threshold not in ot:
                        continue
                    value = nt.get(threshold)
                    if (value is None or
                        threshold == "min" and value < ot[threshold] or
                        threshold in ("max", "max_increase") and value > ot[threshold] or
                        threshold == "no_significant_drop" and ot[threshold] and not value):
                        problems.append(f"ratchet: loosened {name}/{threshold}")
        ratchet(base_spec.get("metrics", []), spec.get("metrics", []), lambda m: m["id"], True)
        ratchet(base_spec.get("slices", []), spec.get("slices", []), lambda m: (m["name"], m["metric"]), False)
    return problems


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for rule in spec.get("slices", []):
        name, metric = rule["name"], rule["metric"]
        mid = f"slice:{name}/{metric}"
        a, b = per_item(pr, metric, name), per_item(base, metric, name)
        keys = sorted(a)
        fail = not keys or set(a) != set(b)
        value = sum(a.values()) / len(a) if a else None
        note = ""
        if value is not None and value < rule.get("min", float("-inf")):
            fail = True
        if keys and set(a) == set(b) and rule.get("no_significant_drop"):
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                confidence=bs.get("confidence", 0.95))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            fail |= hi < 0
        if fail and rule.get("blocking"):
            blocked.append(mid)
        lines.append(f"  {mid}: {value} {note} {'BLOCK' if fail else 'ok'}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                                               confidence=bs.get("confidence", 0.95))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
