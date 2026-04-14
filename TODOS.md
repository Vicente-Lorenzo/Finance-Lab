# Quant Trading Framework - Implementation Plan (TODOs)

This document tracks the phased implementation to modernize the Quant Trading Framework. It serves as a master checklist. 
**Instructions for LLM Assistants:** When provided this file, review the checked items (`[x]`) to understand the current progress, and begin work on the first unchecked item (`[ ]`).

---

## Phase 1: Archiving Legacy Systems & Cleanup

- [ ] **1.1. Create Archive Directory**
  - [ ] Create an `Archive/` folder at the root directory of the project.
- [ ] **1.2. Archive C# Server Logic**
  - [ ] Move `Sources/Indicators/SystemAPI.cs` to `Archive/Sources/Indicators/SystemAPI.cs`.
  - [ ] Move `Sources/Robots/SystemAPI.cs` to `Archive/Sources/Robots/SystemAPI.cs`.
- [ ] **1.3. Archive Python Realtime Logic**
  - [ ] Move `Library/Robots/System/Realtime.py` to `Archive/Library/Robots/System/Realtime.py`.

---

## Phase 2: Architectural Flattening & Renaming

- [ ] **2.1. Create `Library/Systems/`**
  - [ ] Create the `Library/Systems/` directory.
  - [ ] Move `Library/Robots/System/System.py` to `Library/Systems/System.py`.
  - [ ] Move `Library/Robots/System/Backtesting.py` -> `Library/Systems/Backtesting.py` and rename classes to `BacktestingAPI`.
  - [ ] Move `Library/Robots/System/Optimisation.py` -> `Library/Systems/Optimization.py` and rename classes to `OptimizationAPI`.
  - [ ] Move `Library/Robots/System/Learning.py` -> `Library/Systems/Learning.py` and rename classes to `LearningAPI`.
  - [ ] Move `Library/Robots/System/Native.py` -> `Library/Systems/Trading.py` and rename classes to `TradingAPI`.
- [ ] **2.2. Flatten Core Domains**
  - [ ] Move `Library/Robots/Strategy/` to `Library/Strategy/`.
  - [ ] Move `Library/Robots/Engine/` to `Library/Engine/`.
  - [ ] Move `Library/Robots/Analyst/` to `Library/Analyst/`.
  - [ ] Move `Library/Robots/Manager/` to `Library/Manager/`.
  - [ ] Move `Library/Robots/Protocol/` to `Library/Protocol/`.
- [ ] **2.3. Cleanup Core Directory**
  - [ ] Delete the empty `Library/Robots/` folder.
- [ ] **2.4. Update Imports**
  - [ ] Perform a global search and replace for `Library.Robots.` -> `Library.`.
  - [ ] Update imports within the `Library/Systems/` module to reflect the new class names and locations.
- [ ] **2.5. Verify Refactor**
  - [ ] Run `pytest` to ensure no module `ImportError` regressions exist.

---

## Phase 3: Scalable Parameter Management (JSONB Database)

- [ ] **3.1. Design Postgres JSONB Schema**
  - [ ] Use `PostgresDatabaseAPI` to define a `Configurations` table. 
  - [ ] Schema: `(id SERIAL PRIMARY KEY, broker VARCHAR, asset_group VARCHAR, symbol VARCHAR, timeframe VARCHAR, system_type VARCHAR, strategy_name VARCHAR, parameters JSONB)`.
- [ ] **3.2. YAML to Database Migration Script**
  - [ ] Write a one-off Python script to parse the deeply nested YAML files in `Library/Parameters/`.
  - [ ] Inject parsed YAML payloads into the `Configurations` Postgres table.
- [ ] **3.3. Update System APIs**
  - [ ] Refactor `BacktestingAPI`, `OptimizationAPI`, and `TradingAPI` to fetch their configuration payloads directly from the Postgres database.
- [ ] **3.4. Dash Frontend Integration**
  - [ ] Create a form (`Library/App/Form.py`) to query configurations from the database.
  - [ ] Implement a JSON/YAML editor component in Dash to modify the `parameters` JSONB payload and save it back to Postgres.

---

## Phase 4: Execution Engine Finalization

- [ ] **4.1. Polish `TradingAPI` (Live/Native Connection)**
  - [ ] Ensure `Trading.py` efficiently handles `on_start`, `on_tick`, `on_bar_closed`, and `on_shutdown` natively via Python `clr`.
  - [ ] Update C# bot templates (e.g., `Sources/Robots/Strategy NNFX/Strategy NNFX/Strategy NNFX.cs` and `NativeBot.py`) to load `TradingAPI`.
- [ ] **4.2. Verify Native Integration**
  - [ ] Compile C# bot and attach to a cTrader chart to test live event forwarding to Python without named pipes.
- [ ] **4.3. Finalize `BacktestingAPI`**
  - [ ] Ensure the Python standalone backtester accurately mirrors the state machine logic tested in cTrader.
- [ ] **4.4. Integrate `LearningAPI`**
  - [ ] Hook the DDPG Agent (`DDPGAgentAPI`) into the `LearningAPI` execution loop to enable training.

---

## Phase 5: End-to-End Validation

- [ ] **5.1. Full Research Cycle Test**
  - [ ] Define a new DDPG+NNFX Strategy config in the Database via the Dash UI.
  - [ ] Run a backtest using `BacktestingAPI`.
  - [ ] Train the model using `LearningAPI`.
  - [ ] Optimize the rule-based thresholds using `OptimizationAPI`.
  - [ ] Deploy the final config to cTrader using `TradingAPI`.