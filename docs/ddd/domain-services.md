# Domain Services

> IDDD Ch. 7 — *"A Domain Service is used when an operation doesn't conceptually belong to any domain object. It is stateless and operates on domain objects passed to it as parameters."*

Vernon's criteria for a Domain Service:
- The operation is a significant domain concept.
- It involves multiple aggregates or value objects — it does not belong to any one of them.
- It is **stateless** — it holds no instance variables.
- It is **pure Python** — no I/O, no infrastructure dependencies.

---

## QrlGuards

**File**: `src/app/domain/services/qrl_guards.py`
**Purpose**: Business guard rules specific to QRL/USDT trading. These conditions must hold before any order is submitted.

| Function | Invariant Enforced |
|----------|-------------------|
| `ensure_price_range(price, min, max)` | QRL price must be within an optional allowed band. Prevents fat-finger orders or runaway strategies. |
| `ensure_sufficient_balance(available_usdt, cost)` | Available USDT must cover the full order cost. Prevents overdraft attempts. |
| `prevent_duplicate(client_order_id, existing_ids)` | A `ClientOrderId` must not be reused within the same session. Ensures idempotency. |
| `enforce_rate_limit(remaining_requests)` | Must have remaining API capacity before submitting. Prevents exchange bans. |

**Usage**: Called by `PlaceOrder` use case before invoking the exchange port.

```python
# Application layer usage pattern
qrl_guards.ensure_price_range(command.price, config.min_price, config.max_price)
qrl_guards.ensure_sufficient_balance(balance.available, command.cost())
qrl_guards.prevent_duplicate(command.client_order_id, session.existing_ids())
```

---

## SlippageAnalyzer

**File**: `src/app/domain/services/slippage_analyzer.py`
**Purpose**: Compute expected vs. actual slippage for an order and determine if it is within tolerance.

| Operation | Description |
|-----------|-------------|
| `calculate_slippage(expected_price, actual_price)` | Returns a `Slippage` VO representing the percentage deviation. |
| `is_within_tolerance(slippage, max_tolerance)` | Returns `True` if the slippage is acceptable. |

**Why a Domain Service**: Slippage calculation uses both `QrlPrice` (an order VO) and market data (`Ticker`). It belongs to neither aggregate exclusively.

---

## ValuationService

**File**: `src/app/domain/services/valuation_service.py`
**Purpose**: Compute monetary values derived from market and order data.

| Operation | Description |
|-----------|-------------|
| `calculate_mid_price(order_book)` | Returns the `Price` midpoint between best bid and best ask. |
| `calculate_order_cost(price, quantity)` | Returns the gross USDT cost of a potential order (before fees). |

**Why a Domain Service**: Cost and mid-price calculations span both `OrderBook` (market) and `Quantity`/`Price` (trading) — neither aggregate owns this logic.

---

## DepthCalculator

**File**: `src/app/domain/services/depth_calculator.py`
**Purpose**: Analyse order book depth to assess liquidity and market impact.

| Operation | Description |
|-----------|-------------|
| `cumulative_volume_at_price(book, price_limit)` | Returns total available volume up to a given price level. |
| `estimated_fill_price(book, quantity)` | Estimates volume-weighted average fill price for a quantity. |

---

## BalanceComparisonRule

**File**: `src/app/domain/services/balance_comparison_rule.py`
**Purpose**: Express and evaluate named rules for comparing balance states.

Used to detect rebalancing triggers (e.g. QRL/USDT ratio drifts beyond threshold).

| Operation | Description |
|-----------|-------------|
| `evaluate(current, target, tolerance)` | Returns a `BalanceComparisonResult` VO indicating the deviation direction and magnitude. |

---

## Domain Service Rules

1. **No infrastructure**: Domain services must not call Redis, the exchange API, or any I/O.
2. **No state**: They are functions operating on VOs and entities passed as arguments.
3. **No application layer awareness**: They do not know about use cases or DTOs.
4. **Testable in isolation**: Each function can be unit-tested with pure domain objects, no mocks required.
5. **Named as domain concepts**: `SlippageAnalyzer`, `QrlGuards` — not `SlippageHelper` or `OrderUtil`.
