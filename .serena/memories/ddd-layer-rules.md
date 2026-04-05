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

## Factory pattern (aggregates.py)
- Factory 使用 Aggregate 行為方法重建：build_trading_session() 呼叫 add_order()/record_trade()；build_account_state() 呼叫 record_order()；build_market_snapshot() 呼叫 update_depth()/add_trade()/update_ticker()
- 重建後呼叫 pop_events() 清除重建產生的事件

## Command Object pattern
- Use Case 接受 Command frozen dataclass，不接受散裝 primitives
- 範例：PlaceQrlOrderCommand 含 Side, OrderType, QrlPrice, QrlQuantity, TimeInForce VO
- Controller (Interface 層) 負責 Pydantic → VO → Command 轉換

## Protobuf boundary (CRITICAL)
- Domain must NOT import _pb2
- Application must NOT import _pb2
- Only Infrastructure adapters translate proto → domain
- Use absolute imports: from app.infrastructure.exchange.mexc.generated import Xxx_pb2

## Use Case Result pattern
- Return Ok/Err result, never raise from use cases
- Never return dicts or accept primitives in Use Cases
- Boundary conversion: infra primitives → Use Case converts to VO → Interface converts to DTO

## Value Object ClassVar pattern (avoid RUF012)
Mutable class-level attributes in frozen dataclasses need ClassVar annotation:
```python
from typing import ClassVar
_allowed: ClassVar[set[str]] = {"LIMIT", "MARKET"}
```

## ruff per-file-ignores for generated protobuf
```toml
"src/app/infrastructure/exchange/mexc/generated/**" = ["E402", "E501", "ERA001", "F401", "N999"]
```
See pyproject.toml. NEVER edit _pb2.py files manually.

## Full lint rules: docs/ddd/ddd-lint-rules.md
## Full DDD docs: docs/ddd/
