from __future__ import annotations

import pytest

from arena.hypothesizer import Arm, EmptyArmSetError, SymbolicHypothesizer, UCB1Bandit


def test_bandit_cold_start_pulls_each_arm_in_config_order() -> None:
    arms = [
        Arm("runtime", "core", ("src/pkg/core.py",)),
        Arm("coverage", "errors", ("src/pkg/errors.py",)),
        Arm("typing", "validate", ("src/pkg/validate.py",)),
    ]
    bandit = UCB1Bandit(arms, alpha=1.25)

    first = bandit.select_arm()
    bandit.record_reward(first, 0.0)
    second = bandit.select_arm()
    bandit.record_reward(second, 0.0)
    third = bandit.select_arm()

    assert [first.key, second.key, third.key] == [arm.key for arm in arms]


def test_bandit_uses_ucb_after_cold_start() -> None:
    arms = [
        Arm("runtime", "core", ("src/pkg/core.py",)),
        Arm("coverage", "errors", ("src/pkg/errors.py",)),
        Arm("typing", "validate", ("src/pkg/validate.py",)),
    ]
    bandit = UCB1Bandit(arms, alpha=1.25)
    for reward in (1.0, 0.0, 0.0):
        arm = bandit.select_arm()
        bandit.record_reward(arm, reward)

    assert bandit.select_arm() == arms[0]


def test_bandit_rejects_empty_arm_set() -> None:
    with pytest.raises(EmptyArmSetError):
        UCB1Bandit([])


def test_symbolic_hypothesizer_creates_hypothesis_without_filesystem_writes(tmp_path) -> None:
    arms = [Arm("runtime", "core", ("src/pkg/core.py", "tests/test_core.py"))]
    bandit = UCB1Bandit(arms)
    hypothesizer = SymbolicHypothesizer(bandit)

    before = sorted(tmp_path.iterdir())
    proposal = hypothesizer.propose(cycle_id="cycle-7", ast_diff_pattern="loop_to_dict")
    after = sorted(tmp_path.iterdir())

    assert before == after == []
    assert proposal.arm == arms[0]
    assert proposal.hypothesis.cycle_id == "cycle-7"
    assert proposal.hypothesis.technique_tag == "runtime"
    assert proposal.hypothesis.target_cluster == "core"
    assert proposal.hypothesis.target_files == ["src/pkg/core.py", "tests/test_core.py"]
    assert proposal.hypothesis.fingerprint_id == proposal.fingerprint.id
