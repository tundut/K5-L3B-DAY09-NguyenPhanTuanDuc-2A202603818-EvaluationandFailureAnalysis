"""Reproduce taxonomy evidence without editing Lab 8 or the public variants.

Run from src: python -m scripts.lab9_evidence
"""
import json
import tempfile
from pathlib import Path

from lab8.shapes import SHAPES
from lab9.eval import load_spec, load_world, make_task
from lab9.variant_agent import make_shape

CASES = [
    ('FM-01', 'leaky_trace', 'C-001'),
    ('FM-02', 'ignore_denied', 'C-007'),
    ('FM-03', 'ticket_trust', 'C-002'),
    ('FM-04', 'sum_parts', 'C-014'),
    ('FM-05', 'pre_deducted', 'C-014'),
    ('FM-06', 'stale_clause', 'C-006'),
    ('FM-07', 'sibling_refund', 'C-010'),
    ('FM-08', 'misreport', 'C-008'),
    ('FM-09', 'no_override', 'C-005'),  # negative control; not an observed breach
]


def main():
    world, claims = load_world(load_spec(Path('config/metric_spec_v2.yaml')))
    labels = {claim['claim_id']: claim['expected'] for claim in claims}
    evidence = {}
    for mode, bug, claim_id in CASES:
        name = 'evidence_' + mode
        SHAPES[name] = make_shape(name, {'no_override', bug})
        try:
            with tempfile.TemporaryDirectory() as tmp:
                task = make_task(name, world, claims, labels, Path(tmp))
                trial = task({'claim_id': claim_id, 'seed': 11})
            evidence[mode] = {'claim': claim_id, 'seed': 11, 'bugs': sorted({'no_override', bug}),
                              'control': mode == 'FM-09', 'trial': trial}
            print(mode, claim_id, 'lab8_pass=', trial['lab8_pass'], 'ledger=', trial['snapshot'])
            for number, event in enumerate(trial['events'], 1):
                print(number, event['kind'], json.dumps(event.get('payload'), ensure_ascii=False)[:400])
        finally:
            SHAPES.pop(name, None)
    path = Path('reports/failure_evidence.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
