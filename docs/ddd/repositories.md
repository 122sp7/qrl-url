# Repositories

> IDDD Ch. 12 — *"A Repository represents all objects of a certain type as a conceptual set. It acts like a collection, except with more elaborate querying capability. Objects of the appropriate type are added and removed, and the machinery behind the Repository inserts objects or deletes them from the database."*

Vernon's rules:
- Repositories are defined per **Aggregate Root** — never per entity.
- The interface lives in the **Application layer** (port); the implementation lives in **Infrastructure**.
- The domain model never knows how persistence works.
- Repositories handle collections of aggregates; they do not leak SQL or Redis constructs into the domain.

---

## Repository Pattern in This Project

This project is primarily a **read-through / write-through** system: the exchange is the system of record. There is no local relational database. Instead, repositories correspond to two concerns:

1. **Exchange-backed repositories** — read from or write to MEXC via REST (implemented as `ExchangeService` adapters).
2. **Cache-backed repositories** — read/write short-lived state to Redis (order state, balance snapshots).

The `ExchangeService` port in `src/app/application/ports/exchange_service.py` acts as the combined repository interface for exchange-domain aggregates.

---

## Aggregate → Repository Mapping

### TradingSession Repository

**Port responsibility** (in `ExchangeService`):

| Method | Description |
|--------|-------------|
| `place_order(command) → OrderEvent` | Persist a new Order by submitting to the exchange |
| `cancel_order(order_id) → OrderEvent` | Mark an Order as CANCELLED on the exchange |
| `get_order(order_id) → Order` | Reconstitute an Order entity from exchange state |
| `list_orders(symbol, status) → list[Order]` | Fetch a collection of Orders for a symbol |
| `list_trades(symbol, limit) → list[Trade]` | Fetch Trade records for a symbol |

**Cache responsibility** (Redis, in infrastructure):
- Open order IDs cached with short TTL to avoid redundant API calls.
- `ClientOrderId` set cached to enforce duplicate detection without an API round-trip.

### AccountState Repository

**Port responsibility** (in `ExchangeService`):

| Method | Description |
|--------|-------------|
| `get_balance() → AccountState` | Reconstitute `AccountState` aggregate from exchange response |

**Cache responsibility** (Redis):
- Balance snapshot cached with TTL ≤ 5 s to reduce latency in guard checks.

### MarketSnapshot Repository

**Port responsibility** (in `ExchangeService`):

| Method | Description |
|--------|-------------|
| `get_ticker(symbol) → Ticker` | Fetch latest Ticker VO |
| `get_depth(symbol, limit) → OrderBook` | Fetch current OrderBook |
| `get_kline(symbol, interval, limit) → list[Kline]` | Fetch Kline entities |
| `get_stats_24h(symbol) → Stats24h` | Fetch 24 h statistics |

**Cache responsibility** (Redis):
- Ticker and depth cached with TTL 1–5 s.
- Kline data cached with TTL 60 s (less volatile).

---

## Infrastructure Implementations

| Port | Implementation location |
|------|------------------------|
| `ExchangeService` | `src/app/infrastructure/exchange/` |
| `ExchangeGateway` | `src/app/infrastructure/exchange/` (WebSocket adapter) |
| Redis cache layer | `src/app/infrastructure/` (used internally by adapters) |

Infrastructure adapters:
- Translate raw MEXC JSON → domain VOs/entities (ACL role).
- Apply HMAC-SHA256 signing.
- Handle retries and rate limiting.
- Manage Redis TTL caching transparently.

---

## Repository Rules

1. **Repository interfaces are in Application layer** (`ports/`), not in Domain.
2. **Infrastructure implements the port** — the Application layer never imports from Infrastructure.
3. **Return domain objects only** — repositories return VOs, Entities, and Aggregates, never dicts or ORM models.
4. **One repository per aggregate root** — not one per entity.
5. **No business logic in repositories** — a repository that decides *whether* to persist is doing too much.
6. **Cache is an implementation detail** — the Application layer is unaware of Redis; caching lives entirely inside the infrastructure adapter.

---

## Why There Is No Traditional ORM Repository

The exchange is the authoritative data store. There is no local PostgreSQL or SQLite. This is a common pattern for trading systems: the exchange holds the order book and account state, and the application maintains only transient session state (open orders in Redis), reconstructing aggregates from exchange responses on each use case invocation.

If local persistence is added in the future (e.g. trade history, PnL records), a new port should be defined in `application/ports/` and implemented in `infrastructure/` following the same pattern.
