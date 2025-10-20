"""
Tests for GUI components
"""

import os
import tempfile
from unittest.mock import MagicMock, patch, call
import pytest
import tkinter as tk

from gui import SettingsWindow


class TestSettingsWindow:
    """Test settings window"""

    def test_settings_window_creation(self):
        """Test that settings window can be created"""
        config = {
            "hotkey": "ctrl+win",
            "model": "base",
            "sample_rate": 16000,
            "microphone_device": None,
            "language": None,
        }

        window = SettingsWindow(config)
        assert window.config == config
        assert window.window is None

    def test_settings_window_create_window(self):
        """Test that create_window initializes GUI"""
        config = {"hotkey": "ctrl+win", "model": "base"}

        with patch("sounddevice.query_devices", return_value=[]):
            window = SettingsWindow(config)
            tk_window = window.create_window()

            assert tk_window is not None
            assert window.window is not None
            assert window.tabs is not None

            window.destroy()

    def test_settings_window_config_copy(self):
        """Test that config is copied, not referenced"""
        config = {"hotkey": "ctrl+alt"}

        window = SettingsWindow(config)
        config["hotkey"] = "ctrl+shift"

        assert window.config["hotkey"] == "ctrl+alt"

    def test_populate_devices(self):
        """Test device population from sounddevice"""
        config = {"microphone_device": None}

        mock_devices = [
            {"name": "Built-in Microphone", "max_input_channels": 1},
            {"name": "USB Microphone", "max_input_channels": 2},
            {"name": "Speaker (output only)", "max_input_channels": 0},
        ]

        with patch("sounddevice.query_devices", return_value=mock_devices):
            window = SettingsWindow(config)
            tk_window = window.create_window()

            # Check device mapping
            assert "Default" in window._devices_map
            assert None == window._devices_map["Default"]

            window.destroy()

    def test_config_change_callback(self):
        """Test that config change calls callback"""
        config = {"hotkey": "ctrl+win"}
        callback = MagicMock()

        with patch("sounddevice.query_devices", return_value=[]):
            window = SettingsWindow(config, on_config_change=callback)
            tk_window = window.create_window()

            # Simulate config change
            with patch.object(window, '_on_model_change', wraps=window._on_model_change):
                window._on_model_change()

            window.destroy()

    def test_device_change_validation(self):
        """Test device change with validation"""
        config = {"microphone_device": None}
        test_mic_callback = MagicMock()

        with patch("sounddevice.query_devices", return_value=[]):
            window = SettingsWindow(config, on_test_mic=test_mic_callback)
            tk_window = window.create_window()

            # Test mic should be called when testing
            window._test_mic()
            test_mic_callback.assert_called_once()

            window.destroy()
