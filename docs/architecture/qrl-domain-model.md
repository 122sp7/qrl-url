---
title: "QRL/USDT Domain Model — Hardcoded Symbol Files"
status: "reference"
updated: "2026-04-05"
tags: ["ddd", "domain", "qrl", "value-objects", "guards"]
---

# QRL/USDT Domain Model — Hardcoded Symbol Files

## Design Rules

1. All QRL/USDT files hardcode the symbol — no runtime `symbol` parameter
2. Risk control logic is centralized in Guard chain
3. These files must not be reused for other trading pairs

---

## Domain Layer (immutable rules)

### Price — `domain/value_objects/qrl_price.py`

- Price precision for QRL/USDT
- Minimum tick size
- Rejects zero or negative values

```python
class QrlPrice(Price):
    TICK_SIZE = Decimal("0.0001")
```

### Quantity — `domain/value_objects/qrl_quantity.py`

- Minimum order quantity
- Step size enforcement
- Fat-finger prevention

### Trading Pair — `domain/value_objects/qrl_usdt_pair.py`

```python
SYMBOL = "QRLUSDT"
BASE = "QRL"
QUOTE = "USDT"
```

Must not be constructed at runtime.

---

## Application Layer (QRL-specific behaviour)

### Market use cases — `application/market/qrl/`

```
get_qrl_price.py    ← price normalization + WS/REST fallback
get_qrl_depth.py
get_qrl_kline.py
```

### Trading use cases — `application/trading/qrl/`

```
place_qrl_order.py    ← must use QrlPrice, QrlQuantity, QrlUsdtPair, Guard chain
cancel_qrl_order.py
get_qrl_order.py
```

### Guard chain — `application/trading/qrl/guards/`

```
qrl_balance_guard.py
qrl_price_guard.py
qrl_duplicate_guard.py
qrl_rate_limit_guard.py
```

---

## Infrastructure Layer (QRL ↔ MEXC)

### API Client — `infrastructure/exchange/mexc/qrl/`

```
qrl_rest_client.py    ← no symbol parameter accepted
qrl_ws_client.py
qrl_settings.py
```

### Mappers — `infrastructure/exchange/mexc/qrl/`

```
qrl_price_mapper.py
qrl_order_mapper.py
qrl_trade_mapper.py
```

### WS State — `infrastructure/exchange/mexc/qrl/ws/`

```
qrl_stream_state.py
qrl_snapshot_loader.py
qrl_reconnect_policy.py
```

---

## Interfaces Layer (read-only dashboard)

```
interfaces/http/pages/dashboard_routes.py
interfaces/http/pages/templates/dashboard/index.html
```

Displays: QRL price, QRL position, QRL open orders.

---

## Minimum Required Files Checklist

| Type | File |
|------|------|
| Price | `qrl_price.py` |
| Quantity | `qrl_quantity.py` |
| Trading Pair | `qrl_usdt_pair.py` |
| Market | `get_qrl_price.py` |
| Order | `place_qrl_order.py` |
| Guards | `qrl_*_guard.py` |
| REST client | `qrl_rest_client.py` |
| WS client | `qrl_ws_client.py` |

---

See also: [qrl-domain-overview.md](../ddd/qrl-domain-overview.md), [dashboard-realtime-flow.md](dashboard-realtime-flow.md)
