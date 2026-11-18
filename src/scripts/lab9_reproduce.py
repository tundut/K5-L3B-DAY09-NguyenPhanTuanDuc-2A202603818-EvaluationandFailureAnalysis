"""Regenerate submission evidence. Run from src: python -m scripts.lab9_reproduce."""
import subprocess
import sys


def main():
    commands = [
        'lab9.evalset --build --check',
        'lab9.evalset --v2 --build',
        'lab9.eval --shape swarm --out reports/baseline_v1.json',
        'lab9.eval --shape fixed --out reports/eval_fixed.json',
        'lab9.eval --shape seeded_regression --out reports/eval_seeded_regression.json',
        'lab9.eval --shape swarm --spec config/metric_spec_v2.yaml --out reports/baseline_v2.json',
        'lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml --out reports/eval_slice_regression.json',
        'scripts.lab9_evidence',
        'scripts.lab9_validate',
    ]
    for command in commands:
        subprocess.run([sys.executable, '-m', *command.split()], check=True)


if __name__ == '__main__':
    main()
