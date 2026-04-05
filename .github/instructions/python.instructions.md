---
description: 'Python coding conventions for this project (Python 3.11+, FastAPI, DDD)'
applyTo: '**/*.py'
---

# Python Coding Conventions

## Style & Formatting

- Follow **PEP 8**; max line length **100** characters (black + ruff enforced).
- Use 4 spaces for indentation; never tabs.
- Use type hints on **all** function signatures (parameters and return types).
- Use `from __future__ import annotations` only when needed for forward refs.
- Prefer `pathlib.Path` over `os.path`.
- Use `logging` (structured JSON) instead of `print`.

## Naming

- Variables, functions, modules: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Private members: prefix with `_`.

## Functions & Classes

- Keep functions small and single-purpose (≤ 30 lines as a guide).
- Write docstrings (PEP 257) for **public** functions and classes only.
- Avoid deeply nested blocks; use guard clauses to return early.
- Do not add comments for obvious code; comment only the *why*.

## Async

- All I/O must be `async`; never use `time.sleep()` — use `asyncio.sleep()`.
- Use `async with` / `async for` correctly; avoid blocking calls in async context.

## Error Handling

- Use the **Result pattern** (`Ok`/`Err`) for use-case return values.
- Define custom exception classes per domain; avoid bare `except`.
- Validate at system boundaries (interfaces layer); trust domain objects internally.

## DDD Layer Rules

- **Domain**: pure Python, no imports from application/infrastructure/interfaces.
- **Application**: orchestrate only; no business logic; no raw dicts as return types.
- **Interfaces**: validate input (Pydantic), map to VO/Command, call use case, map to DTO.
- **Infrastructure**: implement ports; never call domain services directly.

## Dependencies

- Import standard library first, then third-party, then local (`isort` / ruff `I`).
- Never commit secrets; read from environment variables via `config.py`.
