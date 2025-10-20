"""
Shared test configuration, fixtures, and mocks for fnwispr tests
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Add client to path for imports
client_path = Path(__file__).parent.parent / "client"
sys.path.insert(0, str(client_path))


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config = {
            "hotkey": "ctrl+alt",
            "model": "base",
            "sample_rate": 16000,
            "microphone_device": None,
            "language": None,
        }
        json.dump(config, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_wav_file():
    """Create a temporary WAV file with test audio data"""
    from scipy.io.wavfile import write as write_wav

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_path = f.name

    # Create simple test audio (1 second of sine wave at 16kHz)
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 note
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.sin(2 * np.pi * frequency * t) * 0.3  # Reduce amplitude
    audio_int16 = (audio * 32767).astype(np.int16)

    write_wav(temp_path, sample_rate, audio_int16)
    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_sounddevice():
    """Mock sounddevice for testing without actual audio hardware"""
    with patch("sounddevice.InputStream") as mock_input_stream:
        # Create a mock stream instance
        mock_stream = MagicMock()

        # Mock the stream methods
        mock_stream.start = MagicMock()
        mock_stream.stop = MagicMock()
        mock_stream.close = MagicMock()

        # Return mock stream when InputStream is called
        mock_input_stream.return_value = mock_stream

        yield {
            "InputStream": mock_input_stream,
            "stream": mock_stream,
        }


@pytest.fixture
def mock_pyautogui():
    """Mock pyautogui for testing text insertion"""
    with patch("pyautogui.typewrite") as mock_typewrite:
        yield {"typewrite": mock_typewrite}


@pytest.fixture
def mock_whisper():
    """Mock Whisper model for testing"""
    mock_model = MagicMock()
    mock_model.transcribe = MagicMock(
        return_value={
            "text": "This is a test transcription",
            "language": "en",
            "segments": [],
        }
    )

    with patch("whisper.load_model") as mock_load:
        mock_load.return_value = mock_model
        yield {
            "load_model": mock_load,
            "model": mock_model,
        }


@pytest.fixture
def mock_keyboard():
    """Mock pynput keyboard for testing hotkey detection"""
    with patch("pynput.keyboard.Listener") as mock_listener_class:
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener

        # Mock context manager protocol
        mock_listener.__enter__ = MagicMock(return_value=mock_listener)
        mock_listener.__exit__ = MagicMock(return_value=False)

        yield {
            "Listener": mock_listener_class,
            "listener": mock_listener,
        }


@pytest.fixture
def sample_audio_data():
    """Create sample audio data for testing"""
    # Create 1 second of audio at 16kHz with some amplitude variation
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # Create a more complex audio pattern
    sine_wave = np.sin(2 * np.pi * 440 * t) * 0.2  # 440 Hz at 0.2 amplitude
    noise = np.random.normal(0, 0.05, len(t))  # Add some noise
    audio = sine_wave + noise

    return audio.astype(np.float32)


@pytest.fixture
def logger_handler():
    """Capture log output for testing"""
    import logging

    logger = logging.getLogger("__main__")
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    yield handler
    logger.removeHandler(handler)
