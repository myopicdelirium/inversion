"""Determinism canary: characterize the per-process trajectory
flakiness observed 2026-07-24 on the sight-on code path.

Runs the same short configuration in many fresh subprocesses and
counts distinct golden hashes. A healthy machine reports 1 distinct
hash per configuration. Compares sight-on vs sight-off, and with vs
without numpy's advanced CPU dispatch (NPY_DISABLE_CPU_FEATURES), to
localize the source.

Run:  uv run python scripts/determinism_canary.py [n_procs]
"""

import os
import pathlib
import subprocess
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]

CHILD = '''
import sys
sys.path.insert(0, {root!r})
from dataclasses import replace
from core.config import Config
from core.model import run, golden_hash
cfg = replace(Config(), bond_target="partner", n_agents=200, n_hazard=0,
              storm_nest=0, storm_onset=300, storm_ramp=1,
              storm_snare=0.95, storm_damage=0.01, tau_safety=48.0,
              prospect_horizon=60, prospect_sees_grip={sees},
              record_every=10)
print(golden_hash(run(cfg, seed=7, ticks=900)))
'''


def trial(sees, n_procs, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    hashes = []
    for _ in range(n_procs):
        r = subprocess.run(
            [sys.executable, "-c", CHILD.format(root=str(ROOT), sees=sees)],
            capture_output=True, text=True, env=env, cwd=str(ROOT))
        if r.returncode != 0:
            hashes.append("ERROR:" + r.stderr.strip()[-80:])
        else:
            hashes.append(r.stdout.strip())
    counts = Counter(hashes)
    return counts


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    for label, sees, env in [
        ("sight OFF, default dispatch", "False", None),
        ("sight ON,  default dispatch", "True", None),
        ("sight ON,  SIMD dispatch pinned to baseline", "True",
         {"NPY_DISABLE_CPU_FEATURES": "ASIMDHP ASIMDDP ASIMDFHM SVE"}),
    ]:
        counts = trial(sees, n, env)
        distinct = len(counts)
        print(f"{label}: {distinct} distinct hash(es) over {n} processes")
        for h, c in counts.most_common():
            print(f"    {c:>3}x {h[:20]}")


if __name__ == "__main__":
    main()
