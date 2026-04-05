---
title: "DDD Layer Lint Rules — Protobuf Boundaries"
status: "reference"
updated: "2026-04-05"
tags: ["ddd", "architecture", "protobuf", "lint", "enforcement"]
---

# DDD Layer Lint Rules — Protobuf Boundaries

These rules enforce that protobuf dependencies never leak into Domain or Application layers.

---

## Rules

```yaml
rules:

  # 1. Protobuf location
  - id: protobuf-location
    description: Protobuf definitions must stay in Infrastructure layer only.
    severity: error
    conditions:
      - language: python
        pattern: '\.proto$'
    constraints:
      allowed_paths:
        - src/app/infrastructure/**/proto/**
        - src/app/infrastructure/**/generated/**

  # 2. Forbidden imports in Domain layer
  - id: forbid-protobuf-in-domain
    description: Domain layer must not import protobuf generated code.
    severity: error
    conditions:
      - language: python
        path: src/app/domain/**
        pattern: '_pb2'
    message: >
      Domain layer must not depend on protobuf.
      Use Infrastructure adapters to translate proto messages into Domain entities.

  # 3. Forbidden imports in Application layer
  - id: forbid-protobuf-in-application
    description: Application layer must not import protobuf generated code.
    severity: error
    conditions:
      - language: python
        path: src/app/application/**
        pattern: '_pb2'
    message: >
      Application layer must remain infrastructure-agnostic.
      Protobuf may only appear inside Infrastructure adapters.

  # 4. Correct protobuf import style (Infrastructure only)
  - id: enforce-absolute-protobuf-import
    description: Enforce absolute imports for protobuf generated modules.
    severity: warning
    conditions:
      - language: python
        path: src/app/infrastructure/**
        pattern: 'from\s+\w+_pb2\s+import'
    message: >
      Avoid relative or flat protobuf imports.
      Use absolute imports such as:
      from app.infrastructure.exchange.mexc.generated import Xxx_pb2

  # 5. Adapter responsibility
  - id: require-adapter-mapping
    description: Protobuf messages must be mapped to Domain entities via adapters.
    severity: warning
    conditions:
      - language: python
        path: src/app/infrastructure/**/adapters/**
    message: >
      Infrastructure adapters are responsible for translating protobuf messages
      into Domain entities or Value Objects.
      Domain must not be aware of protobuf existence.

  # 6. Generated code is immutable
  - id: forbid-business-logic-in-generated
    description: Generated protobuf code must not contain business logic.
    severity: error
    conditions:
      - language: python
        path: src/app/infrastructure/**/generated/**
        pattern: 'def\s+(?!__init__)'
    message: >
      Generated protobuf code must remain immutable.
      Do not add business logic or custom methods.

  # 7. Protobuf compilation boundary
  - id: protobuf-compilation-boundary
    description: Protobuf compilation is an infrastructure concern.
    severity: info
    message: >
      Protobuf compilation (grpc_tools.protoc) must be executed via scripts, CI, or Docker.
      Generated code should never be manually edited.
```

---

## Recommendations

- Use Infrastructure adapters to translate proto messages into Domain models.
- Expose Application ports/interfaces instead of protobuf types.
- Treat protobuf definitions as external contracts.
- Allow swapping exchanges without touching Domain or Application layers.

---

## Import Examples

```python
# Good
from app.infrastructure.exchange.mexc.generated import PrivateOrdersV3Api_pb2
from app.infrastructure.exchange.mexc.adapters.order_mapper import to_domain

# Bad
from PrivateOrdersV3Api_pb2 import Order
import PrivateOrdersV3Api_pb2
```

---

See also: [exchange-gateway.md](../architecture/exchange-gateway.md), [bounded-contexts.md](bounded-contexts.md)
