"""
ui_widgets.py — reusable Canvas-drawn "flat UI" components.

Native tk.Button/tk.Frame can't do rounded corners, so these are built on
Canvas instead: a rounded, hover-aware IconButton for primary actions, and
a RoundedMeter card that replaces the old flat-Frame stat bars.

NOTE: every Tkinter widget already uses a private `_w` attribute internally
to store its Tcl widget path — subclasses must NOT reuse `self._w`/`self._h`
for anything else, or widget calls silently break. Box dimensions here are
stored as `_bw`/`_bh` instead.
"""

import tkinter as tk

from ui_theme import lighten, darken
from ui_icons import draw_icon


def rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class IconButton(tk.Canvas):
    """A rounded, hover-aware button drawn on a Canvas, with an optional
    vector icon (see ui_icons) to the left of its label."""

    def __init__(self, parent, text="", icon=None, command=None,
                 bg="#1e2130", fg="white", width=132, height=40,
                 radius=10, font=("Arial", 10, "bold"), parent_bg=None, **kwargs):
        self._parent_bg = parent_bg or (parent["bg"] if "bg" in parent.keys() else "#0e1117")
        super().__init__(parent, width=width, height=height,
                          bg=self._parent_bg, highlightthickness=0,
                          cursor="hand2", **kwargs)
        self._bg = bg
        self._fg = fg
        self._text = text
        self._icon = icon
        self._radius = radius
        self._font = font
        self._command = command
        self._bw, self._bh = width, height
        self._disabled = False

        self._render(self._bg)
        self.bind("<Enter>", lambda e: self._render(lighten(self._bg)) if not self._disabled else None)
        self.bind("<Leave>", lambda e: self._render(self._bg))
        self.bind("<Button-1>", self._on_click)

    def _render(self, fill):
        self.delete("all")
        active_fill = "#181a22" if self._disabled else fill
        rounded_rect(self, 1, 1, self._bw - 1, self._bh - 1, self._radius,
                     fill=active_fill, outline="")
        fg = "#4a4a55" if self._disabled else self._fg
        if self._icon:
            draw_icon(self, self._icon, 22, self._bh / 2, 8, fg)
            self.create_text(38, self._bh / 2, text=self._text, fill=fg,
                             font=self._font, anchor="w")
        else:
            self.create_text(self._bw / 2, self._bh / 2, text=self._text, fill=fg,
                             font=self._font, anchor="center")

    def _on_click(self, _event=None):
        if not self._disabled and self._command:
            self._command()

    def set_enabled(self, enabled):
        self._disabled = not enabled
        self.config(cursor="hand2" if enabled else "arrow")
        self._render(self._bg)

    def set_bg(self, color):
        self._bg = color
        self._render(color)


class RoundedMeter(tk.Canvas):
    """A rounded stat-bar card: icon, label, value, and a pill-shaped
    progress track. Replaces the flat Frame+Label bar it's used to redraw."""

    def __init__(self, parent, label, icon, init_val, color, max_val=100,
                 width=200, height=54, parent_bg=None, **kwargs):
        self._parent_bg = parent_bg or (parent["bg"] if "bg" in parent.keys() else "#0e1117")
        super().__init__(parent, width=width, height=height,
                         bg=self._parent_bg, highlightthickness=0, **kwargs)
        self._label = label
        self._icon = icon
        self._max = max_val
        self._bw, self._bh = width, height
        self.bind("<Configure>", self._on_configure)
        self.set_value(init_val, color)

    def _on_configure(self, event):
        if event.width > 1 and event.height > 1:
            self._bw, self._bh = event.width, event.height
            self._render()

    def set_value(self, value, color=None):
        self._value = value
        self._color = color or getattr(self, "_color", "#00ff90")
        self._render()

    def _render(self):
        self.delete("all")
        rounded_rect(self, 0, 0, self._bw, self._bh, 12, fill="#1e2130", outline="")
        draw_icon(self, self._icon, 20, self._bh / 2, 8, self._color)
        self.create_text(38, 13, text=self._label, fill="#888888",
                         font=("Arial", 8), anchor="w")
        value_text = f"{int(self._value)}%" if self._max == 100 else str(int(self._value))
        self.create_text(self._bw - 10, 13, text=value_text, fill=self._color,
                         font=("Arial", 9, "bold"), anchor="e")

        track_x0, track_x1 = 38, self._bw - 10
        track_y0, track_y1 = 30, 40
        rounded_rect(self, track_x0, track_y0, track_x1, track_y1, 5,
                     fill="#0a0d13", outline="")
        frac = max(0.0, min(1.0, self._value / self._max))
        fill_x1 = track_x0 + (track_x1 - track_x0) * frac
        if fill_x1 > track_x0 + 2:
            rounded_rect(self, track_x0, track_y0, fill_x1, track_y1, 5,
                         fill=self._color, outline="")
