export type RunId = string;
export type NorthStarId = string;
export type CycleId = string;
export type HypothesisId = string;
export type FingerprintId = string;
export type VerdictId = string;
export type ScoreRecordId = string;
export type AblationResultId = string;
export type EventId = string;
export type BudgetId = string;
export type HaltRecordId = string;
export type BaselineId = string;
export type WorktreeId = string;
export type DivergenceIndicatorId = string;

export enum LoopState {

    /** Rebuild project model + scorer baseline */
    SCAN = "SCAN",
    /** Bandit selects arm, runner proposes patch */
    HYPOTHESIZE = "HYPOTHESIZE",
    /** Patch materialized in worktree; AST/structural gates */
    APPLY = "APPLY",
    /** Score delta + tests + ablation probes */
    VERIFY = "VERIFY",
    /** ff-merge into main branch, baseline advance */
    PROMOTE = "PROMOTE",
    /** Worktree torn down, fingerprint recorded */
    DISCARD = "DISCARD",
    /** Terminal; only DivergenceDetector or budget can enter */
    HALT = "HALT",
};

export enum RejectReason {

    /** Hypothesis touched scorer/ or verifier/ */
    BOUNDARY_VIOLATION = "BOUNDARY_VIOLATION",
    /** Matches recorded failure */
    FINGERPRINT_COLLISION = "FINGERPRINT_COLLISION",
    /** Edit without fresh read in same turn */
    VIEW_BEFORE_EDIT_VIOLATION = "VIEW_BEFORE_EDIT_VIOLATION",
    /** Claimed symbol absent from intended-after AST */
    STRUCTURAL_VALIDATION_FAIL = "STRUCTURAL_VALIDATION_FAIL",
    /** Delta is nonpositive */
    SCORE_DELTA_NONPOSITIVE = "SCORE_DELTA_NONPOSITIVE",
    /** At least one test regressed or failed */
    TEST_FAILURE = "TEST_FAILURE",
    /** Pinned sub-metric got worse */
    PINNED_METRIC_REGRESSION = "PINNED_METRIC_REGRESSION",
    /** Lanham quorum probe failed */
    ABLATION_REASONING_NOT_LOAD_BEARING = "ABLATION_REASONING_NOT_LOAD_BEARING",
    /** Adapter raised or CLI exit was nonzero */
    RUNNER_ERROR = "RUNNER_ERROR",
    /** Per-cycle wall time exceeded */
    TIMEOUT = "TIMEOUT",
};

export enum HaltReason {

    /** Re-score of baseline drifted beyond tolerance */
    SCORER_NON_DETERMINISTIC = "SCORER_NON_DETERMINISTIC",
    /** Failure rate breach over distinct fingerprints */
    FINGERPRINT_CLUSTER_FAILURE = "FINGERPRINT_CLUSTER_FAILURE",
    /** All budgets spent, no promotion */
    BUDGET_EXHAUSTED_ZERO_PROMOTIONS = "BUDGET_EXHAUSTED_ZERO_PROMOTIONS",
    /** Repeated agent attempts to mutate scorer */
    BOUNDARY_VIOLATION_ATTEMPT = "BOUNDARY_VIOLATION_ATTEMPT",
    /** Consecutive scorer/verifier disagreement */
    SCORER_VERIFIER_DISAGREEMENT = "SCORER_VERIFIER_DISAGREEMENT",
    /** BudgetBreach on wall time */
    WALL_CLOCK_BREACH = "WALL_CLOCK_BREACH",
    /** POST /emergency_stop */
    OPERATOR_EMERGENCY_STOP = "OPERATOR_EMERGENCY_STOP",
    /** Operator override_divergence accepted */
    OVERRIDE_RESUMABLE = "OVERRIDE_RESUMABLE",
    /** Required runner missing at boot */
    RUNNER_UNAVAILABLE = "RUNNER_UNAVAILABLE",
    /** Git main OID differs from active Baseline */
    BASELINE_DRIFT = "BASELINE_DRIFT",
};

export enum RunnerName {

    claude_code = "claude_code",
    codex = "codex",
    copilot = "copilot",
    gemini = "gemini",
    ollama = "ollama",
};

export enum AblationProbe {

    /** Truncate the original CoT before answering. */
    EARLY_ANSWERING = "EARLY_ANSWERING",
    /** Replace the CoT with ellipses. */
    FILLER_TOKENS = "FILLER_TOKENS",
    /** Reword the beginning of the CoT, then regenerate. */
    PARAPHRASING = "PARAPHRASING",
    /** Inject a mistake mid-CoT, then regenerate. */
    ADDING_MISTAKES = "ADDING_MISTAKES",
};

export enum VerdictOutcome {

    PROMOTED = "PROMOTED",
    DISCARDED = "DISCARDED",
    ERROR = "ERROR",
};



export interface Run {
    id: string,
    north_star_id: NorthStarId,
    scorer_lock_sha: string,
    config_sha: string,
    git_head_at_start: string,
    started_ts: number,
    ended_ts?: number,
    halt_record_id?: HaltRecordId,
    cycles_total?: number,
    promotions_total?: number,
}


/**
 * Operator-provided objective; immutable for the life of a Run.
 */
export interface NorthStar {
    id: string,
    description: string,
    score_axes: string[],
    pinned_axes?: string[],
    created_ts: number,
}



export interface Cycle {
    id: string,
    run_id: RunId,
    ordinal: number,
    entered_state: string,
    started_ts: number,
    ended_ts?: number,
    bandit_arm?: string,
    hypothesis_id?: HypothesisId,
    verdict_id?: VerdictId,
    worktree_id?: WorktreeId,
    baseline_id_before?: BaselineId,
    baseline_id_after?: BaselineId,
    runner_used?: string,
}



export interface Hypothesis {
    id: string,
    cycle_id: CycleId,
    intent: string,
    technique_tag: string,
    target_cluster: string,
    target_files: string[],
    fingerprint_id: FingerprintId,
    reasoning_blob_sha?: string,
    patch_blob_sha?: string,
    proposed_ts: number,
}


/**
 * blake2b digest over intent embedding, target files, technique tag, and AST diff pattern.
 */
export interface Fingerprint {
    id: string,
    quantized_intent_embedding_sha: string,
    sorted_target_files_hash: string,
    technique_tag: string,
    ast_diff_pattern_hash: string,
    embedding_model: string,
    first_seen_cycle_id: CycleId,
    failure_count?: number,
    success_count?: number,
}



export interface Verdict {
    id: string,
    hypothesis_id: HypothesisId,
    outcome: string,
    reject_reason?: string,
    score_delta?: number,
    score_before_id: ScoreRecordId,
    score_after_id?: ScoreRecordId,
    tests_passed?: boolean,
    pinned_regression?: string[],
    ablation_result_id?: AblationResultId,
    decided_ts: number,
}



export interface ScoreRecord {
    id: string,
    cycle_id: CycleId,
    git_oid: string,
    scorer_lock_sha: string,
    vector_json_sha: string,
    composite: number,
    computed_ts: number,
}



export interface AblationResult {
    id: string,
    verdict_id: VerdictId,
    probe_set: string,
    probes_changed_output: number,
    quorum_threshold: number,
    load_bearing: boolean,
    runner_used: string,
}


/**
 * Append-only JSONL record. SQLite is a projection of these.
 */
export interface Event {
    id: string,
    run_id: RunId,
    cycle_id?: CycleId,
    seq: number,
    ts: number,
    type: string,
    level?: string,
    payload_json_sha?: string,
    payload_inline?: string,
}



export interface Budget {
    id: string,
    run_id: RunId,
    wall_clock_seconds_cap: number,
    cycle_count_cap: number,
    claude_code_credits_cap?: number,
    codex_credits_cap?: number,
    copilot_premium_cap?: number,
    ollama_unbounded?: boolean,
    wall_clock_seconds_used?: number,
    cycle_count_used?: number,
    claude_code_credits_used?: number,
    codex_credits_used?: number,
    copilot_premium_used?: number,
}



export interface HaltRecord {
    id: string,
    run_id: RunId,
    reason: string,
    detail?: string,
    last_event_seq: number,
    ts: number,
    operator_ack_ts?: number,
}


/**
 * The current promoted commit plus its ScoreRecord.
 */
export interface Baseline {
    id: string,
    run_id: RunId,
    git_oid: string,
    score_record_id: ScoreRecordId,
    promoted_from_verdict_id?: VerdictId,
    promoted_ts: number,
    is_active: boolean,
}



export interface Worktree {
    id: string,
    cycle_id: CycleId,
    path: string,
    base_git_oid: string,
    head_git_oid?: string,
    created_ts: number,
    torn_down_ts?: number,
    lock_reason?: string,
}



export interface DivergenceIndicator {
    id: string,
    run_id: RunId,
    kind: string,
    cycle_window?: number,
    counter?: number,
    threshold: number,
    tripped?: boolean,
    last_observed_ts?: number,
}
