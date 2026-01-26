"""
scope_channel.py

Defines the ScopeChannel class used by the oscilloscope UI.
Each channel stores its own name, color, enable state, and signal data.
This file contains no UI code and no plotting code.
"""
from tkinter import StringVar, DoubleVar


class ScopeChannel:
    """
    Represents a single oscilloscope channel.
    Stores channel metadata and the most recent signal buffer.
    """

    def __init__(self, name: str, color: str, enabled: bool = True):
        self.name = name          # "CH1", "CH2", ...
        self.color = color        # waveform color
        self.enabled = enabled    # checkbox state

        # Signal data
        self.signal = None        # numpy array of samples

        # Future expansion (safe placeholders)
        # Vertical settings
        self.scale = 1.0          # volts per division
        self.offset = 0.0         # vertical offset
        self.probe_factor = 1     # x1, x10, x100
        self.coupling = "DC"      # "DC", "AC", "GND"

        self.signal_type_var: StringVar | None = None
        self.freq_var: DoubleVar | None = None
        self.amp_var: DoubleVar | None = None

    def set_signal(self, sig):
        """Assign a new numpy array to this channel."""
        self.signal = sig
