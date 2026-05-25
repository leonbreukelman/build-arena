from __future__ import annotations

import sys
from pathlib import Path

import tomli_w

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    from scorer.lock import DEFAULT_LOCK_PATH, compute_scorer_tree_sha, default_locked_files

    locked_files = default_locked_files(PROJECT_ROOT)
    scorer_sha = compute_scorer_tree_sha(PROJECT_ROOT, locked_files)
    lock_path = PROJECT_ROOT / DEFAULT_LOCK_PATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        tomli_w.dumps(
            {
                "version": 1,
                "scorer_sha": scorer_sha,
                "locked_files": list(locked_files),
            }
        )
    )
    print(f"updated {lock_path.relative_to(PROJECT_ROOT)} {scorer_sha}")


if __name__ == "__main__":
    main()
