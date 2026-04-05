---
description: 'DDD layer rules and Ubiquitous Language enforcement for this project'
applyTo: '**/*.py'
---

# DDD Architecture Rules

> Based on Implementing Domain-Driven Design (Vaughn Vernon).
> Full knowledge base: [docs/ddd/](../../docs/ddd/README.md)

## Layer Dependency Direction

```
Domain ← Application ← Interfaces
                     ← Infrastructure
```

Outer layers may import inner layers. **Inner layers must never import outer layers.**

| Layer path | May import | Must NOT import |
|---|---|---|
| `src/app/domain/` | stdlib, frozen dataclasses only | application, interfaces, infrastructure |
| `src/app/application/` | domain, ports/* | infrastructure, interfaces |
| `src/app/interfaces/` | application, domain VOs | infrastructure (directly) |
| `src/app/infrastructure/` | domain, application ports | interfaces |

## Aggregate Rules

- All state changes go through the **Aggregate Root** — never mutate child entities from outside.
- Aggregates reference each other by **identity only** (e.g. `SubAccountId`), never by direct object reference.
- One aggregate is modified per use case transaction.
- See [docs/ddd/aggregates.md](../../docs/ddd/aggregates.md) for invariants per aggregate.

## Ubiquitous Language

Use terms exactly as defined in [docs/ddd/ubiquitous-language.md](../../docs/ddd/ubiquitous-language.md).

**Forbidden in domain code:**

```python
# ❌ Never return or accept primitives across use case boundaries
def execute(self) -> dict: ...
def execute(self, symbol: str) -> str: ...

# ✅ Use typed VOs and DTOs
def execute(self) -> Ok[PlaceOrderResultDTO] | Err[DomainException]: ...
def execute(self, command: PlaceOrderCommand) -> Ok[PlaceOrderResultDTO] | Err[DomainException]: ...
```

## Domain Services

Only create a Domain Service when the operation:
- Spans multiple aggregates or value objects.
- Does not conceptually belong to one of them.
- Is **stateless** and **pure Python** (no I/O).

See: [docs/ddd/domain-services.md](../../docs/ddd/domain-services.md)

## Application Use Cases

```python
# ✅ Correct Use Case structure
class PlaceOrderUseCase:
    def __init__(self, exchange: ExchangeService) -> None:
        self._exchange = exchange  # port only, never infra

    async def execute(self, command: PlaceOrderCommand) -> Ok[PlaceOrderResultDTO] | Err[Exception]:
        # 1. load / validate via domain services
        # 2. call domain logic
        # 3. persist via port
        # 4. return Ok(dto) or Err(exception)
```

- No `if/else` business decisions in use cases.
- No primitives as parameters or return types.
- See [docs/ddd/application-services.md](../../docs/ddd/application-services.md)

## Domain Events

- Named in **past tense**: `OrderPlaced`, not `PlaceOrder`.
- **Immutable** (`@dataclass(frozen=True)`).
- Cross the infra boundary only via `ExchangeGateway` / `ExchangeService` ports.
- See [docs/ddd/domain-events.md](../../docs/ddd/domain-events.md)

## Repositories

- Interface lives in `application/ports/`; implementation in `infrastructure/`.
- Return domain objects (VOs, Entities, Aggregates) — never dicts or ORM models.
- Cache (Redis) is an infrastructure-only concern.
- See [docs/ddd/repositories.md](../../docs/ddd/repositories.md)

## Bounded Contexts

This project has 4 contexts: **Trading** (Core), **Market**, **Account**, **System**.
Contexts communicate via DTOs and Domain Events — never via shared domain classes.
See [docs/ddd/bounded-contexts.md](../../docs/ddd/bounded-contexts.md)
