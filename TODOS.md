# Quant Trading Framework - Implementation Plan (TODOs)

This document tracks the phased implementation to modernize the Quant Trading Framework. It serves as a master checklist.
**Instructions for LLM Assistants:** When provided this file, review the checked items (`[x]`) to understand the current progress, and begin work on the first unchecked item (`[ ]`).

---

## Phase 1: Archive Legacy Named-Pipe Bridge

- [ ] **1.1. Create Archive Directory**
  - [ ] Create `Archive/` at the project root (mirrors `Library/` and `Sources/` subtrees inside).
- [ ] **1.2. Archive C# Server Logic**
  - [ ] Move `Sources/Indicators/SystemAPI.cs` -> `Archive/Sources/Indicators/SystemAPI.cs`.
  - [ ] Move `Sources/Robots/SystemAPI.cs` -> `Archive/Sources/Robots/SystemAPI.cs`.
- [ ] **1.3. Archive Python Realtime Logic**
  - [ ] Move `Library/Robots/System/Realtime.py` -> `Archive/Library/Robots/System/Realtime.py`.
- [ ] **1.4. Remove Stale Imports**
  - [ ] Grep for `Realtime` / `SystemAPI.cs` references and drop them.

---

## Phase 2: Adopt the `Security` Domain Model

`Library/Security/` already defines `ProviderAPI`, `CategoryAPI`, `TickerAPI`, `TimeframeAPI`. The current `SystemAPI` still takes loose `broker`/`group`/`symbol`/`timeframe` strings. This must be fixed **before** flattening so the new folder layout isn't built on the old naming.

- [ ] **2.1. Refactor `SystemAPI` signature**
  - [ ] Replace `broker`/`group`/`symbol`/`timeframe` strings with a single `security: SecurityAPI` argument.
  - [ ] Propagate through `NativeSystemAPI`, `BacktestingAPI`, `OptimisationAPI`, `LearningAPI`.
- [ ] **2.2. Update `NativeBot.py`**
  - [ ] Build the `SecurityAPI` from `self.Account.BrokerName` / `self.Symbol.Name` / `self.TimeFrame.Name`.
- [ ] **2.3. Update Parameters Lookup**
  - [ ] `ParametersAPI` should key on `SecurityAPI` (or its tuple), not nested dict strings.

---

## Phase 3: Architectural Flattening & Renaming

Keep `Library/System/` (singular) as the home for all execution drivers. The abstract base stays `SystemAPI`; each concrete driver is a sibling file with a `*API` class.

- [ ] **3.1. Promote `Library/System/`**
  - [ ] Move `Library/Robots/System/System.py`       -> `Library/System/System.py` (abstract `SystemAPI` unchanged).
  - [ ] Move `Library/Robots/System/Backtesting.py` -> `Library/System/Backtesting.py`; class -> `BacktestingAPI`.
  - [ ] Move `Library/Robots/System/Optimisation.py` -> `Library/System/Optimization.py`; class -> `OptimizationAPI` (US spelling).
  - [ ] Move `Library/Robots/System/Learning.py`    -> `Library/System/Learning.py`; class -> `LearningAPI`.
  - [ ] Move `Library/Robots/System/Native.py`      -> `Library/System/Trading.py`; class -> `TradingAPI` (absorb `NativeSystemAPI`).
- [ ] **3.2. Flatten Core Domains**
  - [ ] `Library/Robots/Strategy/` -> `Library/Strategy/`.
  - [ ] `Library/Robots/Engine/`   -> `Library/Engine/`.
  - [ ] `Library/Robots/Analyst/`  -> `Library/Analyst/`.
  - [ ] `Library/Robots/Manager/`  -> `Library/Manager/`.
  - [ ] `Library/Robots/Protocol/` -> `Library/Protocol/`.
- [ ] **3.3. Cleanup**
  - [ ] Move `Library/Robots/NativeBot.py` -> `Library/System/TradingBot.py` (example cTrader entrypoint).
  - [ ] Delete the empty `Library/Robots/`.
- [ ] **3.4. Global Import Rewrite**
  - [ ] `Library.Robots.` -> `Library.` across repo.
  - [ ] Fix renames (`Optimisation` -> `Optimization`, `NativeSystemAPI` -> `TradingAPI`).
- [ ] **3.5. Verify**
  - [ ] `conda run -n Quant python -m pytest Tests/` passes with no `ImportError`.

---

## Phase 4: Configuration Storage & DSL Resolver

The YAMLs embed a mini-language (`1-4:` stage ranges, `Result=1` cross-references, choice lists). Storage is secondary — the resolver is the real work.

- [ ] **4.1. Formalize the Config DSL**
  - [ ] Document the grammar: stage ranges (`1-4`, `3-4`), result references (`Result=N`), choice lists (`[ WMA, HMA, ... ]`).
  - [ ] Write `Library/Parameters/Resolver.py`: expands ranges, resolves `Result=N` against prior stages, validates references.
  - [ ] Unit tests in `Tests/test_Resolver.py` covering each construct on the existing NNFX YAML.
- [ ] **4.2. Pydantic Schema Layer**
  - [ ] Define Pydantic v2 models for `MoneyManagement`, `RiskManagement`, `SignalManagement`, `AnalystManagement`, `ManagerManagement`.
  - [ ] Validation runs *after* the resolver expands the DSL.
- [ ] **4.3. Postgres JSONB Schema**
  - [ ] Table `Configurations(id SERIAL PK, provider TEXT, category TEXT, ticker TEXT, timeframe TEXT, mode TEXT, strategy TEXT, parameters JSONB, updated_at TIMESTAMPTZ)`.
  - [ ] Unique index on `(provider, category, ticker, timeframe, mode, strategy)`.
  - [ ] `mode` values: `Backtesting` / `Optimization` / `Learning` / `Trading`.
- [ ] **4.4. YAML -> Database Migration**
  - [ ] One-off script `Library/Parameters/migrate_yaml.py` walks `Library/Parameters/<Provider>/<Category>/<Ticker>/<Timeframe>/*.yml` and inserts raw payloads.
  - [ ] Migration must be idempotent (upsert on the unique key).
- [ ] **4.5. Update Runners**
  - [ ] `BacktestingAPI`, `OptimizationAPI`, `LearningAPI`, `TradingAPI` fetch payload by `SecurityAPI` + mode, run it through Resolver + Pydantic, then use it.
- [ ] **4.6. Dash Editor**
  - [ ] Page `Library/Workflow/Frontend/Configurations.py` lists configs filterable by provider/category/ticker/timeframe.
  - [ ] JSON editor component (e.g. `dash-ace` or `dash-jsoneditor`) with server-side Pydantic validation on save.
  - [ ] Save returns resolver errors inline.

---

## Phase 5: `TradingAPI` Consolidation & Hardening

`Native.py` is a *first draft* of `TradingAPI`. Finalize it by folding in everything still scattered across the archived pipe implementation and hardening the `clr` boundary.

- [ ] **5.1. Absorb archived logic into `TradingAPI`**
  - [ ] Port missing conversion / event handling from `Archive/Sources/Robots/SystemAPI.cs` (asset-type mapping, sentinel handling, instance-id routing) into `Library/System/Trading.py`.
  - [ ] Port any `Archive/Sources/Indicators/SystemAPI.cs` logic that belongs on the Python side (e.g. bar-series bootstrap).
  - [ ] Port remaining behaviors from `Archive/Library/Robots/System/Realtime.py` not yet in `Native.py` (sync buffer init, start/stop timestamp capture, database push-on-shutdown paths).
  - [ ] Delete `Native.py` wrapper once `TradingAPI` is the single source of truth.
- [ ] **5.2. Tick-thread safety audit**
  - [ ] Confirm `TradingAPI.on_tick` does no blocking work beyond `queue.put`; cTrader's tick thread must return fast.
  - [ ] Benchmark worst-case FX tick rate vs worker-thread drain rate.
- [ ] **5.3. Exception containment**
  - [ ] Wrap every `on_*` handler in `TradingBot.py` and `TradingAPI` with try/except routed to `HandlerAPI` — the `clr` boundary swallows raw Python exceptions.
- [ ] **5.4. Supervisor / Watchdog**
  - [ ] On unhandled worker-thread exception: flush state, halt new orders, alert via Telegram log handler. Never leave positions unmanaged.
- [ ] **5.5. Deployment docs**
  - [ ] Document the `Quant` conda env path cTrader expects and how to configure `PYTHONNET_PYDLL` / cTrader's Python interpreter setting.
- [ ] **5.6. C# Template Cleanup**
  - [ ] Strip any remaining named-pipe code from `Sources/Robots/Strategy NNFX/.../Strategy NNFX.cs` and align the shape with `TradingBot.py`.
- [ ] **5.7. Live Integration Test**
  - [ ] Attach NNFX bot to a demo EURUSD chart; verify `on_start` -> `on_bar_closed` -> order execution -> `on_stop` round-trip with no pipe dependency.

---

## Phase 6: `BacktestingAPI` Optimization (Backbone of Offline Systems)

`BacktestingAPI` is the foundation of `OptimizationAPI` and `LearningAPI` — every offline system runs thousands of backtests, so its per-bar cost multiplies everywhere. Treat performance as a first-class feature.

- [ ] **6.1. Profile the hot path**
  - [ ] Use `Library/Statistics` timers to profile a full EURUSD H1 backtest; record per-bar cost, GC pauses, queue overhead.
  - [ ] Identify the top 5 hot functions (expect: `BarAPI` construction, `queue.Queue` churn, `polars` conversions, analyst indicator recomputes).
- [ ] **6.2. Remove unnecessary threading in offline mode**
  - [ ] `SystemAPI` inherits from `Thread` for the live case. In `BacktestingAPI` the producer/consumer is synchronous — bypass the queue entirely (direct state-machine calls) when running offline.
  - [ ] Benchmark: target ≥ 5x speedup on the NNFX EURUSD H1 backtest vs current queue-based path.
- [ ] **6.3. Vectorize indicator pre-compute**
  - [ ] Have `AnalystAPI.init_market_data` compute all indicators once over the full Polars frame instead of bar-by-bar updates where possible.
  - [ ] Keep the per-bar update path for live/streaming; offline mode uses the vectorized path.
- [ ] **6.4. Memory / allocation discipline**
  - [ ] Replace per-bar `BarAPI` dataclass construction in the hot loop with a pre-allocated Polars frame + row view (or `__slots__` on `BarAPI`).
  - [ ] Avoid repeated `DataFrame` copies when pushing to `DatabaseAPI` — batch at end of run.
- [ ] **6.5. Parallel backtests for Optimization/Learning**
  - [ ] `OptimizationAPI` and `LearningAPI` should run independent `BacktestingAPI` instances across a process pool (not threads — CPU-bound + GIL).
  - [ ] Share the read-only market data frame via shared memory or per-worker load-once.
- [ ] **6.6. Determinism tests**
  - [ ] After each optimization, assert that running the same config twice produces identical trade lists. No silent nondeterminism allowed in the backbone.

---

## Phase 7: End-to-End Validation

- [ ] **7.1. Backtesting parity**
  - [ ] Run same NNFX config through `BacktestingAPI` and a short cTrader live-replay; compare trade list and equity curve within tolerance.
- [ ] **7.2. Full research cycle**
  - [ ] Define a DDPG+NNFX config in the Dash editor.
  - [ ] `BacktestingAPI` -> `LearningAPI` (train DDPG) -> `OptimizationAPI` (tune rule thresholds) -> `TradingAPI` (deploy).
- [ ] **7.3. Sign-off**
  - [ ] All tests green, docs updated, `CLAUDE.md` project map regenerated to match final folder layout.
