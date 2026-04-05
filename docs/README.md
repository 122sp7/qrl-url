---
title: "Documentation Index"
updated: "2026-04-05"
---

# Documentation Index — QRL/USDT Trading Bot

## Structure

```
docs/
├── README.md                          ← this file
├── CHANGELOG.md                       ← release notes
│
├── ddd/                               ← Domain-Driven Design reference
├── architecture/                      ← technical design decisions
├── plans/                             ← work-in-progress analysis & refactor plans
└── runbooks/                          ← operational commands & setup guides
```

---

## DDD Reference (`docs/ddd/`)

Core domain model, bounded contexts, and architecture rules. **Start here** when making design decisions.

| File | Purpose |
|------|---------|
| [README.md](ddd/README.md) | DDD layer map and quick reference |
| [ubiquitous-language.md](ddd/ubiquitous-language.md) | Canonical term definitions |
| [bounded-contexts.md](ddd/bounded-contexts.md) | The 4 context boundaries |
| [subdomains.md](ddd/subdomains.md) | Core / Supporting / Generic subdomains |
| [context-map.md](ddd/context-map.md) | OHS-ACL, Customer-Supplier relationships |
| [aggregates.md](ddd/aggregates.md) | TradingSession, AccountState, MarketSnapshot |
| [domain-events.md](ddd/domain-events.md) | OrderEvent, TradeEvent, BalanceEvent, MarketDepthEvent |
| [domain-services.md](ddd/domain-services.md) | QrlGuards, SlippageAnalyzer, ValuationService |
| [application-services.md](ddd/application-services.md) | All use cases and port interfaces |
| [repositories.md](ddd/repositories.md) | Exchange-backed and cache-backed repositories |
| [qrl-domain-overview.md](ddd/qrl-domain-overview.md) | QRL/USDT full domain model (VOs, events, aggregates) |
| [ddd-lint-rules.md](ddd/ddd-lint-rules.md) | Protobuf boundary enforcement rules |

---

## Architecture (`docs/architecture/`)

Technical design decisions and component integration patterns.

| File | Purpose |
|------|---------|
| [exchange-gateway.md](architecture/exchange-gateway.md) | ExchangeGateway port, MEXC WS adapter, proto → domain mapper |
| [event-bus-domain-events.md](architecture/event-bus-domain-events.md) | Event bus design, mapper pipeline, backpressure |
| [qrl-domain-model.md](architecture/qrl-domain-model.md) | QRL-specific files: hardcoded symbol, guards, WS state |
| [dashboard-realtime-flow.md](architecture/dashboard-realtime-flow.md) | Full data flow: MEXC → infrastructure → application → dashboard |

---

## Plans (`docs/plans/`)

Analysis documents and refactor plans. These are working documents; refer to [CHANGELOG.md](CHANGELOG.md) for completed work.

| File | Purpose |
|------|---------|
| [gap-analysis.md](plans/gap-analysis.md) | Current state snapshot and convergence priorities |
| [allocation-refactor-plan.md](plans/allocation-refactor-plan.md) | `/tasks/allocation` refactor with VO pipeline and slippage checks |
| [allocation-chain-optimization.md](plans/allocation-chain-optimization.md) | Micro-order sizing and execution chain analysis |
| [cloud-scheduler-rebalance-plan.md](plans/cloud-scheduler-rebalance-plan.md) | Cloud Scheduler rebalance integration plan |

---

## Runbooks (`docs/runbooks/`)

Operational commands and setup guides for production.

| File | Purpose |
|------|---------|
| [cloud-scheduler-oidc.md](runbooks/cloud-scheduler-oidc.md) | Cloud Scheduler → Cloud Run OIDC setup (Windows & Linux) |
| [gcloud-commands.md](runbooks/gcloud-commands.md) | Common gcloud CLI commands reference |

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
