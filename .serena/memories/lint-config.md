# Ruff & Pytest Configuration

## pyproject.toml (created at project root)

### Ruff
- line-length: 100, target-version: py311
- select: E,F,I,N,W,UP,B,A,C4,DTZ,T10,ISC,ICN,PIE,PT,Q,SIM,ARG,ERA,PD,PL,NPY,RUF
- Global ignore: B008 (FastAPI Depends() in default args is canonical DI pattern)
- per-file-ignores for generated protobuf:
  - `src/app/infrastructure/exchange/mexc/generated/**`
  - suppresses: E402, E501, ERA001, F401, N999
  - NEVER manually edit generated/_pb2.py files

### Pytest
- asyncio_mode = "auto"
- testpaths = ["tests"]
- pythonpath = [".", "src"]  ← fixes both src.app.X and app.X import styles

## requirements-dev.txt
Added: `pytest>=8.0` and `pytest-asyncio>=0.23`
(was missing; caused "Unknown config option: asyncio_mode" warning)

## Makefile
- lint: `ruff check src/ tests/`   ← was wrong (non-existent directories)
- test: `pytest`

## Running ruff without venv
Use `uvx ruff check src/ tests/` when ruff is not installed globally.

## Running pytest without venv
Use `uvx --with pytest-asyncio pytest tests/` for full async test support.

## Known pre-existing issue
`exchange_gateway.py` and `trade_mapper.py` use `from app.domain...` (no src. prefix).
Fixed by `pythonpath = [".", "src"]` in pytest config.
