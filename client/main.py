"""
fnwispr - Windows Speech-to-Text Hotkey Application
Captures audio when hotkey is pressed and inserts transcribed text using local Whisper
"""

import json
import logging
import os
import sys
import tempfile
import threading
from pathlib import Path
from typing import Optional
import traceback
import numpy as np
import pyautogui
import sounddevice as sd
import whisper
from pynput import keyboard
from scipy.io.wavfile import write as write_wav

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
        self.current_keys = set()

        # Parse hotkey combination
        self.hotkey_combo = self.parse_hotkey(self.config.get("hotkey", "ctrl+win"))
        logger.info(f"Hotkey combination: {self.config.get('hotkey', 'ctrl+win')}")

        # Load Whisper model
        model_name = self.config.get("model", "base")
        logger.info(f"Loading Whisper model: {model_name}")
        try:
            self.whisper_model = whisper.load_model(model_name)
            logger.info(f"Whisper model '{model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model '{model_name}': {e}")
            raise

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
            "hotkey": "ctrl+win",
            "server_url": "http://localhost:8000",
            "model": "base",
            "sample_rate": 16000,
            "microphone_device": None,
            "language": None,
        }

        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                logger.info(f"Default configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save default configuration: {e}")

        return default_config

    def normalize_key(self, key) -> Optional[object]:
        """
        Normalize modifier keys to handle left/right variants
        Only normalizes if the base key (not the specific variant) is in the hotkey combo.

        Example:
        - If hotkey is "ctrl+win": ctrl_l and ctrl_r both normalize to ctrl
        - If hotkey is "ctrl_l+win": ctrl_l and ctrl_r are NOT normalized

        Args:
            key: Key to normalize

        Returns:
            Normalized key if applicable, otherwise the original key
        """
        # Map left/right variants to their base key
        if (
            key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r
        ) and keyboard.Key.ctrl in self.hotkey_combo:
            return keyboard.Key.ctrl
        elif (
            key == keyboard.Key.alt_l or key == keyboard.Key.alt_r
        ) and keyboard.Key.alt in self.hotkey_combo:
            return keyboard.Key.alt
        elif (
            key == keyboard.Key.shift_l or key == keyboard.Key.shift_r
        ) and keyboard.Key.shift in self.hotkey_combo:
            return keyboard.Key.shift
        else:
            return key

    def parse_hotkey(self, hotkey_string: str) -> set:
        """
        Parse hotkey string into a set of keys

        Args:
            hotkey_string: String like "ctrl+alt", "ctrl+win", "ctrl_l+win", etc.
                          Supports: ctrl, alt, shift, win/cmd
                          Also supports left/right variants: ctrl_l, ctrl_r, alt_l, alt_r, shift_l, shift_r

        Returns:
            Set of keyboard.Key or keyboard.KeyCode objects
        """
        key_mapping = {
            "ctrl": keyboard.Key.ctrl,
            "ctrl_l": keyboard.Key.ctrl_l,
            "ctrl_r": keyboard.Key.ctrl_r,
            "alt": keyboard.Key.alt,
            "alt_l": keyboard.Key.alt_l,
            "alt_r": keyboard.Key.alt_r,
            "shift": keyboard.Key.shift,
            "shift_l": keyboard.Key.shift_l,
            "shift_r": keyboard.Key.shift_r,
            "cmd": keyboard.Key.cmd,
            "win": keyboard.Key.cmd,
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

        temp_path = None
        try:
            import time

            # Concatenate audio data
            logger.debug(f"Audio chunks recorded: {len(self.audio_data)}")
            audio = np.concatenate(self.audio_data, axis=0)
            logger.debug(f"Audio shape: {audio.shape}, dtype: {audio.dtype}, min: {audio.min():.4f}, max: {audio.max():.4f}")

            # Create temporary file in system temp directory
            temp_dir = tempfile.gettempdir()
            import uuid

            temp_filename = f"fnwispr_audio_{uuid.uuid4().hex[:8]}.wav"
            temp_path = os.path.join(temp_dir, temp_filename)

            # Write audio data directly to file with error handling
            try:
                write_wav(temp_path, self.sample_rate, audio)
                logger.info(f"Audio saved to temporary file: {temp_path}")
            except Exception as write_err:
                logger.error(f"Failed to write WAV file: {write_err}")
                raise

            # Verify file exists immediately after writing
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                logger.debug(f"WAV file created successfully. Size: {file_size} bytes")
            else:
                raise FileNotFoundError(f"WAV file was not created at {temp_path}")

            # Give Windows filesystem time to flush
            time.sleep(0.1)

            # Send to local Whisper for transcription
            transcribed_text = self.transcribe_audio(temp_path)

            if transcribed_text:
                # Insert text at cursor position
                self.insert_text(transcribed_text)

        except Exception as e:
            logger.error(f"Error processing audio: {e}", exc_info=True)

        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    time.sleep(0.05)
                    os.unlink(temp_path)
                    logger.debug(f"Cleaned up temporary file: {temp_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_path}: {e}")

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file using local Whisper model

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text or None if failed
        """
        try:
            from scipy.io import wavfile

            language = self.config.get("language")

            logger.info(f"Transcribing audio file: {audio_path}")

            # Load audio directly using scipy to avoid ffmpeg dependency
            sample_rate_file, audio_data = wavfile.read(audio_path)
            logger.debug(f"Loaded audio: sample_rate={sample_rate_file}, shape={audio_data.shape}, dtype={audio_data.dtype}")

            # Convert to float32 and normalize (Whisper expects float32 in range [-1, 1])
            if audio_data.dtype != np.float32:
                # Convert to float32
                audio_float = audio_data.astype(np.float32)
                # Normalize to [-1, 1] range
                if audio_data.dtype == np.int16:
                    audio_float = audio_float / 32768.0
                elif audio_data.dtype == np.int32:
                    audio_float = audio_float / 2147483648.0
                elif audio_data.dtype == np.uint8:
                    audio_float = (audio_float - 128) / 128.0
            else:
                audio_float = audio_data

            # Ensure mono (if stereo, take first channel)
            if len(audio_float.shape) > 1:
                audio_float = audio_float[:, 0]

            logger.debug(f"Prepared audio: shape={audio_float.shape}, dtype={audio_float.dtype}, min={audio_float.min():.4f}, max={audio_float.max():.4f}")

            # Build transcribe options
            transcribe_options = {}
            if language:
                transcribe_options["language"] = language

            # Transcribe using the audio data directly (not file path)
            result = self.whisper_model.transcribe(audio_float, language=language)

            transcribed_text = result.get("text", "").strip()
            detected_language = result.get("language")

            logger.info(f"Transcription successful. Language: {detected_language}")
            logger.info(f"Transcribed text: {transcribed_text}")

            return transcribed_text

        except Exception as e:
            logger.error(traceback.format_exc())
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
            # Normalize the key (handle left/right variants of modifiers)
            normalized_key = self.normalize_key(key)

            # Track currently pressed key
            self.current_keys.add(normalized_key)

            # Check if all hotkey keys are currently pressed
            if self.hotkey_combo.issubset(self.current_keys):
                self.start_recording()

        except Exception as e:
            logger.debug(f"Error in on_press: {e}")

    def on_release(self, key):
        """
        Keyboard release event handler

        Args:
            key: Released key
        """
        try:
            # Normalize the key (handle left/right variants of modifiers)
            normalized_key = self.normalize_key(key)

            # Remove released key from tracking
            self.current_keys.discard(normalized_key)

            # Stop recording when any of the hotkey keys is released
            if normalized_key in self.hotkey_combo and self.recording:
                self.stop_recording()

            # Exit on Escape key
            if key == keyboard.Key.esc:
                logger.info("Escape pressed, shutting down...")
                self.is_running = False
                return False
        except Exception as e:
            logger.debug(f"Error in on_release: {e}")

    def run(self):
        """Run the client"""
        logger.info("fnwispr starting...")
        logger.info(f"Press and hold {self.config.get('hotkey', 'ctrl+win')} to record")
        logger.info("Press ESC to exit")

        # Start keyboard listener
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            logger.info("Keyboard listener started. Ready to record!")
            listener.join()

        logger.info("fnwispr stopped")

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
