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
- TradingSession (src/app/domain/aggregates/trading_session.py) — 含 add_order(), record_trade(), close_order(), pop_events()
- AccountState (src/app/domain/aggregates/account_state.py) — 含 record_order(), refresh(), pop_events()
- MarketSnapshot (src/app/domain/aggregates/market_snapshot.py) — 含 update_depth(), update_ticker(), add_trade(), pop_events()

## Key Ports
- ExchangeService: src/app/application/ports/exchange_service.py
- ExchangeGateway: src/app/application/ports/exchange_gateway.py

## Domain Services (src/app/domain/services/)
- BalanceComparisonRule, DepthCalculator, SlippageAnalyzer, ValuationService (原有)
- LimitPriceCalculator — 計算 maker limit price；compute() 計算 spread 內 limit price，best_price() 取最佳報價

## PlaceQrlOrder Use Case
- Use Case: src/app/application/trading/qrl/place_qrl_order.py — 接受 PlaceQrlOrderCommand (frozen dataclass, 含完整 VO)
- Controller: src/app/interfaces/http/api/qrl_routes.py — 負責 Pydantic schema → VO → PlaceQrlOrderCommand 轉換

## Import convention
- 統一使用 from src.app.domain... / from src.app.application... (禁止 from app.domain...)

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

## Deployment (最新)
- GCloud Project: qrl-api
- Service: qrl-trading-api, Region: asia-southeast1
- URL: https://qrl-trading-api-545492969490.asia-southeast1.run.app
- 最新 revision: qrl-trading-api-00285-szh (2026-04-05, Build ddf9ac6e)
