import tkinter as tk
import random
import threading
import math
import yfinance as yf

from constants import STOCK_CATEGORIES, CATEGORY_PRICE_RANGES
from market import StockMarket
from screens_mixin import ScreensMixin
from events_mixin import EventsMixin
from casino_mixin import CasinoMixin
from stock_window_mixin import StockWindowMixin
from assets_mixin import AssetsMixin
from world_map_mixin import WorldMapMixin
from island_map_mixin import IslandMapMixin
from lobby_mixin import LobbyMixin
from black_market_mixin import BlackMarketMixin
from debt_mixin import DebtMixin
from rivals_mixin import RivalsMixin


class DebtClicker(ScreensMixin, EventsMixin, CasinoMixin, StockWindowMixin, AssetsMixin, WorldMapMixin, IslandMapMixin, LobbyMixin, BlackMarketMixin, DebtMixin, RivalsMixin):
    """Main game controller — inherits all feature mixins."""

    def __init__(self, root):
        self.root = root
        self.root.title("Debt Clicker")
        self.root.geometry("520x700")
        self.root.configure(bg="#0e1117")
        self.root.resizable(False, False)

        self.username        = ""
        self.country         = ""
        self.money           = 100_000_000
        self.days            = 0
        self.running         = False
        self.current_category = "All"
        self.stock_labels    = {}

        self._init_flags()

        self.market = StockMarket()
        self.market.money = self.money

        self.tickers = {}
        for category, stocks in STOCK_CATEGORIES.items():
            lo, hi = CATEGORY_PRICE_RANGES.get(category, (10, 500))
            for name, ticker in stocks.items():
                self.tickers[name] = ticker
                self.market.create_stock(name, round(random.uniform(lo, hi), 2), category)

        self.clock_seconds = 0
        self.screens = {}
        self._build_all_screens()
        self.show_screen("start")

    def _init_flags(self):
        self.epstein         = False
        self.subscription    = False
        self.revolution      = True
        self.pet             = True
        self.mansion         = True
        self.family          = True
        self.company         = True
        self.rich_relative   = True
        self.space           = False
        self.ponzi           = False
        self.oil_spill       = False
        self.carbon          = False
        self.insider_trading = False
        self.pandemic        = False
        self.market_effects  = []
        self.owned_assets    = set()
        self.jet_skip_used   = False
        self.bombed_countries = set()
        self.action_taken    = {}
        self.oil_operations  = []
        self.owned_islands   = set()
        self.happiness       = 50
        self.public_opinion  = 75
        self.transgressions  = 0
        self.loans           = []
        self.lobby_immunity  = False
        self.alliance        = None
        self.alliance_days   = 0
        self.sanctions       = {}
        self.wanted_level    = 0
        self.net_worth_history = []
        self.rivals          = {}

    # =========================================================
    # GAME START
    # =========================================================

    def start_game(self):
        self.money   = 100_000_000
        self.days    = 0
        self.running = True
        self.market.money = self.money
        self._init_flags()
        # Apply legacy bonus from previous runs
        legacy = self._load_legacy()
        if legacy > 0:
            self.money += legacy
            self.market.money = self.money
            self.log_event(f"Legacy bonus applied: +${legacy:,}")
        self.init_rivals()
        self.clock_seconds = 0
        self.log_event(f"Welcome, {self.username}. Your empire begins its slow collapse...")
        self.log_event("Fetching live stock data for all markets...")
        self.update_status()
        threading.Thread(target=self.fetch_real_stock_data, daemon=True).start()

    # =========================================================
    # FETCH REAL STOCK DATA
    # =========================================================

    def fetch_real_stock_data(self):
        all_tickers = list(self.tickers.values())
        try:
            raw   = yf.download(all_tickers, period="1y", auto_adjust=True,
                                progress=False, threads=True)
            close = raw["Close"]
            loaded = 0
            for name, ticker in self.tickers.items():
                try:
                    series = close[ticker].dropna()
                    if series.empty:
                        continue
                    history = [float(p) for p in series]
                    self.market.stocks[name]["price"]        = history[-1]
                    self.market.stocks[name]["history"]      = history
                    self.market.stocks[name]["returns"]      = series.pct_change().dropna().tolist()
                    self.market.stocks[name]["return_index"] = 0
                    loaded += 1
                except Exception:
                    pass
            self.root.after(0, lambda: self.log_event(
                f"Loaded {loaded} stocks with full price history."))
        except Exception as e:
            self.root.after(0, lambda: self.log_event(
                f"Data fetch failed: {e}. Using simulated prices."))
        self.root.after(0, self.main_loop)
        self.root.after(0, self.realtime_tick)

    # =========================================================
    # REALTIME TICK  (every 1 second)
    # =========================================================

    def realtime_tick(self):
        if not self.running:
            return
        for name, data in self.market.stocks.items():
            noise = random.gauss(1.0, 0.0015 if data["returns"] else 0.004)
            data["price"] = max(0.01, data["price"] * noise)
        if hasattr(self, "stock_window") and self.stock_window.winfo_exists():
            self.update_market_labels()
        self.clock_seconds = (self.clock_seconds + 1) % 60
        self._draw_clock()
        self.root.after(1000, self.realtime_tick)

    # =========================================================
    # CLOCK
    # =========================================================

    def _draw_clock(self):
        c = self.clock_canvas
        c.delete("all")
        cx, cy, r = 30, 30, 26

        c.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#333", width=2, fill="#0a0d13")

        for i in range(12):
            angle = math.radians(i * 30 - 90)
            r1 = r - 7 if i % 3 == 0 else r - 4
            x1 = cx + r1 * math.cos(angle)
            y1 = cy + r1 * math.sin(angle)
            x2 = cx + (r - 2) * math.cos(angle)
            y2 = cy + (r - 2) * math.sin(angle)
            c.create_line(x1, y1, x2, y2,
                          fill="#555" if i % 3 != 0 else "#888",
                          width=1 if i % 3 != 0 else 2)

        c.create_text(cx, cy - r + 8, text="12", fill="#555", font=("Arial", 5))

        angle = math.radians(self.clock_seconds * 6 - 90)
        hx = cx + (r - 8) * math.cos(angle)
        hy = cy + (r - 8) * math.sin(angle)
        c.create_line(cx, cy, hx, hy, fill="#00ff90", width=2, capstyle="round")
        c.create_oval(cx-3, cy-3, cx+3, cy+3, fill="#00ff90", outline="")

    # =========================================================
    # MAIN LOOP  (every 60 seconds = 1 game day)
    # =========================================================

    def main_loop(self):
        if not self.running:
            return
        self.days += 1
        self.lose_money()
        self.random_events()
        self.update_stock_prices()
        self.process_resource_income()
        self.process_island_income()
        self.process_loans()
        self.process_rivals()
        self.check_war_events()
        self.update_wanted_level()
        self.track_net_worth()
        self.process_sanctions()
        self.process_alliance_tick()
        if self.money <= 0:
            self.running = False
            self.log_event("You lost everything.")
            self.root.after(1500, self._show_end_screen)
            return
        self.root.after(60_000, self.main_loop)

    # =========================================================
    # DAILY MONEY LOSS
    # =========================================================

    def lose_money(self):
        m = self.money
        if m < 50:       lost = random.randint(1, 25)
        elif m < 100:    lost = random.randint(10, 50)
        elif m < 1000:   lost = random.randint(100, 500)
        elif m < 10000:  lost = random.randint(100, 1000)
        elif m < 100000: lost = random.randint(1000, 10000)
        else:            lost = random.randint(100, 10_000_000)
        self.money -= lost
        self.market.money = self.money
        self.log_event(f"Lost ${lost:,}")
        self.apply_asset_costs()
        # Daily metric drift: happiness decays, opinion slowly recovers
        self.happiness      = max(0,   self.happiness      - 2)
        self.public_opinion = min(100, self.public_opinion + 0.5)
        self.update_status()

    # =========================================================
    # STAT HELPERS
    # =========================================================

    def add_happiness(self, n):
        self.happiness = min(100, self.happiness + n)
        self._update_bars()

    def add_transgression(self, n, opinion_hit=None):
        self.transgressions  = min(100, self.transgressions + n)
        hit = opinion_hit if opinion_hit is not None else n // 2
        self.public_opinion  = max(0,   self.public_opinion - hit)
        self._update_bars()

    # =========================================================
    # WANTED LEVEL
    # =========================================================

    def update_wanted_level(self):
        t = self.transgressions
        if t < 20:    level = 0
        elif t < 40:  level = 1
        elif t < 60:  level = 2
        elif t < 80:  level = 3
        else:         level = 4
        if level != self.wanted_level:
            self.wanted_level = level
            labels = ["Clean", "Media Attention", "Senate Investigation", "FBI Target", "Interpol Red Notice"]
            self.log_event(f"Wanted level changed: {labels[level]}")
            self._add_ticker(f"BREAKING: {labels[level]} — threat level rising...")
        # Daily fine for high wanted levels
        if self.wanted_level > 0:
            fine = self.wanted_level * 500_000
            self.money -= fine
            self.market.money = self.money
            self.log_event(f"Wanted level fine: -${fine:,}/day")

    # =========================================================
    # NET WORTH TRACKING
    # =========================================================

    def track_net_worth(self):
        self.net_worth_history.append(int(self.money))

    def open_net_worth_graph(self):
        import matplotlib.pyplot as plt
        if not self.net_worth_history:
            self.log_event("No net worth data yet.")
            return
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(self.net_worth_history, color="#00ff90", linewidth=1.5)
        ax.set_facecolor("#0e1117")
        fig.set_facecolor("#0e1117")
        ax.set_title("Net Worth Over Time", color="white")
        ax.set_xlabel("Days", color="white")
        ax.set_ylabel("Money ($)", color="white")
        ax.tick_params(colors="white")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        plt.tight_layout()
        plt.show()

    # =========================================================
    # SANCTIONS
    # =========================================================

    def process_sanctions(self):
        if not self.sanctions:
            return
        expired = [c for c, days in self.sanctions.items() if days <= 1]
        for c in expired:
            del self.sanctions[c]
            self.log_event(f"Sanctions from {c} have expired.")
        for c in list(self.sanctions.keys()):
            if c not in expired:
                self.sanctions[c] -= 1
                self.money -= 500_000
                self.market.money = self.money
                self.log_event(f"Sanctions: {c} costs -$500,000/day ({self.sanctions[c]} days left)")

    def apply_sanction(self, country, days=10):
        self.sanctions[country] = days
        self.log_event(f"SANCTIONED by {country} for {days} days!")
        self._add_ticker(f"BREAKING: {country} imposes economic sanctions...")

    # =========================================================
    # ALLIANCE
    # =========================================================

    def process_alliance_tick(self):
        if self.alliance and self.alliance_days > 0:
            self.alliance_days -= 1
            if self.alliance_days == 0:
                self.log_event(f"Alliance with {self.alliance} has expired.")
                self.alliance = None

    def get_alliance_discount(self, country):
        """Return cost multiplier based on current alliance."""
        if not self.alliance:
            return 1.0
        usa_discount = {"United States of America", "Canada", "United Kingdom",
                        "Australia", "Japan", "South Korea", "Germany", "France",
                        "Netherlands", "Norway", "Poland", "Sweden", "Denmark"}
        russia_discount = {"Russia", "Kazakhstan", "Belarus", "Ukraine",
                           "Serbia", "Hungary", "Bulgaria"}
        china_discount = {"China", "Taiwan", "South Korea", "Vietnam",
                          "Indonesia", "India", "Singapore", "Thailand"}
        if self.alliance == "USA" and country in usa_discount:
            return 0.70
        if self.alliance == "Russia" and country in russia_discount:
            return 0.70
        if self.alliance == "China" and country in china_discount:
            return 0.70
        return 1.0

    def open_alliance_window(self):
        win = tk.Toplevel(self.root)
        win.title("Alliance System")
        win.configure(bg="#0e1117")
        win.geometry("460x360")
        win.resizable(False, False)

        tk.Label(win, text="ALLIANCE SYSTEM",
                 font=("Impact", 22), bg="#0e1117", fg="#4499ff").pack(pady=(18, 2))

        current = self.alliance or "None"
        days_left = self.alliance_days
        tk.Label(win, text=f"Current Alliance: {current}" + (f" ({days_left} days left)" if self.alliance else ""),
                 font=("Arial", 10), bg="#0e1117", fg="#aaaaaa").pack(pady=(0, 12))

        for ally, desc, countries_hint in [
            ("USA",    "30% discount in Western nations. Costs $50M.", "US, Canada, UK, EU, Australia, Japan"),
            ("Russia", "30% discount in Eastern/Central nations. Costs $50M.", "Russia, Kazakhstan, Belarus, Serbia, Bulgaria"),
            ("China",  "30% discount in Asia-Pacific nations. Costs $50M.", "China, Taiwan, Korea, Indonesia, India"),
        ]:
            row = tk.Frame(win, bg="#1e2130", pady=8, padx=12)
            row.pack(fill="x", padx=16, pady=4)

            info = tk.Frame(row, bg="#1e2130")
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=f"Ally with {ally}", font=("Arial", 11, "bold"),
                     bg="#1e2130", fg="white", anchor="w").pack(anchor="w")
            tk.Label(info, text=desc, font=("Arial", 8),
                     bg="#1e2130", fg="#888", anchor="w").pack(anchor="w")
            tk.Label(info, text=countries_hint, font=("Arial", 7),
                     bg="#1e2130", fg="#555", anchor="w").pack(anchor="w")

            def sign(a=ally, w=win):
                if self.money < 50_000_000:
                    self.log_event("Need $50,000,000 to sign an alliance.")
                    return
                if self.alliance == a:
                    self.log_event(f"Already allied with {a}.")
                    return
                self.money -= 50_000_000
                self.market.money = self.money
                self.alliance = a
                self.alliance_days = 30
                self.log_event(f"Alliance signed with {a}! 30% discount on eligible countries for 30 days.")
                self._add_ticker(f"DIPLOMACY: New strategic alliance formed with {a}...")
                self.update_status()
                w.destroy()
                self.open_alliance_window()

            active = self.alliance == ally
            tk.Button(row,
                      text="ACTIVE" if active else "Sign ($50M)",
                      font=("Arial", 9, "bold"),
                      bg="#00ff90" if active else "#4499ff",
                      fg="black" if active else "white",
                      relief="flat", padx=10, pady=4,
                      state="disabled" if active else "normal",
                      command=sign).pack(side="right")

    # =========================================================
    # WAR EVENTS  (called from main_loop)
    # =========================================================

    def check_war_events(self):
        if self.public_opinion <= 5 and self.running:
            import random
            war_countries = ["France", "Germany", "Brazil", "India", "Turkey", "Egypt"]
            attacker = random.choice(war_countries)
            damage = random.randint(30_000_000, 80_000_000)
            self.money -= damage
            self.market.money = self.money
            self.add_transgression(30, 0)
            self.apply_sanction(attacker, days=15)
            self.apply_market_effect(["Defense"], 1.08, 5, f"War: {attacker}")
            self.apply_market_effect(["Finance", "Retail"], 0.88, 5, f"War crisis")
            self.log_event(f"WAR DECLARED! {attacker} declared war. Lost ${damage:,}!")
            self._add_ticker(f"WAR: {attacker} has declared war — markets in freefall!")
            self.public_opinion = 15  # Reset so it doesn't loop every day
            self.update_status()

    # =========================================================
    # INFAMY TIER
    # =========================================================

    def get_infamy_tier(self):
        t = self.transgressions
        if t < 20:   return 0, "Nobody"
        if t < 40:   return 1, "Shady"
        if t < 60:   return 2, "Crime Lord"
        if t < 80:   return 3, "War Criminal"
        if t < 100:  return 4, "Antichrist"
        return 5, "ENDGAME"

    # =========================================================
    # LEGACY SYSTEM
    # =========================================================

    def _load_legacy(self):
        import json, os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "legacy.json")
        try:
            with open(path) as f:
                return json.load(f).get("bonus", 0)
        except Exception:
            return 0

    def _save_legacy(self):
        import json, os
        if self.days < 10:
            return
        bonus = min(50_000_000, int(self.days * 300_000))
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "legacy.json")
        try:
            with open(path, "w") as f:
                json.dump({"bonus": bonus}, f)
            self.log_event(f"Legacy saved: next run starts with +${bonus:,}")
        except Exception:
            pass
