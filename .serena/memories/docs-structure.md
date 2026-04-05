# docs/ Structure (updated 2026-04-05)

## Layout

```
docs/
├── README.md                       ← total index with cross-links
├── CHANGELOG.md
├── ddd/                            ← DDD reference (stable, do not restructure)
│   ├── README.md
│   ├── ubiquitous-language.md
│   ├── bounded-contexts.md
│   ├── subdomains.md
│   ├── context-map.md
│   ├── aggregates.md
│   ├── domain-events.md
│   ├── domain-services.md
│   ├── application-services.md
│   ├── repositories.md
│   ├── qrl-domain-overview.md      ← NEW: QRL VOs, events, aggregates
│   └── ddd-lint-rules.md           ← NEW: protobuf boundary enforcement rules
├── architecture/                   ← NEW: technical design decisions
│   ├── exchange-gateway.md         ← ExchangeGateway port + MEXC WS adapter
│   ├── event-bus-domain-events.md  ← Event bus + mapper pipeline
│   ├── qrl-domain-model.md         ← QRL-specific files reference
│   └── dashboard-realtime-flow.md  ← Full data flow MEXC → dashboard
├── plans/                          ← NEW: working analysis & refactor plans
│   ├── gap-analysis.md
│   ├── allocation-refactor-plan.md
│   ├── allocation-chain-optimization.md
│   └── cloud-scheduler-rebalance-plan.md
└── runbooks/                       ← NEW: operational commands
    ├── cloud-scheduler-oidc.md
    └── gcloud-commands.md
```

## Removed files
- docs/0.md–6.md (unnamed numbered files, content migrated to architecture/)
- docs/comment.md (PowerShell script → runbooks/gcloud-commands.md)
- .github/qrl_usdt_trading_domain.md (migrated to docs/ddd/qrl-domain-overview.md)

## .gitignore
- Copilot-Processing.md added to root .gitignore
