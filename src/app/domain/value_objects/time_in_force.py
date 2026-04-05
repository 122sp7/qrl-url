from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class TimeInForce:
    """Time in force constraints for limit orders."""

    value: str

    _allowed: ClassVar[set[str]] = {"GTC", "IOC", "FOK"}

    def __post_init__(self):
        if self.value not in self._allowed:
            raise ValueError(f"TimeInForce must be one of {sorted(self._allowed)}")
