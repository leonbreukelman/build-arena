from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.11.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'arena',
     'default_range': 'string',
     'description': 'Autonomous Build Arena data model',
     'id': 'https://arena.local/schema/v1',
     'imports': ['linkml:types'],
     'name': 'arena',
     'prefixes': {'arena': {'prefix_prefix': 'arena',
                            'prefix_reference': 'https://arena.local/schema/v1/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'}},
     'source_file': 'schema/arena.yaml',
     'types': {'Blake2b16': {'base': 'str',
                             'from_schema': 'https://arena.local/schema/v1',
                             'name': 'Blake2b16',
                             'pattern': '^[0-9a-f]{32}$',
                             'uri': 'xsd:string'},
               'GitOid': {'base': 'str',
                          'from_schema': 'https://arena.local/schema/v1',
                          'name': 'GitOid',
                          'pattern': '^[0-9a-f]{40}$',
                          'uri': 'xsd:string'},
               'PathRel': {'base': 'str',
                           'from_schema': 'https://arena.local/schema/v1',
                           'name': 'PathRel',
                           'uri': 'xsd:string'},
               'Sha256': {'base': 'str',
                          'from_schema': 'https://arena.local/schema/v1',
                          'name': 'Sha256',
                          'pattern': '^[0-9a-f]{64}$',
                          'uri': 'xsd:string'},
               'UnixTs': {'base': 'float',
                          'from_schema': 'https://arena.local/schema/v1',
                          'name': 'UnixTs',
                          'uri': 'xsd:double'}}} )

class LoopState(str, Enum):
    SCAN = "SCAN"
    """
    Rebuild project model + scorer baseline
    """
    HYPOTHESIZE = "HYPOTHESIZE"
    """
    Bandit selects arm, runner proposes patch
    """
    APPLY = "APPLY"
    """
    Patch materialized in worktree; AST/structural gates
    """
    VERIFY = "VERIFY"
    """
    Score delta + tests + ablation probes
    """
    PROMOTE = "PROMOTE"
    """
    ff-merge into main branch, baseline advance
    """
    DISCARD = "DISCARD"
    """
    Worktree torn down, fingerprint recorded
    """
    HALT = "HALT"
    """
    Terminal; only DivergenceDetector or budget can enter
    """


class RejectReason(str, Enum):
    BOUNDARY_VIOLATION = "BOUNDARY_VIOLATION"
    """
    Hypothesis touched scorer/ or verifier/
    """
    FINGERPRINT_COLLISION = "FINGERPRINT_COLLISION"
    """
    Matches recorded failure
    """
    VIEW_BEFORE_EDIT_VIOLATION = "VIEW_BEFORE_EDIT_VIOLATION"
    """
    Edit without fresh read in same turn
    """
    STRUCTURAL_VALIDATION_FAIL = "STRUCTURAL_VALIDATION_FAIL"
    """
    Claimed symbol absent from intended-after AST
    """
    SCORE_DELTA_NONPOSITIVE = "SCORE_DELTA_NONPOSITIVE"
    """
    Delta is nonpositive
    """
    TEST_FAILURE = "TEST_FAILURE"
    """
    At least one test regressed or failed
    """
    PINNED_METRIC_REGRESSION = "PINNED_METRIC_REGRESSION"
    """
    Pinned sub-metric got worse
    """
    ABLATION_REASONING_NOT_LOAD_BEARING = "ABLATION_REASONING_NOT_LOAD_BEARING"
    """
    Lanham quorum probe failed
    """
    RUNNER_ERROR = "RUNNER_ERROR"
    """
    Adapter raised or CLI exit was nonzero
    """
    TIMEOUT = "TIMEOUT"
    """
    Per-cycle wall time exceeded
    """


class HaltReason(str, Enum):
    SCORER_NON_DETERMINISTIC = "SCORER_NON_DETERMINISTIC"
    """
    Re-score of baseline drifted beyond tolerance
    """
    FINGERPRINT_CLUSTER_FAILURE = "FINGERPRINT_CLUSTER_FAILURE"
    """
    Failure rate breach over distinct fingerprints
    """
    BUDGET_EXHAUSTED_ZERO_PROMOTIONS = "BUDGET_EXHAUSTED_ZERO_PROMOTIONS"
    """
    All budgets spent, no promotion
    """
    BOUNDARY_VIOLATION_ATTEMPT = "BOUNDARY_VIOLATION_ATTEMPT"
    """
    Repeated agent attempts to mutate scorer
    """
    SCORER_VERIFIER_DISAGREEMENT = "SCORER_VERIFIER_DISAGREEMENT"
    """
    Consecutive scorer/verifier disagreement
    """
    WALL_CLOCK_BREACH = "WALL_CLOCK_BREACH"
    """
    BudgetBreach on wall time
    """
    OPERATOR_EMERGENCY_STOP = "OPERATOR_EMERGENCY_STOP"
    """
    POST /emergency_stop
    """
    OVERRIDE_RESUMABLE = "OVERRIDE_RESUMABLE"
    """
    Operator override_divergence accepted
    """
    RUNNER_UNAVAILABLE = "RUNNER_UNAVAILABLE"
    """
    Required runner missing at boot
    """
    BASELINE_DRIFT = "BASELINE_DRIFT"
    """
    Git main OID differs from active Baseline
    """


class RunnerName(str, Enum):
    claude_code = "claude_code"
    codex = "codex"
    copilot = "copilot"
    gemini = "gemini"
    ollama = "ollama"


class AblationProbe(str, Enum):
    EARLY_ANSWERING = "EARLY_ANSWERING"
    """
    Truncate the original CoT before answering.
    """
    FILLER_TOKENS = "FILLER_TOKENS"
    """
    Replace the CoT with ellipses.
    """
    PARAPHRASING = "PARAPHRASING"
    """
    Reword the beginning of the CoT, then regenerate.
    """
    ADDING_MISTAKES = "ADDING_MISTAKES"
    """
    Inject a mistake mid-CoT, then regenerate.
    """


class VerdictOutcome(str, Enum):
    PROMOTED = "PROMOTED"
    DISCARDED = "DISCARDED"
    ERROR = "ERROR"



class Run(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    north_star_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run']} })
    scorer_lock_sha: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run', 'ScoreRecord']} })
    config_sha: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run']} })
    git_head_at_start: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run']} })
    started_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run', 'Cycle']} })
    ended_ts: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Run', 'Cycle']} })
    halt_record_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Run']} })
    cycles_total: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Run'], 'ifabsent': 'int(0)'} })
    promotions_total: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Run'], 'ifabsent': 'int(0)'} })


class NorthStar(ConfiguredBaseModel):
    """
    Operator-provided objective; immutable for the life of a Run.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    description: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['NorthStar']} })
    score_axes: list[str] = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['NorthStar']} })
    pinned_axes: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['NorthStar']} })
    created_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['NorthStar', 'Worktree']} })


class Cycle(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    run_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'DivergenceIndicator']} })
    ordinal: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle']} })
    entered_state: LoopState = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle']} })
    started_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run', 'Cycle']} })
    ended_ts: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Run', 'Cycle']} })
    bandit_arm: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle']} })
    hypothesis_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle', 'Verdict']} })
    verdict_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle', 'AblationResult']} })
    worktree_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle']} })
    baseline_id_before: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle']} })
    baseline_id_after: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle']} })
    runner_used: Optional[RunnerName] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle', 'AblationResult']} })


class Hypothesis(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    cycle_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis', 'ScoreRecord', 'Event', 'Worktree']} })
    intent: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis']} })
    technique_tag: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis', 'Fingerprint']} })
    target_cluster: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis']} })
    target_files: list[str] = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis']} })
    fingerprint_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis']} })
    reasoning_blob_sha: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis']} })
    patch_blob_sha: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis']} })
    proposed_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis']} })


class Fingerprint(ConfiguredBaseModel):
    """
    blake2b digest over intent embedding, target files, technique tag, and AST diff pattern.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    quantized_intent_embedding_sha: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Fingerprint']} })
    sorted_target_files_hash: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Fingerprint']} })
    technique_tag: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis', 'Fingerprint']} })
    ast_diff_pattern_hash: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Fingerprint']} })
    embedding_model: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Fingerprint']} })
    first_seen_cycle_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Fingerprint']} })
    failure_count: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Fingerprint'], 'ifabsent': 'int(0)'} })
    success_count: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Fingerprint'], 'ifabsent': 'int(0)'} })


class Verdict(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    hypothesis_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle', 'Verdict']} })
    outcome: VerdictOutcome = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    reject_reason: Optional[RejectReason] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    score_delta: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    score_before_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    score_after_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    tests_passed: Optional[bool] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    pinned_regression: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    ablation_result_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })
    decided_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Verdict']} })


class ScoreRecord(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    cycle_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis', 'ScoreRecord', 'Event', 'Worktree']} })
    git_oid: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ScoreRecord', 'Baseline']} })
    scorer_lock_sha: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run', 'ScoreRecord']} })
    vector_json_sha: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ScoreRecord']} })
    composite: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ScoreRecord']} })
    computed_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ScoreRecord']} })


class AblationResult(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    verdict_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle', 'AblationResult']} })
    probe_set: list[AblationProbe] = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AblationResult']} })
    probes_changed_output: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AblationResult']} })
    quorum_threshold: int = Field(default=2, json_schema_extra = { "linkml_meta": {'domain_of': ['AblationResult'], 'ifabsent': 'int(2)'} })
    load_bearing: bool = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['AblationResult']} })
    runner_used: RunnerName = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle', 'AblationResult']} })


class Event(ConfiguredBaseModel):
    """
    Append-only JSONL record. SQLite is a projection of these.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    run_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'DivergenceIndicator']} })
    cycle_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis', 'ScoreRecord', 'Event', 'Worktree']} })
    seq: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Event']} })
    ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Event', 'HaltRecord']} })
    type: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Event']} })
    level: Optional[str] = Field(default="info", json_schema_extra = { "linkml_meta": {'domain_of': ['Event'], 'ifabsent': 'string(info)'} })
    payload_json_sha: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Event']} })
    payload_inline: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Event']} })


class Budget(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    run_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'DivergenceIndicator']} })
    wall_clock_seconds_cap: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Budget']} })
    cycle_count_cap: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Budget']} })
    claude_code_credits_cap: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget']} })
    codex_credits_cap: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget']} })
    copilot_premium_cap: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget']} })
    ollama_unbounded: Optional[bool] = Field(default=True, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget'], 'ifabsent': 'True'} })
    wall_clock_seconds_used: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget'], 'ifabsent': 'int(0)'} })
    cycle_count_used: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget'], 'ifabsent': 'int(0)'} })
    claude_code_credits_used: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget'], 'ifabsent': 'int(0)'} })
    codex_credits_used: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget'], 'ifabsent': 'int(0)'} })
    copilot_premium_used: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Budget'], 'ifabsent': 'int(0)'} })


class HaltRecord(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    run_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'DivergenceIndicator']} })
    reason: HaltReason = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['HaltRecord']} })
    detail: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['HaltRecord']} })
    last_event_seq: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['HaltRecord']} })
    ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Event', 'HaltRecord']} })
    operator_ack_ts: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['HaltRecord']} })


class Baseline(ConfiguredBaseModel):
    """
    The current promoted commit plus its ScoreRecord.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    run_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'DivergenceIndicator']} })
    git_oid: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ScoreRecord', 'Baseline']} })
    score_record_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Baseline']} })
    promoted_from_verdict_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Baseline']} })
    promoted_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Baseline']} })
    is_active: bool = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Baseline']} })


class Worktree(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    cycle_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Hypothesis', 'ScoreRecord', 'Event', 'Worktree']} })
    path: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Worktree']} })
    base_git_oid: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Worktree']} })
    head_git_oid: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Worktree']} })
    created_ts: float = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['NorthStar', 'Worktree']} })
    torn_down_ts: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Worktree']} })
    lock_reason: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Worktree']} })


class DivergenceIndicator(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://arena.local/schema/v1'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Run',
                       'NorthStar',
                       'Cycle',
                       'Hypothesis',
                       'Fingerprint',
                       'Verdict',
                       'ScoreRecord',
                       'AblationResult',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'Worktree',
                       'DivergenceIndicator']} })
    run_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Cycle',
                       'Event',
                       'Budget',
                       'HaltRecord',
                       'Baseline',
                       'DivergenceIndicator']} })
    kind: HaltReason = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['DivergenceIndicator']} })
    cycle_window: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DivergenceIndicator']} })
    counter: Optional[int] = Field(default=0, json_schema_extra = { "linkml_meta": {'domain_of': ['DivergenceIndicator'], 'ifabsent': 'int(0)'} })
    threshold: int = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['DivergenceIndicator']} })
    tripped: Optional[bool] = Field(default=False, json_schema_extra = { "linkml_meta": {'domain_of': ['DivergenceIndicator'], 'ifabsent': 'False'} })
    last_observed_ts: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DivergenceIndicator']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Run.model_rebuild()
NorthStar.model_rebuild()
Cycle.model_rebuild()
Hypothesis.model_rebuild()
Fingerprint.model_rebuild()
Verdict.model_rebuild()
ScoreRecord.model_rebuild()
AblationResult.model_rebuild()
Event.model_rebuild()
Budget.model_rebuild()
HaltRecord.model_rebuild()
Baseline.model_rebuild()
Worktree.model_rebuild()
DivergenceIndicator.model_rebuild()
