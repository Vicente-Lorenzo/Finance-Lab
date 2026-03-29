# 📈 Quant System Setup Guide (Max Performance Edition)

This document outlines the step-by-step "Super Optimized" configuration for an i9-14900K workstation to prepare the environment for the `Library` project.

## 💻 Hardware Specs
- **CPU:** Intel i9-14900K (AMD64)
- **RAM:** 64GB DDR5 @ 6000MHz
- **Storage:** Samsung 990 Pro 1TB (NVMe)
- **GPU:** RTX 3060 Ti (CUDA enabled)

## 🛠️ Step 1: Core Software Installation (IDEs)
Before configuring the subsystems, install the JetBrains suite (using the JetBrains Toolbox is recommended) as these will be your primary development tools:
1. **PyCharm Professional:** For the Python backend, AI modeling, and backtesting systems.
2. **JetBrains Rider:** For C# development (`Sources/`) and compiling cTrader Robots/Indicators.
3. **DataGrip:** For database management, querying, and verifying schemas.

## ⚙️ Step 2: Windows & WSL2 Pre-Flight Configuration
If you run into issues installing WSL, perform these pre-flight checks:

1. **BIOS Check (Crucial):**
   - Restart your PC and enter BIOS (tap `Del` or `F2`).
   - Look for *Advanced CPU Configuration* or *Overclocking\CPU Features*.
   - Ensure **Intel Virtualization Technology (VT-x)** or **VMX** is set to **Enabled**.
   - Save & Exit (usually `F10`).

2. **Enable Windows Features:**
   Open PowerShell as Administrator and run this command to force features on:
   ```powershell
   Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform, Microsoft-Windows-Subsystem-Linux -NoRestart
   ```
   *(Alternative DISM commands if the above fails):*
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

3. **Reboot:** Restart your computer (even if it doesn't prompt you).

4. **Update Kernel:** Sometimes the base kernel provided with Windows is outdated. Open PowerShell (Admin) and run:
   ```powershell
   wsl --update
   ```

5. **Resource Allocation:** Create or edit `%UserProfile%\.wslconfig` (e.g. `C:\Users\Admin\.wslconfig`):
   ```ini
   [wsl2]
   memory=56GB
   processors=30
   swap=0
   guiApplications=false
   ```
   *(Note: WSL RAM is aggressively set to 56GB and 30 cores. This dedicates maximum resources to WSL for model training, live deployment, database hosting, and the web app, leaving 8GB and 2 threads to the host OS).*

6. **Restart WSL:**
   ```powershell
   wsl --shutdown
   ```

## 🐍 Step 3: Python Environment (WSL2)
Set up the environment for the Python `Library`.

1. Open your Ubuntu terminal.
2. Install Miniforge (Mamba/Conda):
   ```bash
   curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
   bash Miniforge3-$(uname)-$(uname -m).sh
   ```
3. Restart your terminal to initialize Conda/Mamba.
4. Create the project environment:
   ```bash
   mamba env create --file /mnt/c/Users/Admin/OneDrive/Documents/cAlgo/Requirements.yml
   ```

## 🗄️ Step 4: Docker & QuantDB Setup
1. **Install Docker Desktop:** Download and install Docker Desktop for Windows (x86_64).
2. Ensure the **WSL 2 backend** is enabled in Settings.
3. **Data Persistence:** Create a folder for database storage: `C:\QuantDB`.
4. **Launch QuantDB:** Open PowerShell and run this command to start the TimescaleDB container (Trust Mode/No Password):
   ```powershell
   docker run -d `
     --name QuantDB `
     -p 5432:5432 `
     -e POSTGRES_DB=QuantDB `
     -e POSTGRES_HOST_AUTH_METHOD=trust `
     -v C:\QuantDB:/var/lib/postgresql/data `
     timescale/timescaledb-ha:pg18
   ```

## ⚡ Step 5: Database "Super-Tuning"
Connect to QuantDB via **DataGrip** (to verify connectivity and ensure everything is correct) and execute these queries to optimize for the system hardware:
   ```sql
   ALTER SYSTEM SET shared_buffers = '14GB';
   ALTER SYSTEM SET effective_cache_size = '40GB';
   ALTER SYSTEM SET random_page_cost = 1.1;
   ALTER SYSTEM SET max_worker_processes = 30;
   ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
   ALTER SYSTEM SET max_parallel_workers = 30;
   SELECT pg_reload_conf();
   ```

## 🌉 Step 6: cTrader Bridge (npiperelay)
Because WSL2 cannot natively see Windows Named Pipes, we use a relay to bridge the C# robots and the Python backend.

1. Download `npiperelay.exe` from GitHub and place it in a Windows folder (e.g., `C:\tools\`).
2. Open your Ubuntu WSL terminal.
3. Install `socat`:
   ```bash
   sudo apt update && sudo apt install socat -y
   ```

## 🚀 Daily Launch Sequence
Whenever you start working on the project:
1. Start **Docker Desktop**.
2. Start the **Bridge Relay** (Keep this WSL terminal open):
   ```bash
   socat UNIX-LISTEN:/tmp/ctrader_pipe,fork EXEC:"/mnt/c/tools/npiperelay.exe -ep -s //./pipe/YourPipeName",binary
   ```
3. Run DRL agents or your Python backend in **PyCharm Professional** (using the `Quant` WSL Interpreter).