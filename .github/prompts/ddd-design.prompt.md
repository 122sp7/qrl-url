---
name: ddd-design
description: Decide where new logic belongs in the DDD architecture before writing any code
agent: ddd-architect
tools:
  - search/codebase
  - search/usages
---

I need to add the following logic to the project:

**Description**: ${input:description}

Before writing any code, analyse the request against the project's DDD knowledge base and produce a **Design Decision** that covers:

1. Which **Bounded Context** owns this logic (Trading / Market / Account / System)?
2. Which **subdomain type** (Core / Supporting / Generic)?
3. Which **DDD building block** is most appropriate:
   - Value Object — immutable, identity-less domain concept
   - Entity — has identity, mutable lifecycle
   - Aggregate Root — consistency boundary over a cluster of objects
   - Domain Service — stateless logic spanning multiple objects
   - Application Use Case — orchestration of domain + infrastructure
   - Port — abstract interface for infrastructure
   - Infrastructure Adapter — concrete implementation of a port
4. Where exactly does the file go (`src/app/<layer>/<module>/`)?
5. Is the proposed **term** consistent with `docs/ddd/ubiquitous-language.md`?
6. Does this operation cross a context boundary? If yes, how (DTO / Domain Event)?

Reference:
- [Ubiquitous Language](../../docs/ddd/ubiquitous-language.md)
- [Bounded Contexts](../../docs/ddd/bounded-contexts.md)
- [Aggregates](../../docs/ddd/aggregates.md)
- [Domain Services](../../docs/ddd/domain-services.md)
- [Application Services](../../docs/ddd/application-services.md)
- [Context Map](../../docs/ddd/context-map.md)

Do **not** write implementation code — produce only the design decision and step-by-step plan.
