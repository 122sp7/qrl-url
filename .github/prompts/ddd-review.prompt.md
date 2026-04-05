---
name: ddd-review
description: Review a file or module for DDD layer violations and Ubiquitous Language compliance
agent: domain-reviewer
tools:
  - search/codebase
  - search/usages
---

Review the following file or module for DDD compliance:

**Target**: ${input:target} (file path or module name, e.g. `src/app/application/trading/use_cases/place_order.py`)

Check against the project's DDD knowledge base:

## 1. Import Violations
Scan all `import` statements. Flag any that violate:
```
Domain     → must NOT import application / interfaces / infrastructure
Application → must NOT import infrastructure / interfaces
Interfaces  → must NOT import infrastructure directly
```
Reference: [docs/ddd/bounded-contexts.md](docs/ddd/bounded-contexts.md)

## 2. Business Logic Placement
- Domain logic inside use cases or controllers → CRITICAL
- Infrastructure calls inside domain → CRITICAL
- `if/else` business decisions in repositories → WARNING

## 3. Ubiquitous Language
Compare all class/function/variable names against [docs/ddd/ubiquitous-language.md](docs/ddd/ubiquitous-language.md).
Flag any term that uses synonyms, abbreviations, or HTTP vocabulary in domain code.

## 4. Aggregate Rules
Verify against [docs/ddd/aggregates.md](docs/ddd/aggregates.md):
- External code mutating child entities directly (bypass aggregate root)?
- Cross-aggregate object references instead of identity references?

## 5. Application Use Case Structure
Verify against [docs/ddd/application-services.md](docs/ddd/application-services.md):
- Accepts typed Command/Query (not primitives or dicts)?
- Returns `Ok(...) | Err(...)` (Result pattern)?
- No business logic (only orchestration)?

## 6. Domain Events
Verify against [docs/ddd/domain-events.md](docs/ddd/domain-events.md):
- Named in past tense?
- Frozen dataclass?
- Not crossing boundaries as raw dicts?

## Output

For each violation:
| File | Line | Severity | Rule | Fix |
|------|------|----------|------|-----|

End with a **verdict**: PASS / NEEDS FIXES / CRITICAL VIOLATIONS.
