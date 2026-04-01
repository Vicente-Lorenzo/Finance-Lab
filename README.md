# 📈 Quant System Setup Guide (Windows Native Edition)

## 💻 Hardware Specs
- **CPU:** Intel i9-14900K (AMD64)
- **RAM:** 64GB DDR5 @ 6000MHz
- **Storage:** Samsung 990 Pro 1TB (NVMe)
- **GPU:** RTX 3060 Ti (CUDA enabled)

## 🛠️ Step 1: Core Software Installation (IDEs)
Install the JetBrains suite (using the JetBrains Toolbox is recommended) as these will be your primary development tools:
1. **PyCharm Professional:** For the Python backend, AI modeling, and backtesting systems. Ensure the interpreter is set to the local Conda environment once created.
2. **JetBrains Rider:** For C# development (`Sources/`) and compiling legacy cTrader Robots/Indicators.
3. **DataGrip:** For database management, querying, tuning, and verifying schemas.

## ⚙️ Step 2: System Preparation (Clean Windows Environment)
To ensure maximum native performance and avoid virtualization overhead, this setup explicitly avoids WSL and Docker.
1. **Uninstall WSL and Docker:** Ensure Windows Subsystem for Linux and Docker Desktop are completely removed from the system.
2. **Disable Virtualization Features:**
   - Press `Win + R`, type `optionalfeatures.exe`, and press Enter.
   - Uncheck **Windows Subsystem for Linux** and **Virtual Machine Platform**.
   - Restart the computer.
3. **Clear Resource Limits:** Ensure any `.wslconfig` files in `C:\Users\<YourUsername>\` are deleted to release all 64GB of RAM back to Windows.

## 🐍 Step 3: Python Environment Setup
We use Miniforge to handle the environment creation, as it includes the Mamba solver natively and prioritizes the `conda-forge` channel for optimized Windows binaries.
1. **Install Miniforge:** Download and install the [Miniforge3 Windows Installer](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe).
2. **Initialize Shell:** Open the **Miniforge Prompt** from the Start Menu and run:
   ```powershell
   mamba init powershell
   mamba init cmd.exe
   Restart Terminal: Close the Miniforge Prompt and open your standard PowerShell.
3. Create the Project Environment: Navigate to your project directory and run:
   ```powerShell
   cd C:\Users\Admin\OneDrive\Documents\cAlgo
   mamba env create --file Requirements.yml

## 🗄️ Step 4: Native QuantDB Setup (PostgreSQL 18 + TimescaleDB)
1. **Install PostgreSQL:** Download and install the [PostgreSQL 18 MSI for Windows](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
2. **Install TimescaleDB:** Download the [TimescaleDB Windows binaries](https://docs.timescale.com/self-hosted/latest/install/installation-windows/).

## ⚡ Step 5: Database Hardware Auto-Tuning
1. Open **PowerShell as Administrator** in Timescale download folder.
2. Run the tuning tool, pointing it to your PG 18 installation and your custom data directory:
   ```powershell
   .\timescaledb-tune.exe --pg-version=18 --conf-path="C:\Program Files\PostgreSQL\18\data\postgresql.conf"