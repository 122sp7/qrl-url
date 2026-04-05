# Bounded Contexts

> IDDD Ch. 2 — *"A Bounded Context is an explicit boundary within which a domain model exists. Inside the boundary, all terms of the Ubiquitous Language have a specific and unambiguous meaning."*

A Bounded Context owns its model completely. No other context reaches inside it.
Cross-context communication always goes through published interfaces or Domain Events.

---

## Context: Trading

**Purpose**: Execute and manage QRL/USDT orders on MEXC.

**Owns**:
- `TradingSession` aggregate (open orders + trades for a symbol in a time window)
- `Order` entity lifecycle
- `Trade` entity records
- Value Objects: `QrlPrice`, `QrlQuantity`, `Symbol`, `Side`, `OrderType`, `OrderStatus`, `TimeInForce`, `ClientOrderId`, `OrderId`, `Slippage`

**Application Use Cases** (`src/app/application/trading/`):
| Use Case | Description |
|----------|-------------|
| `PlaceOrder` | Submit a new limit or market order |
| `CancelOrder` | Cancel an open order by `OrderId` |
| `GetOrder` | Fetch order details by `OrderId` |
| `ListOrders` | List orders with optional status filter |
| `ListTrades` | List executed trades for a symbol |
| `GetKline` | Retrieve OHLCV kline data for a symbol |
| `GetPrice` | Get current mid-price for a symbol |

**Language boundary**: Within this context, *Order* means a submitted trade instruction.
In the Account context, the same word does not exist; there it is a *Balance change*.

---

## Context: Market

**Purpose**: Provide real-time and historical market data for decision-making.

**Owns**:
- `MarketSnapshot` aggregate (Ticker + OrderBook + Klines composite view)
- `OrderBook` / `OrderBookLevel` value objects and entities
- `Kline` entity, `KlineInterval` VO
- `Ticker` VO

**Application Use Cases** (`src/app/application/market/`):
| Use Case | Description |
|----------|-------------|
| `GetTicker` | Latest price snapshot for a symbol |
| `GetDepth` | Current order book levels |
| `GetKline` | Historical candlestick data |
| `GetMarketTrades` | Recent public trades |
| `GetStats24h` | 24 h volume and price statistics |

**Language boundary**: *Price* in Market context means the exchange's quoted price.
In Trading context, *Price* is the price submitted in an Order.

---

## Context: Account

**Purpose**: Track asset balances and sub-account identity.

**Owns**:
- `AccountState` aggregate (current balances)
- `Account` entity
- Value Objects: `Balance`, `NormalizedBalances`, `SubAccountId`, `ApiKey`, `ApiSecret`

**Application Use Cases** (`src/app/application/account/`):
| Use Case | Description |
|----------|-------------|
| `GetBalance` | Return current USDT and QRL balances |

**Language boundary**: *Balance* in Account context is the available/locked quantity of an asset.
In Trading context there is no *Balance*; the concept is referenced as a guard condition only.

---

## Context: System

**Purpose**: Infrastructure and operational concerns (health, scheduler, task management).

**Owns**: No domain model; thin orchestration only.

**Application Use Cases** (`src/app/application/system/`):
- Health check, warm-up, scheduled rebalance triggers.

---

## Boundary Rules

1. A context must never import another context's aggregate or entity classes directly.
2. Data crossing context boundaries must be serialised as DTOs or Domain Events.
3. The Ubiquitous Language of one context does not leak into another.
4. Infrastructure adapters (MEXC REST/WS) are **outside** all domain contexts; they implement ports defined by the Application layer.
