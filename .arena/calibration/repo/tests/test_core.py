from __future__ import annotations

from validatorlib.core import Rule, ValidationItem, process_batch, summarize_results


def test_process_batch_preserves_input_order_and_messages() -> None:
    items = [ValidationItem("name", "Ada"), ValidationItem("age", ""), ValidationItem("city", "London")]
    rules = [Rule("name", bool), Rule("age", bool), Rule("city", bool)]

    results = process_batch(items, rules)

    assert [result.key for result in results] == ["name", "age", "city"]
    assert [result.ok for result in results] == [True, False, True]
    assert results[1].message == "invalid value"


def test_process_batch_reports_missing_rule() -> None:
    results = process_batch([ValidationItem("unknown", "x")], [Rule("known", bool)])
    assert results[0].message == "missing rule"
    assert not results[0].ok


def test_summarize_results_counts_outcomes() -> None:
    items = [ValidationItem("name", "Ada"), ValidationItem("age", "")]
    results = process_batch(items, [Rule("name", bool), Rule("age", bool)])
    assert summarize_results(results) == {"passed": 1, "failed": 1, "total": 2}
