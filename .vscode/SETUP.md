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

fnwispr is now a single, unified application that runs entirely on your Windows machine with no Docker or server/client split. Follow these steps:

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
2. Select "Debug: fnwispr"
3. The app should start with the keyboard listener ready

### 3. Python Interpreter (Automatic)

The Python interpreter is now automatically configured to use the virtual environment created by `init.ps1`.

**If you need to manually select it:**
1. Press `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. Choose `./venv/Scripts/python.exe` from the list

## Essential Extensions

| Extension | Purpose |
|-----------|---------|
| ms-python.python | Python debugging & IntelliSense (Required) |
| ms-python.vscode-pylance | Advanced type checking & IntelliSense |
| ms-python.black-formatter | Code formatting (matches project settings) |
| ms-python.flake8 | Linting (matches project settings) |

## Troubleshooting

### "Python extension not found"
- Restart VS Code completely
- Check Extensions view to confirm it's installed and enabled
- Try uninstalling and reinstalling the Python extension

### "No Python interpreter selected"
- Run `Python: Select Interpreter` from Command Palette
- Ensure Python 3.8+ is installed on your system
- Try providing the full path to python.exe

### App fails to start with "No module named 'X'"
- Run the `Build: Install Dependencies` task
- Or manually: `Ctrl+Shift+P` → `Tasks: Run Task` → `Build: Install Dependencies`

### Hotkey not working
- Make sure VS Code window isn't blocking keyboard input (may need to focus another window)
- Check the log file: `Utility: View Application Logs` task
- Verify your hotkey config in `client/config.json`

## Next Steps

Once environment is initialized and extensions are installed:

1. **Test the App**
   - Press `F5` to start debugging
   - Press Ctrl+Win to record (or your configured hotkey)
   - Speak into your microphone
   - Release the keys to transcribe

2. **Run Tests**
   - Press `Ctrl+Shift+P` → `Tasks: Run Task`
   - Select `Test: All Tests`

3. **Format and Lint Code**
   - Press `Ctrl+Shift+P` → `Tasks: Run Task`
   - Select `Lint: All` to format and check code

4. **Review Available Tasks**
   - Press `Ctrl+Shift+P` → `Tasks: Run Task` to see all available development tasks
