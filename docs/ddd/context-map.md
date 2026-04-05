# Context Map

> IDDD Ch. 3 — *"A Context Map is a diagram or document that shows the relationships between Bounded Contexts and the nature of those relationships."*

Vernon defines several integration patterns. The relationships below describe how this project's contexts interact with each other and with the external MEXC exchange.

---

## Map Diagram

```
                    ┌───────────────────────────────────┐
                    │   MEXC V3 Exchange (External)     │
                    │   REST API + WebSocket Streams     │
                    └──────┬────────────────┬───────────┘
                           │  OHS/ACL        │  OHS/ACL
                           ▼                ▼
               ┌──────────────────┐  ┌──────────────────┐
               │   ExchangeService│  │  ExchangeGateway  │
               │   (REST port)    │  │  (WS port)        │
               └────────┬─────────┘  └────────┬──────────┘
                        │                     │
          ┌─────────────┼─────────────────────┼──────────────┐
          │             │          Infra Layer │              │
          │   ┌─────────▼──────────┐  ┌───────▼────────────┐ │
          │   │  Market Context    │  │  Account Context   │ │
          │   │  (Customer/Supplier│  │  (Customer/Supplier│ │
          │   │   from Exchange)   │  │   from Exchange)   │ │
          │   └─────────┬──────────┘  └───────┬────────────┘ │
          │             │  Conformist           │  Conformist  │
          │             └───────────┬───────────┘              │
          │                        │ Published Events / DTOs   │
          │             ┌──────────▼──────────────────────┐   │
          │             │      Trading Context (Core)      │   │
          │             │   uses Market + Account data     │   │
          │             │   to make order decisions        │   │
          │             └─────────────────────────────────┘   │
          └─────────────────────────────────────────────────────┘
```

---

## Relationship: Trading ↔ Market

**Pattern**: **Customer / Supplier** (Trading is Customer; Market is Supplier)

- Trading uses cases (`PlaceOrder`, `GetPrice`) consume market data produced by Market use cases.
- Trading does **not** import Market domain objects directly — it receives DTOs from Application layer calls.
- If market data changes shape, the Market context is responsible for translating it before Trading sees it.

**Translation mechanism**: Market use cases return typed DTOs (e.g. `TickerDTO`, `DepthDTO`). The Trading use case converts these to domain VOs (`QrlPrice`, `OrderBook`) before using them.

---

## Relationship: Trading ↔ Account

**Pattern**: **Customer / Supplier** (Trading is Customer; Account is Supplier)

- `QrlGuards.ensure_sufficient_balance` requires the current USDT balance before placing an order.
- The balance is fetched via `GetBalance` use case and passed as a domain VO (`Balance`) to the guard.
- Trading context does **not** mutate Account state; it only reads.

---

## Relationship: Trading/Market/Account ↔ MEXC Exchange

**Pattern**: **Open Host Service (OHS) + Anti-Corruption Layer (ACL)**

- MEXC exposes a public REST and WebSocket API (Open Host Service).
- The infrastructure adapters in `src/app/infrastructure/exchange/` act as the ACL: they translate MEXC's JSON responses into project domain VOs and events.
- The domain never sees MEXC API schema directly; it only sees translated objects from the ACL.
- If MEXC changes its API, only the infrastructure adapter changes — the domain is unaffected.

**ACL responsibilities**:
1. Parse raw MEXC JSON into events (`OrderEvent`, `TradeEvent`, `BalanceEvent`, `MarketDepthEvent`).
2. Apply HMAC-SHA256 signing and timestamp injection.
3. Handle rate limits, retries, and WebSocket reconnection — invisible to the domain.

---

## Relationship: System Context ↔ All Others

**Pattern**: **Conformist** (System conforms to what it orchestrates)

- System use cases (health, scheduler, rebalance triggers) invoke Trading/Market/Account use cases.
- System has no domain model; it is a thin entry point for Cloud Scheduler and Cloud Run.

---

## Integration Rules

1. **No shared kernel**: contexts do not share domain classes. DTOs are the only crossing artefacts.
2. **Published Language at the MEXC boundary**: MEXC's API is the published language; our ACL translates it.
3. **Upstream changes are absorbed by the ACL**: if MEXC changes a field name, only `infrastructure/exchange/` adapters change.
4. **Domain Events travel via in-process publish**: for now, events are consumed within the same process; async message broker can be added later without changing domain code.
