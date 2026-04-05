from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class Timestamp:
    """UTC timestamp wrapper."""

    value: datetime

    def __post_init__(self):
        if self.value.tzinfo is None:
            object.__setattr__(self, "value", self.value.replace(tzinfo=UTC))
