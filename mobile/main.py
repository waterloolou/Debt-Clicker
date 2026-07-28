"""
mobile/main.py — Kivy application entry point.

Run from the repo root with:  python -m mobile.main
"""

import os
import sys

# Make sure the repo root (parent of this package) is importable so that
# `from market import StockMarket` etc. inside mobile/state.py resolve,
# whether this is launched as `python mobile/main.py` or `python -m mobile.main`.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.clock import Clock
from kivy.core.window import Window

from mobile.state import GameState
from mobile.widgets import BG, info_popup
from mobile.screens_core import StartScreen, HudScreen, EndScreen, LeaderboardScreen, CareerScreen
from mobile.screens_economy import (
    StockScreen, AssetsScreen, PleasuresScreen, LobbyScreen, BlackMarketScreen,
    DebtScreen, FactoryScreen,
)
from mobile.screens_world import WorldMapScreen, IslandsScreen, RivalsScreen, MilitiaScreen
from mobile.screens_political import ElectionsScreen, CabinetScreen
from mobile.screens_casino import (
    CasinoScreen, RouletteScreen, SlotsScreen, PokerScreen, BlackjackScreen,
)

# One in-game year every 60 real seconds, matching the desktop pace.
DAY_INTERVAL_SECONDS = 60


class DebtClickerApp(App):
    title = "Debt Clicker"

    def build(self):
        Window.clearcolor = BG
        # Portrait, phone-sized default for desktop testing. Android/iOS
        # builds ignore this and always run fullscreen at native resolution.
        Window.size = (420, 780)
        self.state = GameState()
        self.state.on_log = self._on_log
        self.state.on_ticker = self._on_log
        self.state.on_notify = self._on_notify
        self.state.on_warning = self._on_warning
        self.state.on_status = self._on_status
        self.state.on_game_over = self._on_game_over

        self.sm = ScreenManager(transition=NoTransition())
        self._history = []

        screen_classes = [
            StartScreen, HudScreen, StockScreen, AssetsScreen, PleasuresScreen,
            LobbyScreen, BlackMarketScreen, DebtScreen, FactoryScreen,
            WorldMapScreen, IslandsScreen, RivalsScreen, MilitiaScreen,
            ElectionsScreen, CabinetScreen, CasinoScreen, RouletteScreen,
            SlotsScreen, PokerScreen, BlackjackScreen, LeaderboardScreen,
            CareerScreen, EndScreen,
        ]
        name_overrides = {
            StartScreen: "start", HudScreen: "hud", StockScreen: "stock",
            AssetsScreen: "assets", PleasuresScreen: "pleasures", LobbyScreen: "lobby",
            BlackMarketScreen: "blackmarket", DebtScreen: "debt", FactoryScreen: "factory",
            WorldMapScreen: "world", IslandsScreen: "islands", RivalsScreen: "rivals",
            MilitiaScreen: "militia", ElectionsScreen: "elections", CabinetScreen: "cabinet",
            CasinoScreen: "casino", RouletteScreen: "roulette", SlotsScreen: "slots",
            PokerScreen: "poker", BlackjackScreen: "blackjack",
            LeaderboardScreen: "leaderboard", CareerScreen: "career", EndScreen: "end",
        }
        for cls in screen_classes:
            screen = cls(self, name=name_overrides[cls])
            self.sm.add_widget(screen)

        Clock.schedule_interval(self._tick, DAY_INTERVAL_SECONDS)
        self.sm.current = "start"
        return self.sm

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def goto(self, name):
        if self.sm.current != name:
            self._history.append(self.sm.current)
        self.sm.current = name

    def goto_back(self):
        target = self._history.pop() if self._history else "hud"
        self.sm.current = target

    # ------------------------------------------------------------------
    # State hooks
    # ------------------------------------------------------------------

    def _tick(self, _dt):
        if self.state.running:
            self.state.tick_day()

    def _on_log(self, msg):
        hud = self.sm.get_screen("hud") if self.sm.has_screen("hud") else None
        if hud:
            hud.log(msg)

    def _on_notify(self, title, body, _category="event"):
        info_popup(title, body)
        self._on_log(f"{title}: {body}")

    def _on_warning(self, title, body, action):
        info_popup(f"⚠ {title}", f"{body}\n\n{action}")

    def _on_status(self):
        if self.sm.has_screen("hud"):
            hud = self.sm.get_screen("hud")
            if self.sm.current == "hud":
                hud.refresh()

    def _on_game_over(self):
        self.goto("end")


def main():
    DebtClickerApp().run()


if __name__ == "__main__":
    main()
