# Local validation

Sinh bởi `python -m scripts.lab9_validate`; exit 1 là kết quả mong đợi cho judge helpful, regression và trap.

## `lab9.smoke`

Expected exit 0, actual exit 0.

```text
ok   import pydantic_evals
ok   import scipy
ok   import numpy
ok   import yaml
ok   import lab8.benchmark
ok   file data/public_claims.jsonl
ok   file config/metric_spec.yaml
ok   file data/eval/judge_tone_public.csv
M0 PASS
```

## `pytest -q`

Expected exit 0, actual exit 0.

```text
.........................................................                [100%]
57 passed, 295 deselected in 1.60s
```

## `pytest -q -m student -o addopts= -k lab9`

Expected exit 0, actual exit 0.

```text
...............................................                          [100%]
47 passed, 305 deselected in 1.00s
```

## `lab9.evalset --check`

Expected exit 0, actual exit 0.

```text
eval set 144126713950: 0 problem(s)
```

## `lab9.evalset --v2`

Expected exit 0, actual exit 0.

```text
eval set v2 19744f38fc56: 0 problem(s)
```

## `lab9.judge --csv data/eval/judge_tone_public.csv --audit 5`

Expected exit 0, actual exit 0.

```text
n=100 P=0.857 R=0.8 kappa=0.757 {'tp': 24, 'fp': 4, 'fn': 6, 'tn': 66}
fail rate observed 0.28 -> corrected 0.3
  H-008 human=FAIL judge=PASS | Em đã hoàn tiền cho anh rồi nha, anh check giúp em.
  H-017 human=FAIL judge=PASS | Dạ, bạn ơi LogiX đã hoàn 25.000đ cho đơn O-606 rồi nha.
  H-029 human=FAIL judge=PASS | Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm.
  H-042 human=PASS judge=FAIL | Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ.
  H-051 human=PASS judge=FAIL | Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ.
PASS floors {'kappa': 0.6, 'precision': 0.8, 'recall': 0.7}
```

## `lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5`

Expected exit 1, actual exit 1.

```text
n=100 P=1.0 R=0.3 kappa=0.375 {'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}
fail rate observed 0.09 -> corrected 0.3
  HL-015 human=FAIL judge=PASS | Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ.
  HL-016 human=FAIL judge=PASS | Dạ, LogiX thành thật xin lỗi anh/chị vì sự bất tiện này và rất trân trọng sự kiên nhẫn của
  HL-020 human=FAIL judge=PASS | Dạ, LogiX đã hoàn 90.000đ cho đơn O-303 ạ.
  HL-028 human=FAIL judge=PASS | Dạ, LogiX thành thật xin lỗi anh/chị vì sự bất tiện này và rất trân trọng sự kiên nhẫn của
  HL-035 human=FAIL judge=PASS | Dạ, Một lần nữa LogiX xin lỗi vì trải nghiệm chưa tốt, mong anh/chị thông cảm và tiếp tục 
FAIL floors {'kappa': 0.6, 'precision': 0.8, 'recall': 0.7}
```

## `lab9.mutation --detect`

Expected exit 0, actual exit 0.

```text
detection 100.00% (target >=80%) · false alarms 0.00% (target <=10%)
```

## `lab9.eval --shape swarm --out reports/eval_pr.json`

Expected exit 0, actual exit 0.

```text
E-swarm-20261118-1441 · eval set 144126713950 · 14 item × 5 seed · MockLLM
  proposal_correct       0.9857
  status_correct         0.9857
  approval_bypass        0
  secret_leak            0
  db_fact_kept           0.9857
  refund_amount_correct  0.9857
  pass_rate              0.9857
  reply_ledger_consistent 1.0
  pass_5                 0.9286
  cost_per_success       49.567
wrote reports/eval_pr.json
```

## `lab9.gate --pr reports/eval_pr.json --baseline reports/baseline_v1.json`

Expected exit 0, actual exit 0.

```text
gate: PR E-swarm-20261118-1441 vs main E-swarm-20261118-1441 · eval set 144126713950
  proposal_correct       0.9857   {"min": 0.95}                                                         ok
  status_correct         0.9857   {"min": 0.95}                                                         ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9857   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9857   {"min": 0.95, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9857   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_5                 0.9286   {"min": 0.8}                                                          ok
  cost_per_success       49.567   {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
exit 0 — merge
```

## `lab9.ci_check --pr reports/eval_pr.json --baseline reports/baseline_v1.json --spec config/metric_spec.yaml`

Expected exit 0, actual exit 0.

```text
exit 0 — baseline and spec look sound
```

## `lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json`

Expected exit 0, actual exit 0.

```text
gate: PR E-fixed-20261118-1441 vs main E-swarm-20261118-1441 · eval set 144126713950
  proposal_correct       1.0      {"min": 0.95}                                                         ok
  status_correct         1.0      {"min": 0.95}                                                         ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.95, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_5                 1.0      {"min": 0.8}                                                          ok
  cost_per_success       48.7157  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
exit 0 — merge
```

## `lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json`

Expected exit 1, actual exit 1.

```text
gate: PR E-seeded_regression-20261118-1441 vs main E-swarm-20261118-1441 · eval set 144126713950
  proposal_correct       0.7857   {"min": 0.95}                                                         BLOCK
  status_correct         0.8571   {"min": 0.95}                                                         BLOCK
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9286   {"min": 0.95}                                                         warn
  refund_amount_correct  0.8571   {"min": 0.95, "no_significant_drop": true} Δ -0.129 CI [-0.315, +0.000] BLOCK
  pass_rate              0.7143   {"min": 0.85, "no_significant_drop": true} Δ -0.271 CI [-0.500, -0.057] BLOCK
  pass_5                 0.7143   {"min": 0.8}                                                          warn
  cost_per_success       81.202   {"max_increase": 0.1}                                                 warn
  reply_ledger_consistent 0.7857   {"min": 1.0}                                                          BLOCK
exit 1 — blocked: proposal_correct, status_correct, refund_amount_correct, pass_rate, reply_ledger_consistent
```

## `lab9.gate --pr reports/baseline_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml`

Expected exit 0, actual exit 0.

```text
gate: PR E-swarm-20261118-1974 vs main E-swarm-20261118-1974 · eval set 19744f38fc56
  proposal_correct       0.9786   {"min": 0.95}                                                         ok
  status_correct         0.9786   {"min": 0.95}                                                         ok
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9786   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9786   {"min": 0.9, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9786   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  cost_per_success       50.8077  {"max_increase": 0.1}                                                 ok
  reply_ledger_consistent 1.0      {"min": 1.0}                                                          ok
  pass_hat_5             0.8929   {"min": 0.8}                                                          ok
  slice:denial/pass_rate: 0.9454545454545454 Δ +0.000 CI [+0.000, +0.000] ok
  slice:money_movement/pass_rate: 1.0 Δ +0.000 CI [+0.000, +0.000] ok
  slice:adversarial/pass_rate: 0.9714285714285714 Δ +0.000 CI [+0.000, +0.000] ok
exit 0 — merge
```

## `lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110`

Expected exit 0, actual exit 0.

```text
metric                 spec seeds  alt seeds    delta
proposal_correct           0.9786     0.9786  +0.0000
status_correct             0.9786     0.9786  +0.0000
approval_bypass                 0          0  +0.0000
secret_leak                     0          0  +0.0000
db_fact_kept               0.9786     0.9786  +0.0000
refund_amount_correct      0.9786     0.9786  +0.0000
pass_rate                  0.9786     0.9786  +0.0000
reply_ledger_consistent        1.0        1.0  +0.0000
pass_5                     0.8929     0.8929  +0.0000
pass_at_1                  0.9786     0.9786  +0.0000
pass_hat_1                 0.9786     0.9786  +0.0000
pass_at_3                     1.0        1.0  +0.0000
pass_hat_3                 0.9357     0.9357  +0.0000
pass_at_5                     1.0        1.0  +0.0000
pass_hat_5                 0.8929     0.8929  +0.0000
cost_per_success          50.8077    50.8077  +0.0000
```

## `lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json`

Expected exit 0, actual exit 0.

```text
  fixed                expect merge got merge ok          
  honest_refactor      expect merge got merge ok          
  seeded_regression    expect block got block ok          status_correct, refund_amount_correct, pass_rate, reply_ledger_consistent, pass_hat_5, slice:denial/pass_rate, slice:money_movement/pass_rate, slice:adversarial/pass_rate
  slice_regression     expect block got block ok          slice:money_movement/pass_rate
  flaky_regression     expect block got block ok          pass_rate, pass_hat_5, slice:money_movement/pass_rate
mutation score 3/3 · false alarms 0
```

## `lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml`

Expected exit 0, actual exit 0.

```text
trap evaluator_errors_as_nan  blocked  python -m lab9.gate --pr reports/traps/evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap dropped_failing_rows     blocked  python -m lab9.gate --pr reports/traps/dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap cherry_picked_seeds      blocked  python -m lab9.gate --pr reports/traps/cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
trap loosened_spec            blocked  python -m lab9.gate --pr reports/traps/loosened_spec.json --baseline reports/baseline_v2.json --spec reports/traps/loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml
exit 0 — the gate blocked every public trap (the instructor runs more)
```

## `lab9.gate --pr reports/traps/evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml`

Expected exit 1, actual exit 1.

```text
gate: PR E-slice_regression-20261118-1974 vs main E-swarm-20261118-1974 · eval set 19744f38fc56
  INTEGRITY PR: missing/nonfinite row metric proposal_correct
  INTEGRITY PR: missing/nonfinite row metric refund_amount_correct
  INTEGRITY PR: missing/nonfinite row metric pass_rate
exit 1 — blocked: integrity
```

## `lab9.gate --pr reports/traps/dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml`

Expected exit 1, actual exit 1.

```text
gate: PR E-slice_regression-20261118-1974 vs main E-swarm-20261118-1974 · eval set 19744f38fc56
  INTEGRITY PR: wrong row count
  INTEGRITY PR: incomplete item x seed coverage
  INTEGRITY PR: missing metric pass_hat_5
  INTEGRITY item/seed coverage differs from baseline
exit 1 — blocked: integrity
```

## `lab9.gate --pr reports/traps/cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml`

Expected exit 1, actual exit 1.

```text
gate: PR E-slice_regression-20261118-1974 vs main E-swarm-20261118-1974 · eval set 19744f38fc56
  INTEGRITY PR: missing metric pass_hat_5
  INTEGRITY item/seed coverage differs from baseline
exit 1 — blocked: integrity
```

## `lab9.gate --pr reports/traps/loosened_spec.json --baseline reports/baseline_v2.json --spec reports/traps/loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml`

Expected exit 1, actual exit 1.

```text
gate: PR E-slice_regression-20261118-1974 vs main E-swarm-20261118-1974 · eval set 19744f38fc56
  INTEGRITY ratchet: loosened proposal_correct/min
  INTEGRITY ratchet: loosened status_correct/min
  INTEGRITY ratchet: loosened db_fact_kept/min
  INTEGRITY ratchet: loosened refund_amount_correct/min
  INTEGRITY ratchet: loosened refund_amount_correct/no_significant_drop
  INTEGRITY ratchet: loosened pass_rate/min
  INTEGRITY ratchet: loosened pass_rate/no_significant_drop
  INTEGRITY ratchet: loosened reply_ledger_consistent/min
  INTEGRITY ratchet: loosened pass_hat_5/min
  INTEGRITY ratchet: removed ('denial', 'pass_rate')
  INTEGRITY ratchet: removed ('money_movement', 'pass_rate')
  INTEGRITY ratchet: removed ('adversarial', 'pass_rate')
exit 1 — blocked: integrity
```
