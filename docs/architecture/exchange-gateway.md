---
title: "Exchange Gateway & Infrastructure Adapters"
status: "reference"
updated: "2026-04-05"
tags: ["ddd", "infrastructure", "protobuf", "exchange-gateway"]
---

# Exchange Gateway & Infrastructure Adapters

## Architecture Overview (DDD)

```
src/app
├─ domain
│  ├─ events
│  │   ├─ market_depth_event.py
│  │   └─ trade_event.py
│  ├─ value_objects
│  │   ├─ symbol.py
│  │   ├─ price.py
│  │   └─ quantity.py
│  └─ entities
│      └─ order.py
│
├─ application
│  └─ ports
│      └─ exchange_gateway.py   ← Application Port
│
└─ infrastructure
   └─ exchange
      └─ mexc
         ├─ generated           ← *_pb2.py
         ├─ ws
         │   └─ mexc_ws_client.py
         └─ adapters
             ├─ market_event_adapter.py   ← WS → Domain Event
             └─ order_mapper.py           ← proto → Domain
```

---

## ExchangeGateway (Application Port)

Application depends only on capabilities, not on implementations or protobuf.

### `application/ports/exchange_gateway.py`

```python
from typing import Protocol, AsyncIterator
from app.domain.events.market_depth_event import MarketDepthEvent
from app.domain.events.trade_event import TradeEvent
from app.domain.value_objects.symbol import Symbol


class ExchangeGateway(Protocol):
    async def subscribe_market_depth(
        self, symbol: Symbol
    ) -> AsyncIterator[MarketDepthEvent]: ...

    async def subscribe_trades(
        self, symbol: Symbol
    ) -> AsyncIterator[TradeEvent]: ...
```

Application Services depend only on this interface. Future exchanges (Binance, OKX) just swap the adapter.

---

## Domain Event (pure, no protobuf)

### `domain/events/market_depth_event.py`

```python
from dataclasses import dataclass
from app.domain.value_objects import Symbol, Price, Quantity


@dataclass(frozen=True)
class MarketDepthEvent:
    symbol: Symbol
    bids: list[tuple[Price, Quantity]]
    asks: list[tuple[Price, Quantity]]
    timestamp: int
```

---

## MEXC WS Client (technical layer only)

### `infrastructure/exchange/mexc/ws/mexc_ws_client.py`

```python
class MexcWebSocketClient:
    async def subscribe(self, channel: str):
        """Yield raw protobuf bytes or decoded proto messages."""
        ...
```

This layer is a technical detail; Domain never sees it.

---

## WS → Domain Event Adapter

### `infrastructure/exchange/mexc/adapters/market_event_adapter.py`

```python
from app.application.ports.exchange_gateway import ExchangeGateway
from app.domain.events.market_depth_event import MarketDepthEvent
from app.domain.value_objects.symbol import Symbol
from app.infrastructure.exchange.mexc.generated import PublicAggreDepthsV3Api_pb2
from app.infrastructure.exchange.mexc.ws.mexc_ws_client import MexcWebSocketClient
from app.infrastructure.exchange.mexc.adapters.order_mapper import depth_proto_to_domain


class MexcExchangeGateway(ExchangeGateway):

    def __init__(self, ws_client: MexcWebSocketClient):
        self._ws = ws_client

    async def subscribe_market_depth(
        self, symbol: Symbol
    ) -> AsyncIterator[MarketDepthEvent]:
        async for proto_msg in self._ws.subscribe(channel=f"depth:{symbol.value}"):
            yield depth_proto_to_domain(proto_msg)
```

---

## proto → Domain Mapper

### `infrastructure/exchange/mexc/adapters/order_mapper.py`

```python
from app.domain.events.market_depth_event import MarketDepthEvent
from app.domain.value_objects import Symbol, Price, Quantity
from app.infrastructure.exchange.mexc.generated import PublicAggreDepthsV3Api_pb2


def depth_proto_to_domain(proto: PublicAggreDepthsV3Api_pb2.Depth) -> MarketDepthEvent:
    bids = [(Price(float(p.price)), Quantity(float(p.quantity))) for p in proto.bids]
    asks = [(Price(float(p.price)), Quantity(float(p.quantity))) for p in proto.asks]
    return MarketDepthEvent(
        symbol=Symbol(proto.symbol),
        bids=bids,
        asks=asks,
        timestamp=proto.timestamp,
    )
```

### Rules

- Domain must not import `_pb2`
- Application must not know about WS or protobuf
- Infrastructure adapters own the translation responsibility

---

## Application Service Usage

```python
class MarketService:
    def __init__(self, exchange: ExchangeGateway):
        self._exchange = exchange
```

See also: [event-bus-domain-events.md](event-bus-domain-events.md)
