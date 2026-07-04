# Dream Lane Known Issues

- 2026-07-04 handoff: `graphStructural.high_fan_in` currently counts incoming edges of all graph kinds (`defined_in`, `imports`, `calls`, `tests`, etc.), so the signal is semantically mushy; recorded only, no code change in the cycle-anchor/provenance slice.
