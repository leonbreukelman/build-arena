-- # Class: Run
--     * Slot: id
--     * Slot: north_star_id
--     * Slot: scorer_lock_sha
--     * Slot: config_sha
--     * Slot: git_head_at_start
--     * Slot: started_ts
--     * Slot: ended_ts
--     * Slot: halt_record_id
--     * Slot: cycles_total
--     * Slot: promotions_total
-- # Class: NorthStar Description: Operator-provided objective; immutable for the life of a Run.
--     * Slot: id
--     * Slot: description
--     * Slot: created_ts
-- # Class: Cycle
--     * Slot: id
--     * Slot: run_id
--     * Slot: ordinal
--     * Slot: entered_state
--     * Slot: started_ts
--     * Slot: ended_ts
--     * Slot: bandit_arm
--     * Slot: hypothesis_id
--     * Slot: verdict_id
--     * Slot: worktree_id
--     * Slot: baseline_id_before
--     * Slot: baseline_id_after
--     * Slot: runner_used
-- # Class: Hypothesis
--     * Slot: id
--     * Slot: cycle_id
--     * Slot: intent
--     * Slot: technique_tag
--     * Slot: target_cluster
--     * Slot: fingerprint_id
--     * Slot: reasoning_blob_sha
--     * Slot: patch_blob_sha
--     * Slot: proposed_ts
-- # Class: Fingerprint Description: blake2b digest over intent embedding, target files, technique tag, and AST diff pattern.
--     * Slot: id
--     * Slot: quantized_intent_embedding_sha
--     * Slot: sorted_target_files_hash
--     * Slot: technique_tag
--     * Slot: ast_diff_pattern_hash
--     * Slot: embedding_model
--     * Slot: first_seen_cycle_id
--     * Slot: failure_count
--     * Slot: success_count
-- # Class: Verdict
--     * Slot: id
--     * Slot: hypothesis_id
--     * Slot: outcome
--     * Slot: reject_reason
--     * Slot: score_delta
--     * Slot: score_before_id
--     * Slot: score_after_id
--     * Slot: tests_passed
--     * Slot: ablation_result_id
--     * Slot: decided_ts
-- # Class: ScoreRecord
--     * Slot: id
--     * Slot: cycle_id
--     * Slot: git_oid
--     * Slot: scorer_lock_sha
--     * Slot: vector_json_sha
--     * Slot: composite
--     * Slot: computed_ts
-- # Class: AblationResult
--     * Slot: id
--     * Slot: verdict_id
--     * Slot: probes_changed_output
--     * Slot: quorum_threshold
--     * Slot: load_bearing
--     * Slot: runner_used
-- # Class: Event Description: Append-only JSONL record. SQLite is a projection of these.
--     * Slot: id
--     * Slot: run_id
--     * Slot: cycle_id
--     * Slot: seq
--     * Slot: ts
--     * Slot: type
--     * Slot: level
--     * Slot: payload_json_sha
--     * Slot: payload_inline
-- # Class: Budget
--     * Slot: id
--     * Slot: run_id
--     * Slot: wall_clock_seconds_cap
--     * Slot: cycle_count_cap
--     * Slot: claude_code_credits_cap
--     * Slot: codex_credits_cap
--     * Slot: copilot_premium_cap
--     * Slot: ollama_unbounded
--     * Slot: wall_clock_seconds_used
--     * Slot: cycle_count_used
--     * Slot: claude_code_credits_used
--     * Slot: codex_credits_used
--     * Slot: copilot_premium_used
-- # Class: HaltRecord
--     * Slot: id
--     * Slot: run_id
--     * Slot: reason
--     * Slot: detail
--     * Slot: last_event_seq
--     * Slot: ts
--     * Slot: operator_ack_ts
-- # Class: Baseline Description: The current promoted commit plus its ScoreRecord.
--     * Slot: id
--     * Slot: run_id
--     * Slot: git_oid
--     * Slot: score_record_id
--     * Slot: promoted_from_verdict_id
--     * Slot: promoted_ts
--     * Slot: is_active
-- # Class: Worktree
--     * Slot: id
--     * Slot: cycle_id
--     * Slot: path
--     * Slot: base_git_oid
--     * Slot: head_git_oid
--     * Slot: created_ts
--     * Slot: torn_down_ts
--     * Slot: lock_reason
-- # Class: DivergenceIndicator
--     * Slot: id
--     * Slot: run_id
--     * Slot: kind
--     * Slot: cycle_window
--     * Slot: counter
--     * Slot: threshold
--     * Slot: tripped
--     * Slot: last_observed_ts
-- # Class: NorthStar_score_axes
--     * Slot: NorthStar_id Description: Autocreated FK slot
--     * Slot: score_axes
-- # Class: NorthStar_pinned_axes
--     * Slot: NorthStar_id Description: Autocreated FK slot
--     * Slot: pinned_axes
-- # Class: Hypothesis_target_files
--     * Slot: Hypothesis_id Description: Autocreated FK slot
--     * Slot: target_files
-- # Class: Verdict_pinned_regression
--     * Slot: Verdict_id Description: Autocreated FK slot
--     * Slot: pinned_regression
-- # Class: AblationResult_probe_set
--     * Slot: AblationResult_id Description: Autocreated FK slot
--     * Slot: probe_set

CREATE TABLE "Run" (
	id TEXT NOT NULL,
	north_star_id TEXT NOT NULL,
	scorer_lock_sha TEXT NOT NULL,
	config_sha TEXT NOT NULL,
	git_head_at_start TEXT NOT NULL,
	started_ts FLOAT NOT NULL,
	ended_ts FLOAT,
	halt_record_id TEXT,
	cycles_total INTEGER,
	promotions_total INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(north_star_id) REFERENCES "NorthStar" (id),
	FOREIGN KEY(halt_record_id) REFERENCES "HaltRecord" (id)
);
CREATE INDEX "ix_Run_id" ON "Run" (id);

CREATE TABLE "NorthStar" (
	id TEXT NOT NULL,
	description TEXT NOT NULL,
	created_ts FLOAT NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_NorthStar_id" ON "NorthStar" (id);

CREATE TABLE "Cycle" (
	id TEXT NOT NULL,
	run_id TEXT NOT NULL,
	ordinal INTEGER NOT NULL,
	entered_state VARCHAR(11) NOT NULL,
	started_ts FLOAT NOT NULL,
	ended_ts FLOAT,
	bandit_arm TEXT,
	hypothesis_id TEXT,
	verdict_id TEXT,
	worktree_id TEXT,
	baseline_id_before TEXT,
	baseline_id_after TEXT,
	runner_used VARCHAR(11),
	PRIMARY KEY (id),
	FOREIGN KEY(run_id) REFERENCES "Run" (id),
	FOREIGN KEY(hypothesis_id) REFERENCES "Hypothesis" (id),
	FOREIGN KEY(verdict_id) REFERENCES "Verdict" (id),
	FOREIGN KEY(worktree_id) REFERENCES "Worktree" (id),
	FOREIGN KEY(baseline_id_before) REFERENCES "Baseline" (id),
	FOREIGN KEY(baseline_id_after) REFERENCES "Baseline" (id)
);
CREATE INDEX "ix_Cycle_id" ON "Cycle" (id);

CREATE TABLE "Hypothesis" (
	id TEXT NOT NULL,
	cycle_id TEXT NOT NULL,
	intent TEXT NOT NULL,
	technique_tag TEXT NOT NULL,
	target_cluster TEXT NOT NULL,
	fingerprint_id TEXT NOT NULL,
	reasoning_blob_sha TEXT,
	patch_blob_sha TEXT,
	proposed_ts FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(cycle_id) REFERENCES "Cycle" (id),
	FOREIGN KEY(fingerprint_id) REFERENCES "Fingerprint" (id)
);
CREATE INDEX "ix_Hypothesis_id" ON "Hypothesis" (id);

CREATE TABLE "Fingerprint" (
	id TEXT NOT NULL,
	quantized_intent_embedding_sha TEXT NOT NULL,
	sorted_target_files_hash TEXT NOT NULL,
	technique_tag TEXT NOT NULL,
	ast_diff_pattern_hash TEXT NOT NULL,
	embedding_model TEXT NOT NULL,
	first_seen_cycle_id TEXT NOT NULL,
	failure_count INTEGER,
	success_count INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(first_seen_cycle_id) REFERENCES "Cycle" (id)
);
CREATE INDEX "ix_Fingerprint_id" ON "Fingerprint" (id);

CREATE TABLE "Verdict" (
	id TEXT NOT NULL,
	hypothesis_id TEXT NOT NULL,
	outcome VARCHAR(9) NOT NULL,
	reject_reason VARCHAR(35),
	score_delta FLOAT,
	score_before_id TEXT NOT NULL,
	score_after_id TEXT,
	tests_passed BOOLEAN,
	ablation_result_id TEXT,
	decided_ts FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(hypothesis_id) REFERENCES "Hypothesis" (id),
	FOREIGN KEY(score_before_id) REFERENCES "ScoreRecord" (id),
	FOREIGN KEY(score_after_id) REFERENCES "ScoreRecord" (id),
	FOREIGN KEY(ablation_result_id) REFERENCES "AblationResult" (id)
);
CREATE INDEX "ix_Verdict_id" ON "Verdict" (id);

CREATE TABLE "ScoreRecord" (
	id TEXT NOT NULL,
	cycle_id TEXT NOT NULL,
	git_oid TEXT NOT NULL,
	scorer_lock_sha TEXT NOT NULL,
	vector_json_sha TEXT NOT NULL,
	composite FLOAT NOT NULL,
	computed_ts FLOAT NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(cycle_id) REFERENCES "Cycle" (id)
);
CREATE INDEX "ix_ScoreRecord_id" ON "ScoreRecord" (id);

CREATE TABLE "AblationResult" (
	id TEXT NOT NULL,
	verdict_id TEXT NOT NULL,
	probes_changed_output INTEGER NOT NULL,
	quorum_threshold INTEGER NOT NULL,
	load_bearing BOOLEAN NOT NULL,
	runner_used VARCHAR(11) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(verdict_id) REFERENCES "Verdict" (id)
);
CREATE INDEX "ix_AblationResult_id" ON "AblationResult" (id);

CREATE TABLE "HaltRecord" (
	id TEXT NOT NULL,
	run_id TEXT NOT NULL,
	reason VARCHAR(32) NOT NULL,
	detail TEXT,
	last_event_seq INTEGER NOT NULL,
	ts FLOAT NOT NULL,
	operator_ack_ts FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY(run_id) REFERENCES "Run" (id)
);
CREATE INDEX "ix_HaltRecord_id" ON "HaltRecord" (id);

CREATE TABLE "Baseline" (
	id TEXT NOT NULL,
	run_id TEXT NOT NULL,
	git_oid TEXT NOT NULL,
	score_record_id TEXT NOT NULL,
	promoted_from_verdict_id TEXT,
	promoted_ts FLOAT NOT NULL,
	is_active BOOLEAN NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(run_id) REFERENCES "Run" (id),
	FOREIGN KEY(score_record_id) REFERENCES "ScoreRecord" (id),
	FOREIGN KEY(promoted_from_verdict_id) REFERENCES "Verdict" (id)
);
CREATE INDEX "ix_Baseline_id" ON "Baseline" (id);

CREATE TABLE "Worktree" (
	id TEXT NOT NULL,
	cycle_id TEXT NOT NULL,
	path TEXT NOT NULL,
	base_git_oid TEXT NOT NULL,
	head_git_oid TEXT,
	created_ts FLOAT NOT NULL,
	torn_down_ts FLOAT,
	lock_reason TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(cycle_id) REFERENCES "Cycle" (id)
);
CREATE INDEX "ix_Worktree_id" ON "Worktree" (id);

CREATE TABLE "Event" (
	id TEXT NOT NULL,
	run_id TEXT NOT NULL,
	cycle_id TEXT,
	seq INTEGER NOT NULL,
	ts FLOAT NOT NULL,
	type TEXT NOT NULL,
	level TEXT,
	payload_json_sha TEXT,
	payload_inline TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY(run_id) REFERENCES "Run" (id),
	FOREIGN KEY(cycle_id) REFERENCES "Cycle" (id)
);
CREATE INDEX "ix_Event_id" ON "Event" (id);

CREATE TABLE "Budget" (
	id TEXT NOT NULL,
	run_id TEXT NOT NULL,
	wall_clock_seconds_cap INTEGER NOT NULL,
	cycle_count_cap INTEGER NOT NULL,
	claude_code_credits_cap INTEGER,
	codex_credits_cap INTEGER,
	copilot_premium_cap INTEGER,
	ollama_unbounded BOOLEAN,
	wall_clock_seconds_used INTEGER,
	cycle_count_used INTEGER,
	claude_code_credits_used INTEGER,
	codex_credits_used INTEGER,
	copilot_premium_used INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(run_id) REFERENCES "Run" (id)
);
CREATE INDEX "ix_Budget_id" ON "Budget" (id);

CREATE TABLE "DivergenceIndicator" (
	id TEXT NOT NULL,
	run_id TEXT NOT NULL,
	kind VARCHAR(32) NOT NULL,
	cycle_window INTEGER,
	counter INTEGER,
	threshold INTEGER NOT NULL,
	tripped BOOLEAN,
	last_observed_ts FLOAT,
	PRIMARY KEY (id),
	FOREIGN KEY(run_id) REFERENCES "Run" (id)
);
CREATE INDEX "ix_DivergenceIndicator_id" ON "DivergenceIndicator" (id);

CREATE TABLE "NorthStar_score_axes" (
	"NorthStar_id" TEXT,
	score_axes TEXT NOT NULL,
	PRIMARY KEY ("NorthStar_id", score_axes),
	FOREIGN KEY("NorthStar_id") REFERENCES "NorthStar" (id)
);
CREATE INDEX "ix_NorthStar_score_axes_NorthStar_id" ON "NorthStar_score_axes" ("NorthStar_id");
CREATE INDEX "ix_NorthStar_score_axes_score_axes" ON "NorthStar_score_axes" (score_axes);

CREATE TABLE "NorthStar_pinned_axes" (
	"NorthStar_id" TEXT,
	pinned_axes TEXT,
	PRIMARY KEY ("NorthStar_id", pinned_axes),
	FOREIGN KEY("NorthStar_id") REFERENCES "NorthStar" (id)
);
CREATE INDEX "ix_NorthStar_pinned_axes_NorthStar_id" ON "NorthStar_pinned_axes" ("NorthStar_id");
CREATE INDEX "ix_NorthStar_pinned_axes_pinned_axes" ON "NorthStar_pinned_axes" (pinned_axes);

CREATE TABLE "Hypothesis_target_files" (
	"Hypothesis_id" TEXT,
	target_files TEXT NOT NULL,
	PRIMARY KEY ("Hypothesis_id", target_files),
	FOREIGN KEY("Hypothesis_id") REFERENCES "Hypothesis" (id)
);
CREATE INDEX "ix_Hypothesis_target_files_Hypothesis_id" ON "Hypothesis_target_files" ("Hypothesis_id");
CREATE INDEX "ix_Hypothesis_target_files_target_files" ON "Hypothesis_target_files" (target_files);

CREATE TABLE "Verdict_pinned_regression" (
	"Verdict_id" TEXT,
	pinned_regression TEXT,
	PRIMARY KEY ("Verdict_id", pinned_regression),
	FOREIGN KEY("Verdict_id") REFERENCES "Verdict" (id)
);
CREATE INDEX "ix_Verdict_pinned_regression_Verdict_id" ON "Verdict_pinned_regression" ("Verdict_id");
CREATE INDEX "ix_Verdict_pinned_regression_pinned_regression" ON "Verdict_pinned_regression" (pinned_regression);

CREATE TABLE "AblationResult_probe_set" (
	"AblationResult_id" TEXT,
	probe_set VARCHAR(15) NOT NULL,
	PRIMARY KEY ("AblationResult_id", probe_set),
	FOREIGN KEY("AblationResult_id") REFERENCES "AblationResult" (id)
);
CREATE INDEX "ix_AblationResult_probe_set_AblationResult_id" ON "AblationResult_probe_set" ("AblationResult_id");
CREATE INDEX "ix_AblationResult_probe_set_probe_set" ON "AblationResult_probe_set" (probe_set);
