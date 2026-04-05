from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class OrderStatus:
    """Order status with a minimal allowed set."""

    value: str

    _allowed: ClassVar[set[str]] = {
        "NEW",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELED",
        "REJECTED",
    }

    def __post_init__(self):
        if self.value not in self._allowed:
            raise ValueError(f"OrderStatus must be one of {sorted(self._allowed)}")
