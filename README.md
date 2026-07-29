# inversion

A population-scale agent-based model in which agents develop commitments that can, under discoverable conditions, outrank their own survival. The product is the phase diagram: which parameter regions produce preference inversion and which do not.

Inversion is never scripted. Survival is the base attractor; drives respond to body state through one uniform lagged update law, and inversion, when it occurs, is a timing failure. See `CLAUDE.md` for the binding constitution and `docs/BUILD_BRIEF.md` for orientation.

## Layout

- `core/`: the model kernel. Drive state is mutated only in `core/drives.py`.
- `specs/`: one spec per phase, with acceptance criteria, written before code.
- `tests/`: invariant tests (static analysis), determinism tests, golden runs.
- `results/`: committed validation artifacts, one per phase gate.
- `docs/`: build brief and project notes.

## Run tests

```
uv sync
uv run pytest
```

## Licensing

Two licenses, by content type:

- Code (`core/`, `scripts/`, `tests/`, `conftest.py`) is licensed under the Apache License 2.0. See `LICENSE`.
- Specs, documentation, and results data (`specs/`, `docs/`, `results/`, `CLAUDE.md`, this file) are licensed under Creative Commons Attribution 4.0 International. See `LICENSE-CC-BY-4.0`.

If you rerun a protocol or reuse the data, cite the repository; `CITATION.cff` carries the reference. Every registered protocol in `specs/` names its rerun command and its committed artifact so replication needs nothing beyond this repository.
