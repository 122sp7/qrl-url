"""Write-through cached wrapper around MexcExchangeService."""

import json
from decimal import Decimal

from src.app.application.ports.exchange_service import (
    CancelOrderRequest,
    ExchangeService,
    GetOrderRequest,
    PlaceOrderRequest,
)
from src.app.domain.entities.account import Account
from src.app.domain.entities.order import Order
from src.app.domain.entities.trade import Trade
from src.app.domain.value_objects.order_book import OrderBook
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.symbol import Symbol
from src.app.domain.value_objects.timestamp import Timestamp
from src.app.infrastructure.exchange.mexc.service import MexcExchangeService
from src.app.infrastructure.external.redis_client import RedisClient


class CachedMexcExchangeService(ExchangeService):
    """MexcExchangeService with Redis write-through cache for public market data."""

    _TTL_PRICE = 8
    _TTL_DEPTH = 8
    _TTL_KLINE = 30
    _TTL_MARKET_TRADES = 8

    def __init__(self, inner: MexcExchangeService, redis: RedisClient):
        self._inner = inner
        self._redis = redis

    async def __aenter__(self) -> "CachedMexcExchangeService":
        await self._inner.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._inner.__aexit__(exc_type, exc, tb)

    # ------------------------------------------------------------------
    # Passthrough — no caching
    # ------------------------------------------------------------------

    async def get_server_time(self) -> Timestamp:
        return await self._inner.get_server_time()

    async def get_account(self) -> Account:
        return await self._inner.get_account()

    async def place_order(self, request: PlaceOrderRequest) -> Order:
        return await self._inner.place_order(request)

    async def cancel_order(self, request: CancelOrderRequest) -> Order:
        return await self._inner.cancel_order(request)

    async def get_order(self, request: GetOrderRequest) -> Order:
        return await self._inner.get_order(request)

    async def list_open_orders(self, symbol: Symbol | None = None) -> list[Order]:
        return await self._inner.list_open_orders(symbol)

    async def list_trades(self, symbol: Symbol) -> list[Trade]:
        return await self._inner.list_trades(symbol)

    async def get_ticker_24h(self, symbol: Symbol) -> dict:
        return await self._inner.get_ticker_24h(symbol)

    # ------------------------------------------------------------------
    # Write-through cached
    # ------------------------------------------------------------------

    async def get_price(self, symbol: Symbol) -> Price:
        result = await self._inner.get_price(symbol)
        await self._redis.set_json(
            f"price:{symbol.value}",
            {"bid": str(result.bid), "ask": str(result.ask)},
            self._TTL_PRICE,
        )
        return result

    async def get_depth(self, symbol: Symbol, limit: int = 50) -> OrderBook:
        result = await self._inner.get_depth(symbol, limit)
        await self._redis.set_json(
            f"depth:{symbol.value}",
            {
                "bids": [{"price": str(lvl.price), "quantity": str(lvl.quantity)} for lvl in result.bids],
                "asks": [{"price": str(lvl.price), "quantity": str(lvl.quantity)} for lvl in result.asks],
            },
            self._TTL_DEPTH,
        )
        return result

    async def get_kline(self, symbol: Symbol, interval: str, limit: int = 100):
        result = await self._inner.get_kline(symbol, interval, limit)
        await self._redis.set_json(
            f"kline:{symbol.value}:{interval}",
            result,
            self._TTL_KLINE,
        )
        return result

    async def get_market_trades(self, symbol: Symbol, limit: int = 50) -> list[dict]:
        result = await self._inner.get_market_trades(symbol, limit)
        await self._redis.set_json(
            f"market_trades:{symbol.value}",
            result,
            self._TTL_MARKET_TRADES,
        )
        return result
