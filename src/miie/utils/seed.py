"""SeedManager utility for deterministic reproducibility across MIIE components."""

import hashlib
import random
import numpy as np


class SeedManager:
    """Centralized seed management for bitwise-identical reproducibility.

    Provides a single source of randomness for any component that needs
    deterministic sequences.  Uses numpy.random.default_rng (the modern,
    recommended API) instead of the deprecated np.random.seed / global state.

    Attributes:
        seed: The integer seed used for all RNG state.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._rng = np.random.default_rng(seed)
        random.seed(seed)

    @property
    def rng(self) -> np.random.Generator:
        """Return the numpy Generator instance."""
        return self._rng

    def numpy_rng(self) -> np.random.Generator:
        """Return the numpy Generator instance (alias for rng)."""
        return self._rng

    def random_seed(self) -> int:
        """Return the integer seed."""
        return self.seed

    def compute_hash(self, data: str) -> str:
        """Compute a SHA-256 hex-digest of *data*."""
        return hashlib.sha256(data.encode()).hexdigest()
