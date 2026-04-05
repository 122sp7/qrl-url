---
title: "Dashboard Realtime Data Flow"
status: "reference"
updated: "2026-04-05"
tags: ["dashboard", "websocket", "interfaces", "qrl", "realtime"]
---

# Dashboard Realtime Data Flow

## Core Design

All data flows through the same pipeline. The page never touches MEXC directly.

```
MEXC (WS / REST)
   ↓
infrastructure (adapter / mapper)
   ↓
application (QRL-specific use case)
   ↓
interfaces (HTTP / WS endpoint)
   ↓
dashboard page
```

- Domain (`QrlPrice`) is only responsible for correctness
- Interfaces are only responsible for display
- The page consumes normalized, QRL-specific data

---

## Price Feed

### Application — `application/market/qrl/get_qrl_price.py`

```python
class GetQrlPrice:
    def __init__(self, exchange_gateway):
        self._exchange = exchange_gateway

    async def execute(self) -> QrlPrice:
        raw_price = await self._exchange.get_ticker_price("QRLUSDT")
        return QrlPrice(raw_price)
```

### Interface — `interfaces/http/pages/dashboard_routes.py`

```python
@router.get("/dashboard")
async def dashboard(request: Request):
    use_case = GetQrlPrice(exchange_gateway)
    qrl_price = await use_case.execute()
    return templates.TemplateResponse(
        "dashboard/index.html",
        {"request": request, "qrl_price": str(qrl_price)},
    )
```

### WebSocket push — `interfaces/http/api/ws_routes.py`

```python
@router.websocket("/ws/qrl-price")
async def qrl_price_ws(ws: WebSocket):
    await ws.accept()
    while True:
        price = await get_qrl_price_use_case.execute()
        await ws.send_json({"price": str(price)})
        await asyncio.sleep(1)
```

---

## Order Book (Depth)

### Application — `application/market/qrl/get_qrl_depth.py`

Returns sorted, depth-limited structure:

```python
{"bids": [(price, qty), ...], "asks": [(price, qty), ...]}
```

Top-N slicing is done in Application, not in the frontend.

### WebSocket — `interfaces/http/api/ws_routes.py`

```python
@router.websocket("/ws/qrl-depth")
async def qrl_depth_ws(ws):
    await ws.accept()
    async for depth in depth_stream:
        await ws.send_json(depth)
```

---

## Orders & Trades

### Application — `application/trading/qrl/`

```
list_qrl_orders.py    ← returns QRL/USDT only, as domain Order entities
list_qrl_trades.py
```

### Interface — `interfaces/http/api/trading_routes.py`

```python
@router.get("/qrl/orders")
async def qrl_orders():
    orders = await list_qrl_orders.execute()
    return [{"id": o.order_id, "side": o.side.value, ...} for o in orders]
```

---

## Klines

### Application — `application/market/qrl/get_qrl_kline.py`

```python
async def execute(self, interval="1m", limit=100):
    return await self.exchange.get_klines(symbol="QRLUSDT", interval=interval, limit=limit)
```

### Endpoint: `GET /api/qrl/kline?interval=1m`

---

## Responsibility Matrix

| Layer | Responsibility |
|-------|---------------|
| Domain | Value correctness only |
| Application | Decides source (WS vs REST), normalizes |
| Interfaces | Display mapping, no business logic |
| HTML/JS | Zero business logic |

---

## Live Page Readiness Checklist

| Item | Status |
|------|--------|
| Real price via REST | done |
| Correct precision via QrlPrice | done |
| WebSocket live price push | pending |
| Decoupled from order execution | done |

---

See also: [qrl-domain-model.md](qrl-domain-model.md), [gap-analysis.md](../plans/gap-analysis.md)
