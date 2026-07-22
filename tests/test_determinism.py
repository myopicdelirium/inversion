"""Determinism harness tests (CLAUDE.md hard rules).

Half of these run the RNG harness; the other half statically forbid any
other source of randomness inside core/.
"""

import ast
import pathlib

import numpy as np

from core.config import Config
from core.rng import spawn_streams

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "core"

# The only np.random attributes the model may touch: seeding machinery
# and explicit generators. Module-level draw functions are forbidden.
ALLOWED_NP_RANDOM = {"SeedSequence", "Generator", "PCG64", "default_rng"}


def test_same_seed_same_draws():
    world_a, agents_a = spawn_streams(42, 4)
    world_b, agents_b = spawn_streams(42, 4)
    assert np.array_equal(world_a.random(32), world_b.random(32))
    for ga, gb in zip(agents_a, agents_b):
        assert np.array_equal(ga.random(32), gb.random(32))


def test_different_seed_different_draws():
    world_a, _ = spawn_streams(42, 4)
    world_b, _ = spawn_streams(43, 4)
    assert not np.array_equal(world_a.random(32), world_b.random(32))


def test_spawn_stability():
    # Adding agent n+1 must not shift the draws of the world stream or
    # of agents 1..n. This is the SeedSequence.spawn guarantee the
    # constitution depends on.
    world_5, agents_5 = spawn_streams(123, 5)
    world_8, agents_8 = spawn_streams(123, 8)
    assert np.array_equal(world_5.random(32), world_8.random(32))
    for g5, g8 in zip(agents_5, agents_8):
        assert np.array_equal(g5.random(32), g8.random(32))


def test_config_hash_stable_and_sensitive():
    assert Config().config_hash() == Config().config_hash()
    assert Config(n_agents=201).config_hash() != Config().config_hash()


def test_no_global_randomness_in_core():
    """No `import random`, and no np.random.<draw function> anywhere in
    core/. The one RNG is owned by the model and passed explicitly."""
    for path in sorted(CORE.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "random", (
                        f"{path.name}:{node.lineno}: stdlib random is forbidden"
                    )
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "random", (
                    f"{path.name}:{node.lineno}: stdlib random is forbidden"
                )
            elif isinstance(node, ast.Attribute):
                # Matches <anything>.random.<attr>, which catches both
                # np.random.X and numpy.random.X.
                inner = node.value
                if isinstance(inner, ast.Attribute) and inner.attr == "random":
                    assert node.attr in ALLOWED_NP_RANDOM, (
                        f"{path.name}:{node.lineno}: np.random.{node.attr} is "
                        f"forbidden; use an explicit Generator from core/rng.py"
                    )
