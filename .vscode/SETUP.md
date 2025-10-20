# VS Code Setup for fnwispr

## For Local Development (Windows)

Since the fnwispr client must run on Windows (not in Docker), you'll be developing locally. Follow these steps:

### 1. Install Python Extension

The error **"The debug type is not recognized"** means VS Code doesn't have the Python extension installed.

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

### 3. Select Python Interpreter

1. Press `Ctrl+Shift+P`
2. Type: `Python: Select Interpreter`
3. Choose your Python installation (3.8+ required)

## For DevContainer Development

If using the DevContainer (for server-only development):
1. Install the "Dev Containers" extension (`ms-vscode-remote.remote-containers`)
2. Press `Ctrl+Shift+P`
3. Type: `Dev Containers: Reopen in Container`
4. Extensions will be automatically installed inside the container

## Essential Extensions

| Extension | Purpose | Required For |
|-----------|---------|--------------|
| ms-python.python | Python debugging & IntelliSense | **Required** |
| ms-python.vscode-pylance | Advanced type checking | Recommended |
| ms-python.black-formatter | Code formatting | Recommended |
| ms-azuretools.vscode-docker | Docker support | Optional |

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

Once extensions are installed:
1. Review `.vscode/tasks.json` for available tasks
2. Try running "Run: Start Whisper Service" task
3. Use `F5` to start debugging the client or server
