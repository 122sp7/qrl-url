from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from src.app.domain.entities.order import Order
from src.app.domain.entities.trade import Trade
from src.app.domain.events.order_event import OrderEvent
from src.app.domain.value_objects.order_status import OrderStatus
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp


_OPEN_STATUSES = frozenset({"NEW", "PARTIALLY_FILLED"})


@dataclass
class TradingSession:
    """Session-level aggregate for managing open and historical activity."""

    symbol: Symbol
    open_orders: list[Order] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)
    started_at: Timestamp | None = None
    last_activity_at: Timestamp | None = None
    _domain_events: list = field(default_factory=list, init=False, repr=False, compare=False)

    def add_order(self, order: Order) -> None:
        """Register an open order, enforcing symbol and status invariants."""
        if order.symbol != self.symbol:
            raise ValueError(
                f"Order symbol {order.symbol} does not match session {self.symbol}"
            )
        if order.status.value not in _OPEN_STATUSES:
            raise ValueError(
                f"Only NEW/PARTIALLY_FILLED orders belong in TradingSession; got {order.status.value}"
            )
        if any(o.order_id == order.order_id for o in self.open_orders):
            raise ValueError(f"Duplicate order_id {order.order_id.value} in TradingSession")
        self.open_orders.append(order)
        price_value = order.price.value if order.price else Decimal("0")
        self._domain_events.append(
            OrderEvent(
                order_id=order.order_id,
                symbol=order.symbol,
                price=Price.from_single(price_value),
                quantity=order.quantity,
                status=order.status,
                timestamp=int(order.created_at.value.timestamp() * 1000),
            )
        )

    def record_trade(self, trade: Trade) -> None:
        """Record a completed trade and update activity timestamp."""
        from datetime import UTC, datetime

        self.trades.append(trade)
        self.last_activity_at = Timestamp(datetime.now(UTC))

    def close_order(self, order_id_value: str, new_status: OrderStatus) -> None:
        """Transition an open order to a terminal status and remove it from the open list."""
        for order in self.open_orders:
            if order.order_id.value == order_id_value:
                order.status = new_status
                self.open_orders.remove(order)
                return
        raise ValueError(f"Order {order_id_value} not found in open orders")

    def pop_events(self) -> list:
        """Return and clear all pending domain events."""
        events, self._domain_events = self._domain_events, []
        return events

