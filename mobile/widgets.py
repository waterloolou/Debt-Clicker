"""
mobile/widgets.py — shared Kivy building blocks for every screen: colors,
a rounded stat meter, section headers, styled buttons, and a lightweight
modal popup helper (Kivy's Popup, themed to match the desktop's dark UI).
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.widget import Widget

BG = (0.055, 0.067, 0.09, 1)
PANEL = (0.118, 0.129, 0.188, 1)
PANEL_ALT = (0.082, 0.094, 0.125, 1)
TEXT = (1, 1, 1, 1)
TEXT_MUTED = (0.66, 0.66, 0.66, 1)
TEXT_DIM = (0.4, 0.4, 0.4, 1)

RED = (1, 0.13, 0.13, 1)
BLUE = (0.27, 0.6, 1, 1)
GREEN = (0, 1, 0.56, 1)
GOLD = (1, 0.84, 0, 1)
PURPLE = (0.8, 0.27, 1, 1)
ORANGE = (1, 0.67, 0, 1)


class Panel(BoxLayout):
    """A rounded, dark-panel container (mirrors the desktop's Card look)."""

    def __init__(self, color=PANEL, radius=12, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*color)
            self._rect = RoundedRectangle(radius=[dp(radius)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_a):
        self._rect.pos = self.pos
        self._rect.size = self.size


def wrapped_label(text, **kwargs):
    """A Label whose text_size tracks its own box, so halign/valign and
    wrapping actually take effect (Kivy ignores both until text_size is
    bound — a bare Label sizes its texture to the unwrapped text and
    centers it, ignoring the widget's box entirely)."""
    lbl = Label(text=text, **kwargs)
    lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
    return lbl


def section_label(text, color=TEXT_MUTED, size=13, bold=True):
    return Label(text=text, color=color, font_size=dp(size), bold=bold,
                 size_hint_y=None, height=dp(24), halign="left", valign="middle")


def make_button(text, on_press, bg=PANEL, fg=TEXT, height=48, font_size=14):
    btn = Button(text=text, background_normal="", background_down="",
                 background_color=bg, color=fg, font_size=dp(font_size),
                 size_hint_y=None, height=dp(height))
    btn.bind(on_release=lambda *_: on_press())
    return btn


class StatMeter(BoxLayout):
    """A labeled, colored progress bar — the mobile equivalent of the
    desktop's RoundedMeter canvas widget."""

    def __init__(self, label, value=0, max_value=100, color=GREEN, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(46))
        kwargs.setdefault("padding", (dp(8), dp(4)))
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*PANEL)
            self._rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self._update, size=self._update)

        hdr = BoxLayout(size_hint_y=None, height=dp(16))
        self._label_widget = Label(text=label, color=TEXT_MUTED, font_size=dp(10),
                                   halign="left", valign="middle", shorten=True,
                                   shorten_from="right", size_hint_x=0.65)
        self._label_widget.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        self._value_widget = Label(text="", color=color, font_size=dp(11), bold=True,
                                   halign="right", valign="middle", size_hint_x=0.35)
        self._value_widget.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        hdr.add_widget(self._label_widget)
        hdr.add_widget(self._value_widget)
        self.add_widget(hdr)

        self._bar = ProgressBar(max=max_value, value=value, size_hint_y=None, height=dp(10))
        self.add_widget(self._bar)
        self._max = max_value
        self.set_value(value, color)

    def _update(self, *_a):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_value(self, value, color=None):
        self._bar.value = max(0, min(self._max, value))
        suffix = "%" if self._max == 100 else ""
        self._value_widget.text = f"{int(value)}{suffix}"
        if color:
            self._value_widget.color = color


def themed_popup(title, content_widget, size_hint=(0.9, 0.8)):
    popup = Popup(title=title, content=content_widget, size_hint=size_hint,
                  title_color=TEXT, separator_color=BLUE)
    return popup


def info_popup(title, body):
    box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
    lbl = Label(text=body, color=TEXT_MUTED, font_size=dp(13), halign="center", valign="middle")
    lbl.bind(size=lambda w, *_: setattr(w, "text_size", (w.width, None)))
    box.add_widget(lbl)
    popup = themed_popup(title, box, size_hint=(0.85, 0.5))
    close_btn = make_button("OK", popup.dismiss, bg=BLUE)
    box.add_widget(close_btn)
    popup.open()
    return popup


def scrollable_list():
    """Return (scrollview, inner_layout) — a vertical scrolling column."""
    sv = ScrollView(do_scroll_x=False)
    inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6), padding=dp(8))
    inner.bind(minimum_height=inner.setter("height"))
    sv.add_widget(inner)
    return sv, inner


class Row(BoxLayout):
    """A padded, rounded horizontal row card used for list items across screens."""

    def __init__(self, color=PANEL, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(64))
        kwargs.setdefault("padding", (dp(12), dp(6)))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*color)
            self._rect = RoundedRectangle(radius=[dp(10)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_a):
        self._rect.pos = self.pos
        self._rect.size = self.size


def money(v):
    return f"${int(v):,}"
