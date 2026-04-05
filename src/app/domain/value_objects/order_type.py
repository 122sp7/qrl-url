from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class OrderType:
    """Supported MEXC order types."""

    value: str

    _allowed: ClassVar[set[str]] = {"LIMIT", "MARKET"}

    def __post_init__(self):
        if self.value not in self._allowed:
            raise ValueError(f"OrderType must be one of {sorted(self._allowed)}")
