"""
mobile/screens_world.py — World Map (resource countries as a categorized
list rather than a literal map — matplotlib/geopandas are unsuitable for
a phone build), Islands, Rivals, and the Militia/War Room.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.metrics import dp

from mobile.widgets import (
    wrapped_label, Row, make_button, info_popup, scrollable_list, money,
    PANEL, TEXT, TEXT_MUTED, RED, BLUE, GREEN, GOLD, PURPLE
)
from mobile.screens_economy import _header, BackFooter
import mobile.game_data as gd


class WorldMapScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("WORLD MAP", BLUE))
        self.resource_spinner = Spinner(text="Oil", values=list(gd.RESOURCE_DATA.keys()),
                                        size_hint_y=None, height=dp(40))
        self.resource_spinner.bind(text=lambda *_: self.refresh())
        root.add_widget(self.resource_spinner)
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        resource = self.resource_spinner.text
        self.inner.clear_widgets()
        countries = gd.RESOURCE_DATA[resource]["countries"]
        for name, info in countries.items():
            owned = name in s.bombed_countries
            row = Row(height=dp(78))
            col = BoxLayout(orientation="vertical")
            action = s.action_taken.get(name)
            status = f" [{action}]" if owned else ""
            col.add_widget(wrapped_label(text=name + status, bold=True, color=GREEN if owned else TEXT,
                                 halign="left", font_size=dp(12), size_hint_y=None, height=dp(20)))
            discount = s.get_alliance_discount(name)
            cost = int(info["action_cost"] * discount)
            col.add_widget(wrapped_label(text=f"Cost {money(cost)} | Income {money(info['income'])}/yr x {info['days']}yr",
                                 color=TEXT_MUTED, font_size=dp(10), halign="left",
                                 size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
            row.add_widget(col)
            if not owned:
                btns = BoxLayout(size_hint_x=0.5, spacing=dp(4))
                btns.add_widget(make_button("Bomb", lambda n=name, r=resource: self._act(n, r, "Bomb"),
                                            bg=RED, height=36, font_size=10))
                btns.add_widget(make_button("Coup", lambda n=name, r=resource: self._act(n, r, "Stage a Coup"),
                                            bg=PURPLE, height=36, font_size=10))
                row.add_widget(btns)
            self.inner.add_widget(row)

    def _act(self, country, resource, action):
        ok = self.app.state.bomb_or_coup(country, resource, action)
        self.refresh()
        if not ok:
            info_popup("World Map", "Not enough money for that operation.")


class IslandsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("PRIVATE ISLANDS", BLUE))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.inner.clear_widgets()
        for isl in gd.ISLANDS:
            owned = isl["name"] in s.owned_islands
            row = Row(height=dp(66))
            col = BoxLayout(orientation="vertical")
            col.add_widget(wrapped_label(text=isl["name"] + ("  (owned)" if owned else "") + f"  ({isl['loc']})",
                                 bold=True, color=GREEN if owned else TEXT, halign="left",
                                 font_size=dp(12), size_hint_y=None, height=dp(20)))
            col.add_widget(wrapped_label(text=f"Price {money(isl['price'])} | Net {money(isl['income']-isl['upkeep'])}/yr",
                                 color=TEXT_MUTED, font_size=dp(10), halign="left",
                                 size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
            row.add_widget(col)
            if not owned:
                row.add_widget(make_button("Buy", lambda n=isl["name"]: self._buy(n), bg=BLUE,
                                           height=36, font_size=11))
            self.inner.add_widget(row)

    def _buy(self, name):
        ok = self.app.state.buy_island(name)
        self.refresh()
        if not ok:
            info_popup("Islands", "Can't afford that island.")


class RivalsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("RIVALS", (0.8, 0.27, 1, 1)))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.inner.clear_widgets()
        for name, rival in s.rivals.items():
            row = Row(height=dp(60))
            controls = sum(len(c) for c in rival["controls"].values())
            row.add_widget(wrapped_label(text=f"{name}\n{money(rival['money'])}  |  controls {controls}",
                                 color=TEXT, font_size=dp(11), halign="left"))
            self.inner.add_widget(row)


class MilitiaScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("WAR ROOM", RED))
        self.militia_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(12),
                                 size_hint_y=None, height=dp(24))
        root.add_widget(self.militia_lbl)

        buy_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(4))
        for i, tier in enumerate(gd.MILITIA_TIERS):
            buy_row.add_widget(make_button(f"{tier['units']}u\n{tier['cost']//1_000_000}M",
                                           lambda idx=i: self._buy(idx), bg=PANEL, height=40, font_size=9))
        root.add_widget(buy_row)

        self.target_spinner = Spinner(text="", values=[], size_hint_y=None, height=dp(40))
        root.add_widget(self.target_spinner)

        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        s = self.app.state
        names = list(s.rivals.keys())
        self.target_spinner.values = names
        if names and self.target_spinner.text not in names:
            self.target_spinner.text = names[0]
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.militia_lbl.text = f"Militia units: {s.militia}"
        self.inner.clear_widgets()
        for act in gd.WAR_ACTIONS:
            row = Row(height=dp(60))
            row.add_widget(wrapped_label(text=f"{act['name']} ({act['units']}u)\n{act['desc']}", color=TEXT,
                                 font_size=dp(10), halign="left"))
            row.add_widget(make_button("Deploy", lambda a=act["id"]: self._deploy(a), bg=RED,
                                       height=40, font_size=11))
            self.inner.add_widget(row)

    def _buy(self, idx):
        ok = self.app.state.buy_militia(idx)
        self.refresh()
        if not ok:
            info_popup("War Room", "Can't afford that unit.")

    def _deploy(self, action_id):
        target = self.target_spinner.text
        if not target:
            return
        result = self.app.state.deploy_war_action(action_id, target)
        self.refresh()
        info_popup("War Room", result or "Not enough militia units.")
