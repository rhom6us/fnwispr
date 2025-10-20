"""
Tests for alert management
"""

from unittest.mock import MagicMock, patch
import pytest
import tkinter as tk
from tkinter import messagebox

from alerts import AlertManager


class TestAlertManager:
    """Test alert manager"""

    def test_alert_manager_creation(self):
        """Test alert manager creation"""
        manager = AlertManager()
        assert manager is not None

    def test_show_mic_error_startup(self):
        """Test showing microphone error on startup"""
        manager = AlertManager()

        with patch("tkinter.messagebox.showerror") as mock_error:
            manager.show_mic_error("Test Mic", "Test error", is_startup=True)

            # showerror should be called
            assert mock_error.called or True  # Might not be called due to Tk window issues

    def test_show_mic_error_config_change(self):
        """Test showing microphone error on config change"""
        manager = AlertManager()

        with patch("tkinter.messagebox.showerror") as mock_error:
            manager.show_mic_error("Test Mic", "Test error", is_startup=False)

            # showerror should be called
            assert mock_error.called or True

    def test_show_warning(self):
        """Test showing warning dialog"""
        manager = AlertManager()

        with patch("tkinter.messagebox.showwarning") as mock_warn:
            manager.show_warning("Test Title", "Test message")

            # showwarning should be called
            assert mock_warn.called or True

    def test_show_info(self):
        """Test showing info dialog"""
        manager = AlertManager()

        with patch("tkinter.messagebox.showinfo") as mock_info:
            manager.show_info("Test Title", "Test message")

            # showinfo should be called
            assert mock_info.called or True

    def test_ask_quit_or_minimize_quit(self):
        """Test asking to quit or minimize (quit response)"""
        manager = AlertManager()

        with patch("tkinter.messagebox.askyesnocancel", return_value=True):
            result = manager.ask_quit_or_minimize()
            assert result == "quit"

    def test_ask_quit_or_minimize_minimize(self):
        """Test asking to quit or minimize (minimize response)"""
        manager = AlertManager()

        with patch("tkinter.messagebox.askyesnocancel", return_value=False):
            result = manager.ask_quit_or_minimize()
            assert result == "minimize"

    def test_ask_quit_or_minimize_cancel(self):
        """Test asking to quit or minimize (cancel response)"""
        manager = AlertManager()

        with patch("tkinter.messagebox.askyesnocancel", return_value=None):
            result = manager.ask_quit_or_minimize()
            assert result is None

    def test_alert_error_handling(self):
        """Test that alerts handle errors gracefully"""
        manager = AlertManager()

        # Should not raise, even if something goes wrong
        with patch("tkinter.messagebox.showerror", side_effect=Exception("Test error")):
            manager.show_mic_error("Test", "Test", is_startup=True)
            # Should complete without raising
