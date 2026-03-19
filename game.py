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
from multiplayer_mixin import MultiplayerMixin
from militia_mixin import MilitiaMixin
from tutorial_mixin import TutorialMixin


class DebtClicker(ScreensMixin, EventsMixin, CasinoMixin, StockWindowMixin, AssetsMixin, WorldMapMixin, IslandMapMixin, LobbyMixin, BlackMarketMixin, DebtMixin, RivalsMixin, MultiplayerMixin, MilitiaMixin, TutorialMixin):
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
        self.is_multiplayer  = False
        self.net_client      = None

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
        self.epstein_visited = False
        self.epstein_catch_days = 0
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
        self.alliance_tier   = 0
        self.sanctions       = {}
        self.wanted_level    = 0
        self.net_worth_history = []
        self.rivals          = {}
        self.is_multiplayer  = False
        self.warned_happiness   = False
        self.warned_opinion     = False
        self.warned_transgress  = False
        self.death_cause        = "broke"
        self.active_wars        = {}   # rival_name -> days_remaining
        self.militia            = 0
        self.blockaded_days     = 0
        self.advisor_cursed_days = 0

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
        self.update_stock_prices()
        self.process_resource_income()
        self.process_island_income()
        self.process_loans()
        self.process_rivals()
        self.check_war_events()
        self.update_wanted_level()
        self.track_net_worth()
        if self.is_multiplayer and self.net_client and self.net_client.connected:
            self._send_game_state()
        self.process_sanctions()
        self.process_alliance_tick()
        self.process_wars()
        self.process_militia_effects()
        self.check_epstein_caught()
        self._tick_bm_cooldowns()
        self.check_critical_stats()
        if not self.running:
            return
        # Events fire at end of day, after all other processing
        self.random_events()
        if random.random() < 0.45:
            self.random_events()
        if self.money <= 0:
            self.running = False
            self.death_cause = "broke"
            self.log_event("You lost everything.")
            self.root.after(1500, self._show_end_screen)
            return
        self.root.after(60_000, self.main_loop)

    # =========================================================
    # DAILY MONEY LOSS
    # =========================================================

    def lose_money(self):
        m = self.money
        if m < 50:              lost = random.randint(1, 25)
        elif m < 100:           lost = random.randint(10, 50)
        elif m < 1_000:         lost = random.randint(100, 500)
        elif m < 10_000:        lost = random.randint(500, 2_000)
        elif m < 100_000:       lost = random.randint(2_000, 15_000)
        elif m < 1_000_000:     lost = int(m * random.uniform(0.02, 0.06))   # 2–6 %
        elif m < 10_000_000:    lost = int(m * random.uniform(0.015, 0.045)) # 1.5–4.5 %
        elif m < 100_000_000:   lost = int(m * random.uniform(0.008, 0.022)) # 0.8–2.2 %
        else:                   lost = int(m * random.uniform(0.006, 0.016)) # 0.6–1.6 %

        # Idle escalator: extra drain if no active income (no operations running)
        idle = len(self.oil_operations) == 0 and len(self.owned_islands) == 0
        if idle and m >= 1_000_000:
            idle_tax = int(m * 0.005)   # +0.5 % per day while fully idle
            lost += idle_tax
            self.log_event(f"Idle overhead: -${idle_tax:,} (no active operations)")

        self.money -= lost
        self.market.money = self.money
        self.log_event(f"Daily expenses: -${lost:,}")
        self.apply_asset_costs()
        # Daily metric drift
        self.happiness      = max(0,   self.happiness      - 1)    # -1/day (was -2, too punishing)
        self.public_opinion = min(100, self.public_opinion + 0.3)  # slow natural recovery
        # Transgressions very slowly decay when no active heat (below wanted level 2)
        if self.transgressions > 0 and self.wanted_level < 2:
            self.transgressions = max(0, self.transgressions - 0.4)
        self.update_status()

    # =========================================================
    # STAT HELPERS
    # =========================================================

    def process_wars(self):
        """Daily cost of being at war with another player."""
        if not self.active_wars:
            return
        expired = [name for name, days in self.active_wars.items() if days <= 0]
        for name in expired:
            del self.active_wars[name]
            self.log_event(f"[WAR] Ceasefire reached with {name}.")
            self._add_ticker(f"DIPLOMACY: Ceasefire declared — hostilities end with {name}...")
        for name in list(self.active_wars):
            war_tax = 1_500_000
            self.active_wars[name] -= 1
            self.money -= war_tax
            self.market.money = self.money
            self.add_transgression(1, 1)
            self.log_event(f"[WAR] War tax vs {name}: -${war_tax:,}  "
                           f"({self.active_wars[name]} days remaining)")

    def _tick_bm_cooldowns(self):
        if not hasattr(self, "_bm_cooldowns"):
            return
        for key in list(self._bm_cooldowns):
            self._bm_cooldowns[key] -= 1
            if self._bm_cooldowns[key] <= 0:
                del self._bm_cooldowns[key]

    def add_happiness(self, n):
        self.happiness = min(100, self.happiness + n)
        self._update_bars()

    def add_transgression(self, n, opinion_hit=None):
        self.transgressions  = min(100, self.transgressions + n)
        hit = opinion_hit if opinion_hit is not None else n // 2
        self.public_opinion  = max(0,   self.public_opinion - hit)
        self._update_bars()

    # =========================================================
    # CRITICAL STAT CHECKS  (happiness / opinion / transgressions)
    # =========================================================

    def check_critical_stats(self):
        # ── Happiness ────────────────────────────────────────────────────
        if self.happiness <= 0:
            if self.warned_happiness:
                self.running = False
                self.death_cause = "happiness"
                self.log_event("You lost the will to live. The empire crumbles.")
                self.root.after(1500, self._show_end_screen)
                return
            else:
                self.warned_happiness = True
                self._critical_warning(
                    "😶  No Will to Live",
                    "Your happiness has hit zero.\nYou've forgotten why you're doing any of this.",
                    "Increase your happiness within 1 day\nor your empire — and you — are finished.",
                    "#ff9900"
                )
        else:
            self.warned_happiness = False   # recovered — reset warning

        # ── Public Opinion ───────────────────────────────────────────────
        if self.public_opinion <= 0:
            if self.warned_opinion:
                self.running = False
                self.death_cause = "opinion"
                self.log_event("The public turned on you. Riots outside every property you own.")
                self.root.after(1500, self._show_end_screen)
                return
            else:
                self.warned_opinion = True
                self._critical_warning(
                    "📉  Public Opinion Collapse",
                    "Nobody wants anything to do with you.\nYour name is poison.",
                    "Recover public opinion within 1 day\nor the mob tears everything down.",
                    "#ff4444"
                )
        else:
            self.warned_opinion = False

        # ── Transgressions ───────────────────────────────────────────────
        if self.transgressions >= 100:
            if self.warned_transgress:
                self.running = False
                self.death_cause = "transgressions"
                self.log_event("Your crimes caught up with you. Life in prison. No parole.")
                self.root.after(1500, self._show_end_screen)
                return
            else:
                self.warned_transgress = True
                self._critical_warning(
                    "⛓️  Crimes Uncoverable",
                    "Every agency on Earth is building a case against you.\nThe walls are closing in.",
                    "Reduce your transgressions within 1 day\nor face life in a supermax.",
                    "#cc00ff"
                )
        else:
            self.warned_transgress = False

    def _critical_warning(self, title, body, action, color):
        popup = tk.Toplevel(self.root)
        popup.title("⚠️  WARNING")
        popup.configure(bg="#0e1117")
        popup.geometry("420x260")
        popup.resizable(False, False)

        tk.Frame(popup, bg=color, height=5).pack(fill="x")

        tk.Label(popup, text=title,
                 font=("Impact", 18), bg="#0e1117", fg=color).pack(pady=(16, 6))
        tk.Label(popup, text=body,
                 font=("Arial", 10), bg="#0e1117", fg="#dddddd",
                 wraplength=380, justify="center").pack(pady=4)

        tk.Frame(popup, bg="#1e2130", height=1).pack(fill="x", padx=30, pady=8)

        tk.Label(popup, text=action,
                 font=("Arial", 10, "bold"), bg="#0e1117", fg=color,
                 wraplength=380, justify="center").pack(pady=4)

        tk.Label(popup, text="YOU HAVE 1 DAY",
                 font=("Impact", 14), bg="#0e1117", fg="#ff2222").pack(pady=(4, 10))

        tk.Button(popup, text="Understood",
                  font=("Arial", 10, "bold"), bg=color, fg="white",
                  relief="flat", padx=24, pady=6,
                  command=popup.destroy).pack()

        tk.Frame(popup, bg=color, height=5).pack(fill="x", pady=(10, 0))

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

    # Per-ally config: discount countries, daily perks, tier costs/durations
    _ALLIANCE_DATA = {
        "USA": {
            "color": "#3399ff",
            "countries": {"United States of America", "Canada", "United Kingdom",
                          "Australia", "Japan", "South Korea", "Germany", "France",
                          "Netherlands", "Norway", "Poland", "Sweden", "Denmark"},
            "tiers": [
                {"label": "Basic",    "cost": 50_000_000,  "days": 30,
                 "perks": ["30% op discount in Western nations",
                           "+$750K passive income/day",
                           "Rivals' smear/lawsuit blocked 25% of the time"]},
                {"label": "Strategic","cost": 120_000_000, "days": 60,
                 "perks": ["30% op discount in Western nations",
                           "+$2M passive income/day",
                           "Rivals' smear/lawsuit blocked 50% of the time",
                           "-3 transgressions/day (media suppression)",
                           "War damage reduced 30% in multiplayer"]},
            ],
        },
        "Russia": {
            "color": "#dd3333",
            "countries": {"Russia", "Kazakhstan", "Belarus", "Ukraine",
                          "Serbia", "Hungary", "Bulgaria"},
            "tiers": [
                {"label": "Basic",    "cost": 50_000_000,  "days": 30,
                 "perks": ["30% op discount in Eastern nations",
                           "+20 militia units/day",
                           "Rivals' sabotage/raid blocked 25% of the time"]},
                {"label": "Strategic","cost": 120_000_000, "days": 60,
                 "perks": ["30% op discount in Eastern nations",
                           "+40 militia units/day",
                           "Rivals' sabotage/raid blocked 50% of the time",
                           "Your militia attacks deal +25% more damage",
                           "War damage reduced 30% in multiplayer"]},
            ],
        },
        "China": {
            "color": "#ffcc00",
            "countries": {"China", "Taiwan", "South Korea", "Vietnam",
                          "Indonesia", "India", "Singapore", "Thailand"},
            "tiers": [
                {"label": "Basic",    "cost": 50_000_000,  "days": 30,
                 "perks": ["30% op discount in Asia-Pacific nations",
                           "+15% bonus on all resource income/day",
                           "Rivals' regulatory tip-offs blocked 25% of the time"]},
                {"label": "Strategic","cost": 120_000_000, "days": 60,
                 "perks": ["30% op discount in Asia-Pacific nations",
                           "+25% bonus on all resource income/day",
                           "Rivals' regulatory tip-offs blocked 50% of the time",
                           "+5 public opinion/day (state media support)",
                           "War damage reduced 30% in multiplayer"]},
            ],
        },
    }

    def process_alliance_tick(self):
        if not self.alliance:
            return
        tier_idx = getattr(self, "alliance_tier", 0)
        data     = self._ALLIANCE_DATA[self.alliance]
        tier     = data["tiers"][tier_idx]

        # Apply daily perks
        if self.alliance == "USA":
            bonus = 2_000_000 if tier_idx == 1 else 750_000
            self.money += bonus
            self.market.money = self.money
            if tier_idx == 1:
                self.transgressions = max(0, self.transgressions - 3)

        elif self.alliance == "Russia":
            units = 40 if tier_idx == 1 else 20
            self.militia = getattr(self, "militia", 0) + units
            self.log_event(f"Alliance: Russia supplied {units} militia units.")

        elif self.alliance == "China":
            pct  = 0.25 if tier_idx == 1 else 0.15
            bonus = int(sum(op["income"] for op in self.oil_operations) * pct)
            if bonus > 0:
                self.money += bonus
                self.market.money = self.money
            if tier_idx == 1:
                self.public_opinion = min(100, self.public_opinion + 5)

        # Count down
        self.alliance_days -= 1
        if self.alliance_days == 0:
            self.log_event(f"Alliance with {self.alliance} ({tier['label']}) has expired.")
            self.alliance      = None
            self.alliance_tier = 0

    def get_alliance_discount(self, country):
        """Return cost multiplier based on current alliance."""
        if not self.alliance:
            return 1.0
        if country in self._ALLIANCE_DATA[self.alliance]["countries"]:
            return 0.70
        return 1.0

    def get_alliance_block_chance(self, attack_type):
        """Chance (0–1) that the current alliance blocks an incoming attack type."""
        if not self.alliance:
            return 0.0
        tier_idx = getattr(self, "alliance_tier", 0)
        base     = 0.50 if tier_idx == 1 else 0.25
        blocks = {
            "USA":    {"smear", "lawsuit"},
            "Russia": {"sabotage", "raid"},
            "China":  {"lobby"},
        }
        if attack_type in blocks.get(self.alliance, set()):
            return base
        return 0.0

    def get_alliance_war_reduction(self):
        """Damage multiplier applied to incoming war actions (multiplayer)."""
        if not self.alliance:
            return 1.0
        tier_idx = getattr(self, "alliance_tier", 0)
        return 0.70 if tier_idx == 1 else 1.0

    def get_alliance_militia_bonus(self):
        """Outgoing militia attack damage multiplier (Russia Strategic only)."""
        if self.alliance == "Russia" and getattr(self, "alliance_tier", 0) == 1:
            return 1.25
        return 1.0

    def open_alliance_window(self):
        win = tk.Toplevel(self.root)
        win.title("Alliance System")
        win.configure(bg="#0e1117")
        win.geometry("520x600")
        win.resizable(False, False)

        tk.Label(win, text="ALLIANCE SYSTEM",
                 font=("Impact", 22), bg="#0e1117", fg="#4499ff").pack(pady=(18, 2))

        if self.alliance:
            tier_idx  = getattr(self, "alliance_tier", 0)
            tier_name = self._ALLIANCE_DATA[self.alliance]["tiers"][tier_idx]["label"]
            color     = self._ALLIANCE_DATA[self.alliance]["color"]
            tk.Label(win, text=f"Active: {self.alliance}  [{tier_name}]  —  {self.alliance_days} days left",
                     font=("Arial", 10, "bold"), bg="#0e1117", fg=color).pack(pady=(0, 4))

            # Show active perks
            perk_frame = tk.Frame(win, bg="#111820", padx=10, pady=6)
            perk_frame.pack(fill="x", padx=20, pady=(0, 10))
            tk.Label(perk_frame, text="Active Perks:", font=("Arial", 8, "bold"),
                     bg="#111820", fg="#aaa").pack(anchor="w")
            for perk in self._ALLIANCE_DATA[self.alliance]["tiers"][tier_idx]["perks"]:
                tk.Label(perk_frame, text=f"  ✓  {perk}", font=("Arial", 8),
                         bg="#111820", fg="#00dd88").pack(anchor="w")
        else:
            tk.Label(win, text="No active alliance.", font=("Arial", 10),
                     bg="#0e1117", fg="#666").pack(pady=(0, 10))

        tk.Frame(win, bg="#2a2a3a", height=1).pack(fill="x", padx=20, pady=4)

        # Scrollable content
        canvas = tk.Canvas(win, bg="#0e1117", highlightthickness=0)
        sb     = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg="#0e1117")
        cw    = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        for ally, adata in self._ALLIANCE_DATA.items():
            color = adata["color"]
            section = tk.Frame(inner, bg="#0e1117")
            section.pack(fill="x", padx=14, pady=6)
            tk.Label(section, text=f"  {ally}", font=("Arial", 13, "bold"),
                     bg="#0e1117", fg=color).pack(anchor="w")

            for t_idx, tier in enumerate(adata["tiers"]):
                is_active = (self.alliance == ally and
                             getattr(self, "alliance_tier", 0) == t_idx)
                is_upgrade = (self.alliance == ally and
                              getattr(self, "alliance_tier", 0) == 0 and t_idx == 1)
                row = tk.Frame(section, bg="#1e2130", pady=8, padx=12)
                row.pack(fill="x", pady=3)

                info = tk.Frame(row, bg="#1e2130")
                info.pack(side="left", fill="both", expand=True)

                tier_color = "#00ff90" if is_active else color
                tk.Label(info,
                         text=f"{tier['label']} Tier  —  ${tier['cost']//1_000_000}M  |  {tier['days']} days",
                         font=("Arial", 10, "bold"), bg="#1e2130", fg=tier_color).pack(anchor="w")
                for perk in tier["perks"]:
                    tk.Label(info, text=f"  • {perk}", font=("Arial", 8),
                             bg="#1e2130", fg="#888").pack(anchor="w")

                if is_active:
                    btn_text, btn_bg, btn_state = "ACTIVE", "#00ff90", "disabled"
                elif is_upgrade:
                    btn_text, btn_bg, btn_state = "Upgrade", "#ff9900", "normal"
                else:
                    btn_text = "Sign" if not (self.alliance == ally) else "Renew"
                    btn_bg   = color
                    btn_state = "normal"

                def sign(a=ally, ti=t_idx, cost=tier["cost"], days=tier["days"], w=win):
                    if self.money < cost:
                        self.log_event(f"Need ${cost:,} to sign this alliance tier.")
                        return
                    # Loyalty renewal discount (renewing before expiry, same ally)
                    actual_cost = int(cost * 0.8) if (self.alliance == a and self.alliance_days > 0) else cost
                    self.money -= actual_cost
                    self.market.money = self.money
                    self.alliance      = a
                    self.alliance_tier = ti
                    self.alliance_days = days
                    tier_name = self._ALLIANCE_DATA[a]["tiers"][ti]["label"]
                    self.log_event(
                        f"Alliance signed: {a} [{tier_name}] for {days} days. "
                        f"Cost: ${actual_cost:,}"
                        + (" (loyalty renewal 20% off)" if actual_cost < cost else "")
                    )
                    self._add_ticker(f"DIPLOMACY: Strategic pact formed with {a} [{tier_name}]...")
                    self.update_status()
                    w.destroy()
                    self.open_alliance_window()

                tk.Button(row, text=btn_text, font=("Arial", 9, "bold"),
                          bg=btn_bg, fg="black" if is_active else "white",
                          relief="flat", padx=10, pady=4,
                          state=btn_state, command=sign).pack(side="right", padx=4)

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
