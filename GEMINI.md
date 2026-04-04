 # Gemini Code Assist Project Guidelines

 ## PROJECT OVERVIEW
 This is a **multipurpose Quant Trading Framework** designed to work with **cTrader**.
 - **Root Folder:** `cAlgo` (located in Documents for cTrader compatibility).
 - **`Library/` (Python):** Contains the core logic, AI models, Backtesting systems, and a Dash-based Frontend.
 - **`Sources/` (C#):** Contains cAlgo Robots and Indicators that interface with cTrader and communicate with the Python backend.
 
 ## CODING PHILOSOPHY
 1. **Precision & Accuracy:** Prioritize correct, working code over speed.
 2. **Simplicity & Optimization:** Do **not** overthink or over-engineer.
    - Solutions should be as simple and optimized as possible.
    - Avoid unnecessary abstraction or complexity.
    - Prefer concise, readable, and performant code.
 
 ## CODING STYLE NUANCES
 1. **No Documentation:** Do not include docstrings or comments in the code.
 2. **Naming Conventions:**
    - Use `CamelCase` for public fields and properties in dataclasses.
    - Use `_naming_` (snake_case with leading and trailing underscores) for private attributes and methods.
    - In `__post_init__`, keep arguments lowercase (e.g., `raw`) to avoid IDE hints/conflicts with class fields.
 3. **Type Hinting:**
    - Use `Self` from `typing_extensions` for methods returning an instance of the class (to ensure full compatibility).
 4. **Method Architecture:**
    - Favor `@staticmethod` for utility methods like `_decode_` that do not require instance state.
    - Use `InitVar` for raw inputs that are processed during initialization but not stored as fields.
 5. **Module Structure:**
    - Organize imports in a ladder-style (sorted by length or alphabetically in a clean visual block).
    - Separate generic imports (standard library, external packages) from project library imports (e.g., `Library.*`) with a single new line.
    - Ensure files are tidy: no trailing spaces or unnecessary newlines at the end of files.
 6. **Compact Style & Organization:**
    - Use a compact coding style by removing unnecessary empty lines within methods to keep logic dense.
    - Ensure exactly one blank line separates individual methods or class definitions.
    - Maintain standard spacing within signatures, type hints, and assignments (e.g., `def func(a: int | str, b: float = 1.0) -> Self:`) to ensure readability.
    - Order methods logically: simpler utility methods at the top, and more complex methods (those that utilize the simpler ones) towards the bottom.

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
 2. **Propose an Update:** Generate the updated Markdown content for `GEMINI.md` to keep the "master" prompt synchronized with the actual codebase.

 ## PROJECT STRUCTURE MAP
 ### Python (`Library/`)
 - **`Library/App`**: Core Dash wrappers (`AppAPI`, `PageAPI`, `ComponentAPI`) for the Web UI.
 - **`Library/Bloomberg`**: Bloomberg API integration (Historical, Intraday, Reference, Streaming).
 - **`Library/Database`**: Database abstraction layer (`DatabaseAPI`, `QueryAPI`) supporting Oracle, Postgres, and SQL Server.
 - **`Library/Dataclass`**: Data structures (`BarAPI`, `TickAPI`, `TradeAPI`, `SymbolAPI`) and type definitions.
 - **`Library/Dataframe`**: Pandas/Polars/Numpy configuration and wrappers (inheritable `DataframeAPI`).
 - **`Library/Formulas`**: Financial and utility formulas (`DateTime`, `Spot`, `Historical`).
 - **`Library/Indicators`**: Python implementation of Trading Indicators.
 - **`Library/Logging`**: Python logging handlers (Console, Telegram, File, Web).
 - **`Library/Models`**: AI/ML Agents (`AgentAPI`, `DDPG`, `Network`, `Noise`, `Memory`).
 - **`Library/Parameters`**: Configuration management and Broker-specific settings.
 - **`Library/Robots`**: Python Trading Engine (System, Strategy, Analyst, Manager, Engine, Protocol).
 - **`Library/Security`**: Security and Asset Class definitions.
 - **`Library/Service`**: System services and background processes.
 - **`Library/Statistics`**: Performance profiling and timing utilities.
 - **`Library/Utility`**: Extensive helper library (IO, Path, HTML, DateTime, Typing, etc.).
 - **`Library/Warehouse`**: Data storage and retrieval layer for market data (Bars, Ticks, Trades).
 - **`Library/Workflow`**: Business logic and frontend pages implementation.

 ### C# (`Sources/`)
 - **`Sources/Robots`**: cTrader Robots (inherit `RobotAPI`). Bridge to Python via Pipes.
 - **`Sources/Indicators`**: cTrader Indicators (inherit `IndicatorAPI`).
 - **`Sources/Plugins`**: cTrader Plugins and Extensions.
 - **`Sources/Logging`**: C# logging bridge.
 - **`Sources/Export`**: Build artifacts and deployment exports.

 ### Testing (`Tests/`)
 - **`Tests/`**: Unit and integration tests for Python library components.