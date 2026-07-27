"""
ui_theme.py — central design tokens + app-wide Tk enhancements.

install() monkeypatches tkinter.Button and tkinter.Toplevel so every button
in the app (existing and future, in any mixin) gets a hover highlight for
free, and every popup window fades in instead of snapping into existence.
Both patches are purely additive — they subclass the originals and change
nothing about how callers construct or configure widgets.
"""

import tkinter as tk

# ── Design tokens ────────────────────────────────────────────────────────

BG           = "#0e1117"
BG_PANEL     = "#1e2130"
BG_PANEL_ALT = "#151820"
BG_INSET     = "#0a0d13"
BORDER       = "#2a2a3a"

TEXT        = "#ffffff"
TEXT_MUTED  = "#aaaaaa"
TEXT_DIM    = "#666666"

RED     = "#ff2222"
BLUE    = "#4499ff"
GREEN   = "#00ff90"
GOLD    = "#ffd700"
PURPLE  = "#cc44ff"
ORANGE  = "#ffaa00"

FONT_TITLE   = ("Impact", 28)
FONT_HEADING = ("Arial", 13, "bold")
FONT_BODY    = ("Arial", 10)
FONT_SMALL   = ("Arial", 8)
FONT_MONO    = ("Consolas", 10)

_ORIGINAL_BUTTON   = tk.Button
_ORIGINAL_TOPLEVEL = tk.Toplevel


# ── Color helpers ────────────────────────────────────────────────────────

def _clamp(v):
    return max(0, min(255, int(v)))


def lighten(hex_color, factor=0.24):
    """Blend a hex color toward white. Returns the input unchanged if it
    isn't a parseable #rrggbb color (e.g. a platform system color)."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except (ValueError, IndexError, AttributeError):
        return hex_color
    r = _clamp(r + (255 - r) * factor)
    g = _clamp(g + (255 - g) * factor)
    b = _clamp(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def darken(hex_color, factor=0.20):
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except (ValueError, IndexError, AttributeError):
        return hex_color
    r = _clamp(r * (1 - factor))
    g = _clamp(g * (1 - factor))
    b = _clamp(b * (1 - factor))
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Hover-aware button ───────────────────────────────────────────────────

class HoverButton(_ORIGINAL_BUTTON):
    """Drop-in tk.Button that lightens its background on mouse-over.
    Reads the current bg live on each hover so it still works correctly
    on buttons whose color changes at runtime (tier buttons, toggles...)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hover_prev_bg = None
        self.bind("<Enter>", self._on_hover_enter, add="+")
        self.bind("<Leave>", self._on_hover_leave, add="+")

    def _on_hover_enter(self, _event=None):
        try:
            if str(self.cget("state")) == "disabled":
                return
            self._hover_prev_bg = self.cget("bg")
            self.config(bg=lighten(self._hover_prev_bg))
        except tk.TclError:
            pass

    def _on_hover_leave(self, _event=None):
        try:
            if self._hover_prev_bg is not None:
                self.config(bg=self._hover_prev_bg)
        except tk.TclError:
            pass
        finally:
            self._hover_prev_bg = None


# ── Fade-in popups ───────────────────────────────────────────────────────

class FadeToplevel(_ORIGINAL_TOPLEVEL):
    """Drop-in tk.Toplevel that fades in over ~110ms instead of snapping
    into view. Silently does nothing on platforms/window managers that
    don't support per-window alpha."""

    _FADE_STEPS = 8
    _FADE_INTERVAL_MS = 14

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.attributes("-alpha", 0.0)
        except tk.TclError:
            return
        self.after(1, lambda: self._fade_step(0))

    def _fade_step(self, i):
        try:
            if not self.winfo_exists():
                return
            self.attributes("-alpha", i / self._FADE_STEPS)
        except tk.TclError:
            return
        if i < self._FADE_STEPS:
            self.after(self._FADE_INTERVAL_MS, lambda: self._fade_step(i + 1))


_installed = False


def install():
    """Apply the global hover + fade-in enhancements. Idempotent."""
    global _installed
    if _installed:
        return
    tk.Button = HoverButton
    tk.Toplevel = FadeToplevel
    _installed = True
