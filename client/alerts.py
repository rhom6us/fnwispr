"""
Alert and notification dialogs for fnwispr
Handles user-facing error messages and confirmations
"""

import tkinter as tk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages user-facing alerts and notifications"""

    @staticmethod
    def show_mic_error(device_name: str, error_details: str, is_startup: bool = False):
        """
        Show microphone initialization error alert

        Args:
            device_name: Name of the microphone device
            error_details: Technical error message
            is_startup: Whether this is a startup error (vs config change)
        """
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the root window

            if is_startup:
                title = "Microphone Error"
                message = (
                    f"Cannot initialize microphone '{device_name}'.\n\n"
                    f"fnwispr will continue running but recording may not work.\n"
                    f"Please select a different device from the tray menu or Settings.\n\n"
                    f"Technical details: {error_details}"
                )
            else:
                title = "Microphone Configuration Error"
                message = (
                    f"Cannot initialize microphone '{device_name}'.\n\n"
                    f"Reverting to previous device.\n"
                    f"Please check your audio settings.\n\n"
                    f"Technical details: {error_details}"
                )

            messagebox.showerror(title, message)
            root.destroy()
            logger.error(f"Microphone error shown: {device_name} - {error_details}")
        except Exception as e:
            logger.error(f"Failed to show microphone error alert: {e}")

    @staticmethod
    def show_warning(title: str, message: str):
        """
        Show generic warning dialog

        Args:
            title: Dialog title
            message: Warning message
        """
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(title, message)
            root.destroy()
            logger.warning(f"Warning alert shown: {title}")
        except Exception as e:
            logger.error(f"Failed to show warning alert: {e}")

    @staticmethod
    def show_info(title: str, message: str):
        """
        Show generic info dialog

        Args:
            title: Dialog title
            message: Info message
        """
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(title, message)
            root.destroy()
            logger.info(f"Info alert shown: {title}")
        except Exception as e:
            logger.error(f"Failed to show info alert: {e}")

    @staticmethod
    def ask_quit_or_minimize(remember_callback=None):
        """
        Ask user whether to quit or minimize to tray

        Args:
            remember_callback: Callback function(choice) if user checks "Remember my choice"

        Returns:
            "quit" or "minimize"
        """
        try:
            root = tk.Tk()
            root.withdraw()

            result = messagebox.askyesnocancel(
                "Close fnwispr",
                "Do you want to quit fnwispr or minimize to system tray?\n\n"
                "Yes = Quit\n"
                "No = Minimize to tray",
            )

            root.destroy()

            if result is True:
                return "quit"
            elif result is False:
                return "minimize"
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to show quit/minimize dialog: {e}")
            return None
