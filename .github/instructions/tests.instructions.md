---
description: 'Test conventions for this project (pytest, pytest-asyncio, DDD layers)'
applyTo: 'tests/**/*.py'
---

# Test Conventions

## Framework

- Use **pytest** + **pytest-asyncio** (`asyncio_mode = auto` in `pyproject.toml`/`pytest.ini`).
- All async tests use `async def test_*` — no `@pytest.mark.asyncio` decorator needed.
- Use `httpx.MockTransport` to mock external HTTP calls; never hit real APIs in tests.

## Structure

- Follow **Arrange / Act / Assert** within each test function.
- One logical assertion per test; use `assert` with descriptive messages.
- Test file mirrors the source path: `src/app/domain/X.py` → `tests/domain/test_X.py`.

## Naming

- Test functions: `test_<what>_<expected_outcome>` (e.g., `test_place_order_returns_ok_when_valid`).
- Fixtures: descriptive nouns (e.g., `valid_order_command`, `mock_exchange_gateway`).

## Coverage

- Minimum **80%** coverage on domain and application layers.
- All use case happy paths and main error paths must be covered.
- Domain Value Objects must have unit tests for validation rules.

## Mocking

- Mock at the **port boundary** (application ports), not inside domain objects.
- Use `pytest` fixtures with `scope="function"` by default; `scope="module"` only for expensive setup.
- Avoid `unittest.mock.patch` on internal domain functions; redesign instead.

## Forbidden

- No `time.sleep()` in tests.
- No real network calls, file writes, or Redis connections without explicit integration test markers.
- Do not test private methods (`_*`) directly.
