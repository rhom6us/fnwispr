"""
fnwispr Client - Windows Speech-to-Text Hotkey Application
Captures audio when hotkey is pressed and inserts transcribed text
"""

import os
import sys
import json
import logging
import tempfile
import threading
from pathlib import Path
from typing import Optional

import requests
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write as write_wav
from pynput import keyboard
import pyautogui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fnwispr_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FnwisprClient:
    """
    Windows client for fnwispr speech-to-text service
    """

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the client

        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.recording = False
        self.audio_data = []
        self.sample_rate = self.config.get("sample_rate", 16000)
        self.is_running = True

        # Parse hotkey combination
        self.hotkey_combo = self.parse_hotkey(self.config.get("hotkey", "ctrl+alt"))
        logger.info(f"Hotkey combination: {self.config.get('hotkey', 'ctrl+alt')}")
        logger.info(f"Server URL: {self.config.get('server_url')}")
        logger.info(f"Whisper model: {self.config.get('model', 'base')}")

    def load_config(self, config_path: str) -> dict:
        """
        Load configuration from JSON file

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Configuration loaded from {config_path}")
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            logger.info("Creating default configuration file...")
            default_config = self.create_default_config(config_path)
            return default_config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)

    def create_default_config(self, config_path: str) -> dict:
        """
        Create default configuration file

        Args:
            config_path: Path where config should be saved

        Returns:
            Default configuration dictionary
        """
        default_config = {
            "hotkey": "ctrl+alt",
            "server_url": "http://localhost:8000",
            "model": "base",
            "sample_rate": 16000,
            "microphone_device": None,
            "language": None
        }

        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                logger.info(f"Default configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save default configuration: {e}")

        return default_config

    def parse_hotkey(self, hotkey_string: str) -> set:
        """
        Parse hotkey string into a set of keys

        Args:
            hotkey_string: String like "ctrl+alt" or "ctrl+shift+a"

        Returns:
            Set of keyboard.Key or keyboard.KeyCode objects
        """
        key_mapping = {
            'ctrl': keyboard.Key.ctrl,
            'alt': keyboard.Key.alt,
            'shift': keyboard.Key.shift,
            'cmd': keyboard.Key.cmd,
            'win': keyboard.Key.cmd,
        }

        keys = set()
        for part in hotkey_string.lower().split('+'):
            part = part.strip()
            if part in key_mapping:
                keys.add(key_mapping[part])
            elif len(part) == 1:
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                logger.warning(f"Unknown key: {part}")

        return keys

    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback for audio recording

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Stream status
        """
        if status:
            logger.warning(f"Audio stream status: {status}")

        if self.recording:
            self.audio_data.append(indata.copy())

    def start_recording(self):
        """Start audio recording"""
        if not self.recording:
            logger.info("Started recording...")
            self.recording = True
            self.audio_data = []

            # Get microphone device
            device = self.config.get("microphone_device")

            try:
                self.stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=1,
                    callback=self.audio_callback,
                    device=device
                )
                self.stream.start()
            except Exception as e:
                logger.error(f"Failed to start audio recording: {e}")
                self.recording = False

    def stop_recording(self):
        """Stop audio recording and process the audio"""
        if self.recording:
            logger.info("Stopped recording")
            self.recording = False

            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")

            # Process the recorded audio in a separate thread to avoid blocking
            threading.Thread(target=self.process_audio, daemon=True).start()

    def process_audio(self):
        """Process recorded audio and insert transcribed text"""
        if not self.audio_data:
            logger.warning("No audio data recorded")
            return

        try:
            # Concatenate audio data
            audio = np.concatenate(self.audio_data, axis=0)

            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                write_wav(temp_path, self.sample_rate, audio)

            logger.info(f"Audio saved to temporary file: {temp_path}")

            # Send to server for transcription
            transcribed_text = self.transcribe_audio(temp_path)

            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")

            if transcribed_text:
                # Insert text at cursor position
                self.insert_text(transcribed_text)

        except Exception as e:
            logger.error(f"Error processing audio: {e}")

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Send audio to server for transcription

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text or None if failed
        """
        try:
            server_url = self.config.get("server_url")
            model = self.config.get("model", "base")
            language = self.config.get("language")

            url = f"{server_url}/transcribe"

            with open(audio_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {'model_name': model}
                if language:
                    data['language'] = language

                logger.info(f"Sending audio to {url} with model={model}")
                response = requests.post(url, files=files, data=data, timeout=60)

            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '')
                detected_language = result.get('language')
                logger.info(f"Transcription successful. Language: {detected_language}")
                logger.info(f"Transcribed text: {text}")
                return text
            else:
                logger.error(f"Transcription failed with status {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to server: {e}")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

    def insert_text(self, text: str):
        """
        Insert text at current cursor position

        Args:
            text: Text to insert
        """
        try:
            # Small delay to ensure the window is ready
            import time
            time.sleep(0.1)

            # Type the text
            pyautogui.typewrite(text, interval=0.01)
            logger.info(f"Text inserted: {text[:50]}...")

        except Exception as e:
            logger.error(f"Failed to insert text: {e}")

    def on_press(self, key):
        """
        Keyboard press event handler

        Args:
            key: Pressed key
        """
        try:
            # Check if all hotkey keys are currently pressed
            current_keys = self.listener.current_keys

            if self.hotkey_combo.issubset(current_keys):
                self.start_recording()

        except AttributeError:
            pass

    def on_release(self, key):
        """
        Keyboard release event handler

        Args:
            key: Released key
        """
        # Stop recording when any of the hotkey keys is released
        if key in self.hotkey_combo and self.recording:
            self.stop_recording()

        # Exit on Escape key
        if key == keyboard.Key.esc:
            logger.info("Escape pressed, shutting down...")
            self.is_running = False
            return False

    def run(self):
        """Run the client"""
        logger.info("fnwispr client starting...")
        logger.info(f"Press and hold {self.config.get('hotkey', 'ctrl+alt')} to record")
        logger.info("Press ESC to exit")

        # Check server connectivity
        if not self.check_server():
            logger.error("Cannot connect to server. Please ensure the server is running.")
            logger.error(f"Server URL: {self.config.get('server_url')}")
            return

        # Start keyboard listener
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            self.listener = listener
            # Add current_keys tracking
            self.listener.current_keys = set()

            # Monkey-patch to track currently pressed keys
            original_on_press = listener._on_press
            original_on_release = listener._on_release

            def tracked_on_press(key):
                self.listener.current_keys.add(key)
                return original_on_press(key)

            def tracked_on_release(key):
                self.listener.current_keys.discard(key)
                return original_on_release(key)

            listener._on_press = tracked_on_press
            listener._on_release = tracked_on_release

            listener.join()

        logger.info("fnwispr client stopped")

    def check_server(self) -> bool:
        """
        Check if server is accessible

        Returns:
            True if server is accessible, False otherwise
        """
        try:
            server_url = self.config.get("server_url")
            response = requests.get(f"{server_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Server is accessible")
                return True
            else:
                logger.warning(f"Server returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Server check failed: {e}")
            return False


def main():
    """Main entry point"""
    # Look for config file in current directory or script directory
    config_path = "config.json"
    if not os.path.exists(config_path):
        script_dir = Path(__file__).parent
        config_path = script_dir / "config.json"

    client = FnwisprClient(str(config_path))
    client.run()


if __name__ == "__main__":
    main()
