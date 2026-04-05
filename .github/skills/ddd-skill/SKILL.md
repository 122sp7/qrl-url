---
name: ddd-skill
description: DDD knowledge base for the MEXC QRL Trading Bot. Use when making architectural decisions, designing new features, reviewing code for layer violations, or resolving naming questions. Covers Vernon IDDD concepts mapped to this codebase.
---

# DDD Knowledge Base — MEXC QRL Trading Bot

> Based on Implementing Domain-Driven Design by Vaughn Vernon.

## When to use this skill

- Deciding **where** new logic belongs (layer, building block, module)
- Checking if a term is in the **Ubiquitous Language**
- Understanding **aggregate boundaries** and invariants
- Identifying the correct **port interface** to define or implement
- Resolving a **context boundary** crossing question

## Quick Reference

### Bounded Contexts

| Context | Type | Path | Aggregates |
|---------|------|------|-----------|
| Trading | Core Domain | `src/app/application/trading/` | TradingSession |
| Market | Supporting | `src/app/application/market/` | MarketSnapshot |
| Account | Supporting | `src/app/application/account/` | AccountState |
| System | Generic | `src/app/application/system/` | — |

### DDD Building Blocks → Code Locations

| Building Block | Location | Rule |
|---|---|---|
| Value Object | `src/app/domain/value_objects/` | Immutable, frozen dataclass, no identity |
| Entity | `src/app/domain/entities/` | Has identity, mutable lifecycle |
| Aggregate Root | `src/app/domain/aggregates/` | Consistency boundary, owns children |
| Domain Service | `src/app/domain/services/` | Stateless, pure Python, no I/O |
| Domain Event | `src/app/domain/events/` | Frozen dataclass, past tense name |
| Use Case | `src/app/application/*/use_cases/` | Orchestration only, Result pattern |
| Port (interface) | `src/app/application/ports/` | Protocol class, no implementation |
| Repository impl | `src/app/infrastructure/exchange/` | Implements port, handles I/O |
| HTTP Controller | `src/app/interfaces/http/` | Maps DTO ↔ Command/Response |

### Key Aggregates

| Aggregate | Invariants | Cross-refs by identity |
|-----------|-----------|----------------------|
| `TradingSession` | open_orders = NEW/PARTIALLY_FILLED only | `SubAccountId` |
| `AccountState` | available ≥ 0, rebuilt from exchange | `Account.id` |
| `MarketSnapshot` | ticker/orderbook/klines same symbol | `Symbol` |

### Ports

| Port | Type | Methods |
|------|------|---------|
| `ExchangeService` | REST request/response | `place_order`, `cancel_order`, `get_order`, `get_balance`, `get_ticker`, … |
| `ExchangeGateway` | WebSocket streaming | `subscribe_market_depth`, `subscribe_trades`, `subscribe_orders`, `subscribe_balances` |

### Context Integration Patterns

| Relationship | Pattern |
|---|---|
| Any context ↔ MEXC exchange | OHS (Open Host Service) + ACL (Anti-Corruption Layer) |
| Trading ↔ Market | Customer / Supplier |
| Trading ↔ Account | Customer / Supplier |
| System ↔ all | Conformist |

## Full Documentation

| Topic | File |
|-------|------|
| Layer map + rules | [docs/ddd/README.md](../../../docs/ddd/README.md) |
| Canonical terms | [docs/ddd/ubiquitous-language.md](../../../docs/ddd/ubiquitous-language.md) |
| Context boundaries | [docs/ddd/bounded-contexts.md](../../../docs/ddd/bounded-contexts.md) |
| Subdomain types | [docs/ddd/subdomains.md](../../../docs/ddd/subdomains.md) |
| Context relationships | [docs/ddd/context-map.md](../../../docs/ddd/context-map.md) |
| Aggregate invariants | [docs/ddd/aggregates.md](../../../docs/ddd/aggregates.md) |
| Domain events | [docs/ddd/domain-events.md](../../../docs/ddd/domain-events.md) |
| Domain services | [docs/ddd/domain-services.md](../../../docs/ddd/domain-services.md) |
| Use case catalogue | [docs/ddd/application-services.md](../../../docs/ddd/application-services.md) |
| Repository pattern | [docs/ddd/repositories.md](../../../docs/ddd/repositories.md) |

## Enforcement Tools

| Task | Use |
|------|-----|
| Design where logic goes | `/ddd-design` prompt or `ddd-architect` agent |
| Review code for violations | `/ddd-review` prompt or `domain-reviewer` agent |
| Scaffold a use case | `/new-use-case` prompt |
