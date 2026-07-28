"""
mobile/screens_political.py — Elections + Executive Orders, and the
Presidential Cabinet.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

from mobile.widgets import (
    wrapped_label, Row, StatMeter, make_button, info_popup, scrollable_list, money,
    PANEL, TEXT, TEXT_MUTED, RED, BLUE, GREEN, GOLD, ORANGE
)
from mobile.screens_economy import _header, BackFooter
import mobile.game_data as gd


class ElectionsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("ELECTIONS", BLUE))
        self.status_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(12),
                                size_hint_y=None, height=dp(60), halign="left")
        root.add_widget(self.status_lbl)

        self.run_btn = make_button("RUN FOR PRESIDENT", self._run, bg=BLUE, height=50)
        root.add_widget(self.run_btn)
        root.add_widget(make_button("Bribe a Senator ($40M, +5% win chance)", self._bribe, bg=PANEL))

        root.add_widget(wrapped_label(text="Executive Orders (max 3 per term)", color=TEXT_MUTED, bold=True,
                              size_hint_y=None, height=dp(24), font_size=dp(12)))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        if s.game_mode == "billionaire":
            self.status_lbl.text = "Billionaires don't run for office."
            self.run_btn.disabled = True
            self.inner.clear_widgets()
            return
        win_pct = s.calculate_win_probability()
        if s.is_president:
            self.status_lbl.text = (f"STATUS: PRESIDENT — Term {s.presidential_term}/{gd.MAX_TERMS}\n"
                                    f"{s.years_in_office} years remaining")
            self.run_btn.disabled = True
        else:
            self.status_lbl.text = (f"Net worth: {money(s.money)} (need {money(gd.ELECTION_THRESHOLD)})\n"
                                    f"Win chance: {win_pct:.0f}%  |  Senators bribed: {s.senators_bribed}/6")
            self.run_btn.disabled = s.money < gd.ELECTION_THRESHOLD or s.presidential_term >= gd.MAX_TERMS

        self.inner.clear_widgets()
        if not s.is_president:
            return
        for order in s.executive_orders:
            row = Row(height=dp(50))
            row.add_widget(wrapped_label(text=order["description"], color=GREEN, font_size=dp(11), halign="left"))
            self.inner.add_widget(row)
        if len(s.executive_orders) < 3:
            for tmpl in gd.EXECUTIVE_ORDER_TEMPLATES:
                row = Row(height=dp(50))
                row.add_widget(wrapped_label(text=tmpl["label"], color=TEXT, font_size=dp(11), halign="left"))
                row.add_widget(make_button("Sign", lambda t=tmpl: self._sign(t), bg=ORANGE,
                                           fg=(0,0,0,1), height=36, font_size=10))
                self.inner.add_widget(row)

    def _run(self):
        won = self.app.state.run_election()
        self.refresh()
        info_popup("Election", "You won! Welcome, Mr./Madam President." if won else "You lost. Try again next time.")

    def _bribe(self):
        s = self.app.state
        cost = 40_000_000
        if s.money < cost or s.senators_bribed >= 6:
            info_popup("Elections", "Can't bribe another senator.")
            return
        s.money -= cost
        s.market.money = s.money
        s.senators_bribed += 1
        s.add_transgression(5, 3)
        self.refresh()

    def _sign(self, template):
        ok = self.app.state.sign_executive_order(template)
        self.refresh()
        if not ok:
            info_popup("Executive Orders", "Maximum 3 orders per term.")


class CabinetScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("CABINET", BLUE))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.inner.clear_widgets()
        if not s.is_president:
            self.inner.add_widget(wrapped_label(text="You must be President to have a Cabinet.",
                                        color=TEXT_MUTED, size_hint_y=None, height=dp(40)))
            return
        if not s.cabinet:
            s._form_cabinet()
        for role, seat in s.cabinet.items():
            row = Row(height=dp(60))
            col = BoxLayout(orientation="vertical")
            if seat.get("vacant"):
                col.add_widget(wrapped_label(text=f"{role} — VACANT", color=TEXT_MUTED, halign="left",
                                     font_size=dp(12), size_hint_y=None, height=dp(24)))
            else:
                col.add_widget(wrapped_label(text=f"{role}: {seat['name']}", color=TEXT, bold=True,
                                     halign="left", font_size=dp(12), size_hint_y=None, height=dp(20)))
                approval = seat["approval"]
                color = GREEN if approval >= 70 else (ORANGE if approval >= 35 else RED)
                meter = StatMeter("Approval", approval, color=color)
                col.add_widget(meter)
            row.add_widget(col)
            self.inner.add_widget(row)
