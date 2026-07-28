"""Headless smoke-test driver: walks through every screen and saves a
screenshot from each using Kivy's own Window.screenshot."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from kivy.clock import Clock
from mobile.main import DebtClickerApp

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
app = DebtClickerApp()


def _shot(name):
    from kivy.core.window import Window
    path = os.path.join(OUT_DIR, f"m2_{name}.png")
    Window.screenshot(name=path)
    print(f"SCREENSHOT: {path}")


def dismiss_popups():
    from kivy.uix.popup import Popup
    from kivy.core.window import Window
    for w in list(Window.children):
        if isinstance(w, Popup):
            w.dismiss()


SEQUENCE = [
    ("start", lambda: _shot("01_start")),
    ("_go", lambda: app.state.start_game("Tester", "United States of America", "president")),
    ("_go", lambda: app.goto("hud")),
    ("hud", lambda: _shot("02_hud")),
    ("_go", lambda: app.goto("assets")),
    ("assets", lambda: _shot("03_assets")),
    ("_go", lambda: app.goto("pleasures")),
    ("pleasures", lambda: _shot("04_pleasures")),
    ("_go", lambda: app.goto("lobby")),
    ("lobby", lambda: _shot("05_lobby")),
    ("_go", lambda: app.goto("blackmarket")),
    ("blackmarket", lambda: _shot("06_blackmarket")),
    ("_go", lambda: app.goto("debt")),
    ("debt", lambda: _shot("07_debt")),
    ("_go", lambda: app.goto("islands")),
    ("islands", lambda: _shot("08_islands")),
    ("_go", lambda: app.goto("rivals")),
    ("rivals", lambda: _shot("09_rivals")),
    ("_go", lambda: app.goto("militia")),
    ("militia", lambda: _shot("10_militia")),
    ("_go", lambda: (app.goto("casino"), app.goto("slots"))),
    ("_go", lambda: app.state.spin_slots(1000)),
    ("_go", lambda: app.sm.get_screen("slots")._spin()),
    ("slots", lambda: _shot("11_slots")),
    ("_go", lambda: app.goto("poker")),
    ("_go", lambda: app.sm.get_screen("poker")._deal()),
    ("poker", lambda: _shot("12_poker")),
    ("_go", lambda: app.sm.get_screen("poker")._draw()),
    ("poker2", lambda: _shot("13_poker_draw")),
    ("_go", lambda: app.goto("blackjack")),
    ("_go", lambda: app.sm.get_screen("blackjack")._deal()),
    ("blackjack", lambda: _shot("14_blackjack")),
    ("_go", lambda: app.goto("hud")),
    ("hud2", lambda: _shot("15_hud_after")),
    ("_go", dismiss_popups),
]

_delay = 0.0
_STEP = 0.4
for name, fn in SEQUENCE:
    _delay += _STEP
    Clock.schedule_once(lambda dt, f=fn: f(), _delay)

Clock.schedule_once(lambda dt: (print("TEST SEQUENCE COMPLETE"), app.stop()), _delay + 1.0)

app.run()
