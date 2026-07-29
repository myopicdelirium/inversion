"""RNG harness. One master seed; stream 0 belongs to the world, streams
1..n to agents. Nothing in the model may touch any other source of
randomness (enforced by tests/test_determinism.py).
"""

import numpy as np


def spawn_streams(
    master_seed: int, n_agents: int
) -> tuple[np.random.Generator, list[np.random.Generator]]:
    """Return (world_stream, [agent_streams]).

    Per-agent streams come from SeedSequence.spawn, so adding agent n+1
    never shifts the draws of agents 1..n.
    """
    children = np.random.SeedSequence(master_seed).spawn(n_agents + 1)
    generators = [np.random.Generator(np.random.PCG64(c)) for c in children]
    return generators[0], generators[1:]


def spawn_birth_streams(master_seed: int, n_agents: int) -> list:
    """One dedicated stream per slot for rebirth draws (Amendment 10).
    Spawned from children n_agents+1.. of the same SeedSequence, so
    the world and agent streams are untouched, and consumed only when
    the slot is reborn: behavior-dependent consumption of a dedicated
    stream replays exactly."""
    children = np.random.SeedSequence(master_seed).spawn(2 * n_agents + 1)
    return [np.random.Generator(np.random.PCG64(c))
            for c in children[n_agents + 1:]]
