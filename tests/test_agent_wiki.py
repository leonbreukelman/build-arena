from __future__ import annotations

from pathlib import Path

import pytest

from arena.agent_wiki import WikiRecord, append_record, read_records


def test_wiki_record_append_and_read_roundtrip(tmp_path: Path) -> None:
    store = tmp_path / "docs" / "agent-wiki" / "records.jsonl"

    written = append_record(
        store,
        record_type="failure_mode",
        created_run_id="run-1",
        payload={"finding_id": "live-proposer-no-repair-retry", "note": "doubled src prefix"},
    )
    append_record(store, record_type="gate_recipe", created_run_id="run-1", payload={"command": "uv run pytest"})

    records = read_records(store, record_type="failure_mode")

    assert records == [written]
    assert isinstance(records[0], WikiRecord)
    assert records[0].record_type == "failure_mode"
    assert records[0].created_run_id == "run-1"
    assert records[0].payload["finding_id"] == "live-proposer-no-repair-retry"
    assert records[0].id
    assert records[0].content_hash


def test_wiki_rejects_secret_like_payloads(tmp_path: Path) -> None:
    store = tmp_path / "records.jsonl"

    with pytest.raises(ValueError, match="secret"):
        append_record(
            store,
            record_type="failure_mode",
            created_run_id="run-1",
            payload={"api_key": "sk-1234567890abcdef"},
        )

    assert not store.exists()


def test_wiki_rejects_secret_like_json_keys_even_without_sk_prefix(tmp_path: Path) -> None:
    store = tmp_path / "records.jsonl"

    with pytest.raises(ValueError, match="secret"):
        append_record(
            store,
            record_type="failure_mode",
            created_run_id="run-1",
            payload={"api_key": "redacted-but-still-a-secret-field"},
        )

    assert not store.exists()
