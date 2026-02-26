import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patheffects as pe

# ─────────────────────────────────────────────
#    COLORS & FONTS (Disney Look)
# ─────────────────────────────────────────────
COLORS = {
    "bg_top":       "#050a14",   
    "bg_bottom":    "#0a121e",   
    "interface":    "#00f2ff",   
    "incident":     "#ff00ff",   
    "refracted":    "#00f2ff",   
    "reflected":    "#ff0044",   
    "normal":       "#4a7fa5",
    "critical":     "#a78bfa",
    "text":         "#ffffff",
    "panel_bg":     "#0f172a",   
    "accent":       "#00f2ff",
}

F_TITLE = ("Verdana", 16, "bold")
F_SUB   = ("Courier", 11)
F_LABEL = ("Verdana", 10, "bold")
F_NUM   = ("Courier", 18, "bold") 

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

    # Background Regions
    ax.fill_between([-1, 1], 0, 1,  color=COLORS["bg_top"], alpha=1, zorder=0)
    ax.fill_between([-1, 1], -1, 0, color=COLORS["bg_bottom"], alpha=1, zorder=0)

    # Interface Glow
    ax.plot([-1, 1], [0, 0], color=COLORS["interface"], lw=3, alpha=0.8, zorder=5,
            path_effects=[pe.withStroke(linewidth=6, foreground=COLORS["interface"], alpha=0.2)])

    ax.text(-0.95, 0.85, f"LIQUID (n₂={n2})", color=COLORS["text"], fontsize=11, fontweight='bold', zorder=10)
    ax.text(-0.95, -0.9, f"GLASS (n₁={n1})", color=COLORS["text"], fontsize=11, fontweight='bold', zorder=10)

    origin = np.array([0.0, 0.0])
    theta1 = np.radians(angle_deg)
    sinT2  = (n1 / n2) * np.sin(theta1)
    is_tir = sinT2 >= 1.0
    L = 0.85 

    # Normal Line
    ax.plot([0, 0], [-L, L], color=COLORS["normal"], lw=1.5, linestyle='--', alpha=0.4)

    # Incident Ray
    ix, iy = -np.sin(theta1)*L, -np.cos(theta1)*L
    ax.plot([ix, 0], [iy, 0], color=COLORS["incident"], lw=4, zorder=7,
            path_effects=[pe.withStroke(linewidth=8, foreground=COLORS["incident"], alpha=0.15)])
    
    # Reflected Ray
    rx, ry = np.sin(theta1)*L, -np.cos(theta1)*L
    relw = 4 if is_tir else 1.5
    realpha = 1.0 if is_tir else 0.3
    ax.plot([0, rx], [0, ry], color=COLORS["reflected"], lw=relw, alpha=realpha, zorder=7)

    if not is_tir:
        theta2 = np.arcsin(sinT2)
        r2x, r2y = np.sin(theta2)*L, np.cos(theta2)*L
        ax.plot([0, r2x], [0, r2y], color=COLORS["refracted"], lw=4, zorder=7,
                path_effects=[pe.withStroke(linewidth=8, foreground=COLORS["refracted"], alpha=0.15)])
        
        ax.text(0.15, 0.25, f"{np.degrees(theta2):.0f}°", color=COLORS["refracted"], 
                fontsize=12, fontweight='bold', bbox=dict(facecolor='black', alpha=0.4, edgecolor='none'))
    else:
        # Total Internal Reflection Label
        msg = "⚡ TOTAL INTERNAL REFLECTION" if angle_deg < 90 else "⚡ SURFACE GRAZING"
        ax.text(0, 0.4, msg, color=COLORS["reflected"], 
                fontsize=14, fontweight='bold', ha='center', path_effects=[pe.withSimplePatchShadow()])

    # Critical indicator
    crad = np.radians(CRIT_DEG)
    ax.plot([-np.sin(crad)*0.7, 0], [-np.cos(crad)*0.7, 0], color=COLORS["critical"], lw=1, linestyle=':')

def _section_styled(parent, title):
    f = tk.Frame(parent, bg=COLORS["panel_bg"], pady=10)
    f.pack(fill='x')
    tk.Label(f, text=title, font=F_LABEL, fg=COLORS["accent"], bg=COLORS["panel_bg"]).pack(anchor='w', padx=10)
    inner = tk.Frame(f, bg="#1e293b", padx=10, pady=10, highlightthickness=1, highlightbackground="#334155")
    inner.pack(fill='x', padx=10, pady=5)
    return inner

class ModernTIR:
    def __init__(self, root):
        self.root = root
        root.title("Disney Cinematic Refractometer")
        root.geometry("1100x750")
        root.configure(bg=COLORS["panel_bg"])

        # Title
        header = tk.Frame(root, bg="#0f172a", pady=20)
        header.pack(fill='x')
        tk.Label(header, text="⚗ THE CHEMICAL LOCK ANALYSIS", font=F_TITLE, fg=COLORS["accent"], bg="#0f172a").pack()
        tk.Label(header, text="Refractive Index Identification Protocol", font=F_SUB, fg="#64748b", bg="#0f172a").pack()

        main = tk.Frame(root, bg=COLORS["panel_bg"])
        main.pack(fill='both', expand=True, padx=20, pady=10)

        left = tk.Frame(main, bg="#000000", borderwidth=2, relief="flat")
        left.pack(side='left', fill='both', expand=True)
        self.fig, self.ax = plt.subplots(figsize=(6, 6), facecolor=COLORS["bg_bottom"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=left)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        right = tk.Frame(main, bg=COLORS["panel_bg"], width=320)
        right.pack(side='right', fill='y', padx=(20, 0))
        right.pack_propagate(False)

        # --- MODIFIED SLIDER HERE ---
        s1 = _section_styled(right, "LASER CONTROL")
        self.angle_var = tk.DoubleVar(value=40)
        # We changed 'to' from 85 to 90
        self.slider = tk.Scale(s1, from_=0, to=90, orient='horizontal', variable=self.angle_var, 
                 bg="#1e293b", fg="white", highlightthickness=0, troughcolor="#0f172a",
                 command=lambda e: self.update())
        self.slider.pack(fill='x')
        
        self.val_label = tk.Label(s1, text="40°", font=F_NUM, fg=COLORS["incident"], bg="#1e293b")
        self.val_label.pack(pady=10)

        s2 = _section_styled(right, "IDENTIFICATION DATA")
        math_txt = f"n₁ (Glass) = {n1}\nn₂ (Target) = {n2}\nθc = {CRIT_DEG}°"
        tk.Label(s2, text=math_txt, font=("Courier New", 11, "bold"), fg="#94a3b8", bg="#1e293b", justify='left').pack()
        
        self.res_label = tk.Label(right, text="💧 LIQUID: WATER", font=("Verdana", 14, "bold"), 
                                  fg="#00f2ff", bg="#1e293b", pady=20, relief="groove")
        self.res_label.pack(fill='x', padx=10, pady=20)

        self.update()

    def update(self):
        angle = self.angle_var.get()
        self.val_label.config(text=f"{angle:.0f}°")
        draw_scene(self.ax, angle)
        self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernTIR(root)
    root.mainloop()