 # Gemini Code Assist Project Guidelines

 ## PROJECT OVERVIEW
 This is a **multi-purpose Quant Trading Framework** designed to work with **cTrader**.
 - **Root Folder:** `cAlgo` (located in Documents for cTrader compatibility).
 - **`Library/` (Python):** Contains the core logic, AI models, Backtesting systems, and a Dash-based Frontend.
 - **`Sources/` (C#):** Contains cAlgo Robots and Indicators that interface with cTrader and communicate with the Python backend.
 
 ## CODING PHILOSOPHY
 1. **Precision & Accuracy:** Prioritize correct, working code over speed.
 2. **Simplicity & Optimization:** Do **not** overthink or over-engineer.
    - Solutions should be as simple and optimized as possible.
    - Avoid unnecessary abstraction or complexity.
    - Prefer concise, readable, and performant code.
 
 ## CONTEXT AWARENESS PROTOCOL
 Before answering code-related questions, execute this check:
 
 1. **Scan References:** Identify classes/functions referenced in the request.
 2. **Verify Context:** Check if definitions are present.
 3. **Criticality Assessment:**
    - **Missing Core Logic:** If a missing file is *crucial* to the business logic being modified **STOP** and ask for it.
    - **Missing Utilities/Peripheral:** If the missing code is a generic utility, a standard library wrapper, or not central to the specific task, **PROCEED**. Do not waste time asking for files that aren't strictly necessary for the operation.
 
 ## DOCUMENTATION MAINTENANCE
 If you detect changes to the project structure (new folders, modules, or significant architectural changes) that are not reflected in this `GEMINI.md` file:
 1. **Notify the User:** Explicitly mention the discrepancy.
 2. **Propose an Update:** Generate the updated markdown content for `GEMINI.md` to keep the "master" prompt synchronized with the actual codebase.

 ## PROJECT STRUCTURE MAP
 ### Python (`Library/`)
 - **`Library/App`:** Core Dash wrappers (`AppAPI`, `PageAPI`, `ComponentAPI`) for the Web UI.
 - **`Library/Database`:** Database abstraction layer (`DatabaseAPI`, `QueryAPI`) supporting Oracle, Postgres, and SQL Server.
 - **`Library/Dataclass`:** Data structures (`BarAPI`, `TickAPI`, `TradeAPI`, `SymbolAPI`) and type definitions.
 - **`Library/Dataframe`:** Pandas/Polars/Numpy configuration and wrappers (inheritable `DataframeAPI`).
 - **`Library/Formulas`:** Financial and utility formulas (`DateTime`, `Spot`, `Historical`).
 - **`Library/Workflow`:** Business logic and frontend pages implementation.
 - **`Library/Models`:** AI/ML Agents (`AgentAPI`, `DDPG`, `Noise`, `Memory`).
 - **`Library/Robots`:** Python Trading Engine (System, Strategy, Analyst, Manager, Engine).
 - **`Library/Logging`:** Python logging handlers (Console, Telegram, File, Web).
 
 ### C# (`Sources/`)
 - **`Sources/Robots`:** cTrader Robots (inherit `RobotAPI`). Bridge to Python via Pipes.
 - **`Sources/Indicators`:** cTrader Indicators (inherit `IndicatorAPI`).
 - **`Sources/Logging`:** C# logging bridge.