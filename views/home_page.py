# views/home_page.py

import tkinter as tk
from tkinter import ttk
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

        # Row 0–5
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

        # ---------- CHANNEL MODEL LIST ----------
        self.channels: list[ScopeChannel] = []
        """ # enable/disable per channel """
        self.channel_vars: list[tk.BooleanVar] = []

        # For now: 2 channels, but scalable to 8
        color_list = [
            "yellow", "cyan", "magenta",
            "green", "red", "blue", "orange", "white"
            ]
        n_init_channels = 2

        for i in range(n_init_channels):
            ch = ScopeChannel(
                name=f"CH{i+1}",
                color=color_list[i],
                enabled=True
            )
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

        # ---------- BUILD UI ----------
        self._build_channel_controls()
        self._build_signal_generator_panel()
        self._build_waveform_area()
        self._build_fft_area()
        self._build_measure_label()

        self._build_status_bar()  # Create Status bar
        self.start_realtime()  # Start real-time mode automatically (optional)

    # ---------- UI BUILDERS ----------
    def _build_channel_controls(self):
        """Create per-channel enable checkboxes and settings buttons."""
        ctrl_frame = tk.Frame(self)
        ctrl_frame.grid(
            row=1, column=0, columnspan=1, sticky="w", padx=10, pady=5)

        for idx, ch in enumerate(self.channels):
            row_frame = tk.Frame(ctrl_frame)
            row_frame.pack(side="left", padx=10)

            var = tk.BooleanVar(value=ch.enabled)
            self.channel_vars.append(var)

            cb = tk.Checkbutton(
                row_frame,
                text=ch.name,
                variable=var,
                onvalue=True,
                offvalue=False,
                command=lambda i=idx: self._on_channel_toggle(i)
            )
            cb.pack(side="top", anchor="w")

            btn = tk.Button(
                row_frame,
                text="Settings",
                command=lambda i=idx: self._open_channel_menu(i)
            )
            btn.pack(side="top", pady=2)

    def _on_channel_toggle(self, index):
        enabled = self.channel_vars[index].get()

        if index == 0:  # CH1
            if enabled:
                self.sb_ch1.config(text="CH1: ON", bg="#303030")
            else:
                self.sb_ch1.config(text="CH1: OFF", bg="#404040")

        if index == 1:  # CH2
            if enabled:
                self.sb_ch2.config(text="CH2: ON", bg="#303030")
            else:
                self.sb_ch2.config(text="CH2: OFF", bg="#404040")

        self.update_waveform()

    def _build_signal_generator_panel(self):
        """Create signal generator controls (per-channel tabs)."""
        gen_frame = tk.Frame(self)
        gen_frame.grid(
            row=1, column=7, rowspan=3,
            sticky="ns", padx=10, pady=5
        )

        # -----------------------------------------
        # notebook container
        nb_container = tk.Frame(gen_frame)
        nb_container.pack(fill="both", expand=False)

        # Notebook for CH1, CH2, ... CHn
        channelbook = ttk.Notebook(nb_container)
        channelbook.pack(fill="both", expand=True)
        # -----------------------------------------

        # Create one tab per channel
        self.channel_panels = []

        for ch in self.channels:
            tab = ttk.Frame(channelbook)
            channelbook.add(tab, text=ch.name)
            self.channel_panels.append(tab)

            # grid layout with 3 columns
            for col in range(3):
                tab.columnconfigure(col, weight=1)

            # --- Signal Type ---
            tk.Label(tab, text="Type:").grid(
                row=0, column=0, sticky="w", padx=5, pady=2)
            ch.signal_type_var = tk.StringVar(value="sine")
            tk.OptionMenu(
                tab, ch.signal_type_var, "sine", "square", "noise"
            ).grid(row=0, column=1)

            # --- Frequency slider ---
            tk.Label(tab, text="Freq (Hz):").grid(
                row=1, column=0, sticky="w", padx=5, pady=2)
            ch.freq_var = tk.DoubleVar(value=5.0)
            tk.Scale(
                tab, from_=1, to=50,
                orient="horizontal", variable=ch.freq_var, length=120
                ).grid(row=1, column=1)

            # --- Amplitude slider ---
            tk.Label(tab, text="Amp:").grid(
                row=2, column=0, sticky="w", padx=5, pady=2)
            ch.amp_var = tk.DoubleVar(value=1.0)
            tk.Scale(
                tab, from_=0.1, to=5.0, resolution=0.1,
                orient="horizontal",
                variable=ch.amp_var, length=120
                    ).grid(row=2, column=1)

        # --- Global controls  ---
        ctrl_frame = tk.Frame(gen_frame)
        ctrl_frame.pack(fill="x", pady=5)

        # Left side: sampling rate slider
        rate_frame = tk.Frame(ctrl_frame)
        rate_frame.pack(side="left", padx=5)

        tk.Label(rate_frame, text="Rate (Hz):").pack(side="left", padx=5)
        tk.Scale(rate_frame,
                 from_=100, to=5000, resolution=100,
                 orient="horizontal",
                 variable=self.sampling_rate, length=120
                 ).pack()

        # Right side: control buttons
        btn_frame = tk.Frame(ctrl_frame)
        btn_frame.pack(side="right", padx=10)

        # RT status LED
        self.rt_status = tk.Label(
            btn_frame,
            text="RT OFF",
            bg="#444444",
            fg="white",
            font=("Arial", 10, "bold"),
            width=8,
            height=1,
            relief="ridge",
            bd=2
        )
        self.rt_status.pack(side="right", padx=10)
        self.rt_status.config(text="RT OFF", bg="#444444")

        tk.Button(btn_frame, text="Start RT", command=self.start_realtime
                  ).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Stop RT", command=self.stop_realtime
                  ).pack(side="right", padx=5)
        tk.Button(btn_frame, text="Generate", command=self._generate_manual
                  ).pack(side="right", padx=10)

    def _build_waveform_area(self):
        """Create waveform plot area."""
        self.wave_frame = tk.Frame(self)
        self.wave_frame.grid(
            row=2, column=0, columnspan=7,
            sticky="nsew", padx=10, pady=10)

        self.fig = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.ax.set_title("Signal Waveform")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Amplitude")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.wave_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # Click for cursors
        self.canvas.mpl_connect("button_press_event", self._on_waveform_click)

    def _build_fft_area(self):
        """Create FFT plot area."""
        self.fft_frame = tk.Frame(self)
        self.fft_frame.grid(
            row=3, column=0, columnspan=7,
            sticky="nsew", padx=10, pady=10
        )

        self.fig_fft = Figure(figsize=(6, 3), dpi=100)
        self.ax_fft = self.fig_fft.add_subplot(111)

        self.ax_fft.set_title("FFT Spectrum")
        self.ax_fft.set_xlabel("Frequency (Hz)")
        self.ax_fft.set_ylabel("Magnitude")

        self.canvas_fft = FigureCanvasTkAgg(
            self.fig_fft, master=self.fft_frame)
        self.canvas_fft.get_tk_widget().pack(fill="both", expand=True)

    def _build_measure_label(self):
        """Create bottom measurement label."""
        self.measure_label = tk.Label(
            self,
            text="Peak: --   RMS: --   Freq: --"
        )
        self.measure_label.grid(
            row=5, column=0, columnspan=8,
            pady=5
        )

    def _build_status_bar(self):
        self.status_frame = tk.Frame(self, bg="#202020")
        self.status_frame.grid(row=4, column=0, columnspan=8, sticky="ew")

        # Make it stretch
        self.status_frame.columnconfigure(0, weight=1)
        self.status_frame.columnconfigure(1, weight=1)
        self.status_frame.columnconfigure(2, weight=1)
        self.status_frame.columnconfigure(3, weight=1)
        self.status_frame.columnconfigure(4, weight=1)
        self.status_frame.columnconfigure(5, weight=1)

        def make_block(parent, text, col):
            lbl = tk.Label(
                parent,
                text=text,
                bg="#303030",
                fg="white",
                font=("Arial", 9, "bold"),
                width=10,
                height=1,
                relief="ridge",
                bd=2,
                anchor="w",
                padx=4
            )
            lbl.grid(row=0, column=col, padx=2, pady=2, sticky="ew")
            return lbl

        # Segments
        self.sb_rt = make_block(self.status_frame, "RT: OFF", 0)
        self.sb_trig = make_block(self.status_frame, "TRIG: AUTO", 1)
        self.sb_acq = make_block(self.status_frame, "ACQ: SAMPLE", 2)
        self.sb_ch1 = make_block(self.status_frame, "CH1: ON", 3)
        self.sb_ch2 = make_block(self.status_frame, "CH2: ON", 4)
        self.sb_meas = make_block(self.status_frame, "MEAS: OFF", 5)

    # ---------- PER-CHANNEL SETTINGS UI ----------
    def _open_channel_menu(self, index: int):
        """Open a small per-channel settings dialog
        (scale, offset, probe, coupling)."""
        ch = self.channels[index]

        win = tk.Toplevel(self)
        win.title(f"{ch.name} Settings")
        win.grab_set()

        tk.Label(
            win, text=f"Settings for {ch.name}", font=("Arial", 12, "bold")
            ).grid(
            row=0, column=0, columnspan=2, pady=5
        )

        # Scale
        tk.Label(win, text="Scale (V/div):"
                 ).grid(row=1, column=0, sticky="e", padx=5, pady=2)
        scale_var = tk.DoubleVar(value=ch.scale)
        tk.Entry(win, textvariable=scale_var, width=10
                 ).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Offset
        tk.Label(win, text="Offset (V):"
                 ).grid(row=2, column=0, sticky="e", padx=5, pady=2)
        offset_var = tk.DoubleVar(value=ch.offset)
        tk.Entry(win, textvariable=offset_var, width=10
                 ).grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Probe factor
        tk.Label(win, text="Probe:"
                 ).grid(row=3, column=0, sticky="e", padx=5, pady=2)

        probe_var = tk.StringVar(value=str(ch.probe_factor))

        tk.OptionMenu(
            win,
            probe_var,
            "1", "10", "100"
        ).grid(row=3, column=1, sticky="w", padx=5, pady=2)

        # Coupling
        tk.Label(win, text="Coupling:"
                 ).grid(row=4, column=0, sticky="e", padx=5, pady=2)
        coupling_var = tk.StringVar(value=ch.coupling)
        tk.OptionMenu(win, coupling_var, "DC", "AC", "GND"
                      ).grid(row=4, column=1, sticky="w", padx=5, pady=2)

        def apply_and_close():
            ch.scale = scale_var.get()
            ch.offset = offset_var.get()
            ch.probe_factor = int(probe_var.get())   # ← FIXED
            ch.coupling = coupling_var.get()
            self.update_waveform()
            win.destroy()

        tk.Button(win, text="Apply", command=apply_and_close).grid(
            row=5, column=0, columnspan=2, pady=10
        )

    # ---------- SIGNAL GENERATION & PLOTTING ----------
    def _generate_single_channel(self, sig_type, t, freq, amp):
        """Legacy single-channel generator (used by Generate button)."""

        if sig_type == "sine":
            return amp * np.sin(2 * np.pi * freq * t)
        if sig_type == "square":
            return amp * np.sign(np.sin(2 * np.pi * freq * t))
        if sig_type == "noise":
            return amp * np.random.normal(0, 1, len(t))

        return np.zeros_like(t)

    def generate_signal(self):
        """Manual single-shot generation for CH1/CH2 (not real-time)."""
        # Time base: 1 second, N samples
        n_samples = self.n_samples
        t = np.linspace(0, 1, n_samples, endpoint=False)

        for ch in self.channels:
            if (
                ch.signal_type_var is None or
                ch.freq_var is None or
                ch.amp_var is None
            ):
                continue  # or raise an error

            sig = self._generate_single_channel(
                ch.signal_type_var.get(),
                t,
                ch.freq_var.get(),
                ch.amp_var.get()
            )
            ch.set_signal(sig)

        self.update_waveform()
        self.update_fft()
        self._auto_measure_first_enabled_channel()

    def _generate_manual(self):
        self.stop_realtime()      # Stop RT so it doesn't overwrite your signal
        self.generate_signal()    # Now generate CH1/CH2 signals

    def update_waveform(self):
        """Plot all enabled channels with their scale/offset applied."""
        self.ax.clear()
        self.ax.set_title("Signal Waveform")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Amplitude")

        for ch, var in zip(self.channels, self.channel_vars):
            if var.get() and ch.signal is not None:
                y = ch.scale * ch.signal + ch.offset
                self.ax.plot(y, color=ch.color, label=ch.name)

        if any(var.get() for var in self.channel_vars):
            self.ax.legend(loc="upper left")

        self.canvas.draw()

    def update_fft(self):
        """Compute and plot FFT of the first enabled channel."""
        enabled_channels = [
            (ch, var) for ch, var in zip(self.channels, self.channel_vars)
            if var.get() and ch.signal is not None
        ]
        if not enabled_channels:
            self.ax_fft.clear()
            self.ax_fft.set_title("FFT Spectrum")
            self.ax_fft.set_xlabel("Frequency (Hz)")
            self.ax_fft.set_ylabel("Magnitude")
            self.canvas_fft.draw()
            return

        # Runtime + Pylance safety
        ch, _ = enabled_channels[0]
        sig = ch.signal
        if sig is None:
            return
        # -------------------------------

        fs = self.sampling_rate.get()
        n = len(sig)

        freqs = np.fft.rfftfreq(n, d=1.0 / fs)
        spectrum = np.abs(np.fft.rfft(sig))

        # placeholder:
        self.ax_fft.clear()
        self.ax_fft.plot(freqs, spectrum, color=ch.color)
        self.ax_fft.set_title(f"FFT Spectrum ({ch.name})")
        self.ax_fft.set_xlabel("Frequency [Hz]")
        self.ax_fft.set_ylabel("Magnitude")
        self.canvas.draw()
        pass

    def compute_measurements(self, signal):
        """Compute basic measurements for a given signal (used by Generate)."""
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

    # ---------- CURSOR & MEASUREMENT LOGIC ----------
    def _get_first_enabled_channel(self):
        for ch, var in zip(self.channels, self.channel_vars):
            if var.get() and ch.signal is not None:
                return ch
        return None

    def _on_waveform_click(self, event):
        if event.inaxes != self.ax:
            return

        x = int(event.xdata)

        if self.cursor_a is None:
            self.cursor_a = x
        elif self.cursor_b is None:
            self.cursor_b = x
        else:
            # Reset
            self.cursor_a = None
            self.cursor_b = None
            self._clear_cursor_lines()

            if self.measure_overlay is not None:
                self.measure_overlay.remove()
                self.measure_overlay = None

            self.measure_label.config(text="Peak: --   RMS: --   Freq: --")
            self.sb_meas.config(text="MEAS: OFF", bg="#303030")
            self.canvas.draw()
            return

        self._draw_cursors()
        self._compute_cursor_measurements()

    def _draw_cursors(self):
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

    def _update_measure_overlay(self, text):
        if self.measure_overlay is not None:
            self.measure_overlay.remove()

        self.measure_overlay = AnchoredText(
            text,
            loc="upper right",
            prop={"size": 10, "color": "white"},
            frameon=True,
            pad=0.4,
            borderpad=0.5
        )

        self.measure_overlay.patch.set_facecolor("black")
        self.measure_overlay.patch.set_alpha(0.6)
        self.measure_overlay.patch.set_edgecolor("white")

        self.ax.add_artist(self.measure_overlay)
        self.canvas.draw()

    def _compute_cursor_measurements(self):
        self.sb_meas.config(text="MEAS: ON", bg="#004488")
        """Compute peak, RMS, and frequency based on cursor positions."""
        ch = self._get_first_enabled_channel()
        if ch is None or ch.signal is None:
            return

        sig = ch.signal
        n = len(sig)

        if self.cursor_a is None or self.cursor_a < 0 or self.cursor_a >= n:
            return

        fs = self.sampling_rate.get()

        # Single cursor: show value
        if self.cursor_b is None:
            y = sig[self.cursor_a]
            overlay_text = (
                f"{ch.name}\n"
                f"Cursor A: {self.cursor_a}\n"
                f"Value: {y:.3f}"
            )
            self._update_measure_overlay(overlay_text)
            return

        # Two cursors: region
        if self.cursor_b < 0 or self.cursor_b >= n:
            return

        a, b = sorted([self.cursor_a, self.cursor_b])
        region = sig[a:b]

        if len(region) < 2:
            return

        peak = np.max(np.abs(region))
        rms = np.sqrt(np.mean(region**2))
        dt = (b - a) / fs
        freq = 1 / dt if dt > 0 else 0

        overlay_text = (
            f"{ch.name}\n"
            f"Cursor A: {a}\n"
            f"Cursor B: {b}\n"
            f"ΔX: {b - a} samples ({dt:.4f} s)\n"
            f"Peak: {peak:.3f}\n"
            f"RMS: {rms:.3f}\n"
            f"Freq: {freq:.2f} Hz"
        )

        self._update_measure_overlay(overlay_text)

    def _auto_measure_first_enabled_channel(self):
        self.sb_meas.config(text="MEAS: ON", bg="#004488")
        ch = self._get_first_enabled_channel()
        if ch is None or ch.signal is None:
            return

        sig = ch.signal
        peak = np.max(np.abs(sig))
        rms = np.sqrt(np.mean(sig**2))
        self.measure_label.config(
            text=f"{ch.name}  Peak: {peak:.3f}   RMS: {rms:.3f}"
        )

    # ---------- REAL-TIME LOOP ----------
    def start_realtime(self):
        print("Start RT instance:", id(self))

        """Start the real-time oscilloscope loop."""
        if not self.realtime_running:
            print(">>> Start RT pressed")

            self.realtime_running = True
            # indicator ON
            self.rt_status.config(
                text="RT ON", bg="#00aa00")   # #00aa00 Tektronix green
            # status bar
            self.sb_rt.config(text="RT: ON", bg="#006600")
            self._realtime_loop()

    def stop_realtime(self):
        print("Stop RT instance:", id(self))

        """Stop the real-time oscilloscope loop."""
        print(">>> Stop RT pressed")

        self.realtime_running = False
        # indicator OFF
        self.rt_status.config(text="RT OFF", bg="#660000")
        # status bar
        self.sb_rt.config(text="RT: OFF", bg="#660000")

    def _realtime_loop(self):

        if not self.realtime_running:

            return
        print(">>> RT loop running")
        self.measure_label.config(text="RT: ON")

        fs = self.sampling_rate.get()
        n = self.n_samples

        # Get signals from waveform.py
        signals = waveform.get_signals(len(self.channels), n, fs, home=self)

        # Assign signals to channels
        for ch, sig in zip(self.channels, signals):
            ch.set_signal(sig)

        # Update plots and measurements
        self.update_waveform()
        self.update_fft()
        self._auto_measure_first_enabled_channel()

        # Schedule next frame (16 ms = ~60 FPS)
        self.after(16, self._realtime_loop)

    # ---------- TEXT REFRESH (I18N) ----------
    def refresh_text(self):
        self.label.config(text=self.controller.t("home"))
        self.btn_settings.config(text=self.controller.t("go_settings"))
        self.btn_initial.config(text=self.controller.t("go_initial"))
