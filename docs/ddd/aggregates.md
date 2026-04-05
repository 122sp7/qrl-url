# Aggregates

> IDDD Ch. 10 — *"An Aggregate is a cluster of associated objects that we treat as a unit for the purpose of data changes. Each Aggregate has a root and a boundary."*

Vernon's rules:
1. Design small aggregates.
2. Reference other aggregates by identity only.
3. Use eventual consistency between aggregates.
4. Protect business invariants inside aggregate boundaries.

---

## TradingSession

**File**: `src/app/domain/aggregates/trading_session.py`
**Aggregate Root**: `TradingSession`
**Invariants**:
- A session belongs to exactly one `Symbol`.
- `open_orders` contains only Orders with status `NEW` or `PARTIALLY_FILLED`.
- A `Trade` added to `trades` must reference an `OrderId` that exists in `open_orders` or was previously managed by this session.

**Child objects**:
| Object | Type | Owned by |
|--------|------|----------|
| `Order` | Entity | TradingSession |
| `Trade` | Entity | TradingSession |
| `Symbol` | Value Object | TradingSession (root identity) |
| `Timestamp` | Value Object | TradingSession (session window) |

**Lifecycle**:
```
start_session(symbol) → TradingSession(open_orders=[], trades=[])
    │
    ├─ add_order(order: Order)     → open_orders updated
    ├─ record_trade(trade: Trade)  → trades updated; order status updated
    └─ close_session()            → last_activity_at set; session becomes immutable
```

**External references**: References `Account` by `SubAccountId` (identity only), never embeds `AccountState`.

---

## AccountState

**File**: `src/app/domain/aggregates/account_state.py`
**Aggregate Root**: `AccountState`
**Invariants**:
- An `AccountState` belongs to exactly one `Account` (referenced by identity).
- `available` balance for any asset must be ≥ 0.
- `locked` balance represents funds held as collateral for open orders.

**Child objects**:
| Object | Type | Owned by |
|--------|------|----------|
| `NormalizedBalances` | Value Object | AccountState |
| `Balance` (per asset) | Value Object | NormalizedBalances |

**Lifecycle**:
```
from_exchange_response(raw) → AccountState via Factory
    │
    └─ read-only; updated only by incoming BalanceEvent from ExchangeGateway
```

**Note**: AccountState is rebuilt from the exchange response, not persisted locally. It is always fresh data.

---

## MarketSnapshot

**File**: `src/app/domain/aggregates/market_snapshot.py`
**Aggregate Root**: `MarketSnapshot`
**Invariants**:
- Belongs to exactly one `Symbol`.
- `ticker`, `order_book`, and `klines` are always internally consistent (same symbol, same approximate timestamp).

**Child objects**:
| Object | Type | Owned by |
|--------|------|----------|
| `Ticker` | Value Object | MarketSnapshot |
| `OrderBook` | Value Object | MarketSnapshot |
| `OrderBookLevel` | Entity | OrderBook |
| `Kline` | Entity | MarketSnapshot |

**Lifecycle**:
```
compose(ticker, order_book, klines) → MarketSnapshot via Factory
    │
    └─ read-only snapshot; replaced entirely on next market data fetch
```

---

## Aggregate Design Rules Applied

| Rule (Vernon) | Application in this project |
|---|---|
| **Small aggregates** | Each aggregate owns only its immediately required children. `TradingSession` does not embed `AccountState`. |
| **Reference by ID** | `TradingSession` references `Account` by `SubAccountId`; never embeds it. |
| **Eventual consistency** | `AccountState` is refreshed from exchange events, not synchronised with `TradingSession` in a single transaction. |
| **Transactional boundary** | One aggregate is modified per use case transaction. `PlaceOrder` works only on `TradingSession`. |
| **No direct access to internals** | External code calls methods on the aggregate root; it never directly appends to `open_orders`. |

---

## Factory

**File**: `src/app/domain/factories/aggregates.py`

Aggregate construction is delegated to factory functions to keep domain objects free of parsing logic.

```python
# Pattern
def create_trading_session(symbol: Symbol, started_at: Timestamp) -> TradingSession: ...
def create_account_state(raw_balance_data: ...) -> AccountState: ...
def create_market_snapshot(ticker: ..., depth: ..., klines: ...) -> MarketSnapshot: ...
```
