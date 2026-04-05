# Subdomains

> IDDD Ch. 2 — *"A subdomain is a sub-part of your overall business domain. Subdomains are discovered through domain analysis and are used to identify what the business considers important."*

Vernon classifies subdomains into three types:

| Type | Definition |
|------|-----------|
| **Core Domain** | The strategic differentiator; where the most investment belongs. |
| **Supporting Subdomain** | Necessary to support the core, but not differentiating. |
| **Generic Subdomain** | Common to many businesses; can be bought or sourced off-the-shelf. |

---

## Core Domain — QRL Trading Intelligence

**Why core**: This is the system's reason for existing. The decisions about *when* and *how* to place QRL/USDT orders, guard conditions, slippage analysis, and the trading session model are proprietary logic that provides competitive value.

**What it contains**:
- `TradingSession` aggregate — manages order and trade state for a symbol session
- `QrlGuards` domain service — price range, balance sufficiency, duplicate prevention, rate limiting
- `SlippageAnalyzer` domain service — slippage detection and tolerance validation
- `ValuationService` domain service — mid-price and cost calculations
- All QRL-specific VOs: `QrlPrice`, `QrlQuantity`, `QrlUsdtPair`
- `OrderCommand` VO — encapsulates a validated trade instruction

**Code path**: `src/app/domain/` + `src/app/application/trading/`

**Investment priority**: High. New trading logic, guard rules, and session behaviour belong here first.

---

## Supporting Subdomain — Market Data

**Why supporting**: Real-time market data is required to trade, but the logic for *fetching* and *structuring* it is not proprietary. It supports Trading decisions without being the decision itself.

**What it contains**:
- `MarketSnapshot` aggregate — composed view of ticker, depth, and klines
- `OrderBook` / `Kline` constructs
- Market use cases: `GetTicker`, `GetDepth`, `GetKline`, `GetStats24h`, `GetMarketTrades`

**Code path**: `src/app/domain/aggregates/market_snapshot.py` + `src/app/application/market/`

**Investment priority**: Medium. Optimise for data freshness and caching (Redis TTL); avoid over-modelling.

---

## Supporting Subdomain — Account Management

**Why supporting**: Knowing the current balance is a prerequisite for trading decisions, but the balance management itself (credit, debit, reconciliation) lives on the exchange, not here.

**What it contains**:
- `AccountState` aggregate — reflects current USDT and QRL positions
- `Account` entity, `Balance` VO, `NormalizedBalances` VO
- Use case: `GetBalance`

**Code path**: `src/app/domain/aggregates/account_state.py` + `src/app/application/account/`

**Investment priority**: Low–Medium. Defer complexity; the exchange is the source of truth.

---

## Generic Subdomain — Exchange Integration (MEXC V3 API)

**Why generic**: REST/WebSocket integration with a centralised exchange is a well-understood engineering problem with no domain differentiation. It could be replaced by a different exchange adapter without changing the core domain.

**What it contains**:
- `ExchangeGateway` port (WebSocket streams)
- `ExchangeService` port (REST request/response)
- Infrastructure adapters in `src/app/infrastructure/exchange/` and `external/`
- HMAC-SHA256 signing, retry/backoff, rate-limit handling

**Code path**: `src/app/application/ports/` (interfaces) + `src/app/infrastructure/` (implementations)

**Investment priority**: Low. Use proven patterns; do not invent. Replace with a generic library if one becomes available.

---

## Generic Subdomain — Infrastructure Plumbing

**Why generic**: Redis caching, Cloud Run deployment, Cloud Scheduler, structured logging, and configuration management are commodity concerns shared with virtually every cloud service.

**What it contains**:
- `src/app/infrastructure/config.py`
- Redis client, Docker, Cloud Run health endpoint
- `cloudbuild.yaml`, `Dockerfile`

**Investment priority**: Minimal. Follow established patterns; keep it boring.

---

## Summary

```
┌─────────────────────────────────────────────────────┐
│                   CORE DOMAIN                       │
│          QRL Trading Intelligence                   │
│   TradingSession · QrlGuards · SlippageAnalyzer     │
│         OrderCommand · QrlPrice · QrlQuantity        │
└───────────────────┬─────────────────────────────────┘
                    │ uses
        ┌───────────┴──────────┐
        │                      │
┌───────▼──────────┐  ┌────────▼─────────┐
│  SUPPORTING:     │  │  SUPPORTING:     │
│  Market Data     │  │  Account Mgmt    │
│  MarketSnapshot  │  │  AccountState    │
│  Ticker · Depth  │  │  Balance         │
└───────┬──────────┘  └────────┬─────────┘
        │                      │
        └──────────┬───────────┘
                   │ via ports
        ┌──────────▼──────────────────────┐
        │        GENERIC:                 │
        │  MEXC V3 Exchange Integration   │
        │  ExchangeService · Gateway      │
        │  Redis · Cloud Run · Scheduler  │
        └─────────────────────────────────┘
```
