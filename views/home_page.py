# views/home_page.py

import tkinter as tk
from views.themed_frame import ThemedFrame

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnchoredText

from .scope_channel import ScopeChannel
import waveform


class HomePage(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.controller = controller

        # ---------- GRID LAYOUT ----------
        # Rows:
        # 0: Title
        # 1: Signal generator panel
        # 2: Waveform plot
        # 3: FFT plot
        # 4: Navigation buttons
        # 5: Measurement display
        for r in range(6):
            self.rowconfigure(r, weight=0)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=3)

        # Columns 0–7
        for c in range(8):
            self.columnconfigure(c, weight=1)

        # ---------- TITLE ----------
        self.label = tk.Label(
            self,
            text=self.controller.t("home"),
            font=("Arial", 20)
        )
        self.label.grid(column=3, row=0, sticky=tk.NE, padx=5, pady=5)

        # ---------- NAVIGATION BUTTONS ----------
        self.btn_settings = tk.Button(
            self,
            text=self.controller.t("go_settings"),
            command=lambda: controller.show_frame("SettingsPage")
        )
        self.btn_settings.grid(column=0, row=4, sticky=tk.EW, padx=5, pady=5)

        self.btn_initial = tk.Button(
            self,
            text=self.controller.t("go_initial"),
            command=lambda: controller.show_frame("InitialPage")
        )
        self.btn_initial.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)

        # ---------- SIGNAL PARAMETERS ----------
        self.sampling_rate = tk.DoubleVar(value=500.0)  # Hz
        self.freq = tk.DoubleVar(value=5.0)             # Hz
        self.amp = tk.DoubleVar(value=1.0)              # amplitude
        self.n_samples = 500

        # ---------- CHANNELS ----------
        self.channels = []
        self.channel_vars = []  # BooleanVar per channel

        # For now: 2 channels, but scalable to 8
        color_list = [
            "yellow", "cyan", "magenta",
            "green", "red", "blue", "orange", "white"
            ]
        n_init_channels = 2

        for i in range(n_init_channels):
            ch = ScopeChannel(
                name=f"CH{i+1}", color=color_list[i], enabled=True)
            self.channels.append(ch)

        # ---------- CURSOR STATE ----------
        # Cursor A and B positions (sample indices)
        self.cursor_a = None
        self.cursor_b = None

        # Matplotlib line objects for cursor visuals
        self.cursor_lines = []

        # ---------- MEASUREMENT OVERLAY ----------
        # Floating Tektronix-style measurement box inside the waveform plot
        self.measure_overlay = None

        # ---------- REAL-TIME OSCILLOSCOPE STATE ----------
        # Flag used to start/stop the real-time update loop
        self.realtime_running = False

        # ---------- UI LAYOUT ----------
        self._build_channel_controls()
        self._build_waveform_area()
        self._build_measure_label()

        # Start real-time mode automatically (optional)
        self.start_realtime()

        # ---------- WAVEFORM PLOT AREA ----------
        self.wave_frame = tk.Frame(self)
        self.wave_frame.grid(
            row=2, column=0, columnspan=8,
            sticky="nsew", padx=10, pady=10
        )

        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.ax.plot([], [])
        self.ax.set_title("Signal Waveform")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Amplitude")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.wave_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # Enable cursor click detection on waveform
        self.canvas.mpl_connect("button_press_event", self._on_waveform_click)

        # ---------- FFT PLOT AREA ----------
        self.fft_frame = tk.Frame(self)
        self.fft_frame.grid(
            row=3, column=0, columnspan=8,
            sticky="nsew", padx=10, pady=10
        )

        self.fig_fft = Figure(figsize=(6, 3), dpi=100)
        self.ax_fft = self.fig_fft.add_subplot(111)

        self.ax_fft.plot([], [])
        self.ax_fft.set_title("FFT Spectrum")
        self.ax_fft.set_xlabel("Frequency (Hz)")
        self.ax_fft.set_ylabel("Magnitude")

        self.canvas_fft = FigureCanvasTkAgg(
            self.fig_fft, master=self.fft_frame)
        self.canvas_fft.get_tk_widget().pack(fill="both", expand=True)

        # ---------- MEASUREMENT DISPLAY ----------
        self.measure_label = tk.Label(
            self,
            text="Peak: --   RMS: --   Freq: --"
        )
        self.measure_label.grid(
            row=5, column=0, columnspan=8,
            pady=5
        )

        # ---------- SIGNAL GENERATOR PANEL ----------
        gen_frame = tk.Frame(self)
        gen_frame.grid(
            row=1, column=0, columnspan=8,
            sticky="ew", padx=10, pady=5
        )

        # CH1 type
        tk.Label(gen_frame, text="CH1:").pack(side="left", padx=5)
        self.signal_type = tk.StringVar(value="sine")
        tk.OptionMenu(
            gen_frame, self.signal_type, "sine", "square", "noise"
        ).pack(side="left")

        # CH2 type
        tk.Label(gen_frame, text="CH2:").pack(side="left", padx=5)
        self.signal_type_ch2 = tk.StringVar(value="sine")
        tk.OptionMenu(
            gen_frame, self.signal_type_ch2, "sine", "square", "noise"
        ).pack(side="left")

        # Sampling rate slider
        tk.Label(gen_frame, text="Rate (Hz):").pack(side="left", padx=5)
        tk.Scale(
            gen_frame,
            from_=100,
            to=5000,
            resolution=100,
            orient="horizontal",
            variable=self.sampling_rate,
            length=120
        ).pack(side="left")

        # Frequency slider
        tk.Label(gen_frame, text="Freq (Hz):").pack(side="left", padx=5)
        tk.Scale(
            gen_frame,
            from_=1,
            to=50,
            orient="horizontal",
            variable=self.freq,
            length=120
        ).pack(side="left")

        # Amplitude slider
        tk.Label(gen_frame, text="Amp:").pack(side="left", padx=5)
        tk.Scale(
            gen_frame,
            from_=0.1,
            to=5.0,
            resolution=0.1,
            orient="horizontal",
            variable=self.amp,
            length=120
        ).pack(side="left")

        # --- Real-time oscilloscope controls ---
        # Start real-time mode (30–60 FPS)
        tk.Button(
            gen_frame,
            text="Start RT",
            command=self.start_realtime
        ).pack(side="left", padx=5)

        # Stop real-time mode
        tk.Button(
            gen_frame,
            text="Stop RT",
            command=self.stop_realtime
        ).pack(side="left", padx=5)

        # Generate button
        tk.Button(
            gen_frame,
            text="Generate",
            command=self.generate_signal
        ).pack(side="left", padx=10)

    # ---------- CHANNEL SELECTION CONTROLS ----------
    def _build_channel_controls(self):
        """Create channel enable/disable checkboxes."""
        ctrl_frame = tk.Frame(self)
        ctrl_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        for ch in self.channels:
            var = tk.BooleanVar(value=True)
            self.channel_vars.append(var)
            cb = tk.Checkbutton(
                ctrl_frame,
                text=ch.name,
                variable=var,
                onvalue=True,
                offvalue=False
            )
            cb.pack(side="left", padx=5)

    # ---------- SIGNAL GENERATION & PLOTTING ----------
    def _generate_single_channel(self, sig_type, t):
        freq = self.freq.get()
        amp = self.amp.get()

        if sig_type == "sine":
            return amp * np.sin(2 * np.pi * freq * t)
        if sig_type == "square":
            return amp * np.sign(np.sin(2 * np.pi * freq * t))
        if sig_type == "noise":
            return amp * np.random.normal(0, 1, len(t))

        return np.zeros_like(t)

    def generate_signal(self):
        # Time base: 1 second, N samples
        n_samples = 500
        t = np.linspace(0, 1, n_samples, endpoint=False)

        # CH1 and CH2
        sig1 = self._generate_single_channel(self.signal_type.get(), t)
        sig2 = self._generate_single_channel(self.signal_type_ch2.get(), t)

        # Update waveform and FFT
        self.update_waveform_dual(sig1, sig2)
        self.update_fft_dual(sig1, sig2)

        # Measurements on CH1
        self.compute_measurements(sig1)

    def update_waveform_dual(self, sig1, sig2):
        self.ax.clear()
        self.ax.plot(sig1, color="blue", label="CH1")
        self.ax.plot(sig2, color="green", label="CH2")
        self.ax.set_title("Signal Waveform")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Amplitude")
        self.ax.legend()
        self.canvas.draw()

    def update_fft_dual(self, sig1, sig2):
        fs = self.sampling_rate.get()
        n = len(sig1)

        freqs = np.fft.fftfreq(n, d=1 / fs)
        idx = freqs >= 0

        fft1 = np.abs(np.fft.fft(sig1))
        fft2 = np.abs(np.fft.fft(sig2))

        self.ax_fft.clear()
        self.ax_fft.plot(freqs[idx], fft1[idx], color="red", label="CH1")
        self.ax_fft.plot(freqs[idx], fft2[idx], color="orange", label="CH2")
        self.ax_fft.set_title("FFT Spectrum")
        self.ax_fft.set_xlabel("Frequency (Hz)")
        self.ax_fft.set_ylabel("Magnitude")
        self.ax_fft.legend()
        self.canvas_fft.draw()

    def compute_measurements(self, signal):
        peak = np.max(np.abs(signal))
        rms = np.sqrt(np.mean(signal ** 2))

        fs = self.sampling_rate.get()
        n = len(signal)
        freqs = np.fft.fftfreq(n, d=1 / fs)
        fft_vals = np.abs(np.fft.fft(signal))
        idx = freqs >= 0

        if np.any(idx):
            peak_freq = freqs[idx][np.argmax(fft_vals[idx])]
        else:
            peak_freq = 0.0

        self.measure_label.config(
            text=(
                f"Peak: {peak:.3f}   "
                f"RMS: {rms:.3f}   "
                f"Freq: {peak_freq:.2f} Hz"
            )
        )

        # ---------- CURSOR INTERACTION ----------

    # ---------- CURSOR INTERACTION ----------
    def _draw_cursors(self):
        """Draw vertical cursor lines on the waveform."""
        self._clear_cursor_lines()

        if self.cursor_a is not None:
            line_a = self.ax.axvline(
                self.cursor_a, color="yellow", linestyle="--"
            )
            self.cursor_lines.append(line_a)

        if self.cursor_b is not None:
            line_b = self.ax.axvline(
                self.cursor_b, color="cyan", linestyle="--"
            )
            self.cursor_lines.append(line_b)

        self.canvas.draw()

    def _clear_cursor_lines(self):
        """Remove all cursor lines from the plot."""
        for line in self.cursor_lines:
            line.remove()
        self.cursor_lines.clear()

    # ---------- MEASUREMENT OVERLAY BOX ----------
    def _update_measure_overlay(self, text):
        """Create or update the measurement overlay box."""
        # Remove old overlay
        if self.measure_overlay is not None:
            self.measure_overlay.remove()

        # Create new overlay
        self.measure_overlay = AnchoredText(
            text,
            loc="upper right",
            prop={"size": 10, "color": "white"},
            frameon=True,
            pad=0.4,
            borderpad=0.5
        )

        # Style the box like Tektronix
        self.measure_overlay.patch.set_facecolor("black")
        self.measure_overlay.patch.set_alpha(0.6)
        self.measure_overlay.patch.set_edgecolor("white")

        self.ax.add_artist(self.measure_overlay)
        self.canvas.draw()

    def _compute_cursor_measurements(self):
        """Compute peak, RMS, and frequency based on cursor positions."""
        if self.cursor_a is None:
            return

        # Use CH1 for measurement
        n_samples = 500
        t = np.linspace(0, 1, n_samples, endpoint=False)
        sig = self._generate_single_channel(self.signal_type.get(), t)

        # If only one cursor: show value at that point
        if self.cursor_b is None:
            y = sig[self.cursor_a]

            overlay_text = (
                f"Cursor A: {self.cursor_a}\n"
                f"Value: {y:.3f}"
            )

            self._update_measure_overlay(overlay_text)
            return

        # Two cursors: measure region
        a, b = sorted([self.cursor_a, self.cursor_b])
        region = sig[a:b]

        if len(region) < 2:
            return

        peak = np.max(np.abs(region))
        rms = np.sqrt(np.mean(region**2))

        # Frequency from time difference
        fs = self.sampling_rate.get()
        dt = (b - a) / fs
        freq = 1 / dt if dt > 0 else 0

        # ---------- OVERLAY TEXT  ----------
        overlay_text = (
            f"Cursor A: {a}\n"
            f"Cursor B: {b}\n"
            f"ΔX: {b - a} samples ({dt:.4f} s)\n"
            f"Peak: {peak:.3f}\n"
            f"RMS: {rms:.3f}\n"
            f"Freq: {freq:.2f} Hz"
        )

        self._update_measure_overlay(overlay_text)

    # ---------- REAL-TIME LOOP ----------

    def start_realtime(self):
        """Start the real-time oscilloscope loop."""
        if not self.realtime_running:
            self.realtime_running = True
            self._realtime_loop()

    def stop_realtime(self):
        """Stop the real-time oscilloscope loop."""
        self.realtime_running = False

    def _realtime_loop(self):
        """Internal loop that updates the oscilloscope at ~60 FPS."""
        if not self.realtime_running:
            return

        # Time base
        n_samples = 500
        t = np.linspace(0, 1, n_samples, endpoint=False)

        # Generate CH1 and CH2
        sig1 = self._generate_single_channel(self.signal_type.get(), t)
        sig2 = self._generate_single_channel(self.signal_type_ch2.get(), t)

        # Update UI
        self.update_waveform_dual(sig1, sig2)
        self.update_fft_dual(sig1, sig2)
        self.compute_measurements(sig1)

        # Schedule next frame (16 ms = ~60 FPS)
        self.after(16, self._realtime_loop)

        # ---------- CURSOR INTERACTION ----------

    def _on_waveform_click(self, event):
        """Handle mouse clicks on the waveform to place cursors."""
        # Ignore clicks outside the waveform axes
        if event.inaxes != self.ax:
            return

        x = int(event.xdata)

        # First click sets Cursor A
        if self.cursor_a is None:
            self.cursor_a = x

        # Second click sets Cursor B
        elif self.cursor_b is None:
            self.cursor_b = x

        # Third click → Reset everything
        else:
            self.cursor_a = None
            self.cursor_b = None
            self._clear_cursor_lines()

            # Remove overlay box
            if self.measure_overlay is not None:
                self.measure_overlay.remove()
                self.measure_overlay = None

            # Reset bottom label
            self.measure_label.config(text="Peak: --   RMS: --   Freq: --")

            # Redraw canvas
            self.canvas.draw()
            return
        self._draw_cursors()
        self._compute_cursor_measurements()

    # ---------- TEXT REFRESH (I18N) ----------
    def refresh_text(self):
        self.label.config(text=self.controller.t("home"))
        self.btn_settings.config(text=self.controller.t("go_settings"))
        self.btn_initial.config(text=self.controller.t("go_initial"))
