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


class DebtClicker(ScreensMixin, EventsMixin, CasinoMixin, StockWindowMixin, AssetsMixin, WorldMapMixin, IslandMapMixin):
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

    # =========================================================
    # GAME START
    # =========================================================

    def start_game(self):
        self.money   = 100_000_000
        self.days    = 0
        self.running = True
        self.market.money = self.money
        self._init_flags()
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
