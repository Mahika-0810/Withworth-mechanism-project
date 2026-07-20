# =============================================================================
# FILE: stage2_redesigned.py
# PROJECT: Kinematics & Dynamics of Mechanisms — Stage II Simulator
# REDESIGNED: Complete UI overhaul — dark engineering theme, premium aesthetics
#             ALL MECHANISM MATH IS UNCHANGED
# =============================================================================

import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QPushButton, QFrame, QStackedWidget,
    QSlider, QGroupBox, QTextEdit, QListWidget, QListWidgetItem, QTabWidget,
    QGraphicsDropShadowEffect, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPalette, QLinearGradient, QGradient

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# =============================================================================
# PREMIUM DARK ENGINEERING THEME — MATPLOTLIB
# =============================================================================
mpl.rcParams.update({
    'figure.facecolor':  '#282A36',
    'axes.facecolor':    '#282A36',
    'axes.edgecolor':    '#44475A',
    'text.color':        '#F8F8F2',
    'axes.labelcolor':   '#6272A4',
    'xtick.color':       '#6272A4',
    'ytick.color':       '#6272A4',
    'grid.color':        '#44475A',
    'grid.alpha':         0.8,
    'legend.facecolor':  '#282A36',
    'legend.edgecolor':  '#44475A',
    'axes.titlecolor':   '#F8F8F2',
    'figure.titlesize':  12,
    'axes.spines.top':   True,
    'axes.spines.right': True,
})

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#282A36"       # Dracula background
PANEL   = "#21222C"       # darker panel
BORDER  = "#44475A"       # borders
HOVER   = "#44475A"       # hover state
ACCENT  = "#8BE9FD"       # cyan
ACCENT2 = "#BD93F9"       # purple
SUCCESS = "#50FA7B"       # green
WARN    = "#FFB86C"       # orange
DANGER  = "#FF5555"       # red
MUTED   = "#6272A4"       # comment/muted
TEXT    = "#F8F8F2"       # foreground
DIM     = "#E6E6E6"       # bright text

# ── Stylesheet ────────────────────────────────────────────────────────────────
STYLE = f"""
QMainWindow, QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: 'Consolas', 'Courier New', monospace;
}}

QListWidget {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    outline: none;
    padding: 4px;
}}
QListWidget::item {{
    padding: 13px 16px;
    border-radius: 7px;
    margin: 2px 0;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 0.5px;
    color: {MUTED};
}}
QListWidget::item:selected {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8BE9FD, stop:1 #BD93F9);
    color: #282A36;
}}
QListWidget::item:hover:!selected {{
    background: {HOVER};
    color: {TEXT};
}}

QPushButton {{
    padding: 10px 22px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 0.8px;
    border: none;
    color: {BG};
}}
QPushButton:hover {{
    opacity: 0.85;
}}
QPushButton:pressed {{
    padding: 11px 20px 9px 24px;
}}

QDoubleSpinBox {{
    background: {BG};
    color: {ACCENT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 12px;
    font-family: 'Consolas', monospace;
    font-weight: bold;
}}
QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
}}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {HOVER};
    border: none;
    width: 18px;
}}

QLabel {{
    color: {DIM};
    font-size: 11px;
}}

QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 14px;
    color: {ACCENT};
    font-weight: bold;
    font-size: 11px;
    letter-spacing: 1px;
    background: {PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    background: {PANEL};
}}

QTextEdit {{
    background: {PANEL};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px;
    font-size: 12px;
    font-family: 'Consolas', monospace;
    line-height: 1.6;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {HOVER};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}

QTabWidget::pane {{
    border: none;
}}
QTabBar::tab {{
    background: {HOVER};
    color: {MUTED};
    padding: 8px 20px;
    font-size: 11px;
    font-weight: bold;
    border-radius: 6px 6px 0 0;
    margin-right: 2px;
    letter-spacing: 0.5px;
}}
QTabBar::tab:selected {{
    color: {BG};
}}

QScrollBar:vertical {{
    background: {BG};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
}}
"""

# =============================================================================
# CUSTOM WIDGETS
# =============================================================================

class GlowButton(QPushButton):
    def __init__(self, text, color1, color2=None, parent=None):
        super().__init__(text, parent)
        c2 = color2 or color1
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {color1}, stop:1 {c2});
                color: {'#282A36' if color1 != DANGER else '#FFFFFF'};
                padding: 10px 24px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 1px;
                border: none;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c2}, stop:1 {color1});
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(color1))
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class DividerLine(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")

class StatCard(QWidget):
    def __init__(self, label, value="—", accent=ACCENT, parent=None):
        super().__init__(parent)
        self.accent = accent
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(2)
        self._lbl = QLabel(label.upper())
        self._lbl.setStyleSheet(f"color:{MUTED}; font-size:9px; letter-spacing:1.5px; font-weight:bold;")
        self._val = QLabel(value)
        self._val.setStyleSheet(f"color:{accent}; font-size:16px; font-weight:bold; font-family:'Consolas';")
        lay.addWidget(self._lbl)
        lay.addWidget(self._val)
        self.setStyleSheet(f"""
            StatCard {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-left: 3px solid {accent};
                border-radius: 8px;
            }}
        """)

    def set_value(self, v):
        self._val.setText(str(v))

# =============================================================================
# MAIN WINDOW
# =============================================================================

class WhitworthSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ME2220  ·  Whitworth Quick-Return Mechanism Simulator")
        self.setGeometry(30, 30, 1500, 950)
        self.setStyleSheet(STYLE)

        # ── Timer: fires at fixed 16ms (~60 fps cap), advances by angle_step internally
        self.timer = QTimer()
        self.timer.setInterval(16)          # ~60 fps — smooth wall-clock cadence
        self.timer.timeout.connect(self.update_animation)

        self.current_angle = 0.0
        self.angle_step    = 2.0            # degrees per timer tick (tuned for smoothness)
        self.FORWARD_DEG   = 240.0
        self.RETURN_DEG    = 120.0
        self.syn           = None

        # Animation state
        self._is_paused      = False

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        sidebar = self._build_sidebar()
        root.addWidget(sidebar, stretch=0)

        main_area = self._build_main_area()
        root.addWidget(main_area, stretch=1)

        self.setup_synthesis_ui()
        self.setup_animation_ui()
        self.setup_abc_ui()
        self.setup_kinplots_ui()
        self.setup_dynamics_ui()

        self.synthesize()

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(270)
        sidebar.setStyleSheet(f"background:{PANEL}; border-right:1px solid {BORDER};")
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(16, 20, 16, 20)
        lay.setSpacing(0)

        logo_lbl = QLabel("⚙")
        logo_lbl.setStyleSheet(f"font-size:28px; color:{ACCENT};")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo_lbl)

        title = QLabel("WHITWORTH")
        title.setStyleSheet(f"color:{TEXT}; font-size:15px; font-weight:bold; letter-spacing:3px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("MECHANISM SIMULATOR")
        sub.setStyleSheet(f"color:{MUTED}; font-size:9px; letter-spacing:2px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)

        lay.addSpacing(16)
        lay.addWidget(DividerLine())
        lay.addSpacing(16)

        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(f"color:{MUTED}; font-size:9px; letter-spacing:2px; font-weight:bold;")
        lay.addWidget(nav_label)
        lay.addSpacing(6)

        self.nav_list = QListWidget()
        self.nav_list.setSpacing(1)
        nav_items = [
            ("⬡", "Synthesis Overview"),
            ("▶", "Live Animation"),
            ("◈", "Kinematics A·B·C"),
            ("⌁", "Kinematic Plots"),
            ("⚡", "Dynamic Analysis"),
        ]
        for icon, label in nav_items:
            item = QListWidgetItem(f"  {icon}   {label}")
            self.nav_list.addItem(item)

        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.change_page)
        self.nav_list.setFixedHeight(240)
        self.nav_list.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_list.setStyleSheet(
            f"QListWidget {{ background: transparent; border: none; }}"
            f"QListWidget::item {{ padding:12px 10px; border-radius:8px; margin:2px 0; font-size:12px; font-weight:bold; color:{MUTED}; }}"
            f"QListWidget::item:selected {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {ACCENT},stop:1 {ACCENT2}); color:#282A36; }}"
            f"QListWidget::item:hover:!selected {{ background:{HOVER}; color:{TEXT}; }}"
        )
        lay.addWidget(self.nav_list)
        lay.addSpacing(20)
        lay.addWidget(DividerLine())
        lay.addSpacing(20)

        params_label = QLabel("PARAMETERS")
        params_label.setStyleSheet(f"color:{MUTED}; font-size:9px; letter-spacing:2px; font-weight:bold;")
        lay.addWidget(params_label)
        lay.addSpacing(10)

        params_frame = QWidget()
        params_frame.setStyleSheet(f"background:{BG}; border-radius:10px; border:1px solid {BORDER};")
        pf_lay = QVBoxLayout(params_frame)
        pf_lay.setContentsMargins(12, 12, 12, 12)
        pf_lay.setSpacing(8)

        self.sp_R     = self._spin("R (cm)",      pf_lay, 0.1, 5000.0,  5.0)
        self.sp_dropB = self._spin("Drop B (mm)", pf_lay, 0.1, 5000.0,  5.0)
        self.sp_dropC = self._spin("Drop C (mm)", pf_lay, 0.1, 5000.0, 15.0)
        self.sp_rpm   = self._spin("RPM",         pf_lay, 1.0, 5000.0, 60.0)
        self.sp_cs    = self._spin("CS (mm)",     pf_lay, 1.0, 1000.0,  8.0)
        lay.addWidget(params_frame)
        lay.addSpacing(14)

        self.btn_syn = GlowButton("⚙  SYNTHESIZE", ACCENT, ACCENT2)
        self.btn_syn.clicked.connect(self.synthesize)
        lay.addWidget(self.btn_syn)

        lay.addStretch()

        ver = QLabel("ME2220  ·  Stage II  ·  v5.0")
        ver.setStyleSheet(f"color:{BORDER}; font-size:9px; letter-spacing:1px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ver)

        return sidebar

    def _spin(self, label, layout, lo, hi, default):
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color:{MUTED}; font-size:10px; min-width:70px;")
        sb = QDoubleSpinBox()
        sb.setRange(lo, hi)
        sb.setValue(default)
        sb.setFixedWidth(90)
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(sb)
        layout.addLayout(row)
        return sb

    # =========================================================================
    # MAIN AREA
    # =========================================================================
    def _build_main_area(self):
        widget = QWidget()
        lay = QVBoxLayout(widget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        topbar = QWidget()
        topbar.setFixedHeight(52)
        topbar.setStyleSheet(f"background:{PANEL}; border-bottom:1px solid {BORDER};")
        tb_lay = QHBoxLayout(topbar)
        tb_lay.setContentsMargins(20, 0, 20, 0)

        self.page_title = QLabel("Synthesis Overview")
        self.page_title.setStyleSheet(f"color:{TEXT}; font-size:14px; font-weight:bold; letter-spacing:1px;")
        tb_lay.addWidget(self.page_title)
        tb_lay.addStretch()

        self.status = QLabel("●  Ready")
        self.status.setStyleSheet(f"color:{SUCCESS}; font-size:11px; font-weight:bold; letter-spacing:0.5px;")
        tb_lay.addWidget(self.status)
        lay.addWidget(topbar)

        cards_row = QWidget()
        cards_row.setFixedHeight(66)
        cards_row.setStyleSheet(f"background:{BG}; border-bottom:1px solid {BORDER};")
        cr_lay = QHBoxLayout(cards_row)
        cr_lay.setContentsMargins(16, 8, 16, 8)
        cr_lay.setSpacing(10)

        self.card_qr  = StatCard("Quick-Return Ratio", "—",    ACCENT)
        self.card_fwd = StatCard("Forward Stroke",     "—°",   SUCCESS)
        self.card_ret = StatCard("Return Stroke",      "—°",   WARN)
        self.card_rpm = StatCard("Input Speed",        "— RPM", ACCENT2)
        self.card_rod = StatCard("Conn-Rod Length",    "— mm",  DIM)

        for card in [self.card_qr, self.card_fwd, self.card_ret, self.card_rpm, self.card_rod]:
            cr_lay.addWidget(card)
        cr_lay.addStretch()
        lay.addWidget(cards_row)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{BG};")
        lay.addWidget(self.stack, stretch=1)

        self.page_syn  = QWidget()
        self.page_anim = QWidget()
        self.page_abc  = QWidget()
        self.page_kin  = QWidget()
        self.page_dyn  = QWidget()

        for p in [self.page_syn, self.page_anim, self.page_abc, self.page_kin, self.page_dyn]:
            p.setStyleSheet(f"background:{BG};")
            self.stack.addWidget(p)

        return widget

    PAGE_TITLES = [
        "Synthesis Overview",
        "Live Animation",
        "Kinematics  ·  Positions A · B · C",
        "Kinematic Plots",
        "Dynamic Analysis",
    ]

    def change_page(self, index):
        self.stack.setCurrentIndex(index)
        self.page_title.setText(self.PAGE_TITLES[index])
        if index == 1:
            self.btn_animate_clicked()
        else:
            self.timer.stop()

    def set_status(self, msg, ok=True):
        color = SUCCESS if ok else DANGER
        dot   = "●" if ok else "✕"
        self.status.setText(f"{dot}  {msg}")
        self.status.setStyleSheet(f"color:{color}; font-size:11px; font-weight:bold; letter-spacing:0.5px;")

    # =========================================================================
    # UI SETUP
    # =========================================================================
    def setup_synthesis_ui(self):
        lay = QHBoxLayout(self.page_syn)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Left: pie object positions chart (replaces mechanism skeleton)
        self.fig_syn = Figure(figsize=(7, 6), dpi=100)
        self.canvas_syn = FigureCanvas(self.fig_syn)
        self.canvas_syn.setStyleSheet(f"border-radius:12px; border:1px solid {BORDER};")
        lay.addWidget(self.canvas_syn, stretch=55)

        # Right: detailed synthesis notes panel
        self.txt_notes = QTextEdit()
        self.txt_notes.setReadOnly(True)
        lay.addWidget(self.txt_notes, stretch=45)

    def setup_animation_ui(self):
        lay = QVBoxLayout(self.page_anim)
        lay.setContentsMargins(16, 12, 16, 16)
        lay.setSpacing(10)

        ctrl = QWidget()
        ctrl.setStyleSheet(f"background:{PANEL}; border-radius:8px; border:1px solid {BORDER};")
        ctrl.setFixedHeight(52)
        ct = QHBoxLayout(ctrl)
        ct.setContentsMargins(14, 0, 14, 0)
        ct.setSpacing(16)

        # ── STOP button ──
        btn_stop = GlowButton("⏹  STOP", DANGER)
        btn_stop.setFixedHeight(34)
        btn_stop.clicked.connect(self._stop_animation)
        ct.addWidget(btn_stop)

        # ── PAUSE / RESUME button ──
        self.btn_pause = GlowButton("⏸  PAUSE", WARN, "#D97706")
        self.btn_pause.setFixedHeight(34)
        self.btn_pause.clicked.connect(self._toggle_pause)
        ct.addWidget(self.btn_pause)

        ct.addWidget(DividerLine())

        speed_lbl = QLabel("SPEED")
        speed_lbl.setStyleSheet(f"color:{MUTED}; font-size:9px; letter-spacing:2px; font-weight:bold;")
        ct.addWidget(speed_lbl)

        self.speed_sl = QSlider(Qt.Orientation.Horizontal)
        self.speed_sl.setRange(1, 10)
        self.speed_sl.setValue(4)
        self.speed_sl.setFixedWidth(120)
        # angle_step controls degrees-per-tick; timer stays at 16 ms for smoothness
        self.speed_sl.valueChanged.connect(lambda v: setattr(self, 'angle_step', v * 0.5))
        ct.addWidget(self.speed_sl)

        self.angle_label = QLabel("θ₂ = 0.0°")
        self.angle_label.setStyleSheet(f"color:{ACCENT}; font-size:13px; font-weight:bold; font-family:'Consolas';")
        ct.addWidget(self.angle_label)

        ct.addWidget(DividerLine())

        self.btn_go_A = QPushButton("Go to A")
        self.btn_go_B = QPushButton("Go to B")
        self.btn_go_C = QPushButton("Go to C")
        for btn, pos in zip([self.btn_go_A, self.btn_go_B, self.btn_go_C], ['A', 'B', 'C']):
            btn.setStyleSheet(f"background:{HOVER}; color:{TEXT}; font-weight:bold; border-radius:4px; padding:6px 12px;")
            btn.clicked.connect(lambda checked, p=pos: self.jump_to_angle(p))
            ct.addWidget(btn)

        ct.addWidget(DividerLine())

        self.btn_pres = GlowButton("🎤 PRESENTATION", ACCENT2)
        self.btn_pres.setFixedHeight(30)
        self.btn_pres.clicked.connect(self.toggle_presentation)
        ct.addWidget(self.btn_pres)

        ct.addStretch()
        lay.addWidget(ctrl)

        # ── Phase / Time HUD bar (OUTSIDE the plot) ──
        hud = QWidget()
        hud.setFixedHeight(44)
        hud.setStyleSheet(f"background:{PANEL}; border-radius:8px; border:1px solid {BORDER};")
        hud_lay = QHBoxLayout(hud)
        hud_lay.setContentsMargins(18, 0, 18, 0)
        hud_lay.setSpacing(24)

        self.lbl_phase = QLabel("PHASE:  FORWARD")
        self.lbl_phase.setStyleSheet(f"color:{SUCCESS}; font-size:13px; font-weight:bold; font-family:'Consolas'; letter-spacing:1px;")
        hud_lay.addWidget(self.lbl_phase)

        hud_lay.addWidget(DividerLine())

        self.lbl_fwd_time = QLabel("Forward Stroke:  — s")
        self.lbl_fwd_time.setStyleSheet(f"color:{SUCCESS}; font-size:12px; font-weight:bold; font-family:'Consolas';")
        hud_lay.addWidget(self.lbl_fwd_time)

        self.lbl_ret_time = QLabel("Return Stroke:  — s")
        self.lbl_ret_time.setStyleSheet(f"color:{DANGER}; font-size:12px; font-weight:bold; font-family:'Consolas';")
        hud_lay.addWidget(self.lbl_ret_time)

        hud_lay.addWidget(DividerLine())

        self.lbl_cycle_time = QLabel("Cycle Time:  — s")
        self.lbl_cycle_time.setStyleSheet(f"color:{ACCENT}; font-size:12px; font-weight:bold; font-family:'Consolas';")
        hud_lay.addWidget(self.lbl_cycle_time)

        hud_lay.addStretch()
        lay.addWidget(hud)

        self.fig_anim = Figure(figsize=(12, 7), dpi=100)
        self.canvas_anim = FigureCanvas(self.fig_anim)
        self.canvas_anim.setStyleSheet(f"border-radius:10px; border:1px solid {BORDER};")
        self.ax_anim = self.fig_anim.add_subplot(111)
        lay.addWidget(self.canvas_anim)

        # ZOOM/PAN TOOLBAR for live animation
        lay.addWidget(NavigationToolbar(self.canvas_anim, self))

    def setup_abc_ui(self):
        lay = QVBoxLayout(self.page_abc)
        lay.setContentsMargins(16, 12, 16, 16)
        lay.setSpacing(10)

        # ── Position subtabs ──
        self.abc_subtabs = self._make_subtab(["🟢  Position A", "🟠  Position B", "🔴  Position C"], ACCENT2)
        self.abc_subtabs.currentChanged.connect(self._abc_tab_changed)
        lay.addWidget(self.abc_subtabs)

        # ── Vector-type subtabs ──
        self.abc_vec_subtabs = self._make_subtab(
            ["📍  Position Vectors", "↗  Velocity Polygon", "⚡  Acceleration Polygon"], ACCENT)
        self.abc_vec_subtabs.currentChanged.connect(self._abc_vec_tab_changed)
        lay.addWidget(self.abc_vec_subtabs)

        self.fig_abc = Figure(figsize=(14, 6.5), dpi=100)
        self.canvas_abc = FigureCanvas(self.fig_abc)
        self.canvas_abc.setStyleSheet(f"border-radius:10px; border:1px solid {BORDER};")
        lay.addWidget(self.canvas_abc, stretch=1)

        lay.addWidget(NavigationToolbar(self.canvas_abc, self))
        self._abc_drawn = False

    def setup_kinplots_ui(self):
        lay = QVBoxLayout(self.page_kin)
        lay.setContentsMargins(16, 12, 16, 16)
        lay.setSpacing(10)

        self.kin_subtabs = self._make_subtab(["📉  Displacement", "📈  Velocity", "📊  Acceleration"], WARN)
        self.kin_subtabs.currentChanged.connect(self._kin_tab_changed)
        lay.addWidget(self.kin_subtabs)

        self.fig_kin = Figure(figsize=(12, 6.5), dpi=100)
        self.canvas_kin = FigureCanvas(self.fig_kin)
        self.canvas_kin.setStyleSheet(f"border-radius:10px; border:1px solid {BORDER};")
        lay.addWidget(self.canvas_kin, stretch=1)

        lay.addWidget(NavigationToolbar(self.canvas_kin, self))
        self.kin_data = None

    def setup_dynamics_ui(self):
        lay = QVBoxLayout(self.page_dyn)
        lay.setContentsMargins(16, 12, 16, 16)
        lay.setSpacing(10)

        self.dyn_subtabs = self._make_subtab(
            ["🔄  Input Torque", "⬇  Net Force", "⚡  Power"], DANGER)
        self.dyn_subtabs.currentChanged.connect(self._dyn_tab_changed)
        lay.addWidget(self.dyn_subtabs)

        self.fig_dyn = Figure(figsize=(12, 6.5), dpi=100)
        self.canvas_dyn = FigureCanvas(self.fig_dyn)
        self.canvas_dyn.setStyleSheet(f"border-radius:10px; border:1px solid {BORDER};")
        lay.addWidget(self.canvas_dyn, stretch=1)

        lay.addWidget(NavigationToolbar(self.canvas_dyn, self))
        self.dyn_data = None

    def _make_subtab(self, labels, accent_color):
        tab = QTabWidget()
        tab.setStyleSheet(f"""
            QTabBar::tab {{
                background: {HOVER};
                color: {MUTED};
                padding: 8px 22px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 6px 6px 0 0;
                margin-right: 3px;
                letter-spacing: 0.5px;
                border: 1px solid {BORDER};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background: {accent_color};
                color: #282A36;
            }}
            QTabWidget::pane {{
                border: none;
                max-height: 1px;
                padding: 0;
            }}
        """)
        for lbl in labels:
            dummy = QWidget()
            dummy.setFixedHeight(0)
            tab.addTab(dummy, lbl)
        tab.setFixedHeight(tab.tabBar().sizeHint().height() + 2)
        return tab

    # =========================================================================
    # ANIMATION CONTROLS
    # =========================================================================
    def _stop_animation(self):
        self.timer.stop()
        self._is_paused = False
        self.btn_pause.setText("⏸  PAUSE")

    def _toggle_pause(self):
        if not self._is_paused:
            self.timer.stop()
            self._is_paused = True
            self.btn_pause.setText("▶  RESUME")
        else:
            self._is_paused = False
            self.btn_pause.setText("⏸  PAUSE")
            self.timer.start(16)

    # =========================================================================
    # CORE MATH & LOGIC
    # =========================================================================
    def _partial_circle_props(self, R_m, thickness_m, rho=2700.0):
        A_full = np.pi * R_m**2
        A_miss = A_full / 4.0
        A_obj  = (3.0 / 4.0) * A_full
        m_full = rho * thickness_m * A_full
        m_miss = rho * thickness_m * A_miss
        mass   = rho * thickness_m * A_obj
        miss_x = 4.0 * R_m / (3.0 * np.pi)
        miss_y = 4.0 * R_m / (3.0 * np.pi)
        cg_x = -(A_miss * miss_x) / A_obj
        cg_y = -(A_miss * miss_y) / A_obj
        I_O = 0.5 * (m_full - m_miss) * R_m**2
        return mass, cg_x, cg_y, I_O

    def synthesize(self):
        R_m     = self.sp_R.value() / 100.0
        dropB_m = self.sp_dropB.value() / 1000.0
        dropC_m = self.sp_dropC.value() / 1000.0
        rpm     = self.sp_rpm.value()
        cs_m    = self.sp_cs.value() / 1000.0

        a = max(2.0 * dropC_m, 0.04)
        alpha = np.radians(60.0)
        d = 2.0 * a
        crank_phase = np.radians(300.0)
        crank_dir = -1.0

        theta_fwd = np.degrees(np.pi * 2 - 2 * alpha)
        theta_ret = np.degrees(2 * alpha)
        QR = theta_fwd / theta_ret

        theta_A = 0.0
        theta_C = theta_fwd
        rod_ratio = 4.0

        def slider_y_for_lengths(theta_deg, Lr, Lrod):
            th = crank_phase + crank_dir * np.radians(theta_deg)
            O4x = d
            A_pt = np.array([a * np.cos(th), a * np.sin(th)])
            phi = np.arctan2(A_pt[1], A_pt[0] - O4x)
            tip = np.array([O4x, 0.0]) + Lr * np.array([np.cos(phi), np.sin(phi)])
            dx = O4x - tip[0]
            disc = Lrod**2 - dx**2
            if disc < 0: return None
            return tip[1] - np.sqrt(max(0.0, disc))

        yA_unit = slider_y_for_lengths(theta_A, 1.0, rod_ratio)
        yC_unit = slider_y_for_lengths(theta_C, 1.0, rod_ratio)
        if yA_unit is None or yC_unit is None: return
        unit_drop = yC_unit - yA_unit

        scale = -dropC_m / unit_drop
        L_rocker = scale
        L_rod = rod_ratio * abs(L_rocker)
        yA = slider_y_for_lengths(theta_A, L_rocker, L_rod)
        target_B = -dropB_m

        origin_shift = np.array([-d, -yA])

        scan = np.linspace(theta_A, theta_C, 2001)
        valid_angles, rel_y = [], []
        for deg in scan:
            y = slider_y_for_lengths(deg, L_rocker, L_rod)
            if y is not None:
                valid_angles.append(deg)
                rel_y.append(y - yA)
        valid_angles = np.array(valid_angles)
        rel_y = np.array(rel_y)
        idx = int(np.argmin(np.abs(rel_y - target_B)))
        theta_B = float(valid_angles[idx])

        def crank_pin_distance(theta_deg):
            th = crank_phase + crank_dir * np.radians(theta_deg)
            A_pt = np.array([a * np.cos(th), a * np.sin(th)])
            return float(np.linalg.norm(A_pt - np.array([d, 0.0])))

        slot_arm = max(crank_pin_distance(deg) for deg in np.linspace(0.0, 360.0, 721))
        L_slotted_lever = abs(L_rocker) + slot_arm + max(0.15 * a, 0.006)

        def centre_for_angle(theta_deg):
            return np.array([d, slider_y_for_lengths(theta_deg, L_rocker, L_rod)])

        def rot_for_angle(theta_deg):
            if theta_deg <= theta_B:
                return -45.0 * (theta_deg - theta_A) / max(theta_B - theta_A, 1e-12)
            if theta_deg <= theta_C:
                return -45.0 - 45.0 * (theta_deg - theta_B) / max(theta_C - theta_B, 1e-12)
            return -90.0 * (1.0 - (theta_deg - theta_C) / max(theta_ret, 1e-12))

        def rotate_vec(v, deg):
            c, s_ = np.cos(np.radians(deg)), np.sin(np.radians(deg))
            return np.array([c * v[0] - s_ * v[1], s_ * v[0] + c * v[1]])

        orient_local = np.array([0.75 * R_m, 0.0])
        E_pts = []
        for th_deg in [theta_A, theta_B, theta_C]:
            E_pts.append(centre_for_angle(th_deg) + rotate_vec(orient_local, rot_for_angle(th_deg)))
        p1, p2, p3 = E_pts
        circ_A = np.array([[2.0 * (p2[0] - p1[0]), 2.0 * (p2[1] - p1[1])], [2.0 * (p3[0] - p1[0]), 2.0 * (p3[1] - p1[1])]])
        circ_b = np.array([np.dot(p2, p2) - np.dot(p1, p1), np.dot(p3, p3) - np.dot(p1, p1)])
        if abs(np.linalg.det(circ_A)) < 1e-12:
            orient_ground = np.array([d - R_m, yA])
        else:
            orient_ground = np.linalg.solve(circ_A, circ_b)

        orient_len = float(np.linalg.norm(p1 - orient_ground))
        orient_ground += origin_shift

        omega2 = (rpm * 2.0 * np.pi) / 60.0
        rho = 2700.0
        mu = rho * (cs_m * cs_m)
        m_crank  = mu * a
        m_rocker = mu * L_slotted_lever
        m_rod    = mu * L_rod

        I_crank_cg  = (1.0/12.0) * m_crank  * a**2
        I_rocker_cg = (1.0/12.0) * m_rocker * L_slotted_lever**2
        I_rod_cg    = (1.0/12.0) * m_rod    * L_rod**2
        m_pie, cg_pie_x, cg_pie_y, I_pie_O = self._partial_circle_props(R_m, cs_m, rho)

        self.syn = {
            'R_m': R_m, 'dropB_m': dropB_m, 'dropC_m': dropC_m, 'rpm': rpm, 'cs_m': cs_m,
            'a': a, 'd': d, 'L_rocker': L_rocker, 'L_slot_arm': slot_arm, 'L_slot_total': L_slotted_lever,
            'L_rod': L_rod, 'rod_ratio': rod_ratio, 'alpha': alpha, 'theta_fwd': theta_fwd, 'theta_ret': theta_ret, 'QR': QR,
            'omega2': omega2, 'crank_phase': crank_phase, 'crank_dir': crank_dir,
            'theta_A': theta_A, 'theta_B': theta_B, 'theta_C': theta_C,
            'rho': rho, 'mu': mu, 'm_crank': m_crank, 'm_rocker': m_rocker, 'm_rod': m_rod, 'm_pie': m_pie,
            'I_crank_cg': I_crank_cg, 'I_rocker_cg': I_rocker_cg, 'I_rod_cg': I_rod_cg, 'I_pie_O': I_pie_O,
            'cg_pie_x': cg_pie_x, 'cg_pie_y': cg_pie_y, 'orient_local': orient_local,
            'orient_ground': orient_ground, 'orient_len': orient_len,
            'origin_shift': origin_shift
        }

        all_x, all_y = [], []
        for deg in range(0, 360, 5):
            st = self.calc_whitworth(np.radians(deg))
            if st:
                pts_mm = [p * 1000.0 for p in [st[0], st[1], st[2], st[3], st[4]]]
                _, slot_far = self._slot_endpoints(pts_mm[2], pts_mm[1], pts_mm[3], scale=1000.0)
                pts_mm.append(slot_far)
                for p in pts_mm:
                    all_x.append(p[0]); all_y.append(p[1])
                R_mm = R_m * 1000.0
                all_x.extend([pts_mm[4][0] - R_mm, pts_mm[4][0] + R_mm])
                all_y.extend([pts_mm[4][1] - R_mm, pts_mm[4][1] + R_mm])

        x_span = max(all_x) - min(all_x)
        y_span = max(all_y) - min(all_y)
        pad_x  = x_span * 0.15
        pad_y  = y_span * 0.15
        self.syn['anim_xlim'] = (min(all_x) - pad_x, max(all_x) + pad_x)
        self.syn['anim_ylim'] = (min(all_y) - pad_y, max(all_y) + pad_y)

        self.card_qr.set_value(f"{QR:.3f} : 1")
        self.card_fwd.set_value(f"{theta_fwd:.0f}°")
        self.card_ret.set_value(f"{theta_ret:.0f}°")
        self.card_rpm.set_value(f"{rpm:.0f} RPM")
        self.card_rod.set_value(f"{L_rod*1e3:.1f} mm")

        self._draw_synthesis_diagram()
        self._update_synthesis_notes()
        self._refresh_hud_static()

        # ── Auto-compute all downstream tabs ──
        self.kin_data = self.solve_full_cycle()
        self._recompute_dynamics()
        self._abc_drawn = True
        
        self._update_abc_tab_labels()
        self._redraw_abc()
        
        if self.kin_data:
            self._draw_kin_for_index(self.kin_subtabs.currentIndex())
        if self.dyn_data:
            self._draw_dyn_for_index(self.dyn_subtabs.currentIndex())

        self.set_status("Dynamics OK")

    def _update_synthesis_notes(self):
        """Calculates and renders the required synthesis info & pie object dynamics to HTML."""
        if self.syn is None: return
        s = self.syn
        
        # Compute I_G via parallel axis theorem (I_O = I_G + m*d^2)
        I_O_val = s['I_pie_O']
        d_sq = s['cg_pie_x']**2 + s['cg_pie_y']**2
        I_G_val = I_O_val - (s['m_pie'] * d_sq)

        html = f"""
        <div style="color:{DIM}; font-family:'Consolas','Courier New',monospace; font-size:13px; line-height:1.9;">
            <p style="color:{ACCENT}; font-size:16px; font-weight:bold; letter-spacing:2px; margin-bottom:4px;">WHITWORTH QUICK-RETURN</p>
            <p style="color:{MUTED}; font-size:10px; letter-spacing:2px; margin:0 0 12px;">THREE-POSITION SYNTHESIS</p>

            <p style="color:{ACCENT}; font-size:10px; letter-spacing:2px; font-weight:bold; margin-bottom:6px;">── STROKE ANALYSIS ──</p>
            <table style="border-collapse:collapse; width:100%; margin-bottom:14px;">
                <tr><td style="padding:3px 0; color:{MUTED};">Forward stroke</td><td style="color:{SUCCESS}; font-weight:bold; text-align:right;">{s['theta_fwd']:.1f}°</td></tr>
                <tr><td style="padding:3px 0; color:{MUTED};">Return stroke</td><td style="color:{WARN}; font-weight:bold; text-align:right;">{s['theta_ret']:.1f}°</td></tr>
                <tr><td style="padding:3px 0; color:{MUTED};">QR Ratio</td><td style="color:{ACCENT}; font-weight:bold; text-align:right;">{s['QR']:.4f} : 1</td></tr>
            </table>

            <p style="color:{ACCENT}; font-size:10px; letter-spacing:2px; font-weight:bold; margin-bottom:6px;">── LINK LENGTHS ──</p>
            <table style="border-collapse:collapse; width:100%; margin-bottom:14px;">
                <tr><td style="color:{MUTED}; padding:3px 0;">Crank (a)</td><td style="color:{WARN}; font-weight:bold; text-align:right;">{s['a']*1e3:.2f} mm</td></tr>
                <tr><td style="color:{MUTED}; padding:3px 0;">Ground (d)</td><td style="color:{WARN}; font-weight:bold; text-align:right;">{s['d']*1e3:.2f} mm</td></tr>
                <tr><td style="color:{MUTED}; padding:3px 0;">Rocker</td><td style="color:{WARN}; font-weight:bold; text-align:right;">{abs(s['L_rocker'])*1e3:.2f} mm</td></tr>
                <tr><td style="color:{MUTED}; padding:3px 0;">Conn Rod</td><td style="color:{WARN}; font-weight:bold; text-align:right;">{s['L_rod']*1e3:.2f} mm</td></tr>
            </table>

            <p style="color:{ACCENT}; font-size:10px; letter-spacing:2px; font-weight:bold; margin-bottom:6px;">── PIE OBJECT (3/4 DISC) ──</p>
            <table style="border-collapse:collapse; width:100%; margin-bottom:14px;">
                <tr><td style="color:{MUTED}; padding:3px 0;">Radius R</td><td style="color:{TEXT}; font-weight:bold; text-align:right;">{s['R_m']*1000.0:.1f} mm</td></tr>
                <tr><td style="color:{MUTED}; padding:3px 0;">Mass M'</td><td style="color:{TEXT}; font-weight:bold; text-align:right;">{s['m_pie']*1000.0:.2f} g</td></tr>
                <tr><td style="color:{MUTED}; padding:3px 0;">CG (x̄ = ȳ)</td><td style="color:{TEXT}; font-weight:bold; text-align:right;">{s['cg_pie_x']*1000.0:.2f} mm</td></tr>
                <tr><td style="color:{MUTED}; padding:3px 0;">I_O = (3/8)MR²</td><td style="color:{TEXT}; font-weight:bold; text-align:right;">{I_O_val*1e6:.4f} ×10⁻⁶ kg·m²</td></tr>
                <tr><td style="color:{MUTED}; padding:3px 0;">I_G (about CG)</td><td style="color:{TEXT}; font-weight:bold; text-align:right;">{I_G_val*1e6:.4f} ×10⁻⁶ kg·m²</td></tr>
            </table>
            <p style="color:{MUTED}; font-size:9px; letter-spacing:0.5px;">Material: Aluminium ρ = 2700 kg/m³</p>
        </div>
        """
        self.txt_notes.setHtml(html)

    def _refresh_hud_static(self):
        """Updates the static maximum stroke length labels based on user input RPM."""
        if self.syn is None: return
        s = self.syn
        cycle_time = 60.0 / s['rpm']
        t_fwd = (s['theta_fwd'] / 360.0) * cycle_time
        t_ret = (s['theta_ret'] / 360.0) * cycle_time
        
        self.lbl_fwd_time.setText(f"Forward Stroke:  {t_fwd:.3f} s")
        self.lbl_ret_time.setText(f"Return Stroke:  {t_ret:.3f} s")
        self.lbl_cycle_time.setText(f"Cycle Time:  {cycle_time:.3f} s")

    def _update_abc_tab_labels(self):
        s = self.syn
        self.abc_subtabs.setTabText(0, f"🟢  Pos A ({s['theta_A']:.0f}°)")
        self.abc_subtabs.setTabText(1, f"🟠  Pos B ({s['theta_B']:.0f}°)")
        self.abc_subtabs.setTabText(2, f"🔴  Pos C ({s['theta_C']:.0f}°)")

    def calc_whitworth(self, th2_rad):
        if self.syn is None: return None
        s = self.syn
        O2 = np.array([0.0, 0.0])
        O4 = np.array([s['d'], 0.0])
        th_phys = s['crank_phase'] + s['crank_dir'] * th2_rad
        A_pt = np.array([s['a'] * np.cos(th_phys), s['a'] * np.sin(th_phys)])
        th4 = np.arctan2(A_pt[1] - O4[1], A_pt[0] - O4[0])
        tip = O4 + s['L_rocker'] * np.array([np.cos(th4), np.sin(th4)])
        slider_x = O4[0]
        disc = s['L_rod']**2 - (slider_x - tip[0])**2
        if disc < 0: return None
        slider_y = tip[1] - np.sqrt(max(0.0, disc))
        slider_pt = np.array([slider_x, slider_y])
        th3 = np.arctan2(slider_pt[1] - tip[1], slider_pt[0] - tip[0])

        shift = s['origin_shift']
        O2 += shift; O4 += shift; A_pt += shift; tip += shift; slider_pt += shift

        return O2, A_pt, O4, tip, slider_pt, th3, th4

    def object_rotation_deg(self, th2_deg):
        if self.syn is None: return 0.0
        s = self.syn
        th = th2_deg % 360.0
        if th <= s['theta_B']:
            return -45.0 * (th - s['theta_A']) / max(s['theta_B'] - s['theta_A'], 1e-12)
        if th <= s['theta_C']:
            return -45.0 - 45.0 * (th - s['theta_B']) / max(s['theta_C'] - s['theta_B'], 1e-12)
        return -90.0 * (1.0 - (th - s['theta_C']) / max(s['theta_ret'], 1e-12))

    def object_control_point(self, th2_deg):
        if self.syn is None: return None
        s = self.syn
        st = self.calc_whitworth(np.radians(th2_deg))
        if st is None: return None
        centre = st[4]
        phi = self.object_rotation_deg(th2_deg)
        c, sn = np.cos(np.radians(phi)), np.sin(np.radians(phi))
        local = s['orient_local']
        E = centre + np.array([c * local[0] - sn * local[1], sn * local[0] + c * local[1]])
        return s['orient_ground'], E

    def calc_kinematics(self, th2_rad):
        if self.syn is None: return None
        s = self.syn
        a, omega2 = s['a'], s['omega2']

        state = self.calc_whitworth(th2_rad)
        if state is None: return None
        O2, A_pt, O4, tip, slider_pt, th3, th4 = state

        h = 1e-4
        state_p = self.calc_whitworth(th2_rad + h)
        state_m = self.calc_whitworth(th2_rad - h)
        if state_p is None or state_m is None: return None

        _, _, _, tip_p, slider_p, th3_p, th4_p = state_p
        _, _, _, tip_m, slider_m, th3_m, th4_m = state_m

        def angle_delta(a2, a1):
            return np.arctan2(np.sin(a2 - a1), np.cos(a2 - a1))

        crank_dir = s.get('crank_dir', 1.0)
        th_phys = s.get('crank_phase', 0.0) + crank_dir * th2_rad
        VA = np.array([-a * omega2 * crank_dir * np.sin(th_phys), a * omega2 * crank_dir * np.cos(th_phys)])
        AA = np.array([-a * omega2**2 * np.cos(th_phys), -a * omega2**2 * np.sin(th_phys)])

        dtip_dth  = (tip_p - tip_m) / (2.0 * h)
        d2tip_dth2 = (tip_p - 2.0 * tip + tip_m) / (h**2)
        V_tip = dtip_dth * omega2
        A_tip = d2tip_dth2 * omega2**2

        dy_dth   = (slider_p[1] - slider_m[1]) / (2.0 * h)
        d2y_dth2 = (slider_p[1] - 2.0 * slider_pt[1] + slider_m[1]) / (h**2)
        Vslider_y = dy_dth * omega2
        Aslider_y = d2y_dth2 * omega2**2

        dth4_dth   = angle_delta(th4_p, th4_m) / (2.0 * h)
        d2th4_dth2 = (angle_delta(th4_p, th4) - angle_delta(th4, th4_m)) / (h**2)
        omega4 = dth4_dth * omega2
        alpha4 = d2th4_dth2 * omega2**2

        dth3_dth   = angle_delta(th3_p, th3_m) / (2.0 * h)
        d2th3_dth2 = (angle_delta(th3_p, th3) - angle_delta(th3, th3_m)) / (h**2)
        omega3 = dth3_dth * omega2
        alpha3 = d2th3_dth2 * omega2**2

        th_deg = np.degrees(th2_rad)
        phi   = np.radians(self.object_rotation_deg(th_deg))
        phi_p = np.radians(self.object_rotation_deg(th_deg + np.degrees(h)))
        phi_m = np.radians(self.object_rotation_deg(th_deg - np.degrees(h)))
        dphi_dth   = angle_delta(phi_p, phi_m) / (2.0 * h)
        d2phi_dth2 = (angle_delta(phi_p, phi) - angle_delta(phi, phi_m)) / (h**2)
        omega_obj = dphi_dth * omega2
        alpha_obj = d2phi_dth2 * omega2**2

        return {
            'pos': {'O2': O2, 'A': A_pt, 'O4': O4, 'tip': tip, 'slider': slider_pt, 'th3': th3, 'th4': th4},
            'vel': {'VA': VA, 'V_tip': V_tip, 'Vslider_y': Vslider_y, 'omega4': omega4, 'omega3': omega3, 'omega_obj': omega_obj},
            'acc': {'AA': AA, 'A_tip': A_tip, 'Aslider_y': Aslider_y, 'alpha4': alpha4, 'alpha3': alpha3, 'alpha_obj': alpha_obj},
        }

    def solve_full_cycle(self):
        if self.syn is None: return None
        angles, slider_y, Vsl, Asl = [], [], [], []
        omega4_arr, alpha4_arr, VA_mag_arr, Vtip_mag_arr = [], [], [], []

        for deg in range(360):
            k = self.calc_kinematics(np.radians(deg))
            if k is None: continue
            angles.append(deg)
            slider_y.append(k['pos']['slider'][1])
            Vsl.append(k['vel']['Vslider_y'])
            Asl.append(k['acc']['Aslider_y'])
            omega4_arr.append(k['vel']['omega4'])
            alpha4_arr.append(k['acc']['alpha4'])
            VA_mag_arr.append(np.hypot(*k['vel']['VA']))
            Vtip_mag_arr.append(np.hypot(*k['vel']['V_tip']))

        return {
            'angles': np.array(angles), 'slider_y': np.array(slider_y),
            'Vslider_y': np.array(Vsl), 'Aslider_y': np.array(Asl),
            'omega4': np.array(omega4_arr), 'alpha4': np.array(alpha4_arr),
            'VA_mag': np.array(VA_mag_arr), 'Vtip_mag': np.array(Vtip_mag_arr),
        }

    # =========================================================================
    # HELPER DRAWING 
    # =========================================================================
    def _draw_modern_joint(self, ax, x, y, color, size_scale=1.0, is_square=False):
        ms = 8 * size_scale
        if is_square:
            ax.plot(x, y, 's', ms=ms*1.2, mfc=PANEL, mec=color, mew=2.5, zorder=10)
            ax.plot(x, y, 's', ms=ms*0.5, color=color, zorder=11)
        else:
            ax.plot(x, y, 'o', ms=ms,     mfc=PANEL, mec=color, mew=2.5, zorder=10)
            ax.plot(x, y, 'o', ms=ms*0.4, color=color, zorder=11)

    def _draw_ground_pin(self, ax, x, y, sz):
        tri_x = [x - sz, x + sz, x, x - sz]
        tri_y = [y - sz, y - sz, y + sz * 0.6, y - sz]
        ax.fill(tri_x, tri_y, color=MUTED, zorder=5, alpha=0.6)
        ax.plot([x - sz * 1.6, x + sz * 1.6], [y - sz, y - sz], color=MUTED, lw=2, zorder=5)

    def _slot_endpoints(self, O4_scaled, A_pt_scaled, tip_scaled, scale=1000.0):
        s = self.syn
        u = A_pt_scaled - O4_scaled
        n = np.linalg.norm(u)
        u_dir = u / n if n > 1e-12 else np.array([1.0, 0.0])
        arm_scaled = (s['L_slot_arm'] + max(0.15 * s['a'], 0.006)) * scale
        slot_far = O4_scaled + u_dir * arm_scaled
        return tip_scaled, slot_far

    def _draw_slotted_lever(self, ax, O4_mm, A_pt_mm, tip_mm, lw=12.0, label=None):
        slot_a, slot_b = self._slot_endpoints(O4_mm, A_pt_mm, tip_mm, scale=1000.0)
        ax.plot([slot_b[0], tip_mm[0]], [slot_b[1], tip_mm[1]], '-',
                color=WARN, lw=lw, alpha=0.85, solid_capstyle='round', label=label, zorder=2)
        ax.plot([slot_b[0], O4_mm[0]], [slot_b[1], O4_mm[1]], '-',
                color=BG,   lw=max(lw*0.3, 2.0), solid_capstyle='round', zorder=3)
        ax.plot(A_pt_mm[0], A_pt_mm[1], 's', color=ACCENT, ms=max(lw*0.7, 6), zorder=5)
        self._draw_modern_joint(ax, tip_mm[0], tip_mm[1], WARN)

    def _draw_pie_object(self, ax, cx, cy, R, angle_deg, color=ACCENT2, alpha=0.75):
        theta1 = 90.0 + angle_deg
        theta2 = 360.0 + angle_deg
        wedge = mpatches.Wedge((cx, cy), R, theta1, theta2,
                               facecolor=color, edgecolor=TEXT,
                               linewidth=1.5, alpha=alpha, zorder=6)
        ax.add_patch(wedge)
        ax.plot(cx, cy, 'o', color=TEXT, ms=5, zorder=7)

    def _draw_orientation_link(self, ax, th2_deg, scale=1000.0):
        ctrl = self.object_control_point(th2_deg)
        if ctrl is None: return
        G, E = ctrl
        G_mm, E_mm = G * scale, E * scale
        ax.plot([G_mm[0], E_mm[0]], [G_mm[1], E_mm[1]], '-o',
                color=ACCENT2, lw=3.0, ms=6, zorder=6, label="Orientation link")
        ax.plot(G_mm[0], G_mm[1], '^', color=ACCENT2, ms=8, zorder=7,
                markeredgecolor=TEXT, markeredgewidth=0.9)

    def add_vector(self, ax, start, end, color, label, show_mag=True, is_pos=False):
        sx, sy = start; ex, ey = end
        mag = float(np.hypot(ex - sx, ey - sy))
        lbl_str = f"{label} |{mag:.3f}|" if show_mag and not is_pos else label
        ax.plot([], [], color=color, lw=2, label=lbl_str)
        ax.annotate('', xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2.5, mutation_scale=18))
        if mag > 1e-9:
            vx, vy = ex - sx, ey - sy
            scl = max(mag, 1e-9)
            mx, my = sx + vx*0.5, sy + vy*0.5
            dx = 0.04 * vx / scl - 0.03 * vy / scl
            dy = 0.04 * vy / scl + 0.03 * vx / scl
            box_props = dict(boxstyle='round,pad=0.2', facecolor=PANEL, edgecolor=color, alpha=0.85)
            ax.text(mx + dx, my + dy, label, fontsize=9, color=TEXT,
                    ha='center', va='center', zorder=15, bbox=box_props)

    def _auto_lim(self, ax, pts, margin=0.005):
        """Auto-limit with generous padding so no vectors are clipped."""
        xs, ys = pts[:, 0], pts[:, 1]
        valid = (np.abs(xs) > 1e-12) | (np.abs(ys) > 1e-12)
        if valid.any():
            xs_v, ys_v = xs[valid], ys[valid]
        else:
            xs_v, ys_v = xs, ys
        xc = (xs_v.min() + xs_v.max()) / 2
        yc = (ys_v.min() + ys_v.max()) / 2
        span = max(xs_v.max() - xs_v.min(), ys_v.max() - ys_v.min()) / 2
        span = max(span * 1.30, margin)
        ax.set_xlim(xc - span, xc + span)
        ax.set_ylim(yc - span, yc + span)

    # =========================================================================
    # DRAWING ACTIONS
    # =========================================================================
    def _draw_synthesis_diagram(self):
        if self.syn is None: return
        s = self.syn
        self.fig_syn.clear()

        from matplotlib.gridspec import GridSpec
        gs = GridSpec(1, 2, figure=self.fig_syn, width_ratios=[50, 50],
                      left=0.06, right=0.97, top=0.88, bottom=0.10, wspace=0.35)

        ax_pie   = self.fig_syn.add_subplot(gs[0])
        ax_polar = self.fig_syn.add_subplot(gs[1], projection='polar')

        pos_colors = [SUCCESS, WARN, DANGER]
        pos_labels = ['A', 'B', 'C']
        pos_angles = [s['theta_A'], s['theta_B'], s['theta_C']]

        # ── Left: Pie object at A, B, C ──
        ax_pie.set_aspect('equal')
        ax_pie.grid(True, alpha=0.3, ls='--', lw=0.6)
        ax_pie.set_xlabel("x (mm)", fontsize=9, color=MUTED)
        ax_pie.set_ylabel("y (mm)", fontsize=9, color=MUTED)
        ax_pie.tick_params(colors=MUTED, labelsize=8)

        gap_x = 3.0 * s['R_m'] * 1000.0
        all_slider_y = []
        for i, (th_deg, col, lbl) in enumerate(zip(pos_angles, pos_colors, pos_labels)):
            state = self.calc_whitworth(np.radians(th_deg))
            if state is None: continue
            _, _, _, _, slider_pt, _, _ = state
            slider_y_mm = slider_pt[1] * 1000.0
            all_slider_y.append(slider_y_mm)
            cx, cy = i * gap_x, slider_y_mm
            pie_rot = self.object_rotation_deg(th_deg)
            self._draw_pie_object(ax_pie, cx, cy, s['R_m']*1000.0, pie_rot, color=col, alpha=0.85)
            ax_pie.text(cx, cy - s['R_m'] * 1350.0, f"Pos {lbl}",
                        ha='center', fontsize=11, color=col, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=PANEL, edgecolor=col, alpha=0.9))
            ax_pie.axhline(cy, color=col, lw=1.0, ls='--', alpha=0.35)
            # drop annotation
            if i > 0:
                drop_mm = abs(slider_y_mm - all_slider_y[0])
                ax_pie.annotate('', xy=(cx, cy), xytext=(cx, all_slider_y[0]),
                                arrowprops=dict(arrowstyle='<->', color=col, lw=1.2))
                ax_pie.text(cx + s['R_m']*800, (cy + all_slider_y[0])/2,
                            f"Δ{drop_mm:.1f} mm", color=col, fontsize=8, va='center')

        R_mm = s['R_m'] * 1000.0
        ax_pie.set_xlim(-R_mm * 1.5, gap_x * 2 + R_mm * 2.2)
        if all_slider_y:
            ax_pie.set_ylim(min(all_slider_y) - R_mm * 2.0, max(all_slider_y) + R_mm * 1.6)
        ax_pie.set_title("Pie Object — Three Prescribed Positions", fontsize=11, color=TEXT, pad=10, fontweight='bold')

        # ── Right: Polar stroke diagram ──
        ax_polar.set_facecolor(BG)
        fwd_rad = np.radians(s['theta_fwd'])
        ret_rad = np.radians(s['theta_ret'])

        # Forward arc (cyan)
        theta_fwd_arr = np.linspace(0, fwd_rad, 300)
        ax_polar.fill_between(theta_fwd_arr, 0, 1, alpha=0.18, color=ACCENT)
        ax_polar.plot(theta_fwd_arr, np.ones_like(theta_fwd_arr), color=ACCENT, lw=2.5)

        # Return arc (red)
        theta_ret_arr = np.linspace(fwd_rad, 2*np.pi, 300)
        ax_polar.fill_between(theta_ret_arr, 0, 1, alpha=0.18, color=DANGER)
        ax_polar.plot(theta_ret_arr, np.ones_like(theta_ret_arr), color=DANGER, lw=2.5)

        # Position markers
        for th_deg, col, lbl in zip(pos_angles, pos_colors, pos_labels):
            th_r = np.radians(th_deg)
            ax_polar.plot(th_r, 1.0, 'o', color=col, ms=10, zorder=5)
            ax_polar.text(th_r, 1.18, lbl, color=col, fontsize=11, fontweight='bold', ha='center')

        ax_polar.set_yticklabels([])
        ax_polar.set_xticks(np.radians([0, 60, 120, 180, 240, 300]))
        ax_polar.set_xticklabels(['0°','60°','120°','180°','240°','300°'], color=MUTED, fontsize=8)
        ax_polar.tick_params(colors=MUTED)
        ax_polar.spines['polar'].set_color(BORDER)
        ax_polar.grid(color=BORDER, alpha=0.5, lw=0.6)

        # Legend patches 
        fwd_patch = mpatches.Patch(color=ACCENT, alpha=0.5, label=f"Forward  {s['theta_fwd']:.0f}°")
        ret_patch = mpatches.Patch(color=DANGER, alpha=0.5, label=f"Return  {s['theta_ret']:.0f}°")
        ax_polar.legend(handles=[fwd_patch, ret_patch], loc='lower center',
                        bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=9,
                        facecolor=PANEL, edgecolor=BORDER)
        ax_polar.set_title(f"Stroke Diagram  ·  QR = {s['QR']:.3f}:1",
                           fontsize=11, color=TEXT, pad=16, fontweight='bold')

        self.canvas_syn.draw_idle()

    def draw_mechanism(self, th2_rad):
        if self.syn is None: return
        state = self.calc_whitworth(th2_rad)
        if state is None: return

        O2, A_pt, O4, tip, slider_pt, _, th4 = state
        O2, A_pt, O4, tip, slider_pt = (x*1000.0 for x in (O2, A_pt, O4, tip, slider_pt))

        ax = self.ax_anim
        ax.clear()
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, ls='--', lw=0.5)
        ax.set_xlim(*self.syn['anim_xlim'])
        ax.set_ylim(*self.syn['anim_ylim'])

        ax.plot([O2[0], O4[0]], [O2[1], O4[1]], '-', color=BORDER, lw=10, solid_capstyle='round', zorder=1)
        self._draw_slotted_lever(ax, O4, A_pt, tip, lw=14.0)
        ax.plot([O2[0], A_pt[0]], [O2[1], A_pt[1]], '-', color=ACCENT, lw=6, zorder=4, solid_capstyle='round')
        ax.plot(A_pt[0], A_pt[1], 's', color=ACCENT, ms=12, zorder=5)
        ax.plot([tip[0], slider_pt[0]], [tip[1], slider_pt[1]], '-', color=SUCCESS, lw=5, zorder=4, solid_capstyle='round')
        ax.axvline(O4[0], color=BORDER, lw=1.5, ls='-', zorder=0)
        self._draw_modern_joint(ax, O2[0], O2[1], TEXT, 1.5)
        self._draw_modern_joint(ax, O4[0], O4[1], TEXT, 1.5)
        self._draw_modern_joint(ax, tip[0], tip[1], WARN)
        ax.plot(slider_pt[0], slider_pt[1], 's', mfc=PANEL, mec=SUCCESS, mew=2, ms=8, zorder=8)

        pie_rot = self.object_rotation_deg(np.degrees(th2_rad))
        self._draw_pie_object(ax, slider_pt[0], slider_pt[1], self.syn['R_m']*1000.0, pie_rot, color=ACCENT2, alpha=0.85)
        self._draw_orientation_link(ax, np.degrees(th2_rad), scale=1000.0)

        lbl_kw = dict(color=TEXT, fontsize=10, fontweight='bold', zorder=15)
        ax.text(O2[0]-25, O2[1]-25, "O₂", **lbl_kw)
        ax.text(O4[0]-25, O4[1]-25, "O₄", **lbl_kw)
        ax.text(A_pt[0]+15, A_pt[1]+15, "A", **lbl_kw)
        ax.text(tip[0]+15, tip[1]+15, "tip", **lbl_kw)
        ax.text(slider_pt[0]+35, slider_pt[1]+35, "slider", **lbl_kw)

        for i, (y_line, l_col, label_str) in enumerate(zip(
            [0, -self.syn['dropB_m']*1000, -self.syn['dropC_m']*1000],
            [SUCCESS, WARN, DANGER],
            ["A", "B", "C"])):
            ax.axhline(y_line, color=l_col, lw=1.5, ls='--', alpha=0.4, zorder=0)
            x_pos = self.syn['anim_xlim'][0] + (self.syn['anim_xlim'][1] - self.syn['anim_xlim'][0]) * 0.02
            ax.text(x_pos, y_line, f"{i+1} (Pos {label_str})", color=l_col, fontsize=10, fontweight='bold',
                    va='bottom', bbox=dict(boxstyle='round,pad=0.2', facecolor=BG, edgecolor='none', alpha=0.7))

        ax.set_xlabel("x (mm)", fontsize=9, color=MUTED)
        ax.set_ylabel("y (mm)", fontsize=9, color=MUTED)
        ax.set_title(f"Live Animation  ·  θ₂ = {np.degrees(th2_rad)%360:.1f}°", color=TEXT, fontweight='bold', fontsize=12)

        # Calculates live physical time for active strokes that perfectly reset to 0 at the start of a phase.
        cycle_time = 60.0 / self.syn['rpm']
        mod_angle = np.degrees(th2_rad) % 360.0
        theta_fwd = self.syn['theta_fwd']
        is_ret = mod_angle > theta_fwd
        
        if not is_ret:
            live_fwd = (mod_angle / 360.0) * cycle_time
            live_ret = 0.0
        else:
            live_fwd = 0.0
            live_ret = ((mod_angle - theta_fwd) / 360.0) * cycle_time

        # Update HUD phase label
        hud_color = DANGER if is_ret else SUCCESS
        hud_text  = "RETURN" if is_ret else "FORWARD"
        self.lbl_phase.setText(f"PHASE:  {hud_text}")
        self.lbl_phase.setStyleSheet(f"color:{hud_color}; font-size:13px; font-weight:bold; font-family:'Consolas'; letter-spacing:1px;")

        # Draw "as before" Live counters directly on the Plot canvas
        ax.text(0.02, 0.95, f"PHASE: {hud_text}", transform=ax.transAxes, color=hud_color, fontsize=12, fontweight='bold', bbox=dict(facecolor=PANEL, edgecolor=hud_color, alpha=0.9))
        ax.text(0.02, 0.88, f"Forward Time: {live_fwd:.3f} s", transform=ax.transAxes, color=SUCCESS, fontsize=10, fontweight='bold')
        ax.text(0.02, 0.83, f"Return Time:  {live_ret:.3f} s", transform=ax.transAxes, color=DANGER, fontsize=10, fontweight='bold')

        self.angle_label.setText(f"θ₂ = {np.degrees(th2_rad)%360:.1f}°")
        self.canvas_anim.draw_idle()

    def update_animation(self):
        """Timer callback — advances angle based on step."""
        if self.syn:
            self.current_angle += self.angle_step
            self.draw_mechanism(np.radians(self.current_angle))

    def btn_animate_clicked(self):
        if self.syn is None: return
        self.current_angle = 0.0
        self._is_paused    = False
        self.btn_pause.setText("⏸  PAUSE")
        self.timer.start(16)

    def toggle_presentation(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def jump_to_angle(self, pos):
        if self.syn is None: return
        self._stop_animation()
        if pos == 'A': self.current_angle = self.syn['theta_A']
        elif pos == 'B': self.current_angle = self.syn['theta_B']
        elif pos == 'C': self.current_angle = self.syn['theta_C']
        self.draw_mechanism(np.radians(self.current_angle))

    # =========================================================================
    # KINEMATICS A·B·C
    # =========================================================================
    def _abc_tab_changed(self, _index):
        if self._abc_drawn:
            self._redraw_abc()

    def _abc_vec_tab_changed(self, _index):
        if self._abc_drawn:
            self._redraw_abc()

    def _redraw_abc(self):
        if self.syn is None: return
        s = self.syn
        pos_angles = [s['theta_A'], s['theta_B'], s['theta_C']]
        pos_names  = ['A', 'B', 'C']
        pos_colors = [SUCCESS, WARN, DANGER]

        pos_idx = self.abc_subtabs.currentIndex()
        vec_idx = self.abc_vec_subtabs.currentIndex()

        th_deg = pos_angles[pos_idx]
        name   = pos_names[pos_idx]
        color  = pos_colors[pos_idx]

        k = self.calc_kinematics(np.radians(th_deg))
        if k is None: return

        self.fig_abc.clear()
        ax = self.fig_abc.add_subplot(111)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, ls='--', lw=0.5)
        ax.tick_params(colors=MUTED, labelsize=9)

        if vec_idx == 0:
            self._draw_position_panel(ax, k, name, color, th_deg)
        elif vec_idx == 1:
            self._draw_velocity_panel(ax, k, name, color, th_deg)
        else:
            self._draw_acceleration_panel(ax, k, name, color, th_deg)

        self.fig_abc.tight_layout(pad=1.5)
        self.canvas_abc.draw()

    # ── individual panel drawers ──────────────────────────────────────────────
    def _draw_position_panel(self, ax, k, name, color, th_deg):
        pos = k['pos']
        O2, A_pt, O4 = pos['O2']*1000.0, pos['A']*1000.0, pos['O4']*1000.0
        tip, slider  = pos['tip']*1000.0, pos['slider']*1000.0

        def draw_link_vector(p1, p2, col, lw=2, style='-'):
            ax.annotate('', xy=(p2[0], p2[1]), xytext=(p1[0], p1[1]),
                        arrowprops=dict(arrowstyle='->', color=col, lw=lw, linestyle=style))

        draw_link_vector(O2, A_pt, ACCENT, lw=3)
        draw_link_vector(O4, tip, WARN, lw=3)
        draw_link_vector(tip, slider, SUCCESS, lw=3)
        draw_link_vector(O2, O4, MUTED, lw=1.5, style='dashed')
        ax.axvline(O4[0], color=MUTED, lw=1.5, linestyle='--')

        fixed_color  = SUCCESS
        moving_color = ACCENT

        for pt, sym, col, ha in [
            (O2, 'O₂', fixed_color,  'right'),
            (O4, 'O₄', fixed_color,  'left'),
            (A_pt, 'A', moving_color, 'left'),
            (tip, 'T', moving_color,  'left'),
            (slider, 'P', moving_color, 'left'),
        ]:
            mk = 's' if sym in ('A',) else 'o'
            ax.plot(pt[0], pt[1], mk, ms=6, mfc=PANEL, mec=col, mew=2, zorder=10)
            off = (-12, -10) if ha == 'right' else (10, 8)
            ax.text(pt[0]+off[0], pt[1]+off[1], sym, color=col, fontsize=8, ha=ha,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor=BG, edgecolor=MUTED))

        ctrl = self.object_control_point(th_deg)
        if ctrl is not None:
            G, E = ctrl
            G_mm, E_mm = G * 1000.0, E * 1000.0
            draw_link_vector(G_mm, E_mm, ACCENT2, lw=2.5)
            draw_link_vector(A_pt, O4, DANGER, lw=1.5, style='dashed')
            draw_link_vector(slider, O4, DANGER, lw=1.5, style='dashed')
            draw_link_vector(E_mm, slider, ACCENT2, lw=2.5)
            draw_link_vector(slider, G_mm, DANGER, lw=1.5, style='dashed')
            for pt, sym, col in [(G_mm, 'O_g', fixed_color), (E_mm, 'E', moving_color)]:
                ax.plot(pt[0], pt[1], 'o', ms=6, mfc=PANEL, mec=col, mew=2.5, zorder=10)
                ax.text(pt[0]+10, pt[1]+8, sym, color=col, fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor=BG, edgecolor=MUTED))

        dropB_mm = self.syn['dropB_m'] * 1000.0
        dropC_mm = self.syn['dropC_m'] * 1000.0
        ax.axhline(0,          color=SUCCESS, ls='--', lw=1.5, alpha=0.7, label='A (0 mm)')
        ax.axhline(-dropB_mm,  color=WARN,    ls='--', lw=1.5, alpha=0.7, label=f'B ({-dropB_mm:.1f} mm)')
        ax.axhline(-dropC_mm,  color=DANGER,  ls='--', lw=1.5, alpha=0.7, label=f'C ({-dropC_mm:.1f} mm)')
        ax.legend(loc='upper right', fontsize=8)

        ax.set_title(f"Position Vectors — {name}  (θ = {th_deg:.1f}°)", fontsize=13, color=color, pad=10)
        ax.set_xlabel("x (mm)", fontsize=10, color=MUTED)
        ax.set_ylabel("y (mm)", fontsize=10, color=MUTED)
        self._auto_lim(ax, np.array([O2, A_pt, O4, tip, slider]), margin=self.syn['a']*1000.0)
        
        # Position Vector Legend Text Box
        pos_legend = (
            "O₂: Crank Ground\n"
            "O₄: Rocker Ground\n"
            "A: Crank Pin\n"
            "T: Slotted Lever Tip\n"
            "P: Slider (Pie Object)\n"
            "E: Orientation Link"
        )
        ax.text(0.02, 0.98, pos_legend, transform=ax.transAxes, va='top',
                color=MUTED, fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor=BG, edgecolor=BORDER, alpha=0.8))


    def _draw_velocity_panel(self, ax, k, name, color, th_deg):
        vel = k['vel']
        VA       = vel['VA']
        V_tip    = vel['V_tip']
        V_slider = np.array([0.0, vel['Vslider_y']])
        origin   = (0.0, 0.0)

        self.add_vector(ax, origin, tuple(VA),       ACCENT,  "V_A")
        self.add_vector(ax, origin, tuple(V_tip),    WARN,    "V_T")
        self.add_vector(ax, origin, tuple(V_slider), SUCCESS, "V_P")
        self.add_vector(ax, tuple(VA),    tuple(V_tip),    ACCENT2, "V_T/A")
        self.add_vector(ax, tuple(V_tip), tuple(V_slider), ACCENT,  "V_P/T")

        ax.legend(loc='upper right', fontsize=9)
        self._auto_lim(ax, np.array([origin, VA, V_tip, V_slider, V_tip - VA, V_slider - V_tip]), margin=0.05)
        ax.set_title(f"Velocity Polygon — {name}  (θ = {th_deg:.1f}°)", fontsize=13, color=color, pad=10)
        ax.set_xlabel("Vx (m/s)", fontsize=10, color=MUTED)
        ax.set_ylabel("Vy (m/s)", fontsize=10, color=MUTED)

        # Velocity Vector Legend Text Box
        vel_legend = (
            "V_A: Vel of Crank Pin\n"
            "V_T: Vel of Lever Tip\n"
            "V_P: Vel of Slider (Pie Object)\n"
            "V_T/A: Slip Vel (Lever vs Pin)\n"
            "V_P/T: Slip Vel (Slider vs Tip)"
        )
        ax.text(0.02, 0.98, vel_legend, transform=ax.transAxes, va='top',
                color=MUTED, fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor=BG, edgecolor=BORDER, alpha=0.8))

    def _draw_acceleration_panel(self, ax, k, name, color, th_deg):
        acc = k['acc']
        AA       = acc['AA']
        A_tip    = acc['A_tip']
        A_slider = np.array([0.0, acc['Aslider_y']])
        origin   = (0.0, 0.0)

        self.add_vector(ax, origin, tuple(AA),       ACCENT,  "A_A")
        self.add_vector(ax, origin, tuple(A_tip),    WARN,    "A_T")
        self.add_vector(ax, origin, tuple(A_slider), SUCCESS, "A_P")
        self.add_vector(ax, tuple(AA),    tuple(A_tip),    ACCENT2, "A_T/A")
        self.add_vector(ax, tuple(A_tip), tuple(A_slider), ACCENT,  "A_P/T")

        ax.legend(loc='upper right', fontsize=9)
        self._auto_lim(ax, np.array([origin, AA, A_tip, A_slider, A_tip - AA, A_slider - A_tip]), margin=0.5)
        ax.set_title(f"Acceleration Polygon — {name}  (θ = {th_deg:.1f}°)", fontsize=13, color=color, pad=10)
        ax.set_xlabel("Ax (m/s²)", fontsize=10, color=MUTED)
        ax.set_ylabel("Ay (m/s²)", fontsize=10, color=MUTED)

        # Acceleration Vector Legend Text Box
        acc_legend = (
            "A_A: Accel of Crank Pin\n"
            "A_T: Accel of Lever Tip\n"
            "A_P: Accel of Slider (Pie Object)\n"
            "A_T/A: Rel Accel (Lever vs Pin)\n"
            "A_P/T: Rel Accel (Slider vs Tip)"
        )
        ax.text(0.02, 0.98, acc_legend, transform=ax.transAxes, va='top',
                color=MUTED, fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor=BG, edgecolor=BORDER, alpha=0.8))

    # =========================================================================
    # KINEMATIC PLOTS
    # =========================================================================
    def _kin_tab_changed(self, index):
        if hasattr(self, 'kin_data') and self.kin_data is not None:
            self._draw_kin_for_index(index)

    def _draw_kin_for_index(self, index):
        if not hasattr(self, 'kin_data') or self.kin_data is None: return
        s = self.syn
        data = self.kin_data
        ang  = data['angles']

        self.fig_kin.clear()
        ax = self.fig_kin.add_subplot(111)
        ax.grid(True, alpha=0.3, ls='--', lw=0.5)
        ax.tick_params(colors=MUTED, labelsize=9)

        if index == 0:
            ydata  = data['slider_y'] * 1000.0
            ylabel = "Displacement (mm)"
            title  = "Slider Displacement vs Crank Angle"
            col    = SUCCESS
        elif index == 1:
            ydata  = data['Vslider_y'] * 1000.0
            ylabel = "Velocity (mm/s)"
            title  = "Slider Velocity vs Crank Angle"
            col    = WARN
        else:
            ydata  = data['Aslider_y'] * 1000.0
            ylabel = "Acceleration (mm/s²)"
            title  = "Slider Acceleration vs Crank Angle"
            col    = ACCENT2

        # Detailed Shading
        ax.axvspan(0,             s['theta_fwd'], alpha=0.06, color=ACCENT)
        ax.axvspan(s['theta_fwd'], 360,           alpha=0.06, color=DANGER)
        
        ax.plot(ang, ydata, color=col, lw=2.5, zorder=4)
        ax.fill_between(ang, ydata, alpha=0.12, color=col)

        for th_deg, mcol, lbl in [(s['theta_A'], SUCCESS, 'A'),
                                   (s['theta_B'], WARN,    'B'),
                                   (s['theta_C'], DANGER,  'C')]:
            ax.axvline(th_deg, color=mcol, lw=1.5, ls='--', alpha=0.9)
            ax.text(th_deg + 3, ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else ydata.min(),
                    lbl, color=mcol, fontsize=10, fontweight='bold')

        # Format custom legends for shaded strokes
        fwd_patch = mpatches.Patch(color=ACCENT, alpha=0.12, label='Forward stroke')
        ret_patch = mpatches.Patch(color=DANGER, alpha=0.12, label='Return stroke')
        val_line = mlines.Line2D([], [], color=col, lw=2.5, label='Value')
        ax.legend(handles=[fwd_patch, ret_patch, val_line], loc='upper right', fontsize=9, facecolor=PANEL, edgecolor=BORDER)

        ax.set_title(title,  fontsize=12, color=TEXT, pad=10, fontweight='bold')
        ax.set_xlabel("Crank Angle (°)", fontsize=10, color=MUTED)
        ax.set_ylabel(ylabel, fontsize=10, color=MUTED)
        self.fig_kin.tight_layout()
        self.canvas_kin.draw_idle()

    # =========================================================================
    # DYNAMICS
    # =========================================================================
    def _recompute_dynamics(self):
        if self.syn is None: return
        s = self.syn
        omega2, g = s['omega2'], 9.81
        torques, angles, F_slider, powers = [], [], [], []

        for deg in range(360):
            k = self.calc_kinematics(np.radians(deg))
            if k is None: continue

            V_CG_crank  = k['vel']['VA'] / 2.0
            V_CG_rocker = k['vel']['V_tip'] / 2.0
            V_CG_rod    = (k['vel']['V_tip'] + np.array([0, k['vel']['Vslider_y']])) / 2.0
            V_CG_slider = np.array([0, k['vel']['Vslider_y']])

            A_CG_crank  = k['acc']['AA'] / 2.0
            A_CG_rocker = k['acc']['A_tip'] / 2.0
            A_CG_rod    = (k['acc']['A_tip'] + np.array([0, k['acc']['Aslider_y']])) / 2.0
            A_CG_slider = np.array([0, k['acc']['Aslider_y']])

            bodies = [
                (s['m_crank'],  s['I_crank_cg'],  A_CG_crank,  V_CG_crank,  omega2, 0.0),
                (s['m_rocker'], s['I_rocker_cg'], A_CG_rocker, V_CG_rocker, k['vel']['omega4'], k['acc']['alpha4']),
                (s['m_rod'],    s['I_rod_cg'],    A_CG_rod,    V_CG_rod,    k['vel'].get('omega3',0), k['acc'].get('alpha3',0)),
                (s['m_pie'],    s['I_pie_O'],     A_CG_slider, V_CG_slider, k['vel'].get('omega_obj',0), k['acc'].get('alpha_obj',0))
            ]

            power = 0.0
            for m_i, I_i, A_i, V_i, om_i, al_i in bodies:
                power += -m_i * np.dot(A_i, V_i)
                power += -m_i * g * V_i[1]
                power += -I_i * al_i * om_i

            T_input = power / omega2 if abs(omega2) > 1e-12 else 0.0
            torques.append(T_input)
            powers.append(power)
            angles.append(deg)
            F_slider.append(s['m_pie'] * (k['acc']['Aslider_y'] + g))

        self.dyn_data = {
            'angles': np.array(angles),
            'torques': np.array(torques),
            'F_slider': np.array(F_slider),
            'powers': np.array(powers)
        }

    def _dyn_tab_changed(self, index):
        if hasattr(self, 'dyn_data') and self.dyn_data is not None:
            self._draw_dyn_for_index(index)

    def _draw_dyn_for_index(self, index):
        if not hasattr(self, 'dyn_data') or self.dyn_data is None: return
        s      = self.syn
        data   = self.dyn_data
        angles = data['angles']

        self.fig_dyn.clear()
        ax = self.fig_dyn.add_subplot(111)
        ax.grid(True, alpha=0.3, ls='--', lw=0.5)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.set_xlabel("Crank Angle (°)", fontsize=10, color=MUTED)

        if index == 0:
            ydata    = data['torques']
            col      = WARN
            title    = "Required Driving Torque on Crank"
            ylabel   = "Torque  T  (N·m)"
            baseline = 0
        elif index == 1:
            ydata    = data['F_slider']
            col      = ACCENT2  # Plot line purplish
            title    = "Required Driving Force on Slider (y-direction)"
            ylabel   = "Force F (N) [+ve = upward]"
            baseline = min(ydata)
        else:
            ydata    = data['powers']
            col      = SUCCESS
            title    = "Total Required System Power"
            ylabel   = "Power  P  (W)"
            baseline = 0

        # Draw shaded regions for Forward / Return Strokes
        ax.axvspan(0,             s['theta_fwd'], alpha=0.06, color=ACCENT)
        ax.axvspan(s['theta_fwd'], 360,           alpha=0.06, color=DANGER)

        ax.plot(angles, ydata, color=col, lw=2.5, zorder=4)
        ax.fill_between(angles, ydata, baseline, alpha=0.12, color=col)
        ax.axhline(0, color=BORDER, lw=1.0, ls='--')

        # Reference specific marker positions A,B,C
        for th_deg, mcol, lbl in [(s['theta_A'], SUCCESS, 'A'),
                                   (s['theta_B'], WARN,    'B'),
                                   (s['theta_C'], DANGER,  'C')]:
            ax.axvline(th_deg, color=mcol, lw=1.5, ls='--', alpha=0.9)
            ax.text(th_deg + 3, ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else ydata.min(),
                    lbl, color=mcol, fontsize=10, fontweight='bold')

        # Virtual Power info text box
        info_text = (
            "Virtual Power Principle | Material: Aluminium ρ=2700 kg/m³\n"
            "Links: square cross-section uniform rods | No external load assumed"
        )
        ax.text(0.02, 0.96, info_text, transform=ax.transAxes, va='top',
                color=MUTED, fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor=BG, edgecolor=BORDER, alpha=0.8))

        # Dynamic Legend including the Custom Peak Marker
        fwd_patch = mpatches.Patch(color=ACCENT, alpha=0.12, label='Forward stroke')
        ret_patch = mpatches.Patch(color=DANGER, alpha=0.12, label='Return stroke')
        val_line  = mlines.Line2D([], [], color=col, lw=2.5, label='Value')
        handles   = [fwd_patch, ret_patch, val_line]

        if len(ydata) > 0:
            max_idx = np.argmax(np.abs(ydata))
            peak_ang = angles[max_idx]
            peak_val = ydata[max_idx]
            ax.plot(peak_ang, peak_val, 'o', color=DANGER, ms=9, zorder=10)
            
            # Format annotation identical to screenshot
            y_offset = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.15
            ax.annotate(f"Peak\n{peak_val:.3f}\nat {peak_ang:.1f}°",
                        xy=(peak_ang, peak_val), xytext=(peak_ang + 25, peak_val - y_offset),
                        color=DANGER, fontweight='bold', fontsize=10,
                        arrowprops=dict(arrowstyle="->", color=DANGER, lw=2),
                        bbox=dict(boxstyle="round,pad=0.4", fc=PANEL, ec=DANGER, lw=1))
            
            peak_marker = mlines.Line2D([], [], color='none', marker='o', mfc=DANGER, mec=DANGER, ms=9, label=f'Peak: {peak_val:.3f}')
            handles.append(peak_marker)

        ax.legend(handles=handles, loc='upper right', fontsize=9, facecolor=PANEL, edgecolor=BORDER)
        ax.set_title(title,  fontsize=12, color=TEXT, pad=10, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=10, color=MUTED)
        self.fig_dyn.tight_layout()
        self.canvas_dyn.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Consolas", 10))
    window = WhitworthSimulator()
    window.show()
    sys.exit(app.exec())