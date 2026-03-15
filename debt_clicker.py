import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import threading
import json
import os
import matplotlib.pyplot as plt
import yfinance as yf

LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")

# -----------------------------
# STOCK CATEGORIES
# -----------------------------

STOCK_CATEGORIES = {
    "AI": {
        "NVIDIA":           "NVDA",
        "AMD":              "AMD",
        "Palantir":         "PLTR",
        "C3.ai":            "AI",
        "Super Micro":      "SMCI",
        "Arm Holdings":     "ARM",
        "SoundHound":       "SOUN",
    },
    "Technology": {
        "Apple":            "AAPL",
        "Microsoft":        "MSFT",
        "Google":           "GOOGL",
        "Meta":             "META",
        "Netflix":          "NFLX",
        "Oracle":           "ORCL",
        "IBM":              "IBM",
        "Qualcomm":         "QCOM",
        "Intel":            "INTC",
        "Salesforce":       "CRM",
        "Snowflake":        "SNOW",
        "Zoom":             "ZM",
    },
    "Energy": {
        "ExxonMobil":       "XOM",
        "Chevron":          "CVX",
        "Shell":            "SHEL",
        "BP":               "BP",
        "ConocoPhillips":   "COP",
        "NextEra":          "NEE",
        "Enphase":          "ENPH",
        "SolarEdge":        "SEDG",
        "Schlumberger":     "SLB",
    },
    "Finance": {
        "JPMorgan":         "JPM",
        "Goldman Sachs":    "GS",
        "Bank of America":  "BAC",
        "Morgan Stanley":   "MS",
        "Visa":             "V",
        "Mastercard":       "MA",
        "Berkshire":        "BRK-B",
        "BlackRock":        "BLK",
        "Charles Schwab":   "SCHW",
        "Coinbase":         "COIN",
        "PayPal":           "PYPL",
        "Robinhood":        "HOOD",
    },
    "Healthcare": {
        "Johnson & Johnson":"JNJ",
        "Pfizer":           "PFE",
        "UnitedHealth":     "UNH",
        "Moderna":          "MRNA",
        "Eli Lilly":        "LLY",
        "Merck":            "MRK",
        "AbbVie":           "ABBV",
        "Intuitive Surgical":"ISRG",
    },
    "Retail": {
        "Amazon":           "AMZN",
        "Walmart":          "WMT",
        "Costco":           "COST",
        "Target":           "TGT",
        "McDonald's":       "MCD",
        "Starbucks":        "SBUX",
        "Nike":             "NKE",
        "Home Depot":       "HD",
        "eBay":             "EBAY",
    },
    "Automotive": {
        "Tesla":            "TSLA",
        "Ford":             "F",
        "GM":               "GM",
        "Rivian":           "RIVN",
        "Lucid":            "LCID",
        "Ferrari":          "RACE",
    },
    "Defense": {
        "Lockheed Martin":  "LMT",
        "Boeing":           "BA",
        "Raytheon":         "RTX",
        "Northrop Grumman": "NOC",
        "General Dynamics": "GD",
        "L3Harris":         "LHX",
    },
    "Entertainment": {
        "Disney":           "DIS",
        "Spotify":          "SPOT",
        "Roblox":           "RBLX",
        "Warner Bros":      "WBD",
        "Live Nation":      "LYV",
        "Electronic Arts":  "EA",
        "Take-Two":         "TTWO",
    },
    "Space": {
        "Rocket Lab":       "RKLB",
        "Virgin Galactic":  "SPCE",
        "Intuitive Machines":"LUNR",
        "Redwire":          "RDW",
    },
}

CATEGORY_PRICE_RANGES = {
    "AI":           (50,  800),
    "Technology":   (50,  500),
    "Energy":       (20,  200),
    "Finance":      (30,  500),
    "Healthcare":   (50,  600),
    "Retail":       (20,  400),
    "Automotive":   (5,   300),
    "Defense":      (100, 600),
    "Entertainment":(10,  200),
    "Space":        (2,   50),
    "Custom":       (10,  500),
}

# -----------------------------
# STOCK MARKET SYSTEM
# -----------------------------

class StockMarket:

    def __init__(self):
        self.stocks = {}
        self.money = 0

    def create_stock(self, name, price, category="Custom"):
        self.stocks[name] = {
            "price":        price,
            "shares":       0,
            "history":      [price],
            "category":     category,
            "returns":      [],
            "return_index": 0,
        }
        return f"{name} created at ${round(price, 2)}"

    def buy_stock(self, name, shares):
        if name not in self.stocks:
            return "Stock does not exist"
        cost = self.stocks[name]["price"] * shares
        if self.money >= cost:
            self.money -= cost
            self.stocks[name]["shares"] += shares
            return f"Bought {shares} share(s) of {name}"
        return "Not enough money"

    def sell_stock(self, name, shares):
        if name not in self.stocks:
            return "Stock does not exist"
        if self.stocks[name]["shares"] >= shares:
            value = self.stocks[name]["price"] * shares
            self.money += value
            self.stocks[name]["shares"] -= shares
            return f"Sold {shares} share(s) of {name}"
        return "Not enough shares"

# -----------------------------
# MAIN GAME
# -----------------------------

class DebtClicker:

    def __init__(self, root):

        self.root = root
        self.root.title("Debt Clicker")
        self.root.geometry("520x700")
        self.root.configure(bg="#0e1117")
        self.root.resizable(False, False)

        self.username = ""
        self.money = 100000000
        self.days = 0
        self.running = False
        self.current_category = "All"
        self.stock_labels = {}

        self._init_flags()

        self.market = StockMarket()
        self.market.money = self.money

        self.tickers = {}
        for category, stocks in STOCK_CATEGORIES.items():
            lo, hi = CATEGORY_PRICE_RANGES.get(category, (10, 500))
            for name, ticker in stocks.items():
                self.tickers[name] = ticker
                self.market.create_stock(name, round(random.uniform(lo, hi), 2), category)

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

    # =========================================================
    # SCREEN MANAGEMENT
    # =========================================================

    def _build_all_screens(self):
        self.screens["start"]       = self._build_start_screen()
        self.screens["game"]        = self._build_game_screen()
        self.screens["end"]         = self._build_end_screen()
        self.screens["leaderboard"] = self._build_leaderboard_screen()

    def show_screen(self, name):
        for frame in self.screens.values():
            frame.place_forget()
        self.screens[name].place(relx=0, rely=0, relwidth=1, relheight=1)

    # =========================================================
    # START SCREEN
    # =========================================================

    def _build_start_screen(self):
        frame = tk.Frame(self.root, bg="#0e1117")

        tk.Label(frame, text="DEBT CLICKER",
                 font=("Impact", 48), bg="#0e1117", fg="#ff2222").pack(pady=(60, 4))

        tk.Label(frame,
                 text="You are in the top 1%.\nYou have become corrupt.\nRandom disasters will destroy your empire.\nHow long can you last?",
                 font=("Arial", 11), bg="#0e1117", fg="#aaaaaa",
                 justify="center").pack(pady=(0, 40))

        tk.Label(frame, text="Enter your name:", font=("Arial", 11),
                 bg="#0e1117", fg="white").pack()

        self.username_entry = tk.Entry(frame, font=("Arial", 13), width=20,
                                       bg="#1e2130", fg="white",
                                       insertbackground="white", relief="flat",
                                       justify="center")
        self.username_entry.pack(pady=8, ipady=6)

        self.start_error = tk.Label(frame, text="", font=("Arial", 9),
                                    bg="#0e1117", fg="#ff4444")
        self.start_error.pack()

        tk.Button(frame, text="START GAME",
                  font=("Arial", 13, "bold"), bg="#ff2222", fg="white",
                  activebackground="#cc0000", relief="flat",
                  padx=30, pady=8,
                  command=self._on_start_clicked).pack(pady=16)

        tk.Button(frame, text="Leaderboard",
                  font=("Arial", 10), bg="#1e2130", fg="#aaaaaa",
                  activebackground="#2e3140", relief="flat",
                  padx=20, pady=5,
                  command=lambda: [self._populate_leaderboard(), self.show_screen("leaderboard")]).pack()

        return frame

    def _on_start_clicked(self):
        name = self.username_entry.get().strip()
        if not name:
            self.start_error.config(text="Please enter a name.")
            return
        self.start_error.config(text="")
        self.username = name
        self.show_screen("game")
        self.start_game()

    # =========================================================
    # GAME SCREEN
    # =========================================================

    def _build_game_screen(self):
        frame = tk.Frame(self.root, bg="#0e1117")

        top = tk.Frame(frame, bg="#0e1117")
        top.pack(fill="x", padx=16, pady=(12, 4))

        self.money_label = tk.Label(top, text="Money: $100,000,000",
                                    font=("Arial", 15, "bold"), bg="#0e1117", fg="#00ff90")
        self.money_label.pack(side="left")

        self.day_label = tk.Label(top, text="Day 0",
                                  font=("Arial", 11), bg="#0e1117", fg="#aaaaaa")
        self.day_label.pack(side="right")

        btn_frame = tk.Frame(frame, bg="#0e1117")
        btn_frame.pack(pady=6)

        for text, cmd in [
            ("Work",         self.work),
            ("Casino",       self.casino),
            ("Stock Market", self.open_stock_market),
        ]:
            tk.Button(btn_frame, text=text,
                      font=("Arial", 10), bg="#1e2130", fg="white",
                      activebackground="#2e3140", relief="flat",
                      padx=14, pady=5,
                      command=cmd).pack(side="left", padx=6)

        self.log = scrolledtext.ScrolledText(frame, height=28, state="disabled",
                                             bg="#0a0d13", fg="#cccccc",
                                             font=("Consolas", 9), relief="flat",
                                             insertbackground="white")
        self.log.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        return frame

    # =========================================================
    # END SCREEN
    # =========================================================

    def _build_end_screen(self):
        frame = tk.Frame(self.root, bg="#0e1117")

        tk.Label(frame, text="YOUR EMPIRE\nHAS COLLAPSED",
                 font=("Impact", 36), bg="#0e1117", fg="#ff2222",
                 justify="center").pack(pady=(80, 20))

        self.end_name_label = tk.Label(frame, text="",
                                       font=("Arial", 14), bg="#0e1117", fg="white")
        self.end_name_label.pack(pady=4)

        self.end_days_label = tk.Label(frame, text="",
                                       font=("Arial", 20, "bold"), bg="#0e1117", fg="#00ff90")
        self.end_days_label.pack(pady=4)

        self.end_rank_label = tk.Label(frame, text="",
                                       font=("Arial", 11), bg="#0e1117", fg="#aaaaaa")
        self.end_rank_label.pack(pady=8)

        btn_frame = tk.Frame(frame, bg="#0e1117")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Play Again",
                  font=("Arial", 12, "bold"), bg="#ff2222", fg="white",
                  activebackground="#cc0000", relief="flat",
                  padx=22, pady=8,
                  command=self._play_again).pack(side="left", padx=12)

        tk.Button(btn_frame, text="Leaderboard",
                  font=("Arial", 12), bg="#1e2130", fg="white",
                  activebackground="#2e3140", relief="flat",
                  padx=22, pady=8,
                  command=lambda: [self._populate_leaderboard(), self.show_screen("leaderboard")]).pack(side="left", padx=12)

        return frame

    def _show_end_screen(self):
        rank, total = self._save_score()
        self.end_name_label.config(text=f"{self.username}'s empire has fallen.")
        self.end_days_label.config(text=f"Survived {self.days} days")
        if rank:
            self.end_rank_label.config(text=f"#{rank} on the leaderboard out of {total} players")
        else:
            self.end_rank_label.config(text="")
        self.show_screen("end")

    def _play_again(self):
        self.username_entry.delete(0, tk.END)
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.config(state="disabled")
        self.show_screen("start")

    # =========================================================
    # LEADERBOARD SCREEN
    # =========================================================

    def _build_leaderboard_screen(self):
        frame = tk.Frame(self.root, bg="#0e1117")

        tk.Label(frame, text="LEADERBOARD",
                 font=("Impact", 36), bg="#0e1117", fg="#ff2222").pack(pady=(50, 30))

        self.lb_frame = tk.Frame(frame, bg="#0e1117")
        self.lb_frame.pack(fill="both", expand=True, padx=40)

        tk.Button(frame, text="Back",
                  font=("Arial", 11), bg="#1e2130", fg="white",
                  activebackground="#2e3140", relief="flat",
                  padx=20, pady=6,
                  command=lambda: self.show_screen("start")).pack(pady=20)

        return frame

    def _populate_leaderboard(self):
        for w in self.lb_frame.winfo_children():
            w.destroy()

        entries = self._load_leaderboard()

        if not entries:
            tk.Label(self.lb_frame, text="No scores yet. Be the first!",
                     font=("Arial", 12), bg="#0e1117", fg="#aaaaaa").pack(pady=20)
            return

        medals = ["🥇", "🥈", "🥉"]

        for i, entry in enumerate(entries[:10]):
            row = tk.Frame(self.lb_frame, bg="#1e2130")
            row.pack(fill="x", pady=3, ipady=6)

            rank_text = medals[i] if i < 3 else f"#{i+1}"
            tk.Label(row, text=rank_text,
                     font=("Arial", 13), bg="#1e2130", fg="#ffdd44",
                     width=4).pack(side="left", padx=10)

            tk.Label(row, text=entry["name"],
                     font=("Arial", 12), bg="#1e2130", fg="white",
                     width=20, anchor="w").pack(side="left")

            tk.Label(row, text=f"{entry['days']} days",
                     font=("Arial", 12, "bold"), bg="#1e2130", fg="#00ff90").pack(side="right", padx=16)

    # =========================================================
    # LEADERBOARD PERSISTENCE
    # =========================================================

    def _load_leaderboard(self):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_score(self):
        entries = self._load_leaderboard()
        entries.append({"name": self.username, "days": self.days})
        entries.sort(key=lambda x: x["days"], reverse=True)
        entries = entries[:50]
        try:
            with open(LEADERBOARD_FILE, "w") as f:
                json.dump(entries, f)
        except Exception:
            pass
        rank = next((i+1 for i, e in enumerate(entries)
                     if e["name"] == self.username and e["days"] == self.days), None)
        return rank, len(entries)

    # =========================================================
    # LOG / STATUS
    # =========================================================

    def log_event(self, msg):
        self.log.config(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state="disabled")

    def update_status(self):
        self.money_label.config(text=f"Money: ${int(self.money):,}")
        self.day_label.config(text=f"Day {self.days}")

    # =========================================================
    # GAME START
    # =========================================================

    def start_game(self):
        self.money = 100000000
        self.days = 0
        self.running = True
        self.market.money = self.money
        self._init_flags()

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
            raw = yf.download(all_tickers, period="1y", auto_adjust=True,
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
            self.root.after(0, lambda: self.log_event(f"Loaded {loaded} stocks with full price history."))
        except Exception as e:
            self.root.after(0, lambda: self.log_event(f"Data fetch failed: {e}. Using simulated prices."))
        self.root.after(0, self.main_loop)
        self.root.after(0, self.realtime_tick)

    # =========================================================
    # REALTIME TICK
    # =========================================================

    def realtime_tick(self):
        if not self.running:
            return
        for name, data in self.market.stocks.items():
            noise = random.gauss(1.0, 0.0015 if data["returns"] else 0.004)
            data["price"] = max(0.01, data["price"] * noise)
        if hasattr(self, "stock_window") and self.stock_window.winfo_exists():
            self.update_market_labels()
        self.root.after(1000, self.realtime_tick)

    # =========================================================
    # MAIN LOOP
    # =========================================================

    def main_loop(self):
        if not self.running:
            return
        self.days += 1
        self.lose_money()
        self.random_events()
        self.update_stock_prices()
        if self.money <= 0:
            self.running = False
            self.log_event("You lost everything.")
            self.root.after(1500, self._show_end_screen)
            return
        self.root.after(5000, self.main_loop)

    # =========================================================
    # DAILY MONEY LOSS
    # =========================================================

    def lose_money(self):
        m = self.money
        if m < 50:           lost = random.randint(1, 25)
        elif m < 100:        lost = random.randint(10, 50)
        elif m < 1000:       lost = random.randint(100, 500)
        elif m < 10000:      lost = random.randint(100, 1000)
        elif m < 100000:     lost = random.randint(1000, 10000)
        else:                lost = random.randint(100, 10000000)
        self.money -= lost
        self.market.money = self.money
        self.log_event(f"Lost ${lost:,}")
        self.update_status()

    # =========================================================
    # RANDOM EVENTS
    # =========================================================

    def random_events(self):
        r = random.randint(1, 70)

        if r == 1 and self.family:
            self.family = False
            self.money /= 2
            self.show_event("Gold Digger!", "Oh no! Your spouse is a gold-digger and has taken HALF your money!")
            self.apply_market_effect(["Finance"], 0.93, 3, "Divorce scandal")

        elif r == 2:
            self.money *= 0.30
            self.show_event("Tax Fraud!", "You filed a fraudulent tax report. The IRS found out — lose 70% of your money!")
            self.apply_market_effect(["Finance"], 0.91, 2, "Tax fraud scandal")

        elif r == 3 and self.company:
            self.money -= 50000
            self.show_event("Factory Incident!", "One of your child workers at your illegal factory got mutilated by machinery. Pay $50,000 to cover it up.")
            self.apply_market_effect(["Retail", "Automotive"], 0.94, 2, "Factory scandal")

        elif r == 4 and self.rich_relative:
            self.rich_relative = False
            self.money += 1000000
            self.show_event("Inheritance!", "Your Grandma died! She left you $1,000,000. RIP.")

        elif r == 5:
            for name in self.market.stocks:
                self.market.stocks[name]["shares"] = 0
            self.show_event("Betrayal!", "Your financial advisor betrayed you and liquidated ALL of your stock shares!")
            self.apply_market_effect(["Finance"], 0.92, 3, "Advisor betrayal")

        elif r == 6:
            if random.randint(1, 5) == 1:
                self.money += 100000
                self.show_event("Lucky Hacker!", "Someone stole your credit ID and went gambling — and WON. They sent you $100,000 out of guilt.")
            else:
                self.money -= 500000
                self.show_event("Identity Theft!", "Someone stole your credit ID and went gambling. You lost $500,000.")
            self.apply_market_effect(["Finance", "Technology"], 0.94, 2, "Identity theft")

        elif r == 7 and not self.epstein:
            self.epstein = True
            self.money -= 10000000
            self.show_event("Island Discovered...", "Your ventures to Epstein's island have been discovered. Lose $10,000,000 to cover it up.")
            self.apply_market_effect(["Entertainment", "Finance"], 0.88, 4, "Epstein scandal")

        elif r == 8:
            self.money -= 5000000
            self.show_event("JFK Investigation!", "You are under investigation for the assassination of JFK. Your assets are temporarily frozen — lose $5,000,000.")
            self.apply_market_effect(["Defense"], 0.91, 3, "Government investigation")

        elif r == 9 and self.pet:
            self.pet = False
            self.money -= 1000
            self.show_event("Pet Incident...", "Your pet wandered into the oven. Your uneducated servant unknowingly turned it on. Something smells burnt... (pet is gone)")

        elif r == 10:
            self.money += 2000000
            self.show_event("Diamond in the Rough!", "You accidentally put a pencil in a pressure cooker and it turned into a diamond! A diamond also went missing from the Louvre... +$2,000,000")

        elif r == 11 and self.family:
            self.money -= 1000000
            self.show_event("Blender Incident!", "Your child accidentally stuck their entire arm into a running blender. Pay $1,000,000 in healthcare bills.")
            self.apply_market_effect(["Healthcare"], 1.04, 2, "Medical lawsuit windfall")

        elif r == 12 and self.revolution:
            self.apply_market_effect(["ALL"], 0.85, 5, "Socialist revolution")
            self.show_revolution_event()
            return

        elif r == 13 and self.company:
            self.company = False
            self.money -= 1000000
            self.show_event("Factory Shutdown!", "All your foreign investments in underage factory workers are exposed. Workers freed — you pay $1,000,000 in damages.")
            self.apply_market_effect(["Retail", "Automotive"], 0.92, 3, "Factory shutdown")

        elif r == 14 and self.mansion:
            self.mansion = False
            self.show_event("Cuba Invades!", "The island your private mansion sits on was just invaded by Cuba. You lost your mansion.")
            self.apply_market_effect(["Defense"], 1.06, 3, "Geopolitical tension")
            self.apply_market_effect(["Space"], 0.93, 2, "Airspace conflict")

        elif r == 15 and not self.subscription:
            self.subscription = True
            self.show_event("NYT Subscription!", "You accidentally subscribed to the New York Times. You now lose $1 every second. Cancel? They don't have a cancel button.")
            self.apply_market_effect(["Entertainment"], 0.96, 1, "Media disruption")
            self.subscription_tick()

        elif r == 16:
            self.money -= 10000000
            self.show_event("Weapons Deal", "You are funding a genocide. Pay $10,000,000 in weapons and supplies.")
            self.apply_market_effect(["Defense"], 1.08, 3, "Weapons demand surge")
            self.apply_market_effect(["Energy"], 0.91, 4, "War zone instability")

        elif r == 17 and not self.space:
            self.space = True
            self.money -= 500000000
            self.show_event("Space Program Disaster!", "You created a space program. On the first launch, the rocket explodes and kills everyone on board. Pay $500,000,000 in damages.")
            self.apply_market_effect(["Space"], 0.75, 5, "Space disaster")
            self.apply_market_effect(["Technology", "Defense"], 0.93, 3, "Space sector contagion")

        elif r == 18:
            self.money += 5000000
            self.show_event("Political Endorsement!", "You 'accidentally' did the salute of a hated Austrian politician in public. The president loved it and hired you into the government. +$5,000,000")
            self.apply_market_effect(["Finance", "Defense"], 1.05, 2, "Government contracts")

        elif r == 19:
            self.money -= 10000000
            self.show_event("Lawsuit Fail!", "You sued a local news outlet for talking badly about you — but forgot about free speech. Lose $10,000,000.")
            self.apply_market_effect(["Entertainment"], 0.94, 2, "Media coverage backlash")

        elif r == 20 and not self.ponzi:
            self.ponzi = True
            self.money -= 20000000
            self.show_event("Ponzi Scheme Exposed!", "Your side Ponzi scheme was discovered by the SEC. 2,000 retirees lost their savings. You lost $20,000,000 in fines.")
            self.apply_market_effect(["Finance"], 0.90, 4, "Ponzi scheme collapse")

        elif r == 21 and not self.oil_spill:
            self.oil_spill = True
            self.money -= 50000000
            self.show_event("Oil Spill!", "Your private tanker had a 'minor' accident off the coast. The ocean is now 40% oil. Pay $50,000,000 in cleanup costs.")
            self.apply_market_effect(["Energy"], 0.88, 5, "Oil spill disaster")

        elif r == 22:
            self.money -= 10000000
            self.show_event("Crypto Rug Pull!", "You launched 'RichCoin' and immediately rug pulled it. Unfortunately you forgot you also invested $10,000,000 in it. Classic.")
            self.apply_market_effect(["Finance", "AI"], 0.93, 2, "Crypto collapse")

        elif r == 23:
            self.money -= 8000000
            self.show_event("Social Media Disaster!", "You accidentally tweeted your offshore bank account password. $8,000,000 vanished within minutes. The tweet got 2 million likes.")
            self.apply_market_effect(["Finance", "Technology"], 0.94, 2, "Data breach panic")

        elif r == 24:
            self.money -= 12000000
            self.show_event("Art Forgery!", "You sold fake Picassos to a Russian oligarch. He found out and sent some very polite gentlemen to collect. Lose $12,000,000.")
            self.apply_market_effect(["Entertainment"], 0.92, 3, "Art fraud scandal")

        elif r == 25 and not self.carbon:
            self.carbon = True
            self.money -= 30000000
            self.show_event("Carbon Credits Scam!", "You sold fake carbon credits to 47 Fortune 500 companies. The EPA found out. Lose $30,000,000. The planet is still dying.")
            self.apply_market_effect(["Energy"], 0.91, 4, "Environmental fraud")

        elif r == 26 and not self.insider_trading:
            self.insider_trading = True
            self.money -= 35000000
            self.show_event("Insider Trading!", "You got caught insider trading NVIDIA stock right before earnings. The SEC fined you $35,000,000. Worth it honestly.")
            self.apply_market_effect(["AI", "Finance"], 0.89, 4, "Insider trading scandal")

        elif r == 27:
            self.money -= 15000000
            self.show_event("Hitman Mishap!", "You hired a hitman to deal with a business rival. He was an undercover FBI agent. Pay $15,000,000 in legal fees. Your rival is fine.")
            self.apply_market_effect(["Defense"], 0.93, 2, "Criminal investigation")

        elif r == 28:
            self.money -= 20000000
            self.show_event("Casino Money Laundering!", "You used a casino to launder money. Casinos report large cash transactions. The IRS called. Lose $20,000,000.")
            self.apply_market_effect(["Finance", "Entertainment"], 0.91, 3, "Money laundering probe")

        elif r == 29:
            self.money -= 10000000
            self.show_event("Lobbyist Caught!", "Your lobbyist was filmed handing a suitcase of cash to a senator in broad daylight. Lose $10,000,000. The senator kept the money.")
            self.apply_market_effect(["Finance", "Defense"], 0.93, 2, "Political corruption scandal")

        elif r == 30:
            self.money -= 5000000
            self.show_event("Drunk Pilot!", "Your personal pilot landed your private jet on a busy highway after one too many in-flight drinks. Pay $5,000,000 in damages.")

        elif r == 31:
            self.money -= 25000000
            self.show_event("Hostile Takeover Attempt!", "A larger corporation tried a hostile takeover of your assets. You survived, but spent $25,000,000 in legal defense. They'll be back.")
            self.apply_market_effect(["Finance"], 1.04, 2, "M&A activity surge")

        elif r == 32:
            self.money -= 7000000
            self.show_event("Bribed the Wrong Judge!", "You bribed a judge but got the wrong courtroom. You needed room 2B, not 2A. Lose $7,000,000. The case is still ongoing.")
            self.apply_market_effect(["Finance"], 0.96, 1, "Legal uncertainty")

        elif r == 33:
            self.money -= 15000000
            self.show_event("Climate Lawsuit!", "You lobbied against climate regulations for 20 years. 47 Pacific island nations just sued you. Lose $15,000,000. Oops.")
            self.apply_market_effect(["Energy"], 0.92, 3, "Climate litigation")
            self.apply_market_effect(["Retail"], 0.96, 2, "Consumer backlash")

        elif r == 34 and not self.pandemic:
            self.pandemic = True
            self.money *= 0.60
            self.show_event("Pandemic Investment!", "You invested your entire liquid assets into a company selling horse dewormer as a COVID cure. Lose 40% of your money. No refunds.")
            self.apply_market_effect(["Healthcare"], 0.88, 3, "Medical misinformation")

        self.market.money = self.money

    # =========================================================
    # EVENT POPUP
    # =========================================================

    def show_event(self, title, text):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg="#0e1117")
        popup.geometry("440x220")
        popup.grab_set()
        popup.resizable(False, False)

        tk.Label(popup, text=title, font=("Arial", 13, "bold"),
                 bg="#0e1117", fg="#ff4444").pack(pady=(18, 6))

        tk.Label(popup, text=text, font=("Arial", 10),
                 bg="#0e1117", fg="white", wraplength=400,
                 justify="center").pack(pady=6, padx=20)

        tk.Button(popup, text="OK", bg="#1e2130", fg="#00ff90",
                  relief="flat", font=("Arial", 10), padx=24, pady=4,
                  command=popup.destroy).pack(pady=12)

        self.update_status()

    # =========================================================
    # REVOLUTION EVENT
    # =========================================================

    def show_revolution_event(self):
        popup = tk.Toplevel(self.root)
        popup.title("Socialist Revolution!")
        popup.configure(bg="#0e1117")
        popup.geometry("440x240")
        popup.grab_set()
        popup.resizable(False, False)

        tk.Label(popup, text="Socialist Revolution!", font=("Arial", 13, "bold"),
                 bg="#0e1117", fg="#ff4444").pack(pady=(18, 6))

        tk.Label(popup,
                 text="While you were on vacation a socialist revolution erupted.\nYou are forced to split your money with the people.\nAccept, or face the consequences...",
                 font=("Arial", 10), bg="#0e1117", fg="white",
                 wraplength=400, justify="center").pack(pady=6, padx=20)

        btn_frame = tk.Frame(popup, bg="#0e1117")
        btn_frame.pack(pady=12)

        def accept():
            self.revolution = False
            self.money = 10000
            self.market.money = self.money
            self.update_status()
            self.log_event("You accepted the revolution. Money reduced to $10,000.")
            popup.destroy()

        def decline():
            self.revolution = False
            self.running = False
            self.log_event("You refused the revolution. They came for you...")
            popup.destroy()
            self.root.after(1500, self._show_end_screen)

        tk.Button(btn_frame, text="Accept", bg="#1e2130", fg="#00ff90",
                  relief="flat", font=("Arial", 10), padx=18, pady=4,
                  command=accept).pack(side="left", padx=12)

        tk.Button(btn_frame, text="Decline (Risk Death)", bg="#1e2130", fg="#ff4444",
                  relief="flat", font=("Arial", 10), padx=18, pady=4,
                  command=decline).pack(side="left", padx=12)

    # =========================================================
    # MARKET EFFECTS
    # =========================================================

    def apply_market_effect(self, categories, multiplier, days, label):
        self.market_effects.append({
            "categories": categories,
            "multiplier": multiplier,
            "days_left":  days,
            "label":      label,
        })
        direction = "📈 boosting" if multiplier > 1 else "📉 crashing"
        cats = ", ".join(categories) if "ALL" not in categories else "ALL"
        self.log_event(f"Market effect: {cats} stocks {direction} for {days} days ({label})")

    # =========================================================
    # NYT SUBSCRIPTION
    # =========================================================

    def subscription_tick(self):
        if not self.subscription or not self.running:
            return
        self.money -= 1
        self.market.money = self.money
        self.update_status()
        self.root.after(1000, self.subscription_tick)

    # =========================================================
    # WORK / CASINO
    # =========================================================

    def work(self):
        gain = random.randint(1000, 50000)
        self.money += gain
        self.market.money = self.money
        self.log_event(f"You worked and earned ${gain:,}")
        self.update_status()

    def casino(self):
        bet = random.randint(1000, 50000)
        c1, c2, c3 = random.randint(0,9), random.randint(0,9), random.randint(0,9)
        self.log_event(f"Rolled {c1}-{c2}-{c3}")
        if c1 == c2 == c3:
            win = bet * 100
            self.money += win
            self.log_event(f"JACKPOT! +${win:,}")
        else:
            self.money -= bet
            self.log_event(f"Lost ${bet:,}")
        self.market.money = self.money
        self.update_status()

    # =========================================================
    # STOCK PRICE MOVEMENT
    # =========================================================

    def update_stock_prices(self):
        for name, data in self.market.stocks.items():
            if data["returns"]:
                idx = data["return_index"] % len(data["returns"])
                change = 1 + data["returns"][idx]
                data["return_index"] += 1
            else:
                change = random.uniform(0.92, 1.08)
            cat = data.get("category", "Custom")
            for effect in self.market_effects:
                if "ALL" in effect["categories"] or cat in effect["categories"]:
                    change *= effect["multiplier"]
            data["price"] = max(0.01, data["price"] * change)
            data["history"].append(data["price"])
        for effect in self.market_effects:
            effect["days_left"] -= 1
            if effect["days_left"] == 0:
                self.log_event(f"Market stabilising: {effect['label']} effect has ended.")
        self.market_effects = [e for e in self.market_effects if e["days_left"] > 0]

    # =========================================================
    # STOCK MARKET WINDOW
    # =========================================================

    def open_stock_market(self):
        self.stock_window = tk.Toplevel(self.root)
        self.stock_window.title("Stock Market")
        self.stock_window.configure(bg="#0e1117")
        self.stock_window.geometry("680x700")

        tk.Label(self.stock_window, text="Stock Market",
                 font=("Arial", 16), bg="#0e1117", fg="white").pack(pady=8)

        cat_outer = tk.Frame(self.stock_window, bg="#0e1117")
        cat_outer.pack(fill="x", padx=10, pady=4)

        for cat in ["All"] + list(STOCK_CATEGORIES.keys()) + ["Custom"]:
            tk.Button(cat_outer, text=cat, bg="#1e2130", fg="#00ff90",
                      activebackground="#00ff90", activeforeground="#0e1117",
                      font=("Arial", 8), relief="flat", padx=6, pady=3,
                      command=lambda c=cat: self.set_category(c)).pack(side="left", padx=2)

        list_frame = tk.Frame(self.stock_window, bg="#0e1117")
        list_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self._canvas = tk.Canvas(list_frame, bg="#0e1117", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self._canvas.yview)
        self.stock_frame = tk.Frame(self._canvas, bg="#0e1117")
        self.stock_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.create_window((0, 0), window=self.stock_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.refresh_market()

        tk.Label(self.stock_window, text="Create Custom Stock",
                 bg="#0e1117", fg="white").pack(pady=(8, 2))

        entry_frame = tk.Frame(self.stock_window, bg="#0e1117")
        entry_frame.pack(pady=4)

        self.stock_name  = tk.Entry(entry_frame, width=10)
        self.stock_price = tk.Entry(entry_frame, width=8)
        self.stock_name.insert(0,  "Name")
        self.stock_price.insert(0, "Price")

        self.custom_category_var = tk.StringVar(value="Custom")
        ttk.Combobox(entry_frame, textvariable=self.custom_category_var,
                     values=list(STOCK_CATEGORIES.keys()) + ["Custom"],
                     width=12, state="readonly").pack(side="left", padx=4)

        self.stock_name.pack(side="left", padx=4)
        self.stock_price.pack(side="left", padx=4)
        tk.Button(entry_frame, text="Create", command=self.create_stock).pack(side="left", padx=4)

    def set_category(self, category):
        self.current_category = category
        self.refresh_market()

    def refresh_market(self):
        for widget in self.stock_frame.winfo_children():
            widget.destroy()
        self.stock_labels = {}
        for name, data in self.market.stocks.items():
            cat = data.get("category", "Custom")
            if self.current_category != "All" and cat != self.current_category:
                continue
            row = tk.Frame(self.stock_frame, bg="#0e1117")
            row.pack(fill="x", pady=2, padx=4)
            tk.Label(row, text=f"[{cat}]", width=12, anchor="w",
                     fg="#555577", bg="#0e1117", font=("Arial", 8)).pack(side="left")
            label = tk.Label(row, text=self._stock_text(name, data),
                             width=36, anchor="w", fg="#00ff90", bg="#0e1117",
                             font=("Arial", 10))
            label.pack(side="left")
            label.bind("<Button-1>", lambda e, s=name: self.show_stock_graph(s))
            self.stock_labels[name] = label
            tk.Button(row, text="Buy", bg="#1e2130", fg="white", relief="flat",
                      command=lambda s=name: self.buy_stock(s)).pack(side="left", padx=2)
            tk.Button(row, text="Sell", bg="#1e2130", fg="white", relief="flat",
                      command=lambda s=name: self.sell_stock(s)).pack(side="left", padx=2)

    def _stock_text(self, name, data):
        return f"{name}   ${data['price']:,.2f}   Shares: {data['shares']}"

    def update_market_labels(self):
        for name, label in self.stock_labels.items():
            if name in self.market.stocks:
                try:
                    label.config(text=self._stock_text(name, self.market.stocks[name]))
                except tk.TclError:
                    pass

    def show_stock_graph(self, stock):
        history = self.market.stocks[stock]["history"]
        plt.figure(figsize=(9, 4))
        plt.plot(history, color="#00ff90", linewidth=1)
        plt.title(stock + " Price History", color="white")
        plt.xlabel("Days", color="white")
        plt.ylabel("Price ($)", color="white")
        plt.gca().set_facecolor("#0e1117")
        plt.gcf().set_facecolor("#0e1117")
        plt.tick_params(colors="white")
        plt.tight_layout()
        plt.show()

    def buy_stock(self, name):
        result = self.market.buy_stock(name, 1)
        self.money = self.market.money
        self.log_event(result)
        self.update_status()
        self.refresh_market()

    def sell_stock(self, name):
        result = self.market.sell_stock(name, 1)
        self.money = self.market.money
        self.log_event(result)
        self.update_status()
        self.refresh_market()

    def create_stock(self):
        name = self.stock_name.get().strip()
        if not name or name == "Name":
            self.log_event("Enter a stock name")
            return
        try:
            price = float(self.stock_price.get())
        except ValueError:
            self.log_event("Invalid price")
            return
        if price < 1:
            self.log_event("Price must be at least $1")
            return
        result = self.market.create_stock(name, price, self.custom_category_var.get())
        self.log_event(result)
        self.refresh_market()

# -----------------------------
# RUN GAME
# -----------------------------

root = tk.Tk()
game = DebtClicker(root)
root.mainloop()
