# waveform.py

import tkinter as tk
from views.themed_frame import ThemedFrame

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnchoredText

from .scope_channel import ScopeChannel
import waveform


def draw_test_waveform(controller):
    home = controller.get_frame("HomePage")

    if home is None:
        print("[Waveform] HomePage not ready yet.")
        return

    # Generate test signals for CH1 and CH2
    t = np.linspace(0, 1, 500)
    sig1 = np.sin(2 * np.pi * 5 * t)          # CH1: 5 Hz sine
    sig2 = 0.5 * np.sin(2 * np.pi * 12 * t)   # CH2: 12 Hz sine

    # Update dual‑channel waveform
    home.update_waveform_dual(sig1, sig2)

    # Update dual‑channel FFT
    home.update_fft_dual(sig1, sig2)

    # Update measurements (CH1 only)
    
def get_signals(n_channels: int, n_samples: int, fs: float):
    """
    Return a list of numpy arrays, one per channel.
    For now: synthetic signals. Later: replace with real hardware input.
    """
    t = np.linspace(0, 1, n_samples, endpoint=False)

    signals = []

    for ch in range(n_channels):
        # Example: different frequency per channel
        freq = 5 * (ch + 1)
        sig = np.sin(2 * np.pi * freq * t)
        signals.append(sig)

    return signals

