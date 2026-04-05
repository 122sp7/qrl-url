from __future__ import annotations

from dataclasses import dataclass, field

from src.app.domain.entities.order_book_level import OrderBookLevel
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.ticker import Ticker
from src.app.domain.value_objects.timestamp import Timestamp


@dataclass
class MarketSnapshot:
    """Combined market view for depth, trades, and ticker."""

    symbol: Symbol
    bids: list[OrderBookLevel] = field(default_factory=list)
    asks: list[OrderBookLevel] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)
    ticker: Ticker | None = None
    updated_at: Timestamp | None = None
    _domain_events: list = field(default_factory=list, init=False, repr=False, compare=False)

    def update_depth(
        self,
        bids: list[OrderBookLevel],
        asks: list[OrderBookLevel],
    ) -> None:
        """Replace depth levels and mark snapshot as updated."""
        from datetime import UTC, datetime

        self.bids = bids
        self.asks = asks
        self.updated_at = Timestamp(datetime.now(UTC))

    def update_ticker(self, ticker: Ticker) -> None:
        """Replace the ticker snapshot."""
        from datetime import UTC, datetime

        self.ticker = ticker
        self.updated_at = Timestamp(datetime.now(UTC))

    def add_trade(self, trade: Trade) -> None:
        """Append a new public trade tick."""
        self.trades.append(trade)

    def pop_events(self) -> list:
        """Return and clear all pending domain events."""
        events, self._domain_events = self._domain_events, []
        return events

