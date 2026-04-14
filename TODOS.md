# Quant Trading Framework - Implementation Plan (TODOs)

This document tracks the phased implementation to modernize the Quant Trading Framework. It serves as a master checklist.
**Instructions for LLM Assistants:** When provided this file, review the checked items (`[x]`) to understand the current progress, and begin work on the first unchecked item (`[ ]`). Phases are unordered headings — work top-to-bottom; completed phases are removed, not crossed out.

---

## Architectural Flattening & Renaming

Keep `Library/System/` (singular) as the home for all execution drivers. The abstract base stays `SystemAPI`; each concrete driver is a sibling file with a `*API` class. Doing the flatten + `TradingAPI` first gives a concrete view of what the `Security` layer must expose before we refactor it.

- [ ] **Promote `Library/System/`**
  - [ ] Move `Library/Robots/System/System.py`       -> `Library/System/System.py` (abstract `SystemAPI` unchanged).
  - [ ] Move `Library/Robots/System/Backtesting.py` -> `Library/System/Backtesting.py`; class -> `BacktestingAPI`.
  - [ ] Move `Library/Robots/System/Optimisation.py` -> `Library/System/Optimization.py`; class -> `OptimizationAPI` (US spelling).
  - [ ] Move `Library/Robots/System/Learning.py`    -> `Library/System/Learning.py`; class -> `LearningAPI`.
  - [ ] Move `Library/Robots/System/Native.py`      -> `Library/System/Trading.py`; class -> `TradingAPI` (absorb `NativeSystemAPI`).
- [ ] **Flatten core domains**
  - [ ] `Library/Robots/Strategy/` -> `Library/Strategy/`.
  - [ ] `Library/Robots/Engine/`   -> `Library/Engine/`.
  - [ ] `Library/Robots/Analyst/`  -> `Library/Analyst/`.
  - [ ] `Library/Robots/Manager/`  -> `Library/Manager/`.
  - [ ] `Library/Robots/Protocol/` -> `Library/Protocol/`.
- [ ] **Cleanup**
  - [ ] Move `Library/Robots/NativeBot.py` -> `Library/System/TradingBot.py` (example cTrader entrypoint).
  - [ ] Delete the empty `Library/Robots/`.
- [ ] **Global import rewrite**
  - [ ] `Library.Robots.` -> `Library.` across repo.
  - [ ] Fix renames (`Optimisation` -> `Optimization`, `NativeSystemAPI` -> `TradingAPI`).
- [ ] **Verify**
  - [ ] `conda run -n Quant python -m pytest Tests/` passes with no `ImportError`.

---

## Adopt the `Security` Domain Model

`Library/Security/` already defines `ProviderAPI`, `CategoryAPI`, `TickerAPI`, `TimeframeAPI`. Once `TradingAPI` exposes the real shape of runtime data from cTrader, collapse the loose `broker`/`group`/`symbol`/`timeframe` strings into a single `SecurityAPI`.

- [ ] **Refactor `SystemAPI` signature**
  - [ ] Replace `broker`/`group`/`symbol`/`timeframe` strings with a single `security: SecurityAPI` argument.
  - [ ] Propagate through `TradingAPI`, `BacktestingAPI`, `OptimizationAPI`, `LearningAPI`.
- [ ] **Update `TradingBot.py`**
  - [ ] Build the `SecurityAPI` from `self.Account.BrokerName` / `self.Symbol.Name` / `self.TimeFrame.Name`.
- [ ] **Update parameters lookup**
  - [ ] `ParametersAPI` should key on `SecurityAPI` (or its tuple), not nested dict strings.

---

## Configuration Storage & DSL Resolver

The YAMLs embed a mini-language (`1-4:` stage ranges, `Result=1` cross-references, choice lists). Storage is secondary — the resolver is the real work.

- [ ] **Formalize the config DSL**
  - [ ] Document the grammar: stage ranges (`1-4`, `3-4`), result references (`Result=N`), choice lists (`[ WMA, HMA, ... ]`).
  - [ ] Write `Library/Parameters/Resolver.py`: expands ranges, resolves `Result=N` against prior stages, validates references.
  - [ ] Unit tests in `Tests/test_Resolver.py` covering each construct on the existing NNFX YAML.
- [ ] **Pydantic schema layer**
  - [ ] Define Pydantic v2 models for `MoneyManagement`, `RiskManagement`, `SignalManagement`, `AnalystManagement`, `ManagerManagement`.
  - [ ] Validation runs *after* the resolver expands the DSL.
- [ ] **Postgres JSONB schema**
  - [ ] Table `Configurations(id SERIAL PK, provider TEXT, category TEXT, ticker TEXT, timeframe TEXT, mode TEXT, strategy TEXT, parameters JSONB, updated_at TIMESTAMPTZ)`.
  - [ ] Unique index on `(provider, category, ticker, timeframe, mode, strategy)`.
  - [ ] `mode` values: `Backtesting` / `Optimization` / `Learning` / `Trading`.
- [ ] **YAML -> database migration**
  - [ ] One-off script `Library/Parameters/migrate_yaml.py` walks `Library/Parameters/<Provider>/<Category>/<Ticker>/<Timeframe>/*.yml` and inserts raw payloads.
  - [ ] Migration must be idempotent (upsert on the unique key).
- [ ] **Update systems**
  - [ ] `BacktestingAPI`, `OptimizationAPI`, `LearningAPI`, `TradingAPI` fetch payload by `SecurityAPI` + mode, run it through Resolver + Pydantic, then use it.
- [ ] **Dash editor**
  - [ ] Page `Library/Workflow/Frontend/Configurations.py` lists configs filterable by provider/category/ticker/timeframe.
  - [ ] JSON editor component (e.g. `dash-ace` or `dash-jsoneditor`) with server-side Pydantic validation on save.
  - [ ] Save returns resolver errors inline.

---

## `TradingAPI` Consolidation & Hardening

`Native.py` is a *first draft* of `TradingAPI`. Finalize it by folding in everything still scattered across the archived pipe implementation and hardening the `clr` boundary.

- [ ] **Absorb archived logic into `TradingAPI`**
  - [ ] Port missing conversion / event handling from `Archive/Sources/Robots/SystemAPI.cs` (asset-type mapping, sentinel handling, instance-id routing) into `Library/System/Trading.py`.
  - [ ] Port any `Archive/Sources/Indicators/SystemAPI.cs` logic that belongs on the Python side (e.g. bar-series bootstrap).
  - [ ] Port remaining behaviors from `Archive/Library/System/Realtime.py` not yet in `Trading.py` (sync buffer init, start/stop timestamp capture, database push-on-shutdown paths).
- [ ] **Tick-thread safety audit**
  - [ ] Confirm `TradingAPI.on_tick` does no blocking work beyond `queue.put`; cTrader's tick thread must return fast.
  - [ ] Benchmark worst-case FX tick rate vs worker-thread drain rate.
- [ ] **Exception containment**
  - [ ] Wrap every `on_*` handler in `TradingBot.py` and `TradingAPI` with try/except routed to `HandlerAPI` — the `clr` boundary swallows raw Python exceptions.
- [ ] **Supervisor / watchdog**
  - [ ] On unhandled worker-thread exception: flush state, halt new orders, alert via Telegram log handler. Never leave positions unmanaged.
- [ ] **Deployment docs**
  - [ ] Document the `Quant` conda env path cTrader expects and how to configure `PYTHONNET_PYDLL` / cTrader's Python interpreter setting.
- [ ] **C# template cleanup**
  - [ ] Strip any remaining named-pipe code from `Sources/Robots/Strategy NNFX/.../Strategy NNFX.cs` and align the shape with `TradingBot.py`.
- [ ] **Live integration test**
  - [ ] Attach NNFX bot to a demo EURUSD chart; verify `on_start` -> `on_bar_closed` -> order execution -> `on_stop` round-trip with no pipe dependency.

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
