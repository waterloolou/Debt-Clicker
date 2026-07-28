"""
mobile/screens_casino.py — Casino hub plus Roulette, Slots, Blackjack,
and 5-Card Draw Poker mini-games.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

from mobile.widgets import wrapped_label, make_button, info_popup, PANEL, TEXT, TEXT_MUTED, RED, BLUE, GREEN, GOLD
from mobile.screens_economy import _header, BackFooter


def _bet_input():
    return TextInput(text="1000000", multiline=False, size_hint_y=None, height=dp(44),
                     font_size=dp(14), input_filter="int")


class CasinoScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(_header("CASINO", GOLD))
        for label, target in [("Russian Roulette", "roulette"), ("Slot Machine", "slots"),
                              ("5-Card Draw Poker", "poker"), ("Blackjack", "blackjack")]:
            root.add_widget(make_button(label, lambda t=target: app.goto(t), bg=PANEL, height=56, font_size=15))
        root.add_widget(BoxLayout())
        root.add_widget(BackFooter(app))
        self.add_widget(root)


class RouletteScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(_header("RUSSIAN ROULETTE", RED))
        root.add_widget(wrapped_label(text="1 in 6 chance. Fire to double your bet or die.",
                              color=TEXT_MUTED, size_hint_y=None, height=dp(30), font_size=dp(11)))
        self.bet_input = _bet_input()
        root.add_widget(self.bet_input)
        self.result_lbl = wrapped_label(text="", color=TEXT, font_size=dp(16), size_hint_y=None, height=dp(60))
        root.add_widget(self.result_lbl)
        root.add_widget(make_button("FIRE", self._fire, bg=RED, height=56, font_size=16))
        root.add_widget(BoxLayout())
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def _fire(self):
        try:
            bet = float(self.bet_input.text)
        except ValueError:
            return
        outcome = self.app.state.roulette_fire(bet)
        if outcome is None:
            self.result_lbl.text = "Invalid bet."
        elif outcome["survived"]:
            self.result_lbl.text = f"CLICK. Survived! +${outcome['winnings']:,.0f}"
            self.result_lbl.color = GREEN
        else:
            self.result_lbl.text = "BANG. You're dead."
            self.result_lbl.color = RED
            self.app.goto("end")


class SlotsScreen(Screen):
    # Plain-text reel symbols — avoids relying on color-emoji glyph coverage,
    # which Kivy's bundled font (like most system fonts on a stock Android
    # image) does not reliably have.
    SYMBOL_EMOJI = {"cherry": "CHERRY", "lemon": "LEMON", "orange": "ORANGE",
                    "grapes": "GRAPES", "diamond": "GEM", "seven": "7-7-7"}

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(_header("SLOT MACHINE", GOLD))
        self.reel_lbl = wrapped_label(text="?  ?  ?", font_size=dp(20), bold=True, size_hint_y=None, height=dp(80))
        root.add_widget(self.reel_lbl)
        self.bet_input = _bet_input()
        root.add_widget(self.bet_input)
        self.result_lbl = wrapped_label(text="", color=TEXT, font_size=dp(14), size_hint_y=None, height=dp(50))
        root.add_widget(self.result_lbl)
        root.add_widget(make_button("SPIN", self._spin, bg=GOLD, fg=(0, 0, 0, 1), height=56, font_size=16))
        root.add_widget(BoxLayout())
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def _spin(self):
        try:
            bet = float(self.bet_input.text)
        except ValueError:
            return
        outcome = self.app.state.spin_slots(bet)
        if outcome is None:
            self.result_lbl.text = "Invalid bet."
            return
        self.reel_lbl.text = "  ".join(self.SYMBOL_EMOJI[s] for s in outcome["result"])
        win = outcome["winnings"] >= 0
        self.result_lbl.text = f"{outcome['label']}  {'+' if win else ''}${outcome['winnings']:,.0f}"
        self.result_lbl.color = GOLD if win else RED


class PokerScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(_header("5-CARD DRAW POKER", GREEN))
        self.hand_lbl = wrapped_label(text="Deal to begin.", font_size=dp(20), size_hint_y=None, height=dp(60))
        root.add_widget(self.hand_lbl)
        self.hold_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(4))
        self.hold_buttons = []
        for i in range(5):
            b = make_button("Hold", lambda idx=i: self._toggle(idx), bg=PANEL, height=44, font_size=10)
            self.hold_row.add_widget(b)
            self.hold_buttons.append(b)
        root.add_widget(self.hold_row)
        self.bet_input = _bet_input()
        root.add_widget(self.bet_input)
        self.result_lbl = wrapped_label(text="", color=TEXT_MUTED, font_size=dp(13), size_hint_y=None, height=dp(30))
        root.add_widget(self.result_lbl)
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btn_row.add_widget(make_button("Deal", self._deal, bg=GREEN, fg=(0,0,0,1)))
        self.draw_btn = make_button("Draw", self._draw, bg=BLUE)
        self.draw_btn.disabled = True
        btn_row.add_widget(self.draw_btn)
        root.add_widget(btn_row)
        root.add_widget(BoxLayout())
        root.add_widget(BackFooter(app))
        self.add_widget(root)
        self._holds = [False] * 5

    def _card_str(self, card):
        return f"{card[0]}{card[1]}"

    def _deal(self):
        try:
            bet = float(self.bet_input.text)
        except ValueError:
            return
        hand = self.app.state.poker_deal(bet)
        if hand is None:
            info_popup("Poker", "Invalid bet.")
            return
        self.hand_lbl.text = "  ".join(self._card_str(c) for c in hand)
        self._holds = [False] * 5
        for b in self.hold_buttons:
            b.background_color = PANEL
        self.draw_btn.disabled = False
        self.result_lbl.text = ""

    def _toggle(self, idx):
        self.app.state.poker_toggle_hold(idx)
        self._holds[idx] = not self._holds[idx]
        self.hold_buttons[idx].background_color = GREEN if self._holds[idx] else PANEL

    def _draw(self):
        outcome = self.app.state.poker_draw()
        self.hand_lbl.text = "  ".join(self._card_str(c) for c in self.app.state.poker_hand)
        win = outcome["profit"] >= 0
        self.result_lbl.text = f"{outcome['name']}  {'+' if win else ''}${outcome['profit']:,.0f}"
        self.result_lbl.color = GOLD if win else RED
        self.draw_btn.disabled = True


class BlackjackScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        root.add_widget(_header("BLACKJACK", BLUE))
        self.dealer_lbl = wrapped_label(text="Dealer: ?", font_size=dp(16), size_hint_y=None, height=dp(30))
        self.player_lbl = wrapped_label(text="You: —", font_size=dp(16), size_hint_y=None, height=dp(30))
        root.add_widget(self.dealer_lbl)
        root.add_widget(self.player_lbl)
        self.bet_input = _bet_input()
        root.add_widget(self.bet_input)
        self.result_lbl = wrapped_label(text="", color=TEXT, font_size=dp(14), size_hint_y=None, height=dp(40))
        root.add_widget(self.result_lbl)

        self.deal_btn = make_button("Deal", self._deal, bg=GREEN, fg=(0, 0, 0, 1))
        action_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))
        self.hit_btn = make_button("Hit", self._hit, bg=BLUE)
        self.stand_btn = make_button("Stand", self._stand, bg=RED)
        self.hit_btn.disabled = True
        self.stand_btn.disabled = True
        action_row.add_widget(self.hit_btn)
        action_row.add_widget(self.stand_btn)

        root.add_widget(self.deal_btn)
        root.add_widget(action_row)
        root.add_widget(BoxLayout())
        root.add_widget(BackFooter(app))
        self.add_widget(root)

    def _card_str(self, card):
        return f"{card[0]}{card[1]}"

    def _deal(self):
        try:
            bet = float(self.bet_input.text)
        except ValueError:
            return
        deal = self.app.state.bj_deal(bet)
        if deal is None:
            info_popup("Blackjack", "Invalid bet.")
            return
        self.player_lbl.text = "You: " + "  ".join(self._card_str(c) for c in deal["player"])
        self.dealer_lbl.text = f"Dealer: {self._card_str(deal['dealer_up'])}  ??"
        self.hit_btn.disabled = False
        self.stand_btn.disabled = False
        self.result_lbl.text = ""

    def _hit(self):
        r = self.app.state.bj_hit()
        self.player_lbl.text = "You: " + "  ".join(self._card_str(c) for c in r["player"]) + f"  ({r['value']})"
        if r["bust"]:
            self.result_lbl.text = "BUST — you lose."
            self.result_lbl.color = RED
            self.hit_btn.disabled = True
            self.stand_btn.disabled = True

    def _stand(self):
        r = self.app.state.bj_stand()
        self.player_lbl.text = "You: " + "  ".join(self._card_str(c) for c in r["player"]) + f"  ({r['p_val']})"
        self.dealer_lbl.text = "Dealer: " + "  ".join(self._card_str(c) for c in r["dealer"]) + f"  ({r['d_val']})"
        colors = {"win": GREEN, "push": TEXT_MUTED, "lose": RED}
        self.result_lbl.text = r["outcome"].upper()
        self.result_lbl.color = colors[r["outcome"]]
        self.hit_btn.disabled = True
        self.stand_btn.disabled = True
