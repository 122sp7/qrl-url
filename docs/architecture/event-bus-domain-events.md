---
title: "Domain Event Bus & Mapper Pipeline"
status: "reference"
updated: "2026-04-05"
tags: ["ddd", "event-bus", "domain-events", "mappers", "backpressure"]
---

# Domain Event Bus & Mapper Pipeline

## Design Principles (DDD)

- Domain Events must not know about WS, protobuf, or async frameworks
- Event Bus is an Application-layer abstraction
- Infrastructure is only responsible for publishing

---

## Domain Events (existing)

```
domain/events/
  market_depth_event.py
  trade_event.py
  order_event.py
  balance_event.py
```

All are pure data, immutable frozen dataclasses.

---

## Application Event Bus Port

### `application/events/event_bus.py`

```python
from typing import Protocol, Type, Callable, Awaitable, Any

DomainEvent = Any
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None: ...
```

Application and Domain Services depend only on this interface.

---

## In-Memory Event Bus (default implementation)

### `infrastructure/event_bus/in_memory_event_bus.py`

```python
from collections import defaultdict
from typing import Type, Dict, List
from app.application.events.event_bus import EventBus


class InMemoryEventBus(EventBus):

    def __init__(self):
        self._handlers: Dict[Type, List] = defaultdict(list)

    def subscribe(self, event_type, handler):
        self._handlers[event_type].append(handler)

    async def publish(self, event):
        for handler in self._handlers[type(event)]:
            await handler(event)
```

---

## Gateway → Event Bus Integration Point

```python
async for event in self._exchange.subscribe_trades(symbol):
    await self._event_bus.publish(event)
```

---

## Mapper Pipeline (one aggregate = one mapper)

### Trade Mapper

```python
# adapters/trade_mapper.py
from app.domain.events.trade_event import TradeEvent
from app.domain.value_objects import Symbol, Price, Quantity, TradeId
from app.infrastructure.exchange.mexc.generated import PublicDealsV3Api_pb2


def trade_proto_to_domain(proto: PublicDealsV3Api_pb2.Deal) -> TradeEvent:
    return TradeEvent(
        trade_id=TradeId(proto.dealId),
        symbol=Symbol(proto.symbol),
        price=Price(float(proto.price)),
        quantity=Quantity(float(proto.quantity)),
        is_buyer_maker=proto.isBuyerMaker,
        timestamp=proto.timestamp,
    )
```

### Order Mapper

```python
# adapters/order_mapper.py
from app.domain.events.order_event import OrderEvent
from app.domain.value_objects import OrderId, Symbol, Price, Quantity, OrderStatus
from app.infrastructure.exchange.mexc.generated import PrivateOrdersV3Api_pb2


def order_proto_to_domain(proto: PrivateOrdersV3Api_pb2.Order) -> OrderEvent:
    return OrderEvent(
        order_id=OrderId(proto.orderId),
        symbol=Symbol(proto.symbol),
        price=Price(float(proto.price)),
        quantity=Quantity(float(proto.quantity)),
        status=OrderStatus.from_exchange(proto.status),
        timestamp=proto.timestamp,
    )
```

### Balance Mapper

```python
# adapters/balance_mapper.py
from app.domain.events.balance_event import BalanceEvent
from app.domain.value_objects import Asset, Quantity
from app.infrastructure.exchange.mexc.generated import PrivateAccountV3Api_pb2


def balance_proto_to_domain(proto: PrivateAccountV3Api_pb2.Balance) -> BalanceEvent:
    return BalanceEvent(
        asset=Asset(proto.asset),
        free=Quantity(float(proto.free)),
        locked=Quantity(float(proto.locked)),
        timestamp=proto.timestamp,
    )
```

---

## WS Backpressure & Replay

WebSocket data can arrive faster than it is consumed; the system must handle restarts without gaps.

### Bounded Async Queue

```python
# infrastructure/streaming/bounded_queue.py
import asyncio


class BoundedAsyncQueue:
    def __init__(self, max_size: int):
        self._queue = asyncio.Queue(maxsize=max_size)
```

Current status: `BoundedAsyncQueue` and `RingBuffer` exist but are not yet wired to WS clients. See [gap-analysis.md](../plans/gap-analysis.md) for the convergence plan.

---

See also: [exchange-gateway.md](exchange-gateway.md)
