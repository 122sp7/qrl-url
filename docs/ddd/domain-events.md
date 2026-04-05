# Domain Events

> IDDD Ch. 8 — *"A Domain Event is a record of something that happened in the domain that domain experts care about. It is named in the past tense and captures the state at the moment it occurred."*

Vernon's rules:
- Named in **past tense** (e.g. `OrderPlaced`, not `PlaceOrder`).
- **Immutable**: events are facts; they never change after creation.
- Contain enough data so consumers do not need to ask for more.
- Published by the aggregate root after a state change.

---

## Event Catalogue

### OrderEvent

**File**: `src/app/domain/events/order_event.py`
**Published when**: The exchange reports a change in an Order's state.
**Consumed by**: Trading use cases, `TradingSession` update logic.

| Field | Type | Meaning |
|-------|------|---------|
| `order_id` | `OrderId` | The affected order |
| `client_order_id` | `ClientOrderId` | Client-side reference |
| `symbol` | `Symbol` | Trading pair |
| `side` | `Side` | BUY or SELL |
| `order_type` | `OrderType` | LIMIT or MARKET |
| `status` | `OrderStatus` | NEW / PARTIALLY_FILLED / FILLED / CANCELLED |
| `price` | `Price` | Order price at time of event |
| `quantity` | `Quantity` | Original quantity |
| `executed_quantity` | `Quantity` | Amount filled so far |
| `timestamp` | `Timestamp` | When the event occurred on the exchange |

**State transitions triggered**:
```
NEW          → order added to TradingSession.open_orders
PARTIALLY_FILLED → order quantity updated
FILLED       → order moved out of open_orders; Trade recorded
CANCELLED    → order removed from open_orders
```

---

### TradeEvent

**File**: `src/app/domain/events/trade_event.py`
**Published when**: A fill (full or partial) occurs for an Order.
**Consumed by**: Trading use cases, reconciliation logic.

| Field | Type | Meaning |
|-------|------|---------|
| `trade_id` | `TradeId` | Unique trade execution ID |
| `order_id` | `OrderId` | The order that was filled |
| `symbol` | `Symbol` | Trading pair |
| `side` | `Side` | BUY or SELL |
| `price` | `Price` | Execution price |
| `quantity` | `Quantity` | Amount executed in this trade |
| `commission` | `Quantity` | Fee charged |
| `commission_asset` | `str` | Asset used for fee (e.g. `QRL`) |
| `timestamp` | `Timestamp` | Execution time |

---

### BalanceEvent

**File**: `src/app/domain/events/balance_event.py`
**Published when**: Account balances change on the exchange.
**Consumed by**: `AccountState` update logic, `QrlGuards.ensure_sufficient_balance`.

| Field | Type | Meaning |
|-------|------|---------|
| `asset` | `str` | Asset symbol (e.g. `USDT`, `QRL`) |
| `available` | `Balance` | New available (free) balance |
| `locked` | `Balance` | New locked (reserved) balance |
| `timestamp` | `Timestamp` | When the balance changed |

---

### MarketDepthEvent

**File**: `src/app/domain/events/market_depth_event.py`
**Published when**: The exchange order book changes.
**Consumed by**: `MarketSnapshot` refresh, `DepthCalculator` domain service.

| Field | Type | Meaning |
|-------|------|---------|
| `symbol` | `Symbol` | Trading pair |
| `bids` | `list[OrderBookLevel]` | Updated bid levels |
| `asks` | `list[OrderBookLevel]` | Updated ask levels |
| `timestamp` | `Timestamp` | Book snapshot time |

---

## Event Flow

```
MEXC WebSocket
    │
    ▼ (raw JSON)
Infrastructure ACL (adapter)
    │ translates to domain event
    ▼
ExchangeGateway port
    │ yields typed event
    ▼
Application Use Case
    │ passes event to aggregate or domain service
    ▼
Aggregate / Domain Service
    │ updates state / raises business exception
    ▼
Application Use Case returns Ok/Err result
    │
    ▼
Interface Controller maps to HTTP response
```

---

## Rules

1. Events are **immutable dataclasses** (`@dataclass(frozen=True)`).
2. Events cross the infrastructure boundary via the `ExchangeGateway` port — they are not raw dicts.
3. The domain never subscribes to its own events; that is an application-layer concern.
4. If an event in the future needs to be persisted (event sourcing), add an outbox in the infrastructure layer — domain code is unchanged.
