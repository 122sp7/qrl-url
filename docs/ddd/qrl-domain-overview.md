---
title: "QRL/USDT Trading Bot — Domain Overview"
status: "reference"
updated: "2026-04-05"
tags: ["ddd", "domain", "qrl", "value-objects", "events", "aggregates"]
---

# QRL/USDT Trading Bot — Domain Overview

This document is the canonical reference for all Domain building blocks in the QRL/USDT trading bot.

---

## 1. Value Objects

| VO | Description | Example |
|----|-------------|---------|
| `Symbol` | Trading pair | `"QRL/USDT"` |
| `OrderType` | Order type | `"MARKET"` / `"LIMIT"` |
| `OrderSide` | Direction | `"BUY"` / `"SELL"` |
| `Quantity` | Order size | `Decimal('10')` QRL |
| `Price` | Limit price | `Decimal('0.12')` USDT |
| `Percentage` | Allocation ratio | `0.0 – 1.0` |
| `TimeFrame` | Kline interval | `"1m"`, `"5m"`, `"1h"` |
| `Signal` | Trading signal | `"BUY"` / `"SELL"` / `"HOLD"` + strength 0–1 |
| `PnL` | Profit & Loss | realized / unrealized |
| `Balance` | Account asset quantity | QRL / USDT amount |
| `TradeId` | Trade identifier | UUID |
| `Timestamp` | Event time | datetime |
| `OrderStatus` | Order state | `"NEW"`, `"FILLED"`, `"CANCELED"`, `"PARTIALLY_FILLED"` |
| `OrderId` | Order identifier | string / UUID |
| `TickSize` | Minimum price movement | used for limit order adjustment |
| `StepSize` | Minimum order quantity | validated before placing order |
| `KlineData` | Candlestick data | open, high, low, close, volume |
| `Slippage` | Price slippage | used in risk calculation |
| `MaxExposure` | Maximum position limit | 0–1, risk control |
| `Fee` | Trading fee | used in P&L calculation |
| `Leverage` | Leverage multiplier | ignored for spot |

---

## 2. Domain Events

| Event | Description | Trigger |
|-------|-------------|---------|
| `OrderPlaced` | Order successfully submitted | `OrderService` on success |
| `OrderCancelled` | Order cancelled | User or system cancel |
| `OrderFilled` | Order fully filled | Market fill report |
| `OrderPartiallyFilled` | Order partially filled | Market report |
| `OrderRejected` | Order rejected by exchange | API error response |
| `TradeExecuted` | Trade completed | Includes qty, price, fee |
| `PriceUpdated` | Market price updated | Kline / Ticker update |
| `SignalGenerated` | Trading signal generated | Strategy triggers buy/sell/hold |
| `StrategySignalGenerated` | Strategy-level signal | e.g. MA crossover, RSI |
| `PositionUpdated` | Position changed | QRL position increase/decrease |
| `PositionOpened` | New position created | After market fill |
| `PositionClosed` | Position closed | Full sell or strategy close |
| `PnLUpdated` | P&L changed | Real-time monitoring |
| `BalanceUpdated` | Account balance changed | Any fund change |
| `RiskLimitBreached` | Risk limit triggered | Position too large or insufficient funds |
| `RiskLimitUpdated` | Risk limit adjusted | Dynamic max position or slippage change |
| `StopLossTriggered` | Stop-loss event | Auto close |
| `TakeProfitTriggered` | Take-profit event | Auto close |
| `TrailingStopUpdated` | Trailing stop adjusted | Based on high/low price |
| `PriceAlertTriggered` | Price alert reached | Technical indicator or price monitor |
| `BotStarted` | Bot started | System startup event |
| `BotStopped` | Bot stopped | System shutdown event |

---

## 3. Entities & Aggregates

| Entity / Aggregate | Description | Contains |
|-------------------|-------------|---------|
| `Order` | Order entity | symbol, type, side, quantity, price, status, fee |
| `Position` | Position entity | symbol, quantity, avg_price, unrealized_pnl |
| `Portfolio` | Aggregate Root | multiple Positions, max exposure, risk control |
| `Trade` | Trade entity | order_id, executed_qty, price, fee, timestamp |
| `Strategy` | Aggregate Root / behaviour | generates `StrategySignalGenerated`, uses `KlineData` |
| `Bot` | Bot entity | manages state (running/stopped), risk limits, portfolio |

---

## 4. Architecture Diagram

```
+------------------------------------------------------+
|                      Application                     |
|  (Orchestrates domain logic & infrastructure)        |
|------------------------------------------------------|
|  OrderService         StrategyService                |
|  RiskManager          BotController                  |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                       Domain                         |
|------------------------------------------------------|
|  Entities / Aggregates                               |
|  Order, Position, Portfolio, Trade, Bot              |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                   Domain Value Objects               |
|------------------------------------------------------|
|  Symbol, OrderType, OrderSide, Quantity, Price       |
|  PnL, Balance, Slippage, MaxExposure, Fee, ...       |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                     Domain Events                    |
|------------------------------------------------------|
|  OrderPlaced, OrderFilled, TradeExecuted             |
|  SignalGenerated, PositionOpened, BotStarted, ...    |
+------------------------------------------------------+
            ↓
+------------------------------------------------------+
|                  Infrastructure                      |
|------------------------------------------------------|
|  MexcClient — place_order, cancel_order              |
|             — get_order_status, get_balance          |
|             — subscribe_klines, subscribe_ticker     |
+------------------------------------------------------+
```

---

## 5. Layer Responsibilities

| Layer | Responsibility |
|-------|---------------|
| Application | Coordinates only: receives signals, calculates order size, calls Infrastructure, emits Domain Events |
| Domain | Entities/Aggregates enforce consistency and business rules |
| Value Objects | Immutable, validated single-concept wrappers |
| Domain Events | Describe what happened inside the domain; no side effects |
| Infrastructure | Wraps MEXC v3 API; Domain never calls API directly |

---

See also: [aggregates.md](aggregates.md), [domain-events.md](domain-events.md), [ubiquitous-language.md](ubiquitous-language.md)
