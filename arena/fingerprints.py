from __future__ import annotations

import hashlib
from collections.abc import Sequence

from arena.generated.models import Fingerprint

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_EMBEDDING_DIM = 384
DEFAULT_QUANTIZATION_BUCKETS = 256


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalized_path(path: str) -> str:
    return path.replace("\\", "/").strip().lstrip("/")


def quantized_intent_embedding(intent: str, *, embedding_model: str = DEFAULT_EMBEDDING_MODEL, dim: int = DEFAULT_EMBEDDING_DIM, buckets: int = DEFAULT_QUANTIZATION_BUCKETS) -> bytes:
    """Return a deterministic quantized pseudo-embedding for Phase 3 fingerprints.

    The live embedding model is integrated in a later phase. For now the pinned
    model name is included in the deterministic expansion so ledgers remain
    model-scoped and reproducible without downloads or API calls.
    """
    if buckets <= 0 or buckets > 256:
        raise ValueError("buckets must be in 1..256")
    seed = f"{embedding_model}\0{intent}".encode()
    output = bytearray()
    counter = 0
    while len(output) < dim:
        output.extend(hashlib.sha256(seed + counter.to_bytes(4, "big")).digest())
        counter += 1
    return bytes(value % buckets for value in output[:dim])


def sorted_target_files_hash(target_files: Sequence[str]) -> str:
    normalized = sorted(_normalized_path(path) for path in target_files)
    return _sha256_hex("\n".join(normalized).encode())


def ast_diff_pattern_hash(ast_diff_pattern: str) -> str:
    return _sha256_hex(ast_diff_pattern.encode())


def compute_fingerprint(
    *,
    intent: str,
    target_files: Sequence[str],
    technique_tag: str,
    ast_diff_pattern: str,
    first_seen_cycle_id: str,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Fingerprint:
    quantized = quantized_intent_embedding(intent, embedding_model=embedding_model)
    intent_sha = _sha256_hex(quantized)
    files_sha = sorted_target_files_hash(target_files)
    ast_sha = ast_diff_pattern_hash(ast_diff_pattern)

    digest = hashlib.blake2b(digest_size=16)
    digest.update(bytes.fromhex(intent_sha))
    digest.update(bytes.fromhex(files_sha))
    digest.update(technique_tag.encode())
    digest.update(bytes.fromhex(ast_sha))

    return Fingerprint(
        id=digest.hexdigest(),
        quantized_intent_embedding_sha=intent_sha,
        sorted_target_files_hash=files_sha,
        technique_tag=technique_tag,
        ast_diff_pattern_hash=ast_sha,
        embedding_model=embedding_model,
        first_seen_cycle_id=first_seen_cycle_id,
        failure_count=0,
        success_count=0,
    )
