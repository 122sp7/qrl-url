# Project Overview — qrl-url (QRL/USDT Trading Bot)

## Tech Stack
- Python 3.11+, FastAPI, httpx, websockets, Redis
- MEXC V3 API (REST + WebSocket + protobuf)
- Cloud Run + Cloud Scheduler + Cloud Build
- DDD 4-layer: Interface → Application → Domain → Infrastructure

## Bounded Contexts
| Context | Type | Path |
|---------|------|------|
| Trading | Core Domain | src/app/application/trading/ |
| Market | Supporting | src/app/application/market/ |
| Account | Supporting | src/app/application/account/ |
| System | Generic | src/app/application/system/ |

## Key Aggregates
- TradingSession (src/app/domain/aggregates/trading_session.py)
- AccountState (src/app/domain/aggregates/account_state.py)
- MarketSnapshot (src/app/domain/aggregates/market_snapshot.py)

## Key Ports
- ExchangeService: src/app/application/ports/exchange_service.py
- ExchangeGateway: src/app/application/ports/exchange_gateway.py

## QRL-specific hardcoded files
- domain/value_objects/qrl_price.py (TICK_SIZE = 0.0001)
- domain/value_objects/qrl_quantity.py
- infrastructure/exchange/mexc/qrl/ (all QRL REST/WS clients)

## Infrastructure entry points
- main.py → FastAPI app
- Dockerfile (Cloud Run, port 8080)
- /tasks/allocation → AllocationUseCase (Cloud Scheduler trigger)
- /tasks/rebalance → RebalanceUseCase

## Style rules
- black line-length 100, py311
- ruff select E,F,I,N,W,UP,B,A,C4,DTZ,T10,ISC,ICN,PIE,PT,Q,SIM,ARG,ERA
- max_file_length: 4000 chars
- pytest asyncio_mode auto
