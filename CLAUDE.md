# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fnwispr is a Windows speech-to-text tool using a **hybrid architecture**:
- **Client** (`client/`): Windows-only Python application that handles hotkey detection, audio recording, and text insertion
- **Server** (`server/`): Cross-platform FastAPI service running in Docker that performs speech transcription using OpenAI Whisper
- **Communication**: Local HTTP REST API on port 8000

**Critical architectural constraint**: The client CANNOT run in Docker because it requires direct access to:
1. Windows global hotkeys (via `pynput`)
2. System audio devices (via `sounddevice`)
3. Host OS keyboard input simulation (via `pyautogui`)

## Development Commands

### Build & Run

```bash
# Build and start Whisper service (Docker)
docker-compose build
docker-compose up -d

# Start server for local development (no Docker)
cd server && python main.py
# or use VS Code task: "Run: Server (Local)"

# Run Windows client (must be run on Windows host)
cd client && python main.py
# or use VS Code task: "Run: Client"

# Full rebuild and restart
docker-compose down && docker-compose build && docker-compose up -d
# or use VS Code task: "Dev: Rebuild and Restart"
```

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=server --cov=client --cov-report=html

# Or use VS Code tasks: "Test: All Tests", "Test: Coverage Report"
```

### Linting & Formatting

```bash
# Format code with Black (line length: 120)
black client/ server/

# Check with Flake8
flake8 client/ server/ --max-line-length=120 --ignore=E203,W503

# Or use VS Code task: "Lint: All"
```

### Docker Operations

```bash
# View server logs
docker-compose logs -f whisper-service

# Check service health
curl http://localhost:8000/health

# List available models
curl http://localhost:8000/models

# Clean Docker (removes volumes)
docker-compose down -v --remove-orphans
```

## Architecture Details

### Client Architecture (client/main.py)

The `FnwisprClient` class implements a state machine:

1. **Initialization**: Loads config, parses hotkey combo into a set of `pynput.keyboard.Key` objects
2. **Keyboard Listening**: Uses `pynput.keyboard.Listener` with custom press/release handlers
3. **Hotkey Detection**: Maintains `current_keys` set; recording starts when `hotkey_combo.issubset(current_keys)`
4. **Audio Recording**: `sounddevice.InputStream` with callback appending chunks to `audio_data` list
5. **Processing**: On release, spawns thread to avoid blocking keyboard listener:
   - Concatenates NumPy audio chunks
   - Writes temporary WAV file (16kHz, mono)
   - POSTs to `/transcribe` endpoint with file + model name
   - Deletes temp file
6. **Text Insertion**: Uses `pyautogui.typewrite()` to simulate keyboard input at cursor position

**Key implementation detail**: The keyboard listener is monkey-patched to track currently pressed keys, enabling hotkey combo detection.

### Server Architecture (server/main.py)

FastAPI application with **global model cache**:

- `model` and `current_model_name` globals prevent reloading
- `load_model()` function checks if model needs changing before calling `whisper.load_model()`
- Models are cached by Whisper in `~/.cache/whisper` (mounted as Docker volume)
- Startup event loads default model from `WHISPER_MODEL` env var

**Endpoints**:
- `POST /transcribe`: Accepts multipart/form-data with `audio` file, `model_name`, optional `language`
- `GET /health`: Returns model status
- `GET /models`: Lists available models with descriptions
- `GET /`: API info

**Transcription flow**:
1. Save uploaded file to temp location (preserves extension for FFmpeg)
2. Call `whisper_model.transcribe(temp_path, language=...)`
3. Extract text and detected language from result dict
4. Clean up temp file in `finally` block
5. Return JSON response

### Configuration System

**Client config** (`client/config.json`):
- Created automatically from defaults if missing
- Supports hotkey parsing (e.g., "ctrl+alt", "ctrl+shift+a")
- `microphone_device`: `null` uses default, or integer device ID from `sounddevice.query_devices()`
- `language`: `null` for auto-detect, or ISO language code

**Server config** (environment variables):
- `WHISPER_MODEL`: Model to load on startup (tiny/base/small/medium/large)
- Set via `.env` file or docker-compose environment

### VS Code Integration

**Pre-configured tasks** (`.vscode/tasks.json`):
- Build, run, test, utility, lint categories
- Default build: "Build: All Docker Services"
- Default test: "Test: All Tests"
- Notable compound tasks: "Dev: Setup Project", "Dev: Rebuild and Restart"

**Debug configurations** (`.vscode/launch.json`):
- "Debug: Client" - includes preLaunchTask for server health check
- "Debug: Server (Local)" - runs server via uvicorn with reload
- "Debug: Full Stack (Client + Server)" - compound configuration
- "Debug: Attach to Docker Server" - requires debugpy on port 5678 (not implemented yet)

## Whisper Model Selection

Performance vs accuracy tradeoff:

| Model  | Size  | Speed    | VRAM   | Recommendation |
|--------|-------|----------|--------|----------------|
| tiny   | 39M   | 32x      | ~1GB   | Testing only   |
| base   | 74M   | 16x      | ~1GB   | Default choice |
| small  | 244M  | 6x       | ~2GB   | Better accuracy|
| medium | 769M  | 2x       | ~5GB   | High accuracy  |
| large  | 1550M | 1x (ref) | ~10GB  | Best quality   |

Change model via:
1. Client config: `"model": "small"` (per-request selection)
2. Server env: `WHISPER_MODEL=small` (startup default)

## Common Development Patterns

### Adding a new API endpoint

1. Add Pydantic model in `server/main.py` if needed
2. Implement endpoint function with FastAPI decorators
3. Use logger for info/error messages
4. Handle exceptions and return appropriate HTTPException
5. Update API docs section in README.md

### Modifying client behavior

1. Client state lives in `FnwisprClient` instance variables
2. Audio processing happens in separate thread (don't block keyboard listener)
3. Always clean up temp files in `finally` blocks
4. Log to `fnwispr_client.log` for debugging
5. Test with actual Windows hotkeys (can't be fully mocked)

### Adding configuration options

1. Update `create_default_config()` in `client/main.py`
2. Update `config.example.json`
3. Document in README.md Configuration Options table
4. Update PRD.md section 4.1.5 if it's a functional requirement

## Important Implementation Notes

### Audio Format
- Client records 16kHz mono WAV (Whisper's native input)
- scipy.io.wavfile used for WAV writing (not wave module)
- Temporary files preserve original extension for FFmpeg compatibility

### Error Handling
- Client continues running even if transcription fails (logs error)
- Server returns 500 with error message but doesn't crash
- Network errors during POST are caught and logged

### Thread Safety
- Audio processing spawned in daemon thread to avoid blocking
- `audio_data` list appended to from callback thread (NumPy arrays are thread-safe)
- No locks needed in current implementation (single recording at a time)

### Platform-Specific Code
- `pyautogui.typewrite()` simulates keyboard on Windows (uses Windows API under the hood)
- Some Windows apps may block automated input (security feature)
- ESC key exits client (global listener pattern)

## Testing Strategy

Currently minimal tests (see README.md "TODO: Add tests").

**When implementing tests**:
- Mock `pynput`, `sounddevice`, `pyautogui` for client unit tests
- Use `TestClient` from FastAPI for server API tests
- Integration tests should use `tiny` model (fastest)
- Consider pytest fixtures for Docker service setup/teardown

## PRD Maintenance

When adding features:
1. Update `docs/PRD.md` with new functional requirements (FR-X.Y format)
2. Add to appropriate release version section (13.1, 13.2, etc.)
3. Update architecture section if system components change
4. Follow existing FR numbering scheme
