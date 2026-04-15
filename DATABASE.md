# Quantitative Trading Framework Database Design (PostgreSQL + TimescaleDB)

---

## 1. Schema Architecture
The **Quant** database is organized into seven functional schemas. CamelCase naming is used throughout to align with application-layer code.

| Schema        | Purpose                             | Data Category            |
|:--------------|:------------------------------------|:-------------------------|
| `Universe`    | Static Reference Data               | Relational               |
| `Market`      | Price Action (Ticks/Bars)           | Time-Series (Hypertable) |
| `Alternative` | Non-Price Data (Economic/Sentiment) | Time-Series (Hypertable) |
| `Indicator`   | Derived Signals (e.g., SMA, RSI)    | Time-Series (Hypertable) |
| `Portfolio`   | Live Positions and Trade History    | Hybrid                   |
| `Schedule`    | Orchestration and Workflow Metadata | Relational               |
| `Logging`     | Application and Operational Logs    | Time-Series              |

---

## 2. Schema: `Universe`
The "Source of Truth" for mapping external vendor symbols to internal asset identities.

* **`AssetClass`**: (ID, Name) - e.g., Equity, FX, Crypto, Futures.
* **`Provider`**: (ID, Name) - e.g., Bloomberg, YahooFinance, cTrader_ICMarkets.
* **`Category`**: (ID, Name) - e.g., Technology, G10, Energy.
* **`Security`**: (InternalID, Name, AssetClassID, CategoryID).
* **`SecurityMapping`**: (InternalID, ProviderID, ProviderSymbol) - Maps your `InternalID` to `AAPL` or `EURUSD`.

---

## 3. Schema: `Market`
High-velocity price data managed as **TimescaleDB Hypertables**.

* **`Tick`**: (Time, SecurityID, ProviderID, Bid, Ask, Volume).
* **`Bar`**: (Time, SecurityID, Resolution, Open, High, Low, Close, Volume).
    * *Strategy:* Store 1-minute bars as the base. Use **Continuous Aggregates** to generate Hourly, Daily, and Yearly views automatically.

---

## 4. Schema: `Alternative`
"Alt-Data" used for fundamental and sentiment analysis. Managed as Hypertables.

* **`Economic`**: (Time, EventID, Country, Actual, Forecast, Previous, Importance).
* **`Sentiment`**: (Time, SecurityID, SourceID, Score, Magnitude, Metadata [JSONB]).

---

## 5. Schema: `Indicator`
Calculated quantitative values. To optimize performance and storage, each indicator utilizes its own Hypertable.

* **`SMA`**: (Time, SecurityID, Resolution, Period, Value).
* **`RSI`**: (Time, SecurityID, Resolution, Period, Value).
* **`BollingerBands`**: (Time, SecurityID, Resolution, Period, Upper, Middle, Lower).

---

## 6. Schema: `Portfolio`
The ledger of active risk and historical performance.

* **`Position`**: (InternalID, SecurityID, Direction, Quantity, EntryPrice, EntryTime).
    * *Purpose:* Represents currently open exposure.
* **`Trade`**: (Time [ExitTime], InternalID, SecurityID, Quantity, EntryPrice, ExitPrice, PnL, Commissions).
    * *Purpose:* Historical record of closed positions. Managed as a Hypertable.

---

## 7. Schema: `Schedule`
Orchestration metadata for the custom workflow engine (Prefect-style).

* **`Workflow`**: Definitions of scheduled processes (e.g., `Daily_EOD_Ingestion`).
* **`Task`**: Atomic steps within a workflow (e.g., `Fetch_Yahoo_Data`, `Compute_Moving_Average`).
* **`Run`**: Individual execution logs (RunID, TaskID, StartTime, EndTime, Status, Logs, AffectedRows).

---

## 8. Schema: `Logging`
Centralized operational and application audit trails.

* **`Event`**: (Time, ComponentID, Level, Message, Metadata [JSONB]).
* **`Error`**: (Time, ComponentID, ExceptionType, Traceback, StackTrace).
