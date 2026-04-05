# Application Services (Use Cases)

> IDDD Ch. 14 — *"Application Services are the direct clients of the domain model. Their responsibility is to orchestrate use case tasks: they coordinate domain objects and infrastructure, but contain no business logic themselves."*

Vernon's rules:
- Application Services are **thin orchestrators**.
- They load domain objects, invoke domain behaviour, commit changes.
- They translate between DTOs (interface layer) and domain objects.
- They **do not** contain `if/else` business decisions.
- One use case = one public method on one Application Service class.

---

## Pattern Applied in This Project

```
Interface Layer (HTTP Controller)
    │ receives validated Pydantic model
    │ converts to Command / Query VO
    ▼
Application Use Case class (__call__ or execute)
    │ loads domain objects via ports
    │ invokes domain services / aggregate methods
    │ returns Ok(ResultDTO) | Err(DomainException)
    ▼
Interface Layer
    │ maps Ok → 200/201 response
    │ maps Err → 4xx/5xx response
```

---

## Trading Use Cases (`src/app/application/trading/use_cases/`)

### PlaceOrder

**File**: `place_order.py`
**Command**: `PlaceOrderCommand` (symbol, side, order_type, price, quantity, client_order_id)
**Orchestration**:
1. Load current `AccountState` via `ExchangeService` port.
2. Run `QrlGuards` (price range, balance check, duplicate check, rate limit).
3. Run `SlippageAnalyzer` against current `MarketSnapshot` if applicable.
4. Call `ExchangeService.place_order(command)` → receive `OrderEvent`.
5. Update `TradingSession` with the new `Order`.
6. Return `Ok(PlaceOrderResultDTO)`.

### CancelOrder

**File**: `cancel_order.py`
**Command**: `CancelOrderCommand` (symbol, order_id)
**Orchestration**:
1. Verify the order is in `TradingSession.open_orders`.
2. Call `ExchangeService.cancel_order(order_id)`.
3. Remove from session on `OrderEvent(CANCELLED)`.
4. Return `Ok(CancelOrderResultDTO)`.

### GetOrder

**File**: `get_order.py`
**Query**: `GetOrderQuery` (symbol, order_id)
**Orchestration**: Fetch from `ExchangeService`; return `Ok(OrderDTO)`.

### ListOrders

**File**: `list_orders.py`
**Query**: `ListOrdersQuery` (symbol, status_filter)
**Orchestration**: Fetch from `ExchangeService`; return `Ok(list[OrderDTO])`.

### ListTrades

**File**: `list_trades.py`
**Query**: `ListTradesQuery` (symbol, limit)
**Orchestration**: Fetch from `ExchangeService`; return `Ok(list[TradeDTO])`.

### GetKline (Trading)

**File**: `get_kline.py`
**Query**: `GetKlineQuery` (symbol, interval, limit)
**Orchestration**: Fetch from `ExchangeService`; return `Ok(list[KlineDTO])`.

### GetPrice

**File**: `get_price.py`
**Query**: `GetPriceQuery` (symbol)
**Orchestration**: Fetch ticker via `ExchangeService`; compute `ValuationService.calculate_mid_price`; return `Ok(PriceDTO)`.

---

## Market Use Cases (`src/app/application/market/use_cases/`)

| Use Case | Query | Returns |
|----------|-------|---------|
| `GetTicker` | symbol | `TickerDTO` |
| `GetDepth` | symbol, limit | `DepthDTO` |
| `GetKline` | symbol, interval, limit | `list[KlineDTO]` |
| `GetMarketTrades` | symbol, limit | `list[TradeDTO]` |
| `GetStats24h` | symbol | `Stats24hDTO` |

---

## Account Use Cases (`src/app/application/account/use_cases/`)

| Use Case | Query | Returns |
|----------|-------|---------|
| `GetBalance` | (no params, uses configured API key) | `BalanceDTO` |

---

## Ports (Application Layer Abstractions)

**File**: `src/app/application/ports/exchange_gateway.py`
```python
class ExchangeGateway(Protocol):
    # WebSocket streaming port
    async def subscribe_market_depth(symbol) -> AsyncIterator[MarketDepthEvent]: ...
    async def subscribe_trades(symbol) -> AsyncIterator[TradeEvent]: ...
    async def subscribe_orders() -> AsyncIterator[OrderEvent]: ...
    async def subscribe_balances() -> AsyncIterator[BalanceEvent]: ...
```

**File**: `src/app/application/ports/exchange_service.py`
```python
class ExchangeService(Protocol):
    # REST request/response port
    async def place_order(command: OrderCommand) -> OrderEvent: ...
    async def cancel_order(order_id: OrderId) -> OrderEvent: ...
    async def get_order(order_id: OrderId) -> Order: ...
    async def get_balance() -> AccountState: ...
    async def get_ticker(symbol: Symbol) -> Ticker: ...
    # … etc.
```

---

## Application Service Rules

1. **No business rules**: Use cases delegate all decisions to domain services and aggregates.
2. **No primitives**: Accept and return typed commands/queries/DTOs, never raw `dict`.
3. **Async context ownership**: Use cases open and close the async client context; controllers never wrap them.
4. **Result pattern**: Always return `Ok(dto)` or `Err(exception)` — never raise across boundaries.
5. **No direct infra calls**: Only call infrastructure through port interfaces defined in `application/ports/`.
