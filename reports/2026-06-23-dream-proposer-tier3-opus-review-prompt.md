You are an independent reviewer for Build Arena. Review the attached packet for the tier-3 advisory dream proposer implementation.

Primary job: break the safety property, not style nitpick. Look for a way this implementation could emit dream.md from fabricated/unresolved premises, launder a dream into proposal.md, bypass the capability-map review gate, or let live generation/research run without explicit model/key preflight.

Scope: only files listed in the packet. The working tree is dirty with unrelated prior files; ignore anything not listed unless it directly invalidates the dream lane. Do not request tools; the packet is self-contained.

Return JSON only with this shape:
{
  "verdict": "ACCEPT" | "ACCEPT_WITH_CHANGES" | "REJECT",
  "summary": "short",
  "blockers": ["..."],
  "requiredChanges": ["..."],
  "advisoryFindings": ["..."],
  "acceptanceAssessment": {
    "premiseGateKillPath": "pass|fail|unclear",
    "emitDeterminismAndNoTrustLeak": "pass|fail|unclear",
    "reviewGate": "pass|fail|unclear",
    "laneSeparation": "pass|fail|unclear",
    "offlineTests": "pass|fail|unclear"
  }
}

Packet path for the command wrapper to read: reports/2026-06-23-dream-proposer-tier3-review-packet.md
