"""
System tray management for fnwispr
Handles tray icon, context menu, and quick settings
"""

import pystray
from PIL import Image, ImageDraw
import logging
import threading
from typing import Callable, Dict, List, Optional
import sounddevice as sd

logger = logging.getLogger(__name__)


class TrayManager:
    """Manages system tray icon and context menu"""

    def __init__(
        self,
        icon_path: Optional[str] = None,
        on_settings: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
        on_model_change: Optional[Callable[[str], None]] = None,
        on_device_change: Optional[Callable[[Optional[int]], None]] = None,
        get_current_model: Optional[Callable[[], str]] = None,
        get_current_device: Optional[Callable[[], Optional[int]]] = None,
    ):
        """
        Initialize tray manager

        Args:
            icon_path: Path to icon file (SVG, PNG, ICO)
            on_settings: Callback when Settings is clicked
            on_exit: Callback when Exit is clicked
            on_model_change: Callback when model is changed
            on_device_change: Callback when microphone device is changed
            get_current_model: Callback to get current model name
            get_current_device: Callback to get current device index
        """
        self.icon_path = icon_path
        self.on_settings = on_settings
        self.on_exit = on_exit
        self.on_model_change = on_model_change
        self.on_device_change = on_device_change
        self.get_current_model = get_current_model or (lambda: "base")
        self.get_current_device = get_current_device or (lambda: None)
        self.icon = None
        self.status = "ready"
        self.status_message = "Ready"

    def _load_icon(self) -> Image.Image:
        """Load and convert icon from SVG or create fallback"""
        if self.icon_path:
            try:
                if self.icon_path.endswith(".svg"):
                    # Convert SVG to PNG
                    import cairosvg
                    import io

                    png_data = io.BytesIO()
                    cairosvg.svg2png(url=self.icon_path, write_to=png_data, output_width=256, output_height=256)
                    png_data.seek(0)
                    return Image.open(png_data).convert("RGBA")
                else:
                    return Image.open(self.icon_path).convert("RGBA")
            except Exception as e:
                logger.warning(f"Failed to load icon from {self.icon_path}: {e}, using fallback")

        # Fallback: Generate simple icon
        return self._generate_fallback_icon()

    @staticmethod
    def _generate_fallback_icon() -> Image.Image:
        """Generate a simple fallback icon"""
        img = Image.new("RGBA", (256, 256), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Blue circle background
        draw.ellipse([10, 10, 246, 246], fill=(59, 130, 246, 255), outline=(30, 64, 175, 255))

        # White "F" text
        try:
            from PIL import ImageFont

            font = ImageFont.load_default()
            draw.text((110, 100), "F", fill=(255, 255, 255, 255), font=font)
        except Exception:
            # If font loading fails, just use the circle
            pass

        return img

    def _get_input_devices(self) -> List[Dict[str, any]]:
        """Get list of available input devices"""
        try:
            devices = sd.query_devices()
            input_devices = []

            for idx, device in enumerate(devices):
                if device.get("max_input_channels", 0) > 0:
                    name = device["name"]
                    # Truncate long names
                    display_name = name[:37] + "..." if len(name) > 40 else name
                    input_devices.append({"index": idx, "name": display_name, "full_name": name})

            return input_devices
        except Exception as e:
            logger.error(f"Failed to query audio devices: {e}")
            return []

    def _build_menu(self) -> pystray.Menu:
        """Build the context menu"""
        menu_items = []

        # Settings
        menu_items.append(pystray.MenuItem("Settings...", lambda icon, item: self._on_settings_click()))

        menu_items.append(pystray.Menu.SEPARATOR)

        # Model submenu
        models = ["tiny", "base", "small", "medium", "large"]
        current_model = self.get_current_model()
        model_items = [
            pystray.MenuItem(
                model,
                lambda icon, item, m=model: self._on_model_select(m),
                checked=lambda item, m=model: current_model == m,
            )
            for model in models
        ]
        menu_items.append(pystray.MenuItem("Model", pystray.Menu(*model_items)))

        # Microphone submenu
        input_devices = self._get_input_devices()
        current_device = self.get_current_device()

        # Add "Default" option
        device_items = [
            pystray.MenuItem(
                "Default",
                lambda icon, item: self._on_device_select(None),
                checked=lambda item: current_device is None,
            )
        ]

        # Add actual devices
        for device in input_devices:
            device_items.append(
                pystray.MenuItem(
                    device["name"],
                    lambda icon, item, idx=device["index"]: self._on_device_select(idx),
                    checked=lambda item, idx=device["index"]: current_device == idx,
                )
            )

        menu_items.append(pystray.MenuItem("Microphone", pystray.Menu(*device_items)))

        menu_items.append(pystray.Menu.SEPARATOR)

        # Exit
        menu_items.append(pystray.MenuItem("Exit", lambda icon, item: self._on_exit_click()))

        return pystray.Menu(*menu_items)

    def _on_settings_click(self):
        """Handle Settings menu click"""
        if self.on_settings:
            threading.Thread(target=self.on_settings, daemon=True).start()

    def _on_model_select(self, model: str):
        """Handle model selection"""
        logger.info(f"Model selected from tray: {model}")
        if self.on_model_change:
            threading.Thread(target=lambda: self.on_model_change(model), daemon=True).start()

    def _on_device_select(self, device_index: Optional[int]):
        """Handle microphone device selection"""
        logger.info(f"Microphone device selected from tray: {device_index}")
        if self.on_device_change:
            threading.Thread(target=lambda: self.on_device_change(device_index), daemon=True).start()

    def _on_exit_click(self):
        """Handle Exit menu click"""
        logger.info("Exit selected from tray")
        if self.on_exit:
            threading.Thread(target=self.on_exit, daemon=True).start()

    def set_status(self, status: str, message: str = ""):
        """
        Update tray icon status and tooltip

        Args:
            status: Status type (ready, recording, error)
            message: Additional status message
        """
        self.status = status
        self.status_message = message
        if self.icon:
            self.icon.title = message or status

    def run(self):
        """Start the tray icon (blocking)"""
        try:
            icon_image = self._load_icon()
            self.icon = pystray.Icon(
                "fnwispr",
                icon_image,
                title="fnwispr - Ready",
                menu=self._build_menu(),
            )
            self.icon.run()
        except Exception as e:
            logger.error(f"Failed to run tray icon: {e}")

    def quit(self):
        """Stop the tray icon"""
        if self.icon:
            self.icon.stop()
