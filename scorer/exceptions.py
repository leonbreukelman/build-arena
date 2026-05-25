class ScorerError(RuntimeError):
    """Base scorer error."""


class ScorerLockMismatchError(ScorerError):
    """Raised when scorer source does not match the pinned lock hash."""


class ScorerNonDeterministicError(ScorerError):
    """Raised when re-scoring the same git OID drifts beyond tolerance."""
