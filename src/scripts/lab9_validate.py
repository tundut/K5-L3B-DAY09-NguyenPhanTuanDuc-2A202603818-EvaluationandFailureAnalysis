"""Reproduce local CI and save exact command output for submission evidence.

Run from src: python -m scripts.lab9_validate
"""
import subprocess
import sys
from pathlib import Path


def main():
    commands = [
        ('lab9.smoke', 0),
        ('pytest -q', 0),
        ('pytest -q -m student -o addopts= -k lab9', 0),
        ('lab9.evalset --check', 0),
        ('lab9.evalset --v2', 0),
        ('lab9.judge --csv data/eval/judge_tone_public.csv --audit 5', 0),
        ('lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5', 1),
        ('lab9.mutation --detect', 0),
        ('lab9.eval --shape swarm --out reports/eval_pr.json', 0),
        ('lab9.gate --pr reports/eval_pr.json --baseline reports/baseline_v1.json', 0),
        ('lab9.ci_check --pr reports/eval_pr.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml', 0),
        ('lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json', 0),
        ('lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json', 1),
        ('lab9.gate --pr reports/baseline_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml', 0),
        ('lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110', 0),
        ('lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json', 0),
        ('lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml', 0),
    ]
    for name in ('evaluator_errors_as_nan', 'dropped_failing_rows', 'cherry_picked_seeds', 'loosened_spec'):
        spec = ('--spec reports/traps/loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml'
                if name == 'loosened_spec' else '--spec config/metric_spec_v2.yaml')
        commands.append((f'lab9.gate --pr reports/traps/{name}.json --baseline reports/baseline_v2.json {spec}', 1))
    blocks = ['# Local validation\n\nSinh bởi `python -m scripts.lab9_validate`; exit 1 là kết quả mong đợi cho judge helpful, regression và trap.\n']
    failures = []
    for command, expected in commands:
        result = subprocess.run([sys.executable, '-m', *command.split()], capture_output=True, text=True)
        output = result.stdout + result.stderr
        blocks.append(f'## `{command}`\n\nExpected exit {expected}, actual exit {result.returncode}.\n\n```text\n{output.rstrip()}\n```\n')
        print(f'{command}: exit {result.returncode} (expected {expected})', flush=True)
        if result.returncode != expected:
            failures.append(command)
    Path('../docs/validation.md').write_text('\n'.join(blocks), encoding='utf-8')
    if failures:
        raise SystemExit('Unexpected result: ' + ', '.join(failures))


if __name__ == '__main__':
    main()
