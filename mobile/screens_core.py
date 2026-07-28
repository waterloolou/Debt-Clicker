"""
mobile/screens_core.py — Start screen, the main HUD/navigation hub, the
End screen, Leaderboard, and Career screens.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.clock import Clock

from mobile.widgets import (
    wrapped_label, Panel, Row, StatMeter, make_button, section_label, info_popup,
    scrollable_list, money, BG, PANEL, TEXT, TEXT_MUTED, RED, BLUE, GREEN, GOLD, ORANGE
)

PLAYABLE_COUNTRIES = sorted([
    "United States of America", "Russia", "China", "Canada", "Australia", "Japan",
    "South Korea", "Israel", "France", "Germany", "United Kingdom", "Italy", "Spain",
    "Poland", "Sweden", "Netherlands", "Ukraine",
])

END_THEMES = {
    "broke": ("YOUR EMPIRE HAS COLLAPSED", RED),
    "happiness": ("YOU LOST THE WILL TO LIVE", ORANGE),
    "opinion": ("HUNTED BY YOUR OWN PEOPLE", RED),
    "transgressions": ("BROUGHT TO JUSTICE", (0.8, 0.27, 1, 1)),
    "roulette": ("BANG.", RED),
    "interpol_siege": ("INTERPOL SIEGE", RED),
    "world_domination_win": ("WORLD DOMINATION", GOLD),
}


class StartScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(12))

        root.add_widget(wrapped_label(text="DEBT CLICKER", font_size=dp(34), bold=True,
                              color=RED, size_hint_y=None, height=dp(56)))
        root.add_widget(wrapped_label(text="You are in the top 1%. You have become corrupt.",
                              color=TEXT_MUTED, font_size=dp(12), size_hint_y=None, height=dp(24)))

        mode_row = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(8))
        self.mode = "president"

        def pick_mode(m):
            self.mode = m
            billionaire_btn.background_color = ORANGE if m == "billionaire" else PANEL
            president_btn.background_color = BLUE if m == "president" else PANEL

        billionaire_btn = make_button("BILLIONAIRE\n$1B start", lambda: pick_mode("billionaire"), bg=PANEL)
        president_btn = make_button("PRESIDENT\n$100M start", lambda: pick_mode("president"), bg=BLUE)
        mode_row.add_widget(billionaire_btn)
        mode_row.add_widget(president_btn)
        root.add_widget(mode_row)

        self.name_input = TextInput(hint_text="Your name", multiline=False, size_hint_y=None,
                                    height=dp(44), font_size=dp(14))
        root.add_widget(self.name_input)

        self.country_spinner = Spinner(text="United States of America", values=PLAYABLE_COUNTRIES,
                                       size_hint_y=None, height=dp(44))
        root.add_widget(self.country_spinner)

        root.add_widget(make_button("START GAME", self._start, bg=RED, height=56, font_size=18))

        row2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        row2.add_widget(make_button("Load Game", self._load, bg=PANEL))
        row2.add_widget(make_button("Leaderboard", lambda: app.goto("leaderboard"), bg=PANEL))
        row2.add_widget(make_button("Career", lambda: app.goto("career"), bg=PANEL))
        root.add_widget(row2)

        self.status_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(11),
                                size_hint_y=None, height=dp(20))
        root.add_widget(self.status_lbl)
        root.add_widget(BoxLayout())  # spacer
        self.add_widget(root)

    def _start(self):
        name = self.name_input.text.strip() or "Player"
        country = self.country_spinner.text
        self.app.state.start_game(name, country, self.mode)
        self.app.goto("hud")

    def _load(self):
        if self.app.state.load_game():
            self.status_lbl.text = "Save loaded."
            self.app.goto("hud")
        else:
            self.status_lbl.text = "No save found."


class HudScreen(Screen):
    """The home base: money/day header, stat bars, ticker/log, and a grid
    of buttons that navigate to every sub-system screen."""

    NAV_BUTTONS = [
        ("Stock Market", "stock"), ("Casino", "casino"), ("World Map", "world"),
        ("Islands", "islands"), ("Assets", "assets"), ("Pleasures", "pleasures"),
        ("Lobby", "lobby"), ("Black Market", "blackmarket"), ("Debt", "debt"),
        ("Rivals", "rivals"), ("Factory", "factory"), ("Elections", "elections"),
        ("Cabinet", "cabinet"), ("War Room", "militia"), ("Leaderboard", "leaderboard"),
        ("Career", "career"), ("Save", "_save"),
    ]

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))

        top = BoxLayout(size_hint_y=None, height=dp(40))
        self.money_lbl = wrapped_label(text="$0", font_size=dp(20), bold=True, color=GREEN, halign="left")
        self.day_lbl = wrapped_label(text="Year 0", font_size=dp(14), color=TEXT_MUTED, halign="right")
        top.add_widget(self.money_lbl)
        top.add_widget(self.day_lbl)
        root.add_widget(top)

        meters = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        self.m_happy = StatMeter("Happiness", 50, color=GREEN)
        self.m_opinion = StatMeter("Public Opinion", 75, color=BLUE)
        self.m_trans = StatMeter("Transgressions", 0, color=ORANGE)
        meters.add_widget(self.m_happy)
        meters.add_widget(self.m_opinion)
        meters.add_widget(self.m_trans)
        root.add_widget(meters)

        self.status_lbl = wrapped_label(text="TIER 0: Nobody   |   Wanted: Clean", font_size=dp(10),
                                color=TEXT_MUTED, size_hint_y=None, height=dp(18))
        root.add_widget(self.status_lbl)

        # Work button — quick clicker action
        root.add_widget(make_button("WORK", self._work, bg=GOLD, fg=(0, 0, 0, 1), height=44))

        grid = GridLayout(cols=3, size_hint_y=None, spacing=dp(6))
        grid.bind(minimum_height=grid.setter("height"))
        for label, target in self.NAV_BUTTONS:
            grid.add_widget(make_button(label, self._make_nav(target), height=48, font_size=12))
        from kivy.uix.scrollview import ScrollView
        nav_scroll = ScrollView(do_scroll_x=False, size_hint=(1, 0.55))
        nav_scroll.add_widget(grid)
        root.add_widget(nav_scroll)

        self.log_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(10), halign="left", valign="top",
                             size_hint=(1, 1))
        log_scroll = ScrollView(do_scroll_x=False)
        log_scroll.add_widget(self.log_lbl)
        root.add_widget(log_scroll)

        self.add_widget(root)
        self._log_lines = []

    def _make_nav(self, target):
        def go():
            if target == "_save":
                ok = self.app.state.save_game()
                info_popup("Save", "Game saved." if ok else "Save failed.")
            else:
                self.app.goto(target)
        return go

    def _work(self):
        gain = self.app.state.work()
        if gain is None:
            self.log("Already worked this year.")
        else:
            self.log(f"Worked and earned {money(gain)}")
        self.refresh()

    def log(self, msg):
        self._log_lines.append(msg)
        self._log_lines = self._log_lines[-40:]
        self.log_lbl.text = "\n".join(self._log_lines)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.money_lbl.text = money(s.money)
        self.day_lbl.text = f"Year {s.days}"
        self.m_happy.set_value(s.happiness, GREEN if s.happiness > 60 else ORANGE if s.happiness > 30 else RED)
        self.m_opinion.set_value(s.public_opinion, BLUE if s.public_opinion > 60 else ORANGE if s.public_opinion > 30 else RED)
        self.m_trans.set_value(s.transgressions, RED if s.transgressions > 70 else ORANGE)
        tier, title = s.get_infamy_tier()
        labels = ["Clean", "Media Attention", "Senate Investigation", "FBI Target", "Interpol Red Notice"]
        self.status_lbl.text = f"TIER {tier}: {title}   |   Wanted: {labels[s.wanted_level]}"


class EndScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(12))
        self.title_lbl = wrapped_label(text="", font_size=dp(26), bold=True, color=RED,
                               size_hint_y=None, height=dp(80), halign="center")
        root.add_widget(self.title_lbl)
        self.detail_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(13),
                                size_hint_y=None, height=dp(120), halign="center")
        root.add_widget(self.detail_lbl)
        root.add_widget(BoxLayout())
        root.add_widget(make_button("Play Again", lambda: app.goto("start"), bg=RED, height=52))
        root.add_widget(make_button("Leaderboard", lambda: app.goto("leaderboard"), bg=PANEL))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        s = self.app.state
        rank, total, badges = s.end_run()
        title, color = END_THEMES.get(s.death_cause, END_THEMES["broke"])
        self.title_lbl.text = title
        self.title_lbl.color = color
        _, infamy = s.get_infamy_tier()
        rank_txt = f"  |  #{rank} of {total}" if rank else ""
        detail = (f"{s.username} — \"{infamy}\"\nSurvived {s.days} years{rank_txt}\n"
                  f"Transgressions: {int(s.transgressions)}  Happiness: {int(s.happiness)}")
        if badges:
            detail += "\n\nNew badges: " + ", ".join(b["name"] for b in badges)
        self.detail_lbl.text = detail


class LeaderboardScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
        root.add_widget(wrapped_label(text="LEADERBOARD", font_size=dp(22), bold=True, color=RED,
                              size_hint_y=None, height=dp(40)))
        tabs = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        tabs.add_widget(make_button("Local", self._show_local, bg=RED))
        tabs.add_widget(make_button("Global", self._show_global, bg=PANEL))
        root.add_widget(tabs)
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(make_button("Back", lambda: app.goto_back(), bg=PANEL))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self._show_local()

    def _render(self, entries, show_country=False):
        self.inner.clear_widgets()
        if not entries:
            self.inner.add_widget(wrapped_label(text="No scores yet.", color=TEXT_MUTED,
                                        size_hint_y=None, height=dp(30)))
            return
        for i, e in enumerate(entries[:20]):
            row = Row()
            name_txt = e["name"] + (f" ({e.get('country','')})" if show_country and e.get("country") else "")
            row.add_widget(wrapped_label(text=f"#{i+1}  {name_txt}", color=TEXT, halign="left"))
            row.add_widget(wrapped_label(text=f"{e['days']}y", color=GREEN, bold=True, size_hint_x=0.3))
            self.inner.add_widget(row)

    def _show_local(self):
        self._render(self.app.state.load_local_leaderboard())

    def _show_global(self):
        self.inner.clear_widgets()
        self.inner.add_widget(wrapped_label(text="Fetching global scores...", color=TEXT_MUTED,
                                    size_hint_y=None, height=dp(30)))

        def cb(data):
            def apply(_dt):
                if data is None:
                    self.inner.clear_widgets()
                    self.inner.add_widget(wrapped_label(text="Server offline.", color=RED,
                                                size_hint_y=None, height=dp(30)))
                else:
                    self._render(data, show_country=True)
            Clock.schedule_once(apply, 0)
        self.app.state.fetch_global_leaderboard(cb)


class CareerScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
        root.add_widget(wrapped_label(text="CAREER", font_size=dp(22), bold=True, color=GOLD,
                              size_hint_y=None, height=dp(40)))
        self.summary_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(12),
                                 size_hint_y=None, height=dp(24))
        root.add_widget(self.summary_lbl)
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(make_button("Back", lambda: app.goto_back(), bg=PANEL))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        from mobile.game_data import BADGES
        data = self.app.state.career_summary()
        self.summary_lbl.text = f"Games played: {data['games_played']}   Best run: {data['best_days']}y"
        self.inner.clear_widgets()
        earned = set(data["badges"])
        for badge in BADGES:
            got = badge["id"] in earned
            row = Row(color=PANEL if got else (0.05, 0.05, 0.06, 1))
            row.add_widget(wrapped_label(text=badge["name"] if got else "???",
                                 color=GOLD if got else (0.3, 0.3, 0.3, 1), bold=True,
                                 halign="left", size_hint_x=0.4))
            row.add_widget(wrapped_label(text=badge["desc"] if got else "Locked",
                                 color=TEXT_MUTED if got else (0.25, 0.25, 0.25, 1), font_size=dp(10)))
            self.inner.add_widget(row)
