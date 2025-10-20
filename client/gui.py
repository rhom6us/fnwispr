"""
Settings GUI window for fnwispr
Provides configuration interface for all settings
"""

import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
import logging
import threading
from typing import Callable, Dict, Optional
import sounddevice as sd

logger = logging.getLogger(__name__)


class SettingsWindow:
    """Settings window for fnwispr configuration"""

    def __init__(
        self,
        config: Dict,
        on_close: Optional[Callable] = None,
        on_config_change: Optional[Callable[[Dict], None]] = None,
        on_test_mic: Optional[Callable[[], bool]] = None,
        on_test_recording: Optional[Callable[[], Optional[str]]] = None,
    ):
        """
        Initialize settings window

        Args:
            config: Current configuration dictionary
            on_close: Callback when window closes
            on_config_change: Callback when config is changed
            on_test_mic: Callback to test microphone
            on_test_recording: Callback to test recording
        """
        self.config = config.copy()
        self.on_close = on_close
        self.on_config_change = on_config_change
        self.on_test_mic = on_test_mic
        self.on_test_recording = on_test_recording
        self.window = None
        self.tabs = None

    def create_window(self) -> tk.Tk:
        """Create and setup the settings window"""
        try:
            self.window = tk.Tk()
        except Exception as e:
            logger.error(f"Failed to create Tkinter window: {e}")
            logger.error("Tcl/Tk may not be installed. Reinstall Python with Tcl/Tk support.")
            raise

        self.window.title("fnwispr Settings")
        self.window.geometry("500x450")
        self.window.resizable(False, False)

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Create notebook (tabs)
        self.tabs = ttk.Notebook(self.window)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self._create_recording_tab()
        self._create_model_tab()
        self._create_general_tab()

        return self.window

    def _create_recording_tab(self):
        """Create Recording configuration tab"""
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text="Recording")

        # Hotkey configuration
        ttk.Label(frame, text="Hotkey:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        hotkey_frame = ttk.Frame(frame)
        hotkey_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        self.hotkey_var = tk.StringVar(value=self.config.get("hotkey", "ctrl+win"))
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, state="readonly", width=25)
        hotkey_entry.pack(side="left")

        ttk.Button(hotkey_frame, text="Record", command=self._record_hotkey, width=10).pack(side="left", padx=5)

        # Microphone device
        ttk.Label(frame, text="Microphone:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(frame, textvariable=self.device_var, state="readonly", width=30)
        self.device_combo.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        self.device_combo.bind("<<ComboboxSelected>>", self._on_device_change)
        self._populate_devices()

        # Test microphone button
        ttk.Button(frame, text="Test Microphone", command=self._test_mic).grid(row=2, column=0, columnspan=2, pady=10)

        # Language configuration
        ttk.Label(frame, text="Language:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.language_var = tk.StringVar(value=self.config.get("language") or "Auto-detect")
        language_combo = ttk.Combobox(
            frame,
            textvariable=self.language_var,
            values=["Auto-detect", "en", "es", "fr", "de", "it", "pt", "nl", "ru", "ja", "zh"],
            state="readonly",
            width=30,
        )
        language_combo.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        language_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        frame.columnconfigure(1, weight=1)

    def _create_model_tab(self):
        """Create Model configuration tab"""
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text="Model")

        # Model selection
        ttk.Label(frame, text="Whisper Model:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        model_frame = ttk.Frame(frame)
        model_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        self.model_var = tk.StringVar(value=self.config.get("model", "base"))

        for i, model in enumerate(["tiny", "base", "small", "medium", "large"]):
            rb = ttk.Radiobutton(model_frame, text=model, variable=self.model_var, value=model, command=self._on_model_change)
            rb.grid(row=i // 3, column=i % 3, sticky="w", padx=5, pady=5)

        # Model info
        info_frame = ttk.LabelFrame(frame, text="Model Information", padding=10)
        info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.model_info_text = tk.Text(info_frame, height=6, width=50, state="disabled")
        self.model_info_text.pack(fill="both", expand=True)

        self._update_model_info()

    def _create_general_tab(self):
        """Create General settings tab"""
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text="General")

        # Auto-start checkbox
        self.auto_start_var = tk.BooleanVar(value=self.config.get("auto_start", False))
        ttk.Checkbutton(frame, text="Start fnwispr at Windows login", variable=self.auto_start_var, command=self._on_auto_start_change).grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )

        # Close behavior
        ttk.Label(frame, text="When closing window:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)

        close_frame = ttk.Frame(frame)
        close_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.close_behavior_var = tk.StringVar(value=self.config.get("close_behavior", "ask"))

        for behavior, text in [("ask", "Ask each time"), ("minimize", "Minimize to tray"), ("quit", "Quit application")]:
            rb = ttk.Radiobutton(close_frame, text=text, variable=self.close_behavior_var, value=behavior, command=self._on_close_behavior_change)
            rb.pack(anchor="w", pady=5)

        # View logs button
        ttk.Button(frame, text="View Logs", command=self._view_logs).grid(row=3, column=0, pady=20)

    def _populate_devices(self):
        """Populate microphone device list"""
        devices = [("Default", None)]
        current_device = self.config.get("microphone_device")

        try:
            all_devices = sd.query_devices()
            for idx, device in enumerate(all_devices):
                if device.get("max_input_channels", 0) > 0:
                    name = device["name"][:37] + "..." if len(device["name"]) > 40 else device["name"]
                    devices.append((name, idx))
        except Exception as e:
            logger.error(f"Failed to query devices: {e}")

        device_names = [name for name, _ in devices]
        self.device_combo["values"] = device_names

        # Set current selection
        current_display = "Default" if current_device is None else next((name for name, idx in devices if idx == current_device), "Default")
        self.device_var.set(current_display)

        self._devices_map = {name: idx for name, idx in devices}

    def _record_hotkey(self):
        """Record new hotkey combination"""
        # Create a simple dialog to capture hotkey
        hotkey_window = tk.Toplevel(self.window)
        hotkey_window.title("Record Hotkey")
        hotkey_window.geometry("300x150")
        hotkey_window.resizable(False, False)

        ttk.Label(hotkey_window, text="Press the key combination you want to use...").pack(pady=20)

        self.recorded_keys = []
        hotkey_window.bind("<KeyPress>", lambda e: self._on_key_press(e, hotkey_window))
        hotkey_window.bind("<KeyRelease>", lambda e: self._on_key_release(e, hotkey_window))

    def _on_key_press(self, event, window):
        """Handle key press during hotkey recording"""
        key_name = event.keysym
        if key_name not in self.recorded_keys:
            self.recorded_keys.append(key_name)

    def _on_key_release(self, event, window):
        """Handle key release during hotkey recording"""
        if len(self.recorded_keys) > 0:
            # Convert key names to fnwispr format
            hotkey_str = "+".join(self.recorded_keys)
            self.hotkey_var.set(hotkey_str)
            self._config_changed("hotkey", hotkey_str)
            window.destroy()

    def _on_device_change(self, event=None):
        """Handle microphone device change"""
        device_name = self.device_var.get()
        device_idx = self._devices_map.get(device_name)
        self._config_changed("microphone_device", device_idx)

    def _on_language_change(self, event=None):
        """Handle language change"""
        language = self.language_var.get()
        language = None if language == "Auto-detect" else language
        self._config_changed("language", language)

    def _on_model_change(self):
        """Handle model change"""
        model = self.model_var.get()
        self._config_changed("model", model)
        self._update_model_info()

    def _update_model_info(self):
        """Update model information display"""
        model_info = {
            "tiny": "39M - 32x speed - ~1GB VRAM - Good for testing",
            "base": "74M - 16x speed - ~1GB VRAM - Default choice (recommended)",
            "small": "244M - 6x speed - ~2GB VRAM - Better accuracy",
            "medium": "769M - 2x speed - ~5GB VRAM - High accuracy",
            "large": "1550M - 1x speed - ~10GB VRAM - Best quality",
        }

        model = self.model_var.get()
        info = model_info.get(model, "Unknown model")

        self.model_info_text.config(state="normal")
        self.model_info_text.delete(1.0, tk.END)
        self.model_info_text.insert(1.0, f"Model: {model}\n\nSize: {info}\n\n" f"Change this from the tray menu for quick access.")
        self.model_info_text.config(state="disabled")

    def _on_auto_start_change(self):
        """Handle auto-start change"""
        self._config_changed("auto_start", self.auto_start_var.get())

    def _on_close_behavior_change(self):
        """Handle close behavior change"""
        self._config_changed("close_behavior", self.close_behavior_var.get())

    def _test_mic(self):
        """Test microphone"""
        if self.on_test_mic:
            threading.Thread(target=self.on_test_mic, daemon=True).start()

    def _view_logs(self):
        """Open log file in default application"""
        log_path = "fnwispr_client.log"
        if os.path.exists(log_path):
            os.startfile(log_path)
        else:
            tk.messagebox.showerror("Error", "Log file not found")

    def _config_changed(self, key: str, value):
        """Handle configuration change"""
        self.config[key] = value
        if self.on_config_change:
            threading.Thread(target=lambda: self.on_config_change(self.config.copy()), daemon=True).start()

    def _on_window_close(self):
        """Handle window close"""
        if self.on_close:
            self.on_close()
        else:
            self.window.destroy()

    def show(self):
        """Show the settings window"""
        if not self.window:
            self.create_window()
        self.window.deiconify()
        self.window.focus()

    def hide(self):
        """Hide the settings window"""
        if self.window:
            self.window.withdraw()

    def destroy(self):
        """Destroy the settings window"""
        if self.window:
            self.window.destroy()
            self.window = None
