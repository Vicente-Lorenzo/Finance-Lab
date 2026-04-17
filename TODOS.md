# Quant Trading Framework - Implementation Plan (TODOs)

This document tracks the phased implementation to modernize the Quant Trading Framework. It serves as a master checklist.
**Instructions for LLM Assistants:** When provided this file, review the checked items (`[x]`) to understand the current progress, and begin work on the first unchecked item (`[ ]`). Phases are unordered headings — work top-to-bottom; completed phases are removed, not crossed out.

---

## Database Setup (`Quant` on PostgreSQL + TimescaleDB)

Stand up the full seven-schema database described in `DATABASE.md`. Each table has a companion class inheriting `PostgresDatabaseAPI` with a typed `_STRUCTURE_` so the framework can `migrate()` / `create()` / `upsert()` it directly. Work schema-by-schema; do not skip ahead until the previous schema migrates cleanly.

- [ ] **Schema: `Universe`** (static reference data)
  - [ ] `CategoryDatabaseAPI` — asset classes (Equity, FX, Crypto, Futures, ...). Replaces the previously separate `AssetClass` table.
  - [ ] `ProviderDatabaseAPI` — data/broker providers (Bloomberg, YahooFinance, cTrader_ICMarkets, ...).
  - [ ] `TickerDatabaseAPI` — canonical tickers (EURUSD, AAPL, ...).
  - [ ] `TimeframeDatabaseAPI` — supported timeframes (M1, M5, H1, D1, ...).
  - [ ] `SecurityDatabaseAPI` — composite (Ticker + Provider + Category) with provider-specific symbol mapping.
  - [ ] `SymbolDatabaseAPI` — broker-specific tick/lot/swap/commission metadata (already exists in `Warehouse/Symbol.py`; wire into `Universe` schema).
- [ ] **Schema: `Market`** (hypertables)
  - [ ] `TickDatabaseAPI`, `BarDatabaseAPI` moved under `Market` schema; configure 1-minute base bar + continuous aggregates for H1/D1/W1/MN1.
- [ ] **Schema: `Alternative`** (hypertables)
  - [ ] `EconomicDatabaseAPI`, `SentimentDatabaseAPI`.
- [ ] **Schema: `Indicator`** (hypertables, one per indicator)
  - [ ] `SMADatabaseAPI`, `RSIDatabaseAPI`, `BollingerBandsDatabaseAPI`, ... driven off `Library/Indicator/`.
- [ ] **Schema: `Portfolio`**
  - [ ] `PositionDatabaseAPI` (open exposure) and `TradeDatabaseAPI` (closed history hypertable).
- [ ] **Schema: `Schedule`**
  - [ ] `WorkflowDatabaseAPI`, `TaskDatabaseAPI`, `RunDatabaseAPI` for the Prefect-style orchestrator.
- [ ] **Schema: `Logging`**
  - [ ] `EventDatabaseAPI`, `ErrorDatabaseAPI` for centralized audit/error streams.
- [ ] **Parameter storage (folded in once Universe is live)**
  - [ ] Add `Configurations` table keyed on `(Provider, Category, Ticker, Timeframe, Mode, Strategy)` with JSONB payload; `mode` values: `Backtesting` / `Optimization` / `Learning` / `Trading`.
  - [ ] DSL resolver `Library/Parameters/Resolver.py` expands stage ranges (`1-4`), `Result=N` references, and choice lists; Pydantic v2 models validate after resolution.
  - [ ] YAML migration script (`Library/Parameters/migrate_yaml.py`) is idempotent (upsert).
  - [ ] Dash editor at `Library/Workflow/Frontend/Configurations.py` with server-side validation.
- [ ] **Verification**
  - [ ] `Tests/test_Universe.py` — round-trip create / upsert / select for each Universe table.
  - [ ] End-to-end migration smoke test: empty DB → `migration()` → all seven schemas populated with expected tables.

---

## `TradingSystemAPI` Consolidation & Hardening

`Trading.py` is now the consolidated implementation. `BacktestingSystemAPI`, `OptimizationSystemAPI`, `LearningSystemAPI` continue to be driven from `Library/System/Main.py` as a CLI. `TradingSystemAPI` is driven exclusively through cTrader Desktop via the `Connector` cBot — no external Python launch path.

- [x] **Absorb archived logic into `TradingSystemAPI`**
  - [x] Port conversion / event handling from `Archive/Sources/Robots/RobotAPI.cs` (asset-type mapping, sentinel handling, instance-id routing, per-ask/bid bar accumulation).
  - [x] Port `LastPositionData` tracking for volume vs stop-loss vs take-profit modification detection.
  - [x] Port position ownership by `pos.Label == api.InstanceId`.
  - [x] Port `FindConversions` raising on not-found (no silent fallback).
  - [x] Port target-trigger independence (multiple targets can fire on one tick; suppress `TickClosed` when any fires).
  - [x] Port sync buffer init, start/stop timestamp capture, database push-on-shutdown from `Archive/Library/System/Realtime.py`.
  - [x] Fix queue protocol to FIFO data items so composite updates (bar+account+position+trade) deserialize in `SystemAPI.deploy`.
- [x] **Exception containment**
  - [x] Every `on_*` handler (`on_tick`, `on_bar_closed`, `_on_position_*`) wrapped in try/except; unhandled exceptions call `api.Stop()`.
  - [x] Every `send_action_*` checks `result.IsSuccessful` and calls `api.Stop()` on failure.
- [x] **Consolidate C# cBots into `Connector`**
  - [x] Single `Sources/Robots/Connector/Connector.cs` replacing `Strategy Download/NNFX/DDPG`.
  - [x] `Strategy`, `Group`, `Console/Telegram/File` verbose exposed as `[Parameter]`.
  - [x] Embeds Python via `pythonnet`; `Py.GIL()` guards every callback.
  - [x] All logic lives in Python (`Library/System/TradingBot.py` + `TradingSystemAPI`); C# side is purely a thin event forwarder.
- [ ] **Deployment docs**
  - [ ] Document `PythonHome` / `ProjectRoot` parameters and the `Quant` conda env requirement for `pythonnet`.
  - [ ] Document how cTrader Desktop discovers the `Connector` assembly after `dotnet build Sources/`.
- [ ] **Tick-thread safety audit**
  - [ ] Confirm `TradingSystemAPI.on_tick` does no blocking work beyond `queue.put` + target check; cTrader's tick thread must return fast.
  - [ ] Benchmark worst-case FX tick rate vs worker-thread drain rate.
- [ ] **Supervisor / watchdog**
  - [ ] On unhandled worker-thread exception: flush state, halt new orders, alert via Telegram log handler. Never leave positions unmanaged.
- [ ] **Live integration test**
  - [ ] Attach `Connector` to a demo EURUSD chart with `Strategy=NNFX`; verify `on_start` -> `on_bar_closed` -> order execution -> `on_stop` round-trip with no pipe dependency.

---

## Improve & Optimize `OptimizationAPI`

Once `TradingAPI` is stable, make `OptimizationAPI` a first-class citizen. It drives the research loop (walk-forward, fitness evaluation, parameter search) and feeds `LearningAPI`.

- [ ] **Define the optimization protocol**
  - [ ] Document search modes: grid, random, CMA-ES / Bayesian (choose one adaptive method).
  - [ ] Document walk-forward contract: training / validation / testing windows fed by the DSL stage ranges (`1-4`).
- [ ] **Parallel execution**
  - [ ] Run each trial as an independent `BacktestingAPI` in a `ProcessPoolExecutor` (threads are useless under the GIL for CPU-bound work).
  - [ ] Share the read-only market frame via shared memory or per-worker load-once.
  - [ ] Progress reporting via `HandlerAPI` (trials completed / ETA / current best fitness).
- [ ] **Fitness & result store**
  - [ ] Write every trial (parameters + fitness + stats) to Postgres (`OptimizationRuns` table) keyed by `SecurityAPI` + run_id.
  - [ ] Support early-stop on no-improvement window.
- [ ] **Determinism**
  - [ ] Seed RNG per trial; assert re-running a trial reproduces the same fitness exactly.
- [ ] **Dash integration**
  - [ ] Page to launch / monitor / cancel an optimization run; plot fitness landscape and walk-forward equity.

---

## Margin Support Across Systems

Margin (used / free) currently travels through `AccountAPI` but isn't fully enforced in the backtest state machine or surfaced to strategies. Bring it to parity with a real broker.

- [ ] **Backtest margin enforcement**
  - [ ] `BacktestingAPI` must reject orders that would exceed `MarginFree`, mirroring cTrader.
  - [ ] Honor `MarginStopLevel` — force-close positions when margin level drops below the configured threshold.
- [ ] **Margin mode coverage**
  - [ ] Support all `MarginMode` variants already in `Dataclass/Account.py` (Net, Hedged, per-broker overrides).
- [ ] **Expose margin to strategies**
  - [ ] `MoneyManagementAPI` should be able to read `Account.MarginFree` / `Account.MarginLevel` for sizing decisions.
- [ ] **TradingAPI parity**
  - [ ] Verify live `TradingAPI` reports the same margin values as the backtest computes for an identical position sequence.
- [ ] **Tests**
  - [ ] `Tests/test_Margin.py`: exhaustive cases (over-leverage, stop-out, swap-adjusted margin, cross-currency margin).

---

## `BacktestingAPI` Modes & Optimization

`BacktestingAPI` is the backbone of every offline system — `OptimizationAPI` and `LearningAPI` run thousands of backtests. Per-bar cost multiplies everywhere, and execution realism determines whether results survive live trading.

- [ ] **Execution-realism modes**
  - [ ] `AccurateTick`: consume full tick stream (highest fidelity, slowest). Default for pre-deployment validation.
  - [ ] `InaccurateTick`: reconstruct synthetic intrabar ticks from OHLC (standard cTrader "m1-based" mode). Default for optimization loops.
  - [ ] `BarOnly`: price events only at bar close (fastest, lowest fidelity). Default for early-stage strategy drafting.
  - [ ] `RandomSpread`: overlay on any mode — draw spread per tick from a distribution (uniform, log-normal, or historical empirical) rather than a fixed value.
  - [ ] Mode selector on `BacktestingAPI`; document accuracy/speed tradeoffs.
- [ ] **Profile the hot path**
  - [ ] Use `Library/Statistics` timers to profile a full EURUSD H1 backtest in each mode; record per-bar cost, GC pauses, queue overhead.
  - [ ] Identify top-5 hot functions (expect: `BarAPI` construction, `queue.Queue` churn, `polars` conversions, analyst indicator recomputes).
- [ ] **Remove unnecessary threading offline**
  - [ ] `SystemAPI` inherits from `Thread` for the live case. In `BacktestingAPI` the producer/consumer is synchronous — bypass the queue entirely (direct state-machine calls) when offline.
  - [ ] Benchmark: target ≥ 5x speedup on NNFX EURUSD H1 `InaccurateTick` vs current queue-based path.
- [ ] **Vectorize indicator pre-compute**
  - [ ] `AnalystAPI.init_market_data` computes all indicators once over the full Polars frame; keep per-bar update for live only.
- [ ] **Memory / allocation discipline**
  - [ ] Replace per-bar `BarAPI` dataclass construction in the hot loop with a pre-allocated Polars frame + row view (or `__slots__` on `BarAPI`).
  - [ ] Batch `DatabaseAPI` pushes at end of run.
- [ ] **Determinism tests**
  - [ ] Same config + same mode + same seed -> identical trade lists.

---

## End-to-End Validation

- [ ] **Backtesting parity**
  - [ ] Run same NNFX config through `BacktestingAPI` (`AccurateTick`) and a short cTrader live-replay; compare trade list and equity curve within tolerance.
- [ ] **Full research cycle**
  - [ ] Define a DDPG+NNFX config in the Dash editor.
  - [ ] `BacktestingAPI` -> `LearningAPI` (train DDPG) -> `OptimizationAPI` (tune rule thresholds) -> `TradingAPI` (deploy).
- [ ] **Sign-off**
  - [ ] All tests green, docs updated, `RULES.md` project map regenerated to match final folder layout.
