---
name: new-use-case
description: Scaffold a new DDD use case following project conventions
agent: agent
tools:
  - search/codebase
  - create_file
  - replace_string_in_file
---

Scaffold a new use case for this Python DDD project.

**Module**: ${input:module} (e.g. `trading`, `market`, `account`)
**Use Case name**: ${input:use_case_name} (e.g. `PlaceQrlOrder`)

Follow these steps:

1. **Domain** – if new Value Objects or Entities are needed, create them under
   `src/app/domain/value_objects/` or `src/app/domain/entities/`.
   Reference existing examples in those folders.

2. **Application Use Case** – create
   `src/app/application/${input:module}/use_cases/${input:use_case_name_snake}.py`.
   - Accept a `Command` or `Query` dataclass (no raw dicts).
   - Return `Ok(result)` or `Err(error)` using the Result pattern.
   - Inject dependencies via constructor (port interfaces only, no infra).
   - Reference `src/app/application/trading/use_cases/` for patterns.

3. **Interface Controller** – add or update a route in
   `src/app/interfaces/http/`.
   - Validate input with Pydantic.
   - Convert to VO/Command; call use case; map result to response DTO.
   - No business logic in the controller.

4. **Unit Test** – create `tests/${input:module}/test_${input:use_case_name_snake}.py`.
   - Mock all port dependencies.
   - Cover happy path and main error path.
   - Use `async def test_*` with `pytest-asyncio`.

5. **Imports** – verify all `__init__.py` exports are updated where needed.

After scaffolding, summarise the files created and any manual wiring steps remaining.
