# Ubiquitous Language

> IDDD Ch. 2 — *"The Ubiquitous Language is a shared language developed by the team — both domain experts and developers — that is used everywhere: in conversations, in the model, and in the code."*

All terms below are canonical. Use them exactly as written in code identifiers, comments, and conversations.
Flag any deviation as a naming violation.

---

## Trading Domain

| Term | Definition | Code Location |
|------|-----------|---------------|
| **QRL** | The traded asset (Quantum Resistant Ledger token). The base currency in all QRL/USDT pairs. | `QrlPrice`, `QrlQuantity`, `QrlUsdtPair` |
| **USDT** | The quote currency. All prices and costs are denominated in USDT. | `Price`, `Balance` |
| **Symbol** | A trading pair identifier (e.g. `QRLUSDT`). Immutable VO. | `src/app/domain/value_objects/symbol.py` |
| **Order** | A single instruction to buy or sell a quantity of QRL at a price. Has a lifecycle (NEW → FILLED / CANCELLED). | `src/app/domain/entities/order.py` |
| **Trade** | A completed execution that partially or fully fills an Order. Immutable record. | `src/app/domain/entities/trade.py` |
| **OrderId** | Exchange-assigned unique identifier for an Order. | `src/app/domain/value_objects/order_id.py` |
| **ClientOrderId** | Client-generated idempotency key for an Order submission. | `src/app/domain/value_objects/client_order_id.py` |
| **Side** | Direction of an Order: `BUY` or `SELL`. | `src/app/domain/value_objects/side.py` |
| **OrderType** | Execution type: `LIMIT` or `MARKET`. | `src/app/domain/value_objects/order_type.py` |
| **OrderStatus** | Lifecycle state: `NEW`, `PARTIALLY_FILLED`, `FILLED`, `CANCELLED`, `REJECTED`. | `src/app/domain/value_objects/order_status.py` |
| **TimeInForce** | Order duration policy: `GTC`, `IOC`, `FOK`. | `src/app/domain/value_objects/time_in_force.py` |
| **Price** | A non-negative decimal representing a per-unit USDT value. | `src/app/domain/value_objects/price.py` |
| **QrlPrice** | A Price specifically validated for QRL/USDT trading. | `src/app/domain/value_objects/qrl_price.py` |
| **Quantity** | An amount of an asset. Always positive. | `src/app/domain/value_objects/quantity.py` |
| **QrlQuantity** | A Quantity specifically validated for QRL token amounts. | `src/app/domain/value_objects/qrl_quantity.py` |
| **Slippage** | The difference between expected and actual execution price, expressed as a percentage. | `src/app/domain/value_objects/slippage.py` |
| **TradingSession** | Aggregate that groups open Orders and Trades for a Symbol within a session window. | `src/app/domain/aggregates/trading_session.py` |

## Account Domain

| Term | Definition | Code Location |
|------|-----------|---------------|
| **Account** | A MEXC sub-account that holds Balances. | `src/app/domain/entities/account.py` |
| **Balance** | The available and locked quantity of a single asset in an Account. | `src/app/domain/value_objects/balance.py` |
| **NormalizedBalances** | A VO that aggregates multiple asset Balances into a canonical view. | `src/app/domain/value_objects/normalized_balances.py` |
| **SubAccountId** | Identifier for a MEXC sub-account. | `src/app/domain/value_objects/sub_account_id.py` |
| **AccountState** | Aggregate that represents the current asset positions of an Account. | `src/app/domain/aggregates/account_state.py` |

## Market Domain

| Term | Definition | Code Location |
|------|-----------|---------------|
| **Ticker** | A snapshot of the latest price and 24 h statistics for a Symbol. | `src/app/domain/value_objects/ticker.py` |
| **OrderBook** | A ranked list of Bids and Asks at specific Price levels. | `src/app/domain/value_objects/order_book.py` |
| **OrderBookLevel** | A single price/quantity entry in an OrderBook. | `src/app/domain/entities/order_book_level.py` |
| **Kline** | OHLCV candlestick data for a Symbol over a KlineInterval. | `src/app/domain/entities/kline.py` |
| **KlineInterval** | The duration of a single Kline (e.g. `1m`, `5m`, `1h`). | `src/app/domain/value_objects/kline_interval.py` |
| **MarketSnapshot** | Aggregate combining the current Ticker, OrderBook, and recent Klines. | `src/app/domain/aggregates/market_snapshot.py` |

## Infrastructure / Integration

| Term | Definition | Code Location |
|------|-----------|---------------|
| **ExchangeGateway** | Port for streaming real-time market and account data via WebSocket. | `src/app/application/ports/exchange_gateway.py` |
| **ExchangeService** | Port for request/response REST operations against the exchange. | `src/app/application/ports/exchange_service.py` |
| **ApiKey / ApiSecret** | Credentials for authenticating with the MEXC V3 API. | `src/app/domain/value_objects/api_key.py` |

---

## Terms That Must NOT Appear in Domain Code

| Avoid | Reason | Use instead |
|-------|--------|-------------|
| `dict`, `str`, `int` as return types from Use Cases | Primitive obsession | Return a typed VO, Entity, or DTO |
| `response`, `request`, `payload` | HTTP vocabulary leaking into domain | `Command`, `Query`, `Event`, `Result` |
| `db`, `cache`, `redis` references | Infrastructure concern | Port interface name |
| `handler`, `controller` | Interface concern | `UseCase`, `ApplicationService` |
