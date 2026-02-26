import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patheffects as pe


COLORS = {
    "bg_top":       "#050a14",
    "bg_bottom":    "#0a121e",
    "interface":    "#00f2ff",
    "incident":     "#99ff00",
    "refracted":    "#00f2ff",
    "reflected":    "#ff0044",
    "normal":       "#4a7fa5",
    "critical":     "#a78bfa",
    "text":         "#ffffff",
    "panel_bg":     "#141c2f",
    "accent":       "#00f2ff",
}

F_TITLE  = ("Verdana", 16, "bold")
F_SUB    = ("Courier", 11)
F_LABEL  = ("Verdana", 10, "bold")
F_NUM    = ("Courier", 18, "bold")
F_LOCK   = ("Courier", 13, "bold")
F_LOCK_S = ("Verdana", 11, "bold")

n1 = 1.60
n2 = 1.326
CRIT_DEG = 56.0


def draw_scene(ax, angle_deg):
    ax.clear()
    ax.set_facecolor(COLORS["bg_bottom"])
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.fill_between([-1, 1], 0,  1, color=COLORS["bg_top"],    alpha=1, zorder=0)
    ax.fill_between([-1, 1], -1, 0, color=COLORS["bg_bottom"], alpha=1, zorder=0)

    ax.plot([-1, 1], [0, 0], color=COLORS["interface"], lw=3, alpha=0.8, zorder=5,
            path_effects=[pe.withStroke(linewidth=6, foreground=COLORS["interface"], alpha=0.2)])

    ax.text(-0.95,  0.85, f"LIQUID (n₂={n2})", color=COLORS["text"], fontsize=11, fontweight='bold', zorder=10)
    ax.text(-0.95, -0.90, f"GLASS  (n₁={n1})", color=COLORS["text"], fontsize=11, fontweight='bold', zorder=10)

    theta1 = np.radians(angle_deg)
    sinT2  = (n1 / n2) * np.sin(theta1)
    is_tir = sinT2 >= 1.0
    L = 0.85

    # Normal
    ax.plot([0, 0], [-L, L], color=COLORS["normal"], lw=1.5, linestyle='--', alpha=0.4)

    # Incident
    ix, iy = -np.sin(theta1)*L, -np.cos(theta1)*L
    ax.annotate("", xy=(0, 0), xytext=(ix, iy),
                arrowprops=dict(arrowstyle='->', color=COLORS["incident"], lw=3,
                                connectionstyle='arc3,rad=0'))
    ax.plot([ix, 0], [iy, 0], color=COLORS["incident"], lw=3.5, zorder=7,
            path_effects=[pe.withStroke(linewidth=7, foreground=COLORS["incident"], alpha=0.15)])

    # Reflected
    rx, ry   = np.sin(theta1)*L, -np.cos(theta1)*L
    rel_lw   = 4   if is_tir else 1.5
    rel_a    = 1.0 if is_tir else 0.3
    ax.annotate("", xy=(rx, ry), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=COLORS["reflected"], lw=rel_lw,
                                connectionstyle='arc3,rad=0', alpha=rel_a))
    ax.plot([0, rx], [0, ry], color=COLORS["reflected"], lw=rel_lw, alpha=rel_a, zorder=7)

    if not is_tir:
        theta2 = np.arcsin(sinT2)
        r2x = np.sin(theta2)*L
        r2y = np.cos(theta2)*L
        ax.annotate("", xy=(r2x, r2y), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color=COLORS["refracted"], lw=3,
                                    connectionstyle='arc3,rad=0'))
        ax.plot([0, r2x], [0, r2y], color=COLORS["refracted"], lw=3.5, zorder=7,
                path_effects=[pe.withStroke(linewidth=7, foreground=COLORS["refracted"], alpha=0.15)])
        ax.text(r2x+0.06, r2y-0.08, f"{np.degrees(theta2):.0f}°",
                color=COLORS["refracted"], fontsize=12, fontweight='bold',
                bbox=dict(facecolor='black', alpha=0.45, edgecolor='none'))
    else:
        ax.text(0, 0.42, "⚡ TOTAL INTERNAL REFLECTION",
                color=COLORS["reflected"], fontsize=13, fontweight='bold',
                ha='center', path_effects=[pe.withSimplePatchShadow()])

    # Critical angle dashed
    crad = np.radians(CRIT_DEG)
    ax.plot([-np.sin(crad)*0.7, 0], [-np.cos(crad)*0.7, 0],
            color=COLORS["critical"], lw=1, linestyle=':', alpha=0.6)
    ax.text(-np.sin(crad)*0.75 - 0.04, -np.cos(crad)*0.75,
            f"θc={CRIT_DEG:.0f}°", color=COLORS["critical"], fontsize=9)

    # Incident angle label
    ax.text(ix - 0.05, iy + 0.06, f"{angle_deg:.0f}°",
            color=COLORS["incident"], fontsize=11, fontweight='bold')


def _section_styled(parent, title):
    f = tk.Frame(parent, bg=COLORS["panel_bg"], pady=10)
    f.pack(fill='x')
    tk.Label(f, text=title, font=F_LABEL, fg=COLORS["accent"],
             bg=COLORS["panel_bg"]).pack(anchor='w', padx=10)
    inner = tk.Frame(f, bg="#1e293b", padx=10, pady=10,
                     highlightthickness=1, highlightbackground="#334155")
    inner.pack(fill='x', padx=10, pady=5)
    return inner


# ── Animated lock widget ─────────────────────────────────────────────────────
class LockWidget(tk.Frame):
    """A pure-tkinter animated lock that shows GRANTED / DENIED."""

    LOCK_CLOSED = (
        "  ┌──────┐  ",
        "  │ ████ │  ",
        "  │ ████ │  ",
        "  └──────┘  ",
        "  │ •  • │  ",
        "  │  ██  │  ",
        "  └──────┘  ",
    )
    LOCK_OPEN = (
        "  ┌──────┐  ",
        "  │      │  ",   # shackle open
        "  │      │  ",
        "┌─┘──────┘  ",
        "│ •  •      ",
        "│  ██       ",
        "└───────    ",
    )

    def __init__(self, parent, **kw):
        super().__init__(parent, bg="#0d1b2a", **kw)
        self._granted = False
        self._blink   = False
        self._blink_id = None

        # ASCII lock display
        self.lock_canvas = tk.Canvas(self, width=160, height=130,
                                     bg="#0d1b2a", highlightthickness=0)
        self.lock_canvas.pack(pady=(10, 0))

        self.status_lbl = tk.Label(self, text="■ LOCKED",
                                   font=("Courier", 14, "bold"),
                                   fg="#ff3355", bg="#0d1b2a")
        self.status_lbl.pack()

        self.sub_lbl = tk.Label(self, text="AWAITING IDENTIFICATION…",
                                font=("Courier", 9), fg="#334155",
                                bg="#0d1b2a", wraplength=200)
        self.sub_lbl.pack(pady=(2, 10))

        # Scan-line bar (hidden by default)
        self.scan_bar = tk.Frame(self, height=2, bg="#00f2ff")
        self._draw_lock(closed=True)

    # ── draw ASCII lock on canvas ──────────────────────────────────────────
    def _draw_lock(self, closed=True):
        self.lock_canvas.delete("all")
        lines  = self.LOCK_CLOSED if closed else self.LOCK_OPEN
        color  = "#00f2ff" if not closed else "#ff3355"
        shadow = "#003344" if not closed else "#330011"
        for i, line in enumerate(lines):
            self.lock_canvas.create_text(
                80, 10 + i*17, text=line,
                font=("Courier", 12, "bold"), fill=shadow, anchor='center')
            self.lock_canvas.create_text(
                79, 9 + i*17, text=line,
                font=("Courier", 12, "bold"), fill=color, anchor='center')

    # ── public method ─────────────────────────────────────────────────────
    def set_state(self, granted: bool):
        if granted == self._granted:
            return
        self._granted = granted
        if granted:
            self._draw_lock(closed=False)
            self.configure(bg="#001a22", highlightbackground="#00f2ff",
                           highlightthickness=2)
            self.lock_canvas.configure(bg="#001a22")
            self.status_lbl.configure(bg="#001a22",
                                      fg="#00f2ff", text="✔ ACCESS GRANTED")
            self.sub_lbl.configure(bg="#001a22",
                                   fg="#00c8d4", text="💧 LIQUID: WATER CONFIRMED")
            self._start_scan()
        else:
            if self._blink_id:
                self.after_cancel(self._blink_id)
                self._blink_id = None
            self._draw_lock(closed=True)
            self.configure(bg="#0d1b2a", highlightbackground="#1e293b",
                           highlightthickness=1)
            self.lock_canvas.configure(bg="#0d1b2a")
            self.status_lbl.configure(bg="#0d1b2a",
                                      fg="#ff3355", text="■ LOCKED")
            self.sub_lbl.configure(bg="#0d1b2a",
                                   fg="#334155", text="AWAITING IDENTIFICATION…")

    # ── scan-line blink ───────────────────────────────────────────────────
    def _start_scan(self):
        self._blink = True
        self._do_blink()

    def _do_blink(self):
        if not self._granted:
            return
        self._blink = not self._blink
        col = "#00f2ff" if self._blink else "#003344"
        # re-draw with alternating glow colour
        self.lock_canvas.delete("all")
        lines = self.LOCK_OPEN
        for i, line in enumerate(lines):
            self.lock_canvas.create_text(
                80, 10 + i*17, text=line,
                font=("Courier", 12, "bold"), fill="#003344", anchor='center')
            self.lock_canvas.create_text(
                79, 9 + i*17, text=line,
                font=("Courier", 12, "bold"), fill=col, anchor='center')
        self._blink_id = self.after(600, self._do_blink)


# ── Main App ─────────────────────────────────────────────────────────────────
class ModernTIR:
    def __init__(self, root):
        self.root = root
        root.title("track02 – Chemical Lock")
        root.geometry("1150x780")
        root.configure(bg=COLORS["panel_bg"])

        # Header
        header = tk.Frame(root, bg="#0a0f1a", pady=18)
        header.pack(fill='x')
        tk.Label(header, text="⚗ THE CHEMICAL LOCK ANALYSIS",
                 font=F_TITLE, fg=COLORS["accent"], bg="#0a0f1a").pack()
        tk.Label(header, text="Refractive Index Identification Protocol",
                 font=F_SUB, fg="#64748b", bg="#0a0f1a").pack()

        main = tk.Frame(root, bg=COLORS["panel_bg"])
        main.pack(fill='both', expand=True, padx=20, pady=10)

        # Left – matplotlib canvas
        left = tk.Frame(main, bg="#000000", borderwidth=2, relief="flat")
        left.pack(side='left', fill='both', expand=True)
        self.fig, self.ax = plt.subplots(figsize=(6, 6),
                                          facecolor=COLORS["bg_bottom"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=left)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Right – controls
        right = tk.Frame(main, bg=COLORS["panel_bg"], width=330)
        right.pack(side='right', fill='y', padx=(20, 0))
        right.pack_propagate(False)

        # Laser control
        s1 = _section_styled(right, "LASER CONTROL")
        self.angle_var = tk.DoubleVar(value=40)
        self.slider = tk.Scale(s1, from_=0, to=90, orient='horizontal',
                               variable=self.angle_var,
                               bg="#1e293b", fg="white", highlightthickness=0,
                               troughcolor="#0f172a",
                               command=lambda e: self.update())
        self.slider.pack(fill='x')
        self.val_label = tk.Label(s1, text="40°", font=F_NUM,
                                  fg=COLORS["incident"], bg="#1e293b")
        self.val_label.pack(pady=8)

        # Identification data
        s2 = _section_styled(right, "IDENTIFICATION DATA")
        self.data_label = tk.Label(
            s2,
            text=f"n₁ (Glass)   = {n1}\nn₂ (Target)  = {n2}\nθc           = {CRIT_DEG}°\nθ refracted  = —",
            font=("Courier New", 11, "bold"), fg="#94a3b8",
            bg="#1e293b", justify='left')
        self.data_label.pack(anchor='w')

        # TIR warning label
        self.tir_label = tk.Label(right, text="", font=("Courier", 10, "bold"),
                                  fg=COLORS["reflected"], bg=COLORS["panel_bg"])
        self.tir_label.pack(pady=(4, 0))

        # ── Lock widget ──
        self.lock = LockWidget(right, highlightthickness=1,
                               highlightbackground="#1e293b")
        self.lock.pack(fill='x', padx=10, pady=14)

        self.update()

    # ─────────────────────────────────────────────────────────────────────
    def update(self):
        angle  = self.angle_var.get()
        theta1 = np.radians(angle)
        sinT2  = (n1 / n2) * np.sin(theta1)
        is_tir = sinT2 >= 1.0

        self.val_label.config(text=f"{angle:.0f}°")

        if not is_tir and angle > 0:
            theta2_deg = np.degrees(np.arcsin(sinT2))
            ref_txt = f"{theta2_deg:.1f}°"
            self.tir_label.config(text="")
        else:
            ref_txt = "— (TIR)"
            if is_tir:
                self.tir_label.config(text="⚡ T.I.R. ACTIVE — NO REFRACTION")
            else:
                self.tir_label.config(text="")

        self.data_label.config(
            text=(f"n₁ (Glass)   = {n1}\n"
                  f"n₂ (Target)  = {n2}\n"
                  f"θc           = {CRIT_DEG}°\n"
                  f"θ refracted  = {ref_txt}"))

        # Granted only when light actually refracts into the liquid
        granted = (not is_tir) and (angle > 0)
        self.lock.set_state(granted)

        draw_scene(self.ax, angle)
        self.canvas.draw_idle()


if __name__ == "__main__":
    root = tk.Tk()
    app  = ModernTIR(root)
    root.mainloop()