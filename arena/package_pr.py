from __future__ import annotations

import sys


def main() -> int:
    print(
        "arena.package_pr is retired: Build Arena emits improvement signals as GitHub issues only. "
        "Use `python -m arena.package_issue` for dry-run issue body rendering or explicitly gated issue creation.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
