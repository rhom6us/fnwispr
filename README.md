# fnwispr

> Speech-to-text anywhere on Windows with a hotkey

fnwispr is a Windows speech-to-text tool that lets you dictate text in any application using a simple hotkey. Press and hold Ctrl+Alt (configurable), speak, release, and your words appear as text - powered by OpenAI's Whisper running locally in Docker.

## Features

- **Universal Text Input**: Works in any Windows application that accepts text
- **Simple Hotkey**: Press and hold to record, release to transcribe
- **Privacy-First**: All processing happens locally using Docker
- **High Accuracy**: Powered by OpenAI's Whisper speech recognition
- **Multi-Language**: Supports 99+ languages with automatic detection
- **Configurable**: Choose your hotkey, model size, and language preferences
- **No Internet Required**: Works completely offline once models are downloaded

## Architecture

fnwispr uses a hybrid architecture:
- **Windows Client** (Python): Handles hotkeys, audio recording, and text insertion
- **Whisper Service** (Docker): Provides speech recognition API
- **Communication**: Local HTTP REST API

## Quick Start

### Prerequisites

- Windows 10 or 11
- [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Python 3.8 or higher
- A working microphone

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fnwispr.git
   cd fnwispr
   ```

2. **Start the Whisper service**
   ```bash
   docker-compose up -d
   ```

   This will download the Whisper model and start the service. First run may take a few minutes.

3. **Install client dependencies**
   ```bash
   cd client
   pip install -r requirements.txt
   ```

4. **Create configuration file**
   ```bash
   copy config.example.json config.json
   ```

   Edit `config.json` if you want to change the hotkey or other settings.

5. **Run the client**
   ```bash
   python main.py
   ```

### Usage

1. Start the client application (see step 5 above)
2. Open any application where you want to type (e.g., Notepad, Word, browser)
3. Click to place your cursor where you want text inserted
4. Press and hold **Ctrl+Alt** (or your configured hotkey)
5. Speak clearly into your microphone
6. Release the hotkey when done speaking
7. Wait a moment for transcription
8. Your spoken words appear as text at the cursor

**Press ESC to exit the client**

## Configuration

Edit `client/config.json` to customize fnwispr:

```json
{
  "hotkey": "ctrl+win",
  "server_url": "http://localhost:8000",
  "model": "base",
  "sample_rate": 16000,
  "microphone_device": null,
  "language": null
}
```

### Configuration Options

| Option | Description | Default | Options |
|--------|-------------|---------|---------|
| `hotkey` | Key combination to activate recording | `"ctrl+win"` | See "Hotkey Configuration" below |
| `server_url` | Whisper service URL | `"http://localhost:8000"` | Any valid URL |
| `model` | Whisper model size | `"base"` | `tiny`, `base`, `small`, `medium`, `large` |
| `sample_rate` | Audio sample rate | `16000` | 16000 recommended |
| `microphone_device` | Microphone to use | `null` (default) | Device ID number |
| `language` | Force specific language | `null` (auto-detect) | `"en"`, `"es"`, `"fr"`, etc. |

### Hotkey Configuration

The `hotkey` option supports flexible key combinations:

**Modifier keys (both left and right work):**
- `ctrl` - Either left or right Ctrl
- `alt` - Either left or right Alt
- `shift` - Either left or right Shift
- `win` or `cmd` - Windows/Command key

**Specific variants (if you want only left or right):**
- `ctrl_l`, `ctrl_r` - Left or right Ctrl specifically
- `alt_l`, `alt_r` - Left or right Alt specifically
- `shift_l`, `shift_r` - Left or right Shift specifically

**Examples:**
- `"ctrl+win"` - Either Ctrl + either Windows key (recommended)
- `"ctrl+alt"` - Either Ctrl + either Alt
- `"ctrl_l+win"` - Only left Ctrl + either Windows key
- `"alt_r+shift"` - Only right Alt + either Shift
- `"ctrl+shift+a"` - Either Ctrl + either Shift + 'a' key

### Whisper Model Selection

Choose the model that best fits your needs:

| Model | Size | Speed | Accuracy | VRAM | Best For |
|-------|------|-------|----------|------|----------|
| `tiny` | 39M | Fastest | Good | ~1GB | Quick testing, low-end systems |
| `base` | 74M | Fast | Better | ~1GB | **Recommended for most users** |
| `small` | 244M | Medium | Great | ~2GB | Better accuracy needed |
| `medium` | 769M | Slow | Excellent | ~5GB | High accuracy required |
| `large` | 1550M | Slowest | Best | ~10GB | Maximum accuracy |

To change the model, update the `model` field in `config.json` and restart the client.

## Finding Your Microphone Device

To list available audio devices:

```python
import sounddevice as sd
print(sd.query_devices())
```

Look for your microphone in the output and note its device ID number. Add it to `config.json`:

```json
{
  "microphone_device": 1
}
```

## Troubleshooting

### Client can't connect to server

**Problem**: Error message: "Cannot connect to server"

**Solutions**:
1. Make sure Docker Desktop is running
2. Check the service is running: `docker-compose ps`
3. If not running: `docker-compose up -d`
4. Check logs: `docker-compose logs whisper-service`
5. Verify service is healthy: visit http://localhost:8000/health in browser

### No audio being recorded

**Problem**: Transcription returns empty or no text appears

**Solutions**:
1. Check your microphone is connected and working
2. Verify microphone isn't muted in Windows settings
3. Try specifying `microphone_device` explicitly in config (see above)
4. Check client logs in `fnwispr_client.log`

### Slow transcription

**Problem**: Takes too long to transcribe

**Solutions**:
1. Use a smaller model (`tiny` or `base`)
2. Speak shorter phrases (under 30 seconds)
3. Close other applications to free up resources
4. Consider GPU acceleration (requires NVIDIA GPU and configuration)

### Text appears in wrong place

**Problem**: Text inserts somewhere unexpected

**Solutions**:
1. Make sure the target application is focused when you release the hotkey
2. Wait for transcription to complete before clicking elsewhere
3. Some applications may not accept automated text input

### Model download is slow

**Problem**: First-time setup taking a long time

**Solutions**:
- First download can take several minutes depending on model size and internet speed
- The model is cached, so subsequent starts are much faster
- Try starting with `tiny` or `base` model for faster initial setup

## Development

### Local Development (Recommended for Client)

Since the **client must run on Windows** (requires system hotkeys, audio, and keyboard access), you'll typically develop locally:

1. **Install VS Code Extensions**
   - Press `Ctrl+Shift+X` to open Extensions
   - Install recommended extensions (especially **Python** by Microsoft)
   - Or click "Install All" when VS Code prompts for workspace recommendations

2. **Setup Python Environment**
   ```bash
   # Install dependencies
   pip install -r client/requirements.txt
   pip install -r server/requirements.txt
   ```

3. **Start Development**
   - Press `F5` to debug client or server
   - Press `Ctrl+Shift+P` → "Tasks: Run Task" to run tasks
   - See `.vscode/SETUP.md` for detailed VS Code configuration

### Using DevContainer (Server Development Only)

For server-only development, you can use the DevContainer:

1. Install [VS Code](https://code.visualstudio.com/) and [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the project in VS Code
3. Click "Reopen in Container" when prompted
4. Extensions install automatically; server dependencies are pre-installed

**Note**: The client cannot run in the DevContainer (needs Windows host access)

### Running Tests

```bash
# TODO: Add tests
pytest
```

### Project Structure

```
fnwispr/
├── client/              # Windows client application
│   ├── main.py         # Main client application
│   ├── config.example.json  # Example configuration
│   ├── requirements.txt
│   └── setup.py
├── server/              # Whisper service
│   ├── main.py         # FastAPI server
│   ├── Dockerfile
│   └── requirements.txt
├── .devcontainer/       # Development container config
│   ├── devcontainer.json
│   └── Dockerfile
├── docs/                # Documentation
│   └── PRD.md          # Product Requirements Document
├── docker-compose.yml   # Production compose file
├── docker-compose.dev.yml  # Development compose file
├── .env.example         # Environment variables example
├── .gitignore
└── README.md
```

## API Documentation

When the Whisper service is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

- `POST /transcribe` - Transcribe audio file to text
- `GET /health` - Health check
- `GET /models` - List available models
- `GET /` - API information

## How It Works

1. **Hotkey Detection**: The client uses `pynput` to detect when your configured hotkey combination is pressed
2. **Audio Recording**: While the hotkey is held, `sounddevice` captures audio from your microphone
3. **Audio Processing**: When released, the audio is saved as a temporary WAV file
4. **Transcription**: The audio file is sent to the local Whisper service via HTTP POST
5. **Speech Recognition**: Whisper processes the audio and returns transcribed text
6. **Text Insertion**: The client uses `pyautogui` to type the text at the current cursor position

## Privacy & Security

- **Local Processing**: All audio processing happens on your computer
- **No Cloud**: No data is sent to external servers
- **Temporary Files**: Audio recordings are deleted immediately after transcription
- **Isolated Service**: Whisper runs in an isolated Docker container

## Limitations

- **Windows Only**: Client currently only supports Windows (service is cross-platform)
- **Press-to-Transcribe**: No real-time streaming (must finish speaking before transcription)
- **Single Speaker**: Optimized for single-speaker dictation
- **Requires Docker**: Service requires Docker Desktop (licensing considerations for enterprise)

## Roadmap

See [docs/PRD.md](docs/PRD.md) for detailed feature roadmap.

**Upcoming features**:
- System tray integration
- Visual recording indicator
- GPU acceleration support
- MacOS and Linux client support
- Real-time streaming transcription

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - The amazing speech recognition model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for the API
- [pynput](https://github.com/moses-palmer/pynput) - Keyboard and mouse control
- [sounddevice](https://python-sounddevice.readthedocs.io/) - Audio recording

## Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/yourusername/fnwispr/issues)
- **Documentation**: See [docs/](docs/) for detailed documentation
- **FAQ**: Check the Troubleshooting section above

---

**Made with speech-to-text** (obviously!)
