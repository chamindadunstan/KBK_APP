# waveform.py

import numpy as np


def draw_test_waveform(controller):
    home = controller.get_frame("HomePage")

    if home is None:
        print("[Waveform] HomePage not ready yet.")
        return

    # Generate test signals for CH1 and CH2
    t = np.linspace(0, 1, 500)
    sig1 = np.sin(2 * np.pi * 5 * t)          # CH1: 5 Hz sine
    sig2 = 0.5 * np.sin(2 * np.pi * 12 * t)   # CH2: 12 Hz sine

    # Assign signals to channels
    if len(home.channels) >= 1:
        home.channels[0].set_signal(sig1)
    if len(home.channels) >= 2:
        home.channels[1].set_signal(sig2)

    # Update UI
    home.update_waveform()
    home.update_fft()
    home._auto_measure_first_enabled_channel()


def get_signals(n_channels, n_samples, fs, home=None):
    """
    Return a list of numpy arrays, one per channel.
    For now: synthetic signals. Later: replace with real hardware input.
    """
    # Safety: avoid Pylance warnings and runtime errors
    if home is None:
        return [np.zeros(n_samples) for _ in range(n_channels)]

    t = np.linspace(0, 1, n_samples, endpoint=False)
    signals = []

    for ch in home.channels:
        sig = home._generate_single_channel(
            ch.signal_type_var.get(),
            t,
            ch.freq_var.get(),
            ch.amp_var.get()
        )
        signals.append(sig)

    return signals
