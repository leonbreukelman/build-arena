from __future__ import annotations

import pytest

from arena.runners.base import ViewBeforeEditViolation
from arena.runners.claude_code import ClaudeStreamGuard


def _tool_event(*blocks: dict) -> dict:
    return {"type": "assistant", "message": {"content": list(blocks)}}


def test_read_then_edit_same_path_in_same_turn_passes() -> None:
    guard = ClaudeStreamGuard()

    guard.process_event(
        _tool_event(
            {"type": "tool_use", "name": "Read", "input": {"file_path": "src/a.py"}},
            {"type": "tool_use", "name": "Edit", "input": {"file_path": "src/a.py"}},
        )
    )


def test_edit_without_same_turn_read_raises() -> None:
    guard = ClaudeStreamGuard()

    with pytest.raises(ViewBeforeEditViolation, match="src/a.py"):
        guard.process_event(
            _tool_event({"type": "tool_use", "name": "Edit", "input": {"file_path": "src/a.py"}})
        )


def test_read_in_previous_turn_does_not_authorize_later_edit() -> None:
    guard = ClaudeStreamGuard()
    guard.process_event(
        _tool_event({"type": "tool_use", "name": "Read", "input": {"file_path": "src/a.py"}})
    )

    with pytest.raises(ViewBeforeEditViolation, match="src/a.py"):
        guard.process_event(
            _tool_event({"type": "tool_use", "name": "Edit", "input": {"file_path": "src/a.py"}})
        )


def test_write_requires_same_turn_read_too() -> None:
    guard = ClaudeStreamGuard()

    with pytest.raises(ViewBeforeEditViolation, match="src/new.py"):
        guard.process_event(
            _tool_event({"type": "tool_use", "name": "Write", "input": {"file_path": "src/new.py"}})
        )
