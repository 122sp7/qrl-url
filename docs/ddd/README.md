# DDD Reference — MEXC QRL Trading Bot

> Based on **Implementing Domain-Driven Design** by Vaughn Vernon (Addison-Wesley, 2013).

This folder maps IDDD concepts to the concrete implementation in this project.
It is the primary reference for architectural decisions, naming conventions, and layer responsibilities.

## Documents

| File | IDDD Chapter | Purpose |
|------|-------------|---------|
| [ubiquitous-language.md](ubiquitous-language.md) | Ch. 2 | Shared vocabulary between domain experts and developers |
| [bounded-contexts.md](bounded-contexts.md) | Ch. 2 | Context boundaries and their responsibilities |
| [subdomains.md](subdomains.md) | Ch. 2 | Core / Supporting / Generic subdomain classification |
| [context-map.md](context-map.md) | Ch. 3 | Relationships and translations between contexts |
| [aggregates.md](aggregates.md) | Ch. 10 | Aggregate roots, invariants, and consistency boundaries |
| [domain-events.md](domain-events.md) | Ch. 8 | Events published by aggregates |
| [domain-services.md](domain-services.md) | Ch. 7 | Stateless domain logic that spans multiple aggregates |
| [application-services.md](application-services.md) | Ch. 14 | Use cases and orchestration layer |
| [repositories.md](repositories.md) | Ch. 12 | Persistence abstraction for aggregates |
| [AGENT.md](AGENT.md) | — | Copilot agent instructions for this DDD context |

## Project Layer Map

```
src/app/
├── domain/              ← Pure business rules (IDDD: all inner building blocks)
│   ├── aggregates/      ← TradingSession, AccountState, MarketSnapshot
│   ├── entities/        ← Order, Trade, Account, TradingPair, Kline, OrderBookLevel
│   ├── value_objects/   ← Price, Quantity, Symbol, OrderId, Side, …
│   ├── events/          ← OrderEvent, TradeEvent, BalanceEvent, MarketDepthEvent
│   ├── services/        ← QrlGuards, SlippageAnalyzer, ValuationService, …
│   └── factories/       ← Aggregate construction
├── application/         ← Use Cases / Application Services (IDDD: Ch. 14)
│   ├── trading/         ← PlaceOrder, CancelOrder, GetOrder, …
│   ├── market/          ← GetTicker, GetDepth, GetKline, …
│   ├── account/         ← GetBalance
│   └── ports/           ← ExchangeGateway, ExchangeService (Ports & Adapters)
├── interfaces/          ← HTTP controllers, WebSocket handlers, task entry points
└── infrastructure/      ← Repository impls, MEXC REST/WS adapters, Redis, config
```

## Key Architectural Rules

1. **Dependency direction**: Domain ← Application ← Interfaces / Infrastructure.
2. **Domain is pure**: no I/O, no imports outside `src/app/domain/`.
3. **Use Cases own the transaction**: they open/close the async context; controllers never do.
4. **Result pattern**: Use Cases return `Ok(T) | Err(E)`; never raise across layer boundaries.
5. **VOs are immutable**: all `value_objects/` are frozen dataclasses or similar.
6. **Aggregates protect invariants**: callers never mutate child entities directly.
