from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from src.app.domain.aggregates.account_state import AccountState
from src.app.domain.aggregates.market_snapshot import MarketSnapshot
from src.app.domain.aggregates.trading_session import TradingSession
from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.entities.order_book_level import OrderBookLevel
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.ticker import Ticker
from src.app.domain.value_objects.timestamp import Timestamp


def _ts_now() -> Timestamp:
    return Timestamp(datetime.now(UTC))


def build_account_state(
    *, symbol: Symbol, account: Account, open_orders: Iterable[Order] = ()
) -> AccountState:
    state = AccountState(symbol=symbol, account=account, updated_at=_ts_now())
    for order in open_orders:
        state.record_order(order)
    return state


def build_trading_session(
    *, symbol: Symbol, orders: Iterable[Order] = (), trades: Iterable[Trade] = ()
) -> TradingSession:
    now = _ts_now()
    session = TradingSession(symbol=symbol, started_at=now, last_activity_at=now)
    for order in orders:
        if order.status.value in {"NEW", "PARTIALLY_FILLED"}:
            session.add_order(order)
    for trade in trades:
        session.record_trade(trade)
    session.pop_events()  # discard reconstitution events
    return session


def build_market_snapshot(
    *,
    symbol: Symbol,
    bids: Iterable[OrderBookLevel] = (),
    asks: Iterable[OrderBookLevel] = (),
    trades: Iterable[Trade] = (),
    ticker: Ticker | None = None,
) -> MarketSnapshot:
    snapshot = MarketSnapshot(symbol=symbol, updated_at=_ts_now())
    snapshot.update_depth(list(bids), list(asks))
    for trade in trades:
        snapshot.add_trade(trade)
    if ticker is not None:
        snapshot.update_ticker(ticker)
    return snapshot
