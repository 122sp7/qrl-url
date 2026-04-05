from __future__ import annotations

from dataclasses import dataclass, field

from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp


_OPEN_STATUSES = frozenset({"NEW", "PARTIALLY_FILLED"})


@dataclass
class AccountState:
    """Aggregate for account balances and outstanding orders."""

    symbol: Symbol
    account: Account
    open_orders: list[Order] = field(default_factory=list)
    updated_at: Timestamp | None = None
    _domain_events: list = field(default_factory=list, init=False, repr=False, compare=False)

    def record_order(self, order: Order) -> None:
        """Track an open order for this account state."""
        if order.status.value not in _OPEN_STATUSES:
            return
        if any(o.order_id == order.order_id for o in self.open_orders):
            return
        self.open_orders.append(order)

    def refresh(self, account: Account) -> None:
        """Replace the underlying account snapshot."""
        from datetime import UTC, datetime

        self.account = account
        self.updated_at = Timestamp(datetime.now(UTC))

    def pop_events(self) -> list:
        """Return and clear all pending domain events."""
        events, self._domain_events = self._domain_events, []
        return events

