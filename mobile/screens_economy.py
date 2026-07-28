"""
mobile/screens_economy.py — Stock Market, Assets, Pleasures, Lobby,
Black Market, Debt, and Factory screens.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

from mobile.widgets import (
    wrapped_label, Row, make_button, info_popup, scrollable_list, money,
    PANEL, TEXT, TEXT_MUTED, RED, BLUE, GREEN, GOLD, ORANGE
)
import mobile.game_data as gd


def _header(text, color=TEXT, back=None):
    box = BoxLayout(size_hint_y=None, height=dp(40))
    box.add_widget(wrapped_label(text=text, font_size=dp(20), bold=True, color=color))
    return box


class BackFooter(BoxLayout):
    def __init__(self, app, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(44))
        super().__init__(**kwargs)
        self.add_widget(make_button("Back", app.goto_back, bg=PANEL))


class StockScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("STOCK MARKET", GREEN))
        self.portfolio_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(11),
                                   size_hint_y=None, height=dp(20))
        root.add_widget(self.portfolio_lbl)
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        total = sum(d["price"] * d["shares"] for d in s.market.stocks.values() if d["shares"] > 0)
        self.portfolio_lbl.text = f"Portfolio: {money(total)}" if total else "No positions held"
        self.inner.clear_widgets()
        owned = [(n, d) for n, d in s.market.stocks.items() if d["shares"] > 0]
        others = [(n, d) for n, d in s.market.stocks.items() if d["shares"] == 0]
        for name, data in (owned + others[:30]):
            self.inner.add_widget(self._build_row(name, data))

    def _build_row(self, name, data):
        row = Row(height=dp(78))
        col = BoxLayout(orientation="vertical")
        col.add_widget(wrapped_label(text=f"{name}  ({data.get('category','Custom')})", color=TEXT,
                             bold=True, font_size=dp(12), halign="left",
                             size_hint_y=None, height=dp(20)))
        shares_txt = f"{data['shares']} shares owned" if data["shares"] else "—"
        col.add_widget(wrapped_label(text=f"{money(data['price'])}   {shares_txt}", color=TEXT_MUTED,
                             font_size=dp(10), halign="left", size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(4))
        btn_row.add_widget(make_button("Buy", lambda n=name: self._buy(n), bg=GREEN, fg=(0,0,0,1), height=32, font_size=11))
        btn_row.add_widget(make_button("Sell", lambda n=name: self._sell(n), bg=RED, height=32, font_size=11))
        btn_row.add_widget(make_button("Pump", lambda n=name: self._pump(n), bg=ORANGE, fg=(0,0,0,1), height=32, font_size=11))
        btn_row.add_widget(make_button("Dump", lambda n=name: self._dump(n), bg=(0.5,0.1,0.1,1), height=32, font_size=11))
        btn_row.add_widget(make_button("Margin", lambda n=name: self._margin(n), bg=BLUE, height=32, font_size=11))
        col.add_widget(btn_row)
        row.add_widget(col)
        return row

    def _buy(self, name):
        self.app.state.buy_stock(name, 1)
        self.refresh()

    def _sell(self, name):
        self.app.state.sell_stock(name, 1)
        self.refresh()

    def _pump(self, name):
        self.app.state.pump_stock(name)
        self.refresh()

    def _dump(self, name):
        self.app.state.dump_stock(name)
        self.refresh()

    def _margin(self, name):
        box = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        dir_spin = Spinner(text="long", values=["long", "short"], size_hint_y=None, height=dp(40))
        lev_spin = Spinner(text="2", values=["2", "5", "10"], size_hint_y=None, height=dp(40))
        term_spin = Spinner(text="7", values=["3", "7", "14"], size_hint_y=None, height=dp(40))
        stake_input = TextInput(text="1000000", multiline=False, size_hint_y=None, height=dp(40))
        box.add_widget(wrapped_label(text="Direction / Leverage / Term(days) / Stake", color=TEXT_MUTED,
                             size_hint_y=None, height=dp(20), font_size=dp(10)))
        box.add_widget(dir_spin)
        box.add_widget(lev_spin)
        box.add_widget(term_spin)
        box.add_widget(stake_input)
        popup_ref = {}

        def place():
            try:
                stake = float(stake_input.text)
            except ValueError:
                return
            ok = self.app.state.place_margin_bet(name, dir_spin.text, stake, int(lev_spin.text), int(term_spin.text))
            popup_ref["p"].dismiss()
            self.refresh()
            info_popup("Margin Bet", "Position opened." if ok else "Could not open position.")

        box.add_widget(make_button("Place Bet", place, bg=BLUE))
        from mobile.widgets import themed_popup
        popup_ref["p"] = themed_popup(f"Margin Desk — {name}", box, size_hint=(0.85, 0.6))
        popup_ref["p"].open()


class AssetsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("ASSETS", GOLD))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.inner.clear_widgets()
        for asset in gd.ASSETS:
            owned = asset["id"] in s.owned_assets
            row = Row(height=dp(70))
            col = BoxLayout(orientation="vertical")
            col.add_widget(wrapped_label(text=asset["name"] + ("  (owned)" if owned else ""), bold=True,
                                 color=GREEN if owned else TEXT, halign="left", font_size=dp(13),
                                 size_hint_y=None, height=dp(22)))
            col.add_widget(wrapped_label(text=f"Cost {money(asset['cost'])} | Upkeep {money(asset['upkeep'])}/yr | Income {money(asset['income'])}/yr",
                                 color=TEXT_MUTED, font_size=dp(10), halign="left",
                                 size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
            row.add_widget(col)
            if not owned:
                row.add_widget(make_button("Buy", lambda a=asset["id"]: self._buy(a), bg=GOLD, fg=(0,0,0,1),
                                           height=40, font_size=12))
            self.inner.add_widget(row)

    def _buy(self, asset_id):
        ok = self.app.state.buy_asset(asset_id)
        self.refresh()
        if not ok:
            info_popup("Assets", "Can't afford that.")


class PleasuresScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("PLEASURES", (0.8, 0.27, 1, 1)))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        self.inner.clear_widgets()
        for p in gd.PLEASURES:
            row = Row(height=dp(70))
            col = BoxLayout(orientation="vertical")
            col.add_widget(wrapped_label(text=p["name"], bold=True, color=TEXT, halign="left",
                                 font_size=dp(13), size_hint_y=None, height=dp(22)))
            risk_txt = f"  |  {int(p['risk']['chance']*100)}% risk" if p["risk"] else "  |  safe"
            col.add_widget(wrapped_label(text=f"Cost {money(p['cost'])} | Happiness +{p['happiness']}{risk_txt}",
                                 color=TEXT_MUTED, font_size=dp(10), halign="left",
                                 size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
            row.add_widget(col)
            row.add_widget(make_button("Indulge", lambda n=p["name"]: self._go(n), bg=(0.8,0.27,1,1),
                                       height=40, font_size=12))
            self.inner.add_widget(row)

    def _go(self, name):
        result = self.app.state.indulge_pleasure(name)
        self.refresh()
        if result is None:
            info_popup("Pleasures", "Can't afford that.")
        elif result["triggered_risk"]:
            info_popup(result["title"], f"{money(result['money'])}")


class LobbyScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("LOBBY", ORANGE))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.inner.clear_widgets()
        for tier in gd.LOBBY_TIERS:
            used = tier["once"] and tier["id"] == "senate_immunity" and s.lobby_immunity
            row = Row(height=dp(70))
            col = BoxLayout(orientation="vertical")
            col.add_widget(wrapped_label(text=tier["name"], bold=True, color=TEXT_MUTED if used else TEXT,
                                 halign="left", font_size=dp(13), size_hint_y=None, height=dp(22)))
            col.add_widget(wrapped_label(text=f"{tier['desc']}  ({money(tier['cost'])})", color=TEXT_MUTED,
                                 font_size=dp(10), halign="left", size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
            row.add_widget(col)
            row.add_widget(make_button("USED" if used else "Buy",
                                       (lambda: None) if used else (lambda t=tier["id"]: self._buy(t)),
                                       bg=(0.2,0.2,0.2,1) if used else ORANGE,
                                       fg=(1,1,1,1) if used else (0,0,0,1), height=40, font_size=12))
            self.inner.add_widget(row)

    def _buy(self, tier_id):
        ok = self.app.state.lobby_action(tier_id)
        self.refresh()
        if not ok:
            info_popup("Lobby", "Can't afford that (or already used).")


class BlackMarketScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("BLACK MARKET", RED))
        self.heat_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(11),
                             size_hint_y=None, height=dp(20))
        root.add_widget(self.heat_lbl)
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.heat_lbl.text = f"Heat: {int(s.bm_heat)}/100  (100+ for 2 days = Interpol siege)"
        self.inner.clear_widgets()
        cds = getattr(s, "_bm_cooldowns", {})
        for item in gd.BLACK_MARKET_ITEMS:
            cd = cds.get(item["id"], 0)
            row = Row(height=dp(70))
            col = BoxLayout(orientation="vertical")
            gain_txt = money(item["gain"]) if item["gain"] > 0 else f"-{money(abs(item['gain']))}"
            col.add_widget(wrapped_label(text=item["name"], bold=True, color=TEXT, halign="left",
                                 font_size=dp(13), size_hint_y=None, height=dp(22)))
            col.add_widget(wrapped_label(text=f"{gain_txt}  |  Trans {item['trans']:+d}", color=TEXT_MUTED,
                                 font_size=dp(10), halign="left", size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
            row.add_widget(col)
            row.add_widget(make_button(f"{cd}d" if cd else "Deal",
                                       (lambda: None) if cd else (lambda i=item["id"]: self._deal(i)),
                                       bg=(0.2,0.2,0.2,1) if cd else RED, height=40, font_size=12))
            self.inner.add_widget(row)

    def _deal(self, item_id):
        ok = self.app.state.black_market_deal(item_id)
        self.refresh()
        if not ok:
            info_popup("Black Market", "Can't do that deal right now.")


class DebtScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("DEBT & LOANS", ORANGE))
        self.score_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(11),
                               size_hint_y=None, height=dp(20))
        root.add_widget(self.score_lbl)
        self.bank_spinner = Spinner(text=gd.BANKS[0]["name"], values=[b["name"] for b in gd.BANKS],
                                    size_hint_y=None, height=dp(40))
        self.bank_spinner.bind(text=lambda *_: self.refresh())
        root.add_widget(self.bank_spinner)
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        score = s.credit_score()
        self.score_lbl.text = f"Credit score: {score}   Active loans: {len(s.loans)}/{s.max_loans}"
        self.inner.clear_widgets()

        for i, loan in enumerate(s.loans):
            row = Row(height=dp(60))
            row.add_widget(wrapped_label(text=f"[{loan.get('bank','')}] {money(loan['remaining'])} — {loan['days_left']}y left",
                                 color=ORANGE, font_size=dp(11), halign="left"))
            row.add_widget(make_button("Repay", lambda idx=i: self._repay(idx), bg=RED, height=36, font_size=11))
            self.inner.add_widget(row)

        bank = next(b for b in gd.BANKS if b["name"] == self.bank_spinner.text)
        ok, reason = s.bank_accessible(bank)
        if not ok:
            self.inner.add_widget(wrapped_label(text=reason, color=RED, size_hint_y=None, height=dp(40),
                                        font_size=dp(11)))
            return
        for idx, opt in enumerate(gd.LOAN_OPTIONS):
            rate = opt["rate"] + bank["rate_bonus"]
            row = Row(height=dp(60))
            row.add_widget(wrapped_label(text=f"{opt['label']}: {money(opt['amount'])} @ {rate*100:.1f}%/yr, {opt['days']}yr",
                                 color=TEXT, font_size=dp(11), halign="left"))
            row.add_widget(make_button("Apply", lambda o=idx, b=bank["name"]: self._apply(b, o),
                                       bg=ORANGE, fg=(0,0,0,1), height=36, font_size=11))
            self.inner.add_widget(row)

    def _repay(self, idx):
        ok = self.app.state.repay_loan(idx)
        self.refresh()
        if not ok:
            info_popup("Debt", "Not enough money to repay.")

    def _apply(self, bank_name, opt_idx):
        ok = self.app.state.take_loan(bank_name, opt_idx)
        self.refresh()
        if not ok:
            info_popup("Debt", "Loan denied.")


class FactoryScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(6))
        root.add_widget(_header("FACTORIES", (0.6, 0.6, 0.6, 1)))
        self.sv, self.inner = scrollable_list()
        root.add_widget(self.sv)
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def on_pre_enter(self, *_a):
        self.refresh()

    def refresh(self):
        s = self.app.state
        self.inner.clear_widgets()
        self.inner.add_widget(wrapped_label(text="Owned Factories", color=TEXT_MUTED, bold=True,
                                    size_hint_y=None, height=dp(24), font_size=dp(12)))
        for i, fac in enumerate(s.factories):
            ftype = gd.FACTORY_BY_ID[fac["type_id"]]
            row = Row(height=dp(72))
            col = BoxLayout(orientation="vertical")
            status = "ON STRIKE" if fac.get("on_strike") else gd.WORKER_BY_ID[fac["worker_tier"]]["name"]
            col.add_widget(wrapped_label(text=ftype["name"], bold=True, color=TEXT, halign="left",
                                 font_size=dp(12), size_hint_y=None, height=dp(20)))
            col.add_widget(wrapped_label(text=f"Workers: {status}", color=RED if fac.get("on_strike") else TEXT_MUTED,
                                 font_size=dp(10), halign="left", size_hint_y=None, height=dp(18), shorten=True, shorten_from="right"))
            tier_spin = Spinner(text=fac["worker_tier"], values=[w["id"] for w in gd.WORKER_TIERS],
                               size_hint_y=None, height=dp(30), font_size=dp(9))
            tier_spin.bind(text=lambda spn, val, idx=i: self._set_tier(idx, val))
            col.add_widget(tier_spin)
            row.add_widget(col)
            self.inner.add_widget(row)

        self.inner.add_widget(wrapped_label(text="Buy New Factory", color=TEXT_MUTED, bold=True,
                                    size_hint_y=None, height=dp(24), font_size=dp(12)))
        for ftype in gd.FACTORY_TYPES:
            row = Row(height=dp(60))
            row.add_widget(wrapped_label(text=f"{ftype['name']}: {money(ftype['price'])} (+{money(ftype['income'])}/yr)",
                                 color=TEXT, font_size=dp(11), halign="left"))
            row.add_widget(make_button("Buy", lambda t=ftype["id"]: self._buy(t), bg=(0.6,0.6,0.6,1),
                                       fg=(0,0,0,1), height=36, font_size=11))
            self.inner.add_widget(row)

    def _set_tier(self, idx, tier_id):
        self.app.state.set_worker_tier(idx, tier_id)

    def _buy(self, type_id):
        ok = self.app.state.buy_factory(type_id)
        self.refresh()
        if not ok:
            info_popup("Factory", "Can't afford that factory.")
