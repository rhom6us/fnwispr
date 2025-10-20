# Contributing to fnwispr

Thank you for your interest in contributing to fnwispr! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title**: Summarize the issue in one line
2. **Description**: Detailed description of the bug
3. **Steps to reproduce**: Step-by-step instructions
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Environment**:
   - Windows version
   - Python version
   - Docker Desktop version
   - Whisper model being used
7. **Logs**: Relevant logs from `fnwispr_client.log` or Docker logs

### Suggesting Features

Feature requests are welcome! Please create an issue with:

1. **Clear title**: Feature name
2. **Problem**: What problem does this solve?
3. **Proposed solution**: How should it work?
4. **Alternatives**: Other approaches you've considered
5. **Additional context**: Screenshots, examples, etc.

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/fnwispr.git
   cd fnwispr
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Test the server
   docker-compose up --build

   # Test the client
   cd client
   python main.py
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

   Follow commit message conventions:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - Description of changes
     - Related issues
     - Testing performed
     - Screenshots (if applicable)

## Development Setup

### Using DevContainer (Recommended)

1. Install [VS Code](https://code.visualstudio.com/)
2. Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
3. Open project in VS Code
4. Click "Reopen in Container"

### Manual Setup

1. **Install dependencies**
   ```bash
   # Server dependencies
   cd server
   pip install -r requirements.txt

   # Client dependencies
   cd ../client
   pip install -r requirements.txt
   ```

2. **Run the service**
   ```bash
   cd server
   python main.py
   ```

3. **Run the client**
   ```bash
   cd client
   python main.py
   ```

## Code Style

### Python

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use type hints where possible
- Write docstrings for functions and classes

Example:
```python
def transcribe_audio(self, audio_path: str) -> Optional[str]:
    """
    Send audio to server for transcription

    Args:
        audio_path: Path to audio file

    Returns:
        Transcribed text or None if failed
    """
    # Implementation
```

### Documentation

- Update README.md for user-facing changes
- Update docs/PRD.md for feature additions
- Add inline comments for complex logic
- Keep documentation clear and concise

## Project Structure

```
fnwispr/
├── client/              # Windows client
│   ├── main.py         # Main application
│   ├── config.example.json
│   └── requirements.txt
├── server/              # Whisper service
│   ├── main.py         # FastAPI server
│   ├── Dockerfile
│   └── requirements.txt
├── .devcontainer/       # Dev environment
├── docs/                # Documentation
└── tests/               # Tests (TBD)
```

## Testing Guidelines

### Manual Testing Checklist

Before submitting a PR, test:

- [ ] Client starts without errors
- [ ] Service starts and responds to health checks
- [ ] Hotkey detection works
- [ ] Audio recording captures sound
- [ ] Transcription returns correct text
- [ ] Text insertion works in multiple applications
- [ ] Configuration changes are respected
- [ ] Error handling works gracefully

### Automated Tests

(To be implemented)

```bash
pytest tests/
```

## Areas for Contribution

### High Priority

- GPU acceleration support
- Automated tests
- System tray integration
- Installation scripts/packaging
- Performance optimizations

### Medium Priority

- Support for more hotkey combinations
- Audio preprocessing (noise reduction)
- Visual recording indicator
- Configuration GUI
- Better error messages

### Low Priority

- MacOS client support
- Linux client support
- Multi-language documentation
- Voice commands for text editing
- Transcription history

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue
- **Chat**: (Discord/Slack to be set up)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to fnwispr!
