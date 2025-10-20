# fnwispr - Product Requirements Document

## 1. Overview

### 1.1 Product Name
**fnwispr** (pronounced "eff-en-whisper")

### 1.2 Product Vision
fnwispr is a Windows-native speech-to-text tool that enables users to seamlessly convert spoken words into text in any application using a simple hotkey combination. By leveraging OpenAI's Whisper model, fnwispr provides accurate, privacy-conscious speech recognition that runs locally.

### 1.3 Target Users
- Writers and content creators who prefer dictation
- Developers writing documentation or comments
- Users with accessibility needs requiring voice input
- Professionals who need quick text entry without switching contexts
- Anyone who wants fast, accurate speech-to-text in any Windows application

---

## 2. Problem Statement

### 2.1 Current Pain Points
1. **Context Switching**: Existing speech-to-text solutions require switching to specific applications or interfaces
2. **Limited Integration**: Most tools don't work universally across all Windows applications
3. **Privacy Concerns**: Cloud-based solutions send audio data to external servers
4. **Latency**: Network-dependent services introduce delays in transcription
5. **Cost**: Many accurate speech recognition services require subscriptions

### 2.2 Solution
fnwispr provides a lightweight, always-available hotkey-triggered speech recognition that:
- Works in ANY Windows application with text input
- Runs locally using Docker for privacy and offline capability
- Requires no context switching or special UI
- Provides fast, accurate transcription using state-of-the-art Whisper models

---

## 3. Product Architecture

### 3.1 System Components

#### 3.1.1 Windows Client Application
- **Technology**: Python
- **Responsibilities**:
  - Global hotkey detection (default: Ctrl+Alt)
  - Microphone audio capture
  - Communication with Whisper service via REST API
  - Text insertion at cursor position
  - Configuration management

#### 3.1.2 Whisper Service (Docker)
- **Technology**: Python, FastAPI, OpenAI Whisper
- **Responsibilities**:
  - Audio transcription using Whisper models
  - REST API endpoint for transcription requests
  - Model management and caching
  - Health monitoring

#### 3.1.3 Development Environment
- **Technology**: VS Code DevContainer
- **Purpose**: Consistent development environment across team members

### 3.2 Communication Flow
```
User → Hotkey Press → Audio Recording →
Audio File → HTTP POST → Whisper Service →
Transcribed Text → Text Insertion → Active Window
```

---

## 4. Functional Requirements

### 4.1 Core Features

#### 4.1.1 Hotkey Activation
- **FR-1.1**: System SHALL listen for configurable hotkey combination (default: Ctrl+Alt)
- **FR-1.2**: Audio recording SHALL start when hotkey is pressed and held
- **FR-1.3**: Audio recording SHALL stop when hotkey is released
- **FR-1.4**: System SHALL provide visual/audio feedback for recording state (future enhancement)

#### 4.1.2 Audio Capture
- **FR-2.1**: System SHALL capture audio from configured microphone device
- **FR-2.2**: System SHALL support 16kHz sample rate by default
- **FR-2.3**: System SHALL handle microphone device selection via configuration
- **FR-2.4**: System SHALL gracefully handle microphone access errors

#### 4.1.3 Speech Recognition
- **FR-3.1**: System SHALL transcribe audio using OpenAI Whisper
- **FR-3.2**: System SHALL support multiple Whisper models (tiny, base, small, medium, large)
- **FR-3.3**: System SHALL support automatic language detection
- **FR-3.4**: System SHALL support manual language specification via configuration
- **FR-3.5**: System SHALL cache Whisper models to avoid re-downloading

#### 4.1.4 Text Insertion
- **FR-4.1**: System SHALL insert transcribed text at current cursor position
- **FR-4.2**: System SHALL work with any Windows application accepting text input
- **FR-4.3**: System SHALL preserve cursor focus and window context
- **FR-4.4**: System SHALL handle text insertion errors gracefully

#### 4.1.5 Configuration
- **FR-5.1**: System SHALL support JSON-based configuration file
- **FR-5.2**: System SHALL create default configuration if none exists
- **FR-5.3**: Configuration SHALL include:
  - Hotkey combination
  - Server URL
  - Whisper model selection
  - Sample rate
  - Microphone device (optional)
  - Language (optional)

### 4.2 Service Management

#### 4.2.1 Whisper Service
- **FR-6.1**: Service SHALL expose REST API on port 8000
- **FR-6.2**: Service SHALL provide `/transcribe` endpoint accepting audio files
- **FR-6.3**: Service SHALL provide `/health` endpoint for monitoring
- **FR-6.4**: Service SHALL provide `/models` endpoint listing available models
- **FR-6.5**: Service SHALL support model selection per request

#### 4.2.2 Docker Integration
- **FR-7.1**: Service SHALL run in Docker container
- **FR-7.2**: Service SHALL be launchable via docker-compose
- **FR-7.3**: Service SHALL persist model cache across container restarts
- **FR-7.4**: Service SHALL support environment-based configuration

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **NFR-1.1**: Transcription SHALL complete within 10 seconds for 30-second audio clips (base model)
- **NFR-1.2**: Text insertion SHALL occur within 500ms of transcription completion
- **NFR-1.3**: Hotkey detection SHALL have <100ms latency
- **NFR-1.4**: Service SHALL handle concurrent transcription requests

### 5.2 Reliability
- **NFR-2.1**: Client SHALL handle service unavailability gracefully
- **NFR-2.2**: Client SHALL log errors for troubleshooting
- **NFR-2.3**: Service SHALL recover from transcription errors without crashing
- **NFR-2.4**: Service SHALL implement health checks for monitoring

### 5.3 Usability
- **NFR-3.1**: Setup SHALL require <10 minutes for technical users
- **NFR-3.2**: Configuration SHALL use human-readable JSON format
- **NFR-3.3**: Error messages SHALL be clear and actionable
- **NFR-3.4**: Documentation SHALL cover common use cases and troubleshooting

### 5.4 Security & Privacy
- **NFR-4.1**: Audio data SHALL NOT be transmitted over network except to local Docker service
- **NFR-4.2**: No audio recordings SHALL be persisted after transcription
- **NFR-4.3**: Service SHALL run in isolated Docker container
- **NFR-4.4**: Client SHALL validate server responses

### 5.5 Compatibility
- **NFR-5.1**: Client SHALL support Windows 10 and Windows 11
- **NFR-5.2**: Service SHALL support x86_64 architecture
- **NFR-5.3**: Client SHALL support Python 3.8+
- **NFR-5.4**: Service SHALL support Docker Desktop for Windows

---

## 6. User Workflows

### 6.1 Initial Setup
1. Clone repository
2. Start Whisper service: `docker-compose up -d`
3. Install client dependencies: `pip install -r client/requirements.txt`
4. Copy and configure `config.example.json` to `config.json`
5. Run client: `python client/main.py`

### 6.2 Daily Usage
1. Ensure Whisper service is running (one-time on system start)
2. Launch client application
3. Navigate to any application with text input
4. Press and hold hotkey while speaking
5. Release hotkey
6. Transcribed text appears at cursor position

### 6.3 Configuration Changes
1. Stop client application
2. Edit `config.json` with desired settings
3. Restart client application

---

## 7. Configuration Specification

### 7.1 Client Configuration (config.json)
```json
{
  "hotkey": "ctrl+alt",           // Hotkey combination
  "server_url": "http://localhost:8000",  // Whisper service URL
  "model": "base",                 // Whisper model (tiny/base/small/medium/large)
  "sample_rate": 16000,            // Audio sample rate
  "microphone_device": null,       // Microphone device ID (null = default)
  "language": null                 // Language code (null = auto-detect)
}
```

### 7.2 Service Configuration (.env)
```env
WHISPER_MODEL=base  # Default model to load on startup
```

---

## 8. API Specification

### 8.1 POST /transcribe
**Description**: Transcribe audio file to text

**Request**:
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `audio` (file): Audio file (WAV, MP3, etc.)
  - `model_name` (string): Whisper model to use (default: "base")
  - `language` (string, optional): Language code

**Response**:
```json
{
  "text": "Transcribed text content",
  "language": "en"
}
```

### 8.2 GET /health
**Description**: Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "base"
}
```

### 8.3 GET /models
**Description**: List available models

**Response**:
```json
{
  "models": ["tiny", "base", "small", "medium", "large"],
  "current_model": "base",
  "description": {
    "tiny": "Fastest, least accurate (~1GB VRAM)",
    "base": "Good balance of speed and accuracy (~1GB VRAM)",
    ...
  }
}
```

---

## 9. Technical Constraints

### 9.1 Hardware Requirements
- **Minimum**:
  - 4GB RAM (for tiny/base models)
  - 2GB disk space
  - Microphone input device
- **Recommended**:
  - 8GB RAM (for small/medium models)
  - 10GB disk space
  - NVIDIA GPU with 4GB+ VRAM (for faster transcription)

### 9.2 Software Requirements
- Windows 10/11
- Docker Desktop for Windows
- Python 3.8 or higher
- Working microphone

### 9.3 Limitations
- Windows-only client (Linux/Mac could use similar architecture)
- Requires Docker Desktop (licensing considerations for enterprise)
- Real-time streaming not supported (press-to-transcribe only)
- No speaker diarization (single speaker assumed)

---

## 10. Future Enhancements

### 10.1 Phase 2 Features
- **FE-1**: System tray integration with status indicator
- **FE-2**: Visual feedback during recording (overlay icon)
- **FE-3**: Push-to-talk alternative mode (click once to start/stop)
- **FE-4**: Audio preprocessing (noise reduction, normalization)
- **FE-5**: Punctuation and capitalization improvements
- **FE-6**: Custom vocabulary and corrections
- **FE-7**: GPU acceleration support for Whisper
- **FE-8**: MacOS and Linux client support

### 10.2 Phase 3 Features
- **FE-9**: Real-time streaming transcription
- **FE-10**: Multi-language switching
- **FE-11**: Voice commands for text editing (delete, capitalize, etc.)
- **FE-12**: Integration with clipboard for non-insertable contexts
- **FE-13**: Transcription history and search
- **FE-14**: Cloud sync for configuration

---

## 11. Success Metrics

### 11.1 Technical Metrics
- Transcription accuracy >90% (measured with WER - Word Error Rate)
- End-to-end latency <5 seconds for typical use
- Client crash rate <1%
- Service uptime >99%

### 11.2 User Metrics
- Setup completion rate >80%
- Daily active usage >5 transcriptions per user
- User satisfaction score >4/5
- Feature request diversity (indicates broad usage)

---

## 12. Open Questions

1. **Q**: Should we support GPU acceleration in initial release?
   - **A**: No, CPU-only for v1.0, GPU support in v1.1

2. **Q**: How should we handle very long recordings (>5 minutes)?
   - **A**: Implement 5-minute limit with user warning, document in README

3. **Q**: Should configuration be GUI-based or JSON-only?
   - **A**: JSON-only for v1.0, GUI configuration tool in v2.0

4. **Q**: Do we need audio preprocessing (noise reduction)?
   - **A**: Not in v1.0, evaluate based on user feedback

---

## 13. Release Plan

### 13.1 Version 1.0 (MVP)
- Core hotkey-to-text functionality
- Docker-based Whisper service
- JSON configuration
- Basic error handling
- Documentation and README

### 13.2 Version 1.1
- GPU acceleration support
- Improved error messages
- System tray integration
- Auto-start with Windows

### 13.3 Version 2.0
- GUI configuration tool
- Visual recording feedback
- Multi-platform support (Linux, MacOS)
- Advanced audio preprocessing

---

## 14. Appendix

### 14.1 Whisper Model Comparison
| Model  | Size | VRAM | Speed | Accuracy |
|--------|------|------|-------|----------|
| tiny   | 39M  | ~1GB | 32x   | Good     |
| base   | 74M  | ~1GB | 16x   | Better   |
| small  | 244M | ~2GB | 6x    | Great    |
| medium | 769M | ~5GB | 2x    | Excellent|
| large  | 1550M| ~10GB| 1x    | Best     |

### 14.2 Supported Audio Formats
Whisper (via FFmpeg) supports:
- WAV
- MP3
- FLAC
- OGG
- M4A
- And many more via FFmpeg

### 14.3 Language Support
Whisper supports 99+ languages including:
- English, Spanish, French, German, Italian, Portuguese
- Chinese (Mandarin), Japanese, Korean
- Arabic, Hindi, Russian
- And many more...

---

**Document Version**: 1.0
**Last Updated**: 2025-10-19
**Author**: fnwispr Team
