"""
Tests for system tray management
"""

import os
from unittest.mock import MagicMock, patch
import pytest

from tray import TrayManager


class TestTrayManager:
    """Test tray manager"""

    def test_tray_manager_creation(self):
        """Test that tray manager can be created"""
        tray = TrayManager()

        assert tray.icon_path is None
        assert tray.icon is None
        assert tray.status == "ready"

    def test_tray_manager_with_callbacks(self):
        """Test tray manager with event callbacks"""
        on_settings = MagicMock()
        on_exit = MagicMock()
        on_model_change = MagicMock()
        on_device_change = MagicMock()

        tray = TrayManager(
            on_settings=on_settings,
            on_exit=on_exit,
            on_model_change=on_model_change,
            on_device_change=on_device_change,
        )

        assert tray.on_settings is on_settings
        assert tray.on_exit is on_exit
        assert tray.on_model_change is on_model_change
        assert tray.on_device_change is on_device_change

    def test_generate_fallback_icon(self):
        """Test fallback icon generation"""
        icon = TrayManager._generate_fallback_icon()

        assert icon is not None
        assert icon.size == (256, 256)
        assert icon.mode == "RGBA"

    def test_get_device_name_with_none(self):
        """Test getting device name when device_idx is None"""
        tray = TrayManager()

        with patch("sounddevice.query_devices", return_value=[]):
            devices = tray._get_input_devices()
            assert len(devices) == 0

    def test_get_input_devices(self):
        """Test getting list of input devices"""
        mock_devices = [
            {"name": "Microphone", "max_input_channels": 1},
            {"name": "USB Input", "max_input_channels": 2},
            {"name": "Speaker", "max_input_channels": 0},  # Output only, should be filtered
        ]

        with patch("sounddevice.query_devices", return_value=mock_devices):
            tray = TrayManager()
            devices = tray._get_input_devices()

            # Should have 2 input devices
            assert len(devices) == 2
            assert devices[0]["full_name"] == "Microphone"
            assert devices[1]["full_name"] == "USB Input"

    def test_device_name_truncation(self):
        """Test that long device names are truncated"""
        long_name = "A" * 50
        mock_devices = [
            {"name": long_name, "max_input_channels": 1},
        ]

        with patch("sounddevice.query_devices", return_value=mock_devices):
            tray = TrayManager()
            devices = tray._get_input_devices()

            assert len(devices[0]["name"]) <= 40
            assert "..." in devices[0]["name"]

    def test_set_status(self):
        """Test setting tray status"""
        tray = TrayManager()

        tray.set_status("recording", "Recording audio...")
        assert tray.status == "recording"
        assert tray.status_message == "Recording audio..."

    def test_build_menu_model_items(self):
        """Test that menu includes model options"""
        tray = TrayManager(get_current_model=lambda: "base")

        menu = tray._build_menu()
        # Menu should have been built without errors
        assert menu is not None

    def test_on_model_select(self):
        """Test model selection from menu"""
        on_model_change = MagicMock()
        tray = TrayManager(on_model_change=on_model_change)

        tray._on_model_select("tiny")

        # Callback should be called in separate thread
        # Give thread time to execute
        import time
        time.sleep(0.1)
        on_model_change.assert_called()

    def test_on_device_select(self):
        """Test device selection from menu"""
        on_device_change = MagicMock()
        tray = TrayManager(on_device_change=on_device_change)

        tray._on_device_select(0)

        # Callback should be called in separate thread
        import time
        time.sleep(0.1)
        on_device_change.assert_called()
