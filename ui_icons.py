"""
ui_icons.py — small vector icon set drawn with plain Canvas primitives.

Every icon is built from lines/ovals/polygons rather than an emoji glyph,
so it renders identically on every OS and font instead of depending on
emoji-font coverage. Kept deliberately minimal/geometric (flat-UI style).
"""

import math


def _money(c, cx, cy, s, color):
    c.create_oval(cx - s, cy - s, cx + s, cy + s, outline=color, width=max(1, s // 5))
    c.create_line(cx, cy - s * 0.55, cx, cy + s * 0.55, fill=color, width=max(1, s // 6))
    c.create_arc(cx - s * 0.45, cy - s * 0.5, cx + s * 0.45, cy, start=90, extent=180,
                 style="arc", outline=color, width=max(1, s // 6))
    c.create_arc(cx - s * 0.45, cy, cx + s * 0.45, cy + s * 0.5, start=270, extent=180,
                 style="arc", outline=color, width=max(1, s // 6))


def _heart(c, cx, cy, s, color):
    r = s * 0.5
    c.create_oval(cx - r * 1.5, cy - r, cx, cy + r * 0.5, fill=color, outline="")
    c.create_oval(cx, cy - r, cx + r * 1.5, cy + r * 0.5, fill=color, outline="")
    c.create_polygon(cx - r * 1.5, cy, cx + r * 1.5, cy, cx, cy + s * 1.15,
                      fill=color, outline="")


def _flag(c, cx, cy, s, color):
    c.create_line(cx - s * 0.6, cy - s, cx - s * 0.6, cy + s, fill=color, width=max(1, s // 6))
    c.create_polygon(cx - s * 0.6, cy - s * 0.9, cx + s * 0.9, cy - s * 0.55,
                      cx - s * 0.6, cy - s * 0.15, fill=color, outline="")


def _shield(c, cx, cy, s, color):
    c.create_polygon(
        cx, cy - s, cx + s * 0.85, cy - s * 0.55, cx + s * 0.85, cy + s * 0.15,
        cx, cy + s, cx - s * 0.85, cy + s * 0.15, cx - s * 0.85, cy - s * 0.55,
        outline=color, fill="", width=max(1, s // 6), joinstyle="round")


def _crown(c, cx, cy, s, color):
    base_y = cy + s * 0.5
    pts = [cx - s, base_y,
           cx - s, cy - s * 0.1, cx - s * 0.5, cy + s * 0.15, cx - s * 0.25, cy - s * 0.65,
           cx, cy + s * 0.05, cx + s * 0.25, cy - s * 0.65, cx + s * 0.5, cy + s * 0.15,
           cx + s, cy - s * 0.1, cx + s, base_y]
    c.create_polygon(pts, outline=color, fill="", width=max(1, s // 6), joinstyle="round")
    c.create_line(cx - s, base_y, cx + s, base_y, fill=color, width=max(1, s // 6))


def _scroll(c, cx, cy, s, color):
    c.create_rectangle(cx - s * 0.6, cy - s * 0.85, cx + s * 0.6, cy + s * 0.85,
                       outline=color, width=max(1, s // 6))
    for yy in (cy - s * 0.85, cy + s * 0.85):
        c.create_oval(cx - s * 0.75, yy - s * 0.18, cx - s * 0.45, yy + s * 0.18,
                      outline=color, width=max(1, s // 7))
    for frac in (-0.35, 0.0, 0.35):
        c.create_line(cx - s * 0.35, cy + s * frac, cx + s * 0.35, cy + s * frac,
                      fill=color, width=max(1, s // 8))


def _globe(c, cx, cy, s, color):
    c.create_oval(cx - s, cy - s, cx + s, cy + s, outline=color, width=max(1, s // 6))
    c.create_oval(cx - s * 0.42, cy - s, cx + s * 0.42, cy + s, outline=color, width=max(1, s // 8))
    c.create_line(cx - s, cy, cx + s, cy, fill=color, width=max(1, s // 8))
    c.create_arc(cx - s, cy - s * 1.4, cx + s, cy - s * 0.35, start=200, extent=140,
                 style="arc", outline=color, width=max(1, s // 8))
    c.create_arc(cx - s, cy + s * 0.35, cx + s, cy + s * 1.4, start=20, extent=140,
                 style="arc", outline=color, width=max(1, s // 8))


def _factory(c, cx, cy, s, color):
    base_y = cy + s * 0.7
    c.create_rectangle(cx - s, base_y - s * 0.9, cx + s, base_y, outline=color, width=max(1, s // 7))
    c.create_polygon(cx - s * 0.75, base_y - s * 0.9, cx - s * 0.25, base_y - s * 1.4,
                      cx - s * 0.25, base_y - s * 0.9, outline=color, fill="", width=max(1, s // 8))
    c.create_rectangle(cx + s * 0.15, base_y - s * 1.35, cx + s * 0.45, base_y - s * 0.9,
                       outline=color, width=max(1, s // 8))


def _dice(c, cx, cy, s, color):
    c.create_rectangle(cx - s, cy - s, cx + s, cy + s, outline=color, width=max(1, s // 6))
    r = s * 0.16
    for dx, dy in [(-0.5, -0.5), (0.5, 0.5), (0, 0), (-0.5, 0.5), (0.5, -0.5)]:
        px, py = cx + dx * s, cy + dy * s
        c.create_oval(px - r, py - r, px + r, py + r, fill=color, outline="")


def _ballot(c, cx, cy, s, color):
    c.create_rectangle(cx - s, cy - s * 0.7, cx + s, cy + s * 0.9, outline=color, width=max(1, s // 6))
    c.create_line(cx - s * 0.55, cy, cx - s * 0.1, cy + s * 0.5, fill=color, width=max(1, s // 5))
    c.create_line(cx - s * 0.1, cy + s * 0.5, cx + s * 0.7, cy - s * 0.5, fill=color, width=max(1, s // 5))


def _star(c, cx, cy, s, color):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rad = s if i % 2 == 0 else s * 0.42
        pts += [cx + rad * math.cos(ang), cy + rad * math.sin(ang)]
    c.create_polygon(pts, fill=color, outline="")


def _chart(c, cx, cy, s, color):
    base_y = cy + s * 0.8
    heights = [0.5, 1.1, 0.8]
    bw = s * 0.42
    for i, h in enumerate(heights):
        x0 = cx - s * 1.1 + i * (bw + s * 0.25)
        c.create_rectangle(x0, base_y - s * h, x0 + bw, base_y, fill=color, outline="")


ICONS = {
    "money":  _money,
    "heart":  _heart,
    "flag":   _flag,
    "shield": _shield,
    "crown":  _crown,
    "scroll": _scroll,
    "globe":  _globe,
    "factory": _factory,
    "dice":   _dice,
    "ballot": _ballot,
    "star":   _star,
    "chart":  _chart,
}


def draw_icon(canvas, kind, cx, cy, size, color):
    """Draw a small vector icon centered at (cx, cy) with the given radius/size."""
    fn = ICONS.get(kind)
    if fn:
        fn(canvas, cx, cy, size, color)
