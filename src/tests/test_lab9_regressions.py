"""Behavioral regressions from traces and adversarial report mutations."""
import copy

import pytest

from lab9 import gate, stats
from lab9.graders import ReplyLedgerConsistent
from lab9.trace_case import investigate
from test_lab9_graders import ctx, trial

pytestmark = pytest.mark.student


def test_lab9_ticket_override_trace_regression():
    broken = investigate('seeded_regression', 'C-002', 11)['trial']
    fixed = investigate('fixed', 'C-002', 11)['trial']
    assert broken['events'][2]['kind'] == 'model_override'
    assert broken['events'][2]['payload'] == {'delay_days': 5}
    assert broken['snapshot']['refund_vnd'] == 20000
    assert not broken['lab8_pass']
    assert fixed['snapshot']['refund_vnd'] == 0
    assert fixed['lab8_pass']
    assert not any(e['kind'] == 'model_override' for e in fixed['events'])


@pytest.mark.parametrize('text,ok', [
    ('Đã hoàn 35.000đ cho O-107.', True),
    ('LogiX đã hoàn phí 35,000 VND cho đơn O-107.', True),
    ('Đã hoàn 35000 đồng.', True),
    ('Đã hoàn 30.000đ cho O-107.', False),
    ('Đã hoàn 35.000đ và 20.000đ.', False),
])
def test_lab9_reply_amount_ignores_order_ids(text, ok):
    output = trial(events=[{'kind': 'reply', 'payload': {'text': text}}])
    assert ReplyLedgerConsistent().evaluate(ctx(output)).value is ok


@pytest.mark.parametrize('text,ok', [
    ('Đã hoàn 20.000đ trong khoản đề xuất 35.000đ.', True),
    ('Đề xuất hoàn 35.000đ, thực tế đã hoàn 20.000đ.', True),
    ('Đề xuất: 20.000đ, đã hoàn 35.000đ.', False),
    ('Đã hoàn 35.000đ trong khoản đề xuất 20.000đ.', False),
])
def test_lab9_proposal_and_paid_amount(text, ok):
    output = trial(refund_vnd=20000, events=[{'kind': 'reply', 'payload': {'text': text}}])
    assert ReplyLedgerConsistent().evaluate(ctx(output)).value is ok


@pytest.mark.parametrize('human', [('PASS', 'PASS'), ('FAIL', 'FAIL'), ('PASS', 'FAIL')])
def test_lab9_constant_judge_cli(tmp_path, capsys, human):
    from lab9 import judge

    path = tmp_path / 'judge.csv'
    path.write_text('human,judge\n' + ''.join(f'{h},{human[0]}\n' for h in human))
    assert judge.main(['--csv', str(path)]) == 1
    out = capsys.readouterr().out
    assert 'FAIL floors' in out and 'corrected N/A' in out


def _fixture():
    rows = [{'item_id': 'E-1', 'seed': s, 'pass_rate': True, 'slices': ['money']} for s in [1, 2]]
    report = {'manifest': {'items': 1, 'seeds': [1, 2], 'eval_set_sha': 'x'},
              'rows': rows, 'metrics': {'pass_rate': 1.0}, 'evaluator_failures': []}
    spec = {'eval_set_version': 'v2', 'metrics': [
        {'id': 'pass_rate', 'threshold': {'min': .8, 'no_significant_drop': True}, 'blocking': True}],
        'slices': [{'name': 'money', 'metric': 'pass_rate', 'min': .9, 'blocking': True}]}
    return report, spec


@pytest.mark.parametrize('mutation', ['duplicate', 'failure', 'row_nan', 'tags', 'seeds'])
def test_lab9_advanced_integrity_on_green_reports(mutation):
    base, spec = _fixture()
    pr = copy.deepcopy(base)
    if mutation == 'duplicate': pr['rows'][1] = copy.deepcopy(pr['rows'][0])
    if mutation == 'failure': pr['evaluator_failures'] = ['grader crashed']
    if mutation == 'row_nan': pr['rows'][0]['pass_rate'] = float('nan')
    if mutation == 'tags': pr['rows'][0]['slices'] = []
    if mutation == 'seeds': pr['rows'][0]['seed'] = 99
    assert gate.integrity_check(pr, base, spec)
    assert gate.integrity_check(base, base, spec) == []


def test_lab9_advanced_ratchet_rejects_removed_slice_and_ci():
    base, spec = _fixture()
    for mutation in ('slice', 'ci', 'blocking'):
        pr_spec = copy.deepcopy(spec)
        if mutation == 'slice': pr_spec['slices'] = []
        if mutation == 'ci': del pr_spec['metrics'][0]['threshold']['no_significant_drop']
        if mutation == 'blocking': pr_spec['metrics'][0]['blocking'] = False
        assert gate.integrity_check(base, base, pr_spec, spec)


@pytest.mark.parametrize('args', [(0, 0, 1), (5, -1, 1), (5, 6, 2), (5, 2, -1), (5.0, 2, 1)])
def test_lab9_advanced_both_estimators_reject_invalid_counts(args):
    for estimator in (stats.pass_at_k, stats.pass_hat_k):
        with pytest.raises(ValueError): estimator(*args)
