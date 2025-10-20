# VS Code Setup for fnwispr

## Quick Start

### 1. Initialize the Development Environment

First-time setup: Run the initialization task to set up your virtual environment and install all dependencies.

**Option A: Via VS Code Task (Recommended)**
1. Press `Ctrl+Shift+P`
2. Type: `Tasks: Run Task`
3. Select: `Dev: Initialize Environment`
4. Wait for completion (includes virtual environment setup and dependency installation)

**Option B: Manual via PowerShell**
```powershell
.\init.ps1
```

### 2. Reload VS Code

After initialization, reload VS Code to activate the virtual environment:
- Press `Ctrl+Shift+P` → type `Developer: Reload Window`
- Or simply close and reopen VS Code

The virtual environment will now be **automatically activated** in all terminals and used by the Python extension.

---

## For Local Development (Windows)

Since the fnwispr client must run on Windows (not in Docker), you'll be developing locally. Follow these steps:

### 1. Install Python Extension

The error **"The debug type is not recognized"** means VS Code doesn't have the Python extension (which includes debugpy) installed.

**Option A: Install All Recommended Extensions (Easiest)**
1. Open VS Code
2. Look for a popup asking to install recommended extensions
3. Click "Install All"

**Option B: Manual Installation**
1. Open Extensions view: `Ctrl+Shift+X`
2. Search for "Python"
3. Install **"Python"** by Microsoft (Extension ID: `ms-python.python`)
4. Reload VS Code when prompted

**Option C: Command Palette**
1. Press `Ctrl+Shift+P`
2. Type: `Extensions: Show Recommended Extensions`
3. Click "Install" next to each extension

### 2. Verify Installation

After installing extensions:
1. Press `F5` or `Ctrl+Shift+D` (Run and Debug)
2. Select a debug configuration (e.g., "Debug: Client")
3. You should no longer see the error

### 3. Python Interpreter (Automatic)

The Python interpreter is now automatically configured to use the virtual environment created by `init.ps1`.

**If you need to manually select it:**
1. Press `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. Choose `./venv/Scripts/python.exe` from the list

## For DevContainer Development

If using the DevContainer (for server-only development):
1. Install the "Dev Containers" extension (`ms-vscode-remote.remote-containers`)
2. Press `Ctrl+Shift+P`
3. Type: `Dev Containers: Reopen in Container`
4. Extensions will be automatically installed inside the container

## Essential Extensions

| Extension | Purpose |
|-----------|---------|
| ms-python.python | Python debugging & IntelliSense (Required) |
| ms-python.vscode-pylance | Advanced type checking & IntelliSense |
| ms-python.black-formatter | Code formatting (matches project settings) |
| ms-python.flake8 | Linting (matches project settings) |
| ms-azuretools.vscode-docker | Docker container management |

## Troubleshooting

### "Python extension not found"
- Restart VS Code completely
- Check Extensions view to confirm it's installed and enabled
- Try uninstalling and reinstalling the Python extension

### "No Python interpreter selected"
- Run `Python: Select Interpreter` from Command Palette
- Ensure Python 3.8+ is installed on your system
- Try providing the full path to python.exe

### Debug configurations still not working
- Verify `.vscode/launch.json` exists
- Check Output panel → Python Language Server for errors
- Ensure you're opening the workspace folder, not individual files

## Next Steps

Once environment is initialized and extensions are installed:

1. **Start the Whisper Service**
   - Press `Ctrl+Shift+P` → `Tasks: Run Task`
   - Select `Run: Start Whisper Service` (or `Run (No Debug): Server in Docker`)
   - Wait for service to be healthy (check logs: `Utility: View Server Logs` task)

2. **Run or Debug the Client**
   - Press `F5` for debugging with breakpoints
   - Or press `Ctrl+Shift+P` → `Tasks: Run Task` → `Run (No Debug): Client` to run without debugging

3. **Review Available Tasks**
   - Press `Ctrl+Shift+P` → `Tasks: Run Task` to see all available development tasks
   - Common tasks: `Dev: Rebuild and Restart`, `Test: All Tests`, `Lint: All`
