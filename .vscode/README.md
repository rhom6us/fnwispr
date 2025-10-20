# VS Code Configuration

This directory contains VS Code workspace configuration for fnwispr development.

## Required Extensions

Before using the debug configurations and tasks, install the recommended extensions:

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Extensions: Show Recommended Extensions"
3. Click "Install All" or install individually

**Critical for debugging:**
- `ms-python.python` - Python language support and debugger

**Recommended for development:**
- `ms-python.vscode-pylance` - Python language server
- `ms-python.black-formatter` - Code formatting
- `ms-azuretools.vscode-docker` - Docker support
- `eamodio.gitlens` - Git integration

## Quick Start

### If you see "debug type is not recognized"

Install the Python extension:
```
1. Press Ctrl+Shift+X (Extensions view)
2. Search for "Python"
3. Install "Python" by Microsoft (ms-python.python)
4. Reload VS Code
```

### Using Tasks

Press `Ctrl+Shift+P` and type "Tasks: Run Task" to see all available tasks.

Common tasks:
- **Build: All Docker Services** - Build the Whisper service
- **Run: Start Whisper Service** - Start the Docker service
- **Run: Client** - Run the Windows client
- **Test: All Tests** - Run test suite
- **Lint: All** - Format and lint code

### Using Debug Configurations

Press `F5` or go to Run and Debug view (`Ctrl+Shift+D`).

Available configurations:
- **Debug: Client** - Debug the Windows client (checks server health first)
- **Debug: Server (Local)** - Debug the FastAPI server locally
- **Debug: Full Stack** - Debug both client and server simultaneously
- **Debug: Current Test File** - Debug the currently open test file

## Files

- `tasks.json` - Task definitions for build, run, test, lint operations
- `launch.json` - Debug configurations
- `settings.json` - Workspace settings (Python, formatting, linting)
- `extensions.json` - Recommended extensions
