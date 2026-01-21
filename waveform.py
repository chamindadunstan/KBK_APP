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

    # Update dual‑channel waveform
    home.update_waveform_dual(sig1, sig2)

    # Update dual‑channel FFT
    home.update_fft_dual(sig1, sig2)

    # Update measurements (CH1 only)
    home.compute_measurements(sig1)
