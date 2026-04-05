import asyncio
import os

from fastapi import APIRouter, Depends, HTTPException, Query

from src.app.application.account.use_cases.get_balance import GetBalanceUseCase
from src.app.application.market.qrl.get_qrl_depth import GetQrlDepth
from src.app.application.market.qrl.get_qrl_kline import GetQrlKline
from src.app.application.market.qrl.get_qrl_price import GetQrlPrice
from src.app.application.market.use_cases.get_market_trades import GetMarketTradesUseCase
from src.app.application.ports.exchange_service import ExchangeServiceFactory
from src.app.application.trading.qrl.cancel_qrl_order import CancelQrlOrder
from src.app.application.trading.qrl.get_qrl_order import GetQrlOrder
from src.app.application.trading.qrl.place_qrl_order import PlaceQrlOrder, PlaceQrlOrderCommand
from src.app.application.trading.use_cases.list_orders import ListOrdersUseCase
from src.app.application.trading.use_cases.list_trades import ListTradesUseCase
from src.app.domain.value_objects.order_type import OrderType
from src.app.domain.value_objects.qrl_price import QrlPrice
from src.app.domain.value_objects.qrl_quantity import QrlQuantity
from src.app.domain.value_objects.side import Side
from src.app.domain.value_objects.time_in_force import TimeInForce
from src.app.infrastructure.external.redis_client import RedisClient
from src.app.interfaces.http.dependencies import get_exchange_factory
from src.app.interfaces.http.schemas import PlaceOrderRequest

router = APIRouter()


async def _trades_from_redis(limit: int = 200) -> list[dict] | None:
    """Return trades from Redis Sorted Set, or None if REDIS_URL not configured."""
    redis_url = os.environ.get("REDIS_URL", "")
    if not redis_url:
        return None
    client = RedisClient(redis_url)
    await client.connect()
    try:
        return await client.list_trades(limit)
    finally:
        await client.close()


@router.get("/trades")
async def qrl_trades(
    limit: int = Query(default=200, ge=1, le=500),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """Return myTrades from Redis when available, falling back to MEXC."""
    cached = await _trades_from_redis(limit)
    if cached is not None:
        return cached
    usecase = ListTradesUseCase(exchange_factory)
    return await usecase.execute(symbol="QRLUSDT")



@router.get("/price")
async def qrl_price(exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)):
    usecase = GetQrlPrice(exchange_factory)
    try:
        snapshot = await usecase.execute()
        return snapshot.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch QRL price: {exc}") from exc


@router.get("/kline")
async def qrl_kline(
    interval: str = Query(default="1m"),
    limit: int = Query(default=50, ge=1, le=500),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    usecase = GetQrlKline(exchange_factory, interval=interval, limit=limit)
    try:
        raw = await usecase.execute()
        normalized = [
            {
                "timestamp": item[0], "open": item[1], "high": item[2],
                "low": item[3], "close": item[4], "volume": item[5],
            }
            for item in raw
        ]
        return normalized
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch QRL klines: {exc}") from exc


@router.get("/depth")
async def qrl_depth(
    limit: int = Query(default=50, ge=5, le=1000),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    usecase = GetQrlDepth(exchange_factory, limit=limit)
    try:
        return await usecase.execute()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch QRL depth: {exc}") from exc


@router.post("/orders")
async def qrl_place_order(
    request: PlaceOrderRequest,
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    usecase = PlaceQrlOrder(exchange_factory)
    command = PlaceQrlOrderCommand(
        side=Side(request.side),
        order_type=OrderType(request.order_type),
        price=QrlPrice(request.price) if request.price is not None else None,
        quantity=QrlQuantity(request.quantity),
        time_in_force=TimeInForce(request.time_in_force) if request.time_in_force else None,
        client_order_id=request.client_order_id,
    )
    return await usecase.execute(command)


@router.post("/orders/{order_id}/cancel")
async def qrl_cancel_order(
    order_id: str, exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)
):
    usecase = CancelQrlOrder(exchange_factory)
    return await usecase.execute(order_id=order_id, client_order_id=None)


@router.get("/orders/{order_id}")
async def qrl_get_order(
    order_id: str, exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory)
):
    usecase = GetQrlOrder(exchange_factory)
    return await usecase.execute(order_id=order_id, client_order_id=None)


@router.get("/summary")
async def qrl_summary(
    interval: str = Query(default="1m"),
    kline_limit: int = Query(default=50, ge=1, le=500),
    depth_limit: int = Query(default=50, ge=5, le=1000),
    trades_limit: int = Query(default=50, ge=1, le=500),
    exchange_factory: ExchangeServiceFactory = Depends(get_exchange_factory),
):
    """Aggregate price, kline, depth, and balance for dashboard consumption."""
    price_uc = GetQrlPrice(exchange_factory)
    kline_uc = GetQrlKline(exchange_factory, interval=interval, limit=kline_limit)
    depth_uc = GetQrlDepth(exchange_factory, limit=depth_limit)
    balance_uc = GetBalanceUseCase(exchange_factory)
    orders_uc = ListOrdersUseCase(exchange_factory)
    market_trades_uc = GetMarketTradesUseCase(exchange_factory)

    (
        price_result, kline_result, depth_result, balance_result, orders, market_trades
    ) = await asyncio.gather(
        price_uc.execute(),
        kline_uc.execute(),
        depth_uc.execute(),
        balance_uc.execute(),
        orders_uc.execute(symbol="QRLUSDT"),
        market_trades_uc.execute(),
    )

    cached_trades = await _trades_from_redis(trades_limit)
    if cached_trades is None:
        trades_uc = ListTradesUseCase(exchange_factory)
        cached_trades = await trades_uc.execute("QRLUSDT")

    normalized_klines = [
        {
            "timestamp": item[0], "open": item[1], "high": item[2],
            "low": item[3], "close": item[4], "volume": item[5],
        }
        for item in kline_result
    ]
    return {
        "price": price_result.to_dict(),
        "klines": normalized_klines,
        "depth": depth_result,
        "balance": balance_result,
        "orders": orders,
        "trades": cached_trades,
        "market_trades": market_trades[:trades_limit],
    }
