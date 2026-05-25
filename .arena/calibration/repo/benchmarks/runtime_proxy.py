from __future__ import annotations

import json

from validatorlib.core import benchmark_units


print(json.dumps({"runtime_p95_ms": benchmark_units() / 1000.0}))
