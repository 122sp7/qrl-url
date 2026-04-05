# DDD Layer Rules — Quick Reference

## Layer Dependency Direction
Interface → Application → Domain ← Infrastructure (Infrastructure implements Application ports)

## What belongs where

| Building Block | Location | Rule |
|---|---|---|
| Value Object | src/app/domain/value_objects/ | Immutable frozen dataclass |
| Entity | src/app/domain/entities/ | Has identity |
| Aggregate Root | src/app/domain/aggregates/ | Consistency boundary |
| Domain Service | src/app/domain/services/ | Stateless, pure Python, no I/O |
| Domain Event | src/app/domain/events/ | Frozen dataclass, past tense |
| Use Case | src/app/application/*/use_cases/ | Orchestration only, Result pattern |
| Port (interface) | src/app/application/ports/ | Protocol class |
| Repository impl | src/app/infrastructure/exchange/ | Implements port |
| HTTP Controller | src/app/interfaces/http/ | Maps DTO ↔ Command/Response |

## Protobuf boundary (CRITICAL)
- Domain must NOT import _pb2
- Application must NOT import _pb2
- Only Infrastructure adapters translate proto → domain
- Use absolute imports: from app.infrastructure.exchange.mexc.generated import Xxx_pb2

## Use Case Result pattern
- Return Ok/Err result, never raise from use cases
- Never return dicts or accept primitives in Use Cases
- Boundary conversion: infra primitives → Use Case converts to VO → Interface converts to DTO

## Full lint rules: docs/ddd/ddd-lint-rules.md
## Full DDD docs: docs/ddd/
