import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import threading
import matplotlib.pyplot as plt
import yfinance as yf

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

# Fallback random price ranges per category
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
        self.root.geometry("500x700")

        self.money = 100000000
        self.days = 0
        self.running = False
        self.current_category = "All"
        self.stock_labels = {}

        # Event state flags
        self.epstein      = False
        self.subscription = False
        self.revolution   = True
        self.pet          = True
        self.mansion      = True
        self.family       = True
        self.company      = True
        self.rich_relative= True
        self.space        = False

        # Active market effects: list of {"categories": [...], "multiplier": float, "days_left": int, "label": str}
        self.market_effects = []

        self.market = StockMarket()
        self.market.money = self.money

        # Build ticker lookup and create all stocks with random starting prices
        self.tickers = {}
        for category, stocks in STOCK_CATEGORIES.items():
            lo, hi = CATEGORY_PRICE_RANGES.get(category, (10, 500))
            for name, ticker in stocks.items():
                self.tickers[name] = ticker
                starting_price = round(random.uniform(lo, hi), 2)
                self.market.create_stock(name, starting_price, category)

        self.setup_gui()

    # -----------------------------
    # GUI
    # -----------------------------

    def setup_gui(self):

        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=10)

        self.money_label = tk.Label(self.status_frame, font=("Arial", 14))
        self.money_label.pack()

        self.day_label = tk.Label(self.status_frame, font=("Arial", 14))
        self.day_label.pack()

        action_frame = tk.Frame(self.root)
        action_frame.pack()

        tk.Button(action_frame, text="Start Game",   command=self.start_game).pack(pady=5)
        tk.Button(action_frame, text="Work",         command=self.work).pack(pady=5)
        tk.Button(action_frame, text="Casino",       command=self.casino).pack(pady=5)
        tk.Button(action_frame, text="Stock Market", command=self.open_stock_market).pack(pady=5)

        self.log = scrolledtext.ScrolledText(self.root, height=20, state="disabled")
        self.log.pack(fill="both", expand=True)

        self.update_status()

    # -----------------------------
    # LOG
    # -----------------------------

    def log_event(self, msg):
        self.log.config(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state="disabled")

    def update_status(self):
        self.money_label.config(text=f"Money: ${int(self.money):,}")
        self.day_label.config(text=f"Days Survived: {self.days}")

    # -----------------------------
    # GAME START
    # -----------------------------

    def start_game(self):

        self.money = 100000000
        self.days = 0
        self.running = True
        self.market.money = self.money

        # Reset event flags
        self.epstein       = False
        self.subscription  = False
        self.revolution    = True
        self.pet           = True
        self.mansion       = True
        self.family        = True
        self.company       = True
        self.rich_relative = True
        self.space         = False
        self.market_effects = []

        self.log_event("Your financial empire begins its slow decline...")
        self.log_event("Fetching live stock data for all markets...")
        self.update_status()

        threading.Thread(target=self.fetch_real_stock_data, daemon=True).start()

    # -----------------------------
    # FETCH REAL STOCK DATA (batch)
    # -----------------------------

    def fetch_real_stock_data(self):

        all_tickers = list(self.tickers.values())

        try:
            raw = yf.download(
                all_tickers,
                period="1y",
                auto_adjust=True,
                progress=False,
                threads=True
            )

            close = raw["Close"]
            loaded = 0

            for name, ticker in self.tickers.items():
                try:
                    series = close[ticker].dropna()
                    if series.empty:
                        continue

                    history = [float(p) for p in series]
                    current_price = history[-1]
                    returns = series.pct_change().dropna().tolist()

                    self.market.stocks[name]["price"]        = current_price
                    self.market.stocks[name]["history"]      = history
                    self.market.stocks[name]["returns"]      = returns
                    self.market.stocks[name]["return_index"] = 0

                    loaded += 1

                except Exception:
                    pass

            self.root.after(0, lambda: self.log_event(f"Loaded {loaded} stocks with full price history."))

        except Exception as e:
            self.root.after(0, lambda: self.log_event(f"Data fetch failed: {e}. Using simulated prices."))

        self.root.after(0, self.main_loop)
        self.root.after(0, self.realtime_tick)

    # -----------------------------
    # REALTIME PRICE TICK (~1s)
    # -----------------------------

    def realtime_tick(self):

        if not self.running:
            return

        for name, data in self.market.stocks.items():
            # Real stocks: tiny intraday noise around their last known price
            # Custom / unloaded stocks: slightly larger random walk
            if data["returns"]:
                noise = random.gauss(1.0, 0.0015)
            else:
                noise = random.gauss(1.0, 0.004)

            data["price"] = max(0.01, data["price"] * noise)

        # Update labels without recreating widgets
        if hasattr(self, "stock_window") and self.stock_window.winfo_exists():
            self.update_market_labels()

        self.root.after(1000, self.realtime_tick)

    # -----------------------------
    # MAIN LOOP (every 5s = 1 game day)
    # -----------------------------

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
            return

        self.root.after(5000, self.main_loop)

    # -----------------------------
    # DAILY MONEY LOSS
    # -----------------------------

    def lose_money(self):
        m = self.money
        if m < 50:
            lost = random.randint(1, 25)
        elif m < 100:
            lost = random.randint(10, 50)
        elif m < 1000:
            lost = random.randint(100, 500)
        elif m < 10000:
            lost = random.randint(100, 1000)
        elif m < 100000:
            lost = random.randint(1000, 10000)
        else:
            lost = random.randint(100, 10000000)
        self.money -= lost
        self.market.money = self.money
        self.log_event(f"Lost ${lost:,}")
        self.update_status()

    # -----------------------------
    # RANDOM EVENTS
    # -----------------------------

    def random_events(self):
        r = random.randint(1, 50)  # ~38% chance an event fires each day

        if r == 1 and self.family:
            self.family = False
            self.money /= 2
            self.show_event("Gold Digger!",
                "Oh no! Your spouse is a gold-digger and has taken HALF your money!")
            self.apply_market_effect(["Finance"], 0.93, 3, "Divorce scandal")

        elif r == 2:
            self.money *= 0.30
            self.show_event("Tax Fraud!",
                "You filed a fraudulent tax report. The IRS found out — lose 70% of your money!")
            self.apply_market_effect(["Finance"], 0.91, 2, "Tax fraud scandal")

        elif r == 3 and self.company:
            self.money -= 50000
            self.show_event("Factory Incident!",
                "One of your child workers at your illegal factory got mutilated by machinery. Pay $50,000 to cover it up.")
            self.apply_market_effect(["Retail", "Automotive"], 0.94, 2, "Factory scandal")

        elif r == 4 and self.rich_relative:
            self.rich_relative = False
            self.money += 1000000
            self.show_event("Inheritance!",
                "Your Grandma died! She left you $1,000,000. RIP.")

        elif r == 5:
            for name in self.market.stocks:
                self.market.stocks[name]["shares"] = 0
            self.show_event("Betrayal!",
                "Your financial advisor betrayed you and liquidated ALL of your stock shares!")
            self.apply_market_effect(["Finance"], 0.92, 3, "Advisor betrayal")

        elif r == 6:
            if random.randint(1, 5) == 1:
                self.money += 100000
                self.show_event("Lucky Hacker!",
                    "Someone stole your credit ID and went gambling — and WON. They sent you $100,000 out of guilt.")
            else:
                self.money -= 500000
                self.show_event("Identity Theft!",
                    "Someone stole your credit ID and went gambling. You lost $500,000.")
            self.apply_market_effect(["Finance", "Technology"], 0.94, 2, "Identity theft")

        elif r == 7 and not self.epstein:
            self.epstein = True
            self.money -= 10000000
            self.show_event("Island Discovered...",
                "Your ventures to Epstein's island have been discovered. Lose $10,000,000 to cover it up.")
            self.apply_market_effect(["Entertainment", "Finance"], 0.88, 4, "Epstein scandal")

        elif r == 8:
            self.money -= 5000000
            self.show_event("JFK Investigation!",
                "You are under investigation for the assassination of JFK. Your assets are temporarily frozen — lose $5,000,000.")
            self.apply_market_effect(["Defense"], 0.91, 3, "Government investigation")

        elif r == 9 and self.pet:
            self.pet = False
            self.money -= 1000
            self.show_event("Pet Incident...",
                "Your pet wandered into the oven. Your uneducated servant unknowingly turned it on. Something smells burnt... (pet is gone)")

        elif r == 10:
            self.money += 2000000
            self.show_event("Diamond in the Rough!",
                "You accidentally put a pencil in a pressure cooker and it turned into a diamond! A diamond also went missing from the Louvre... +$2,000,000")

        elif r == 11 and self.family:
            self.money -= 1000000
            self.show_event("Blender Incident!",
                "Your child accidentally stuck their entire arm into a running blender. Pay $1,000,000 in healthcare bills.")
            self.apply_market_effect(["Healthcare"], 1.04, 2, "Medical lawsuit windfall")

        elif r == 12 and self.revolution:
            self.apply_market_effect(["ALL"], 0.85, 5, "Socialist revolution")
            self.show_revolution_event()
            return

        elif r == 13 and self.company:
            self.company = False
            self.money -= 1000000
            self.show_event("Factory Shutdown!",
                "All your foreign investments in underage factory workers are exposed. Workers freed — you pay $1,000,000 in damages.")
            self.apply_market_effect(["Retail", "Automotive"], 0.92, 3, "Factory shutdown")

        elif r == 14 and self.mansion:
            self.mansion = False
            self.show_event("Cuba Invades!",
                "The island your private mansion sits on was just invaded by Cuba. You lost your mansion.")
            self.apply_market_effect(["Defense"], 1.06, 3, "Geopolitical tension")
            self.apply_market_effect(["Space"], 0.93, 2, "Airspace conflict")

        elif r == 15 and not self.subscription:
            self.subscription = True
            self.show_event("NYT Subscription!",
                "You accidentally subscribed to the New York Times. You now lose $1 every second. Cancel? They don't have a cancel button.")
            self.apply_market_effect(["Entertainment"], 0.96, 1, "Media disruption")
            self.subscription_tick()

        elif r == 16:
            self.money -= 10000000
            self.show_event("Weapons Deal",
                "You are funding a genocide. Pay $10,000,000 in weapons and supplies.")
            self.apply_market_effect(["Defense"], 1.08, 3, "Weapons demand surge")
            self.apply_market_effect(["Energy"], 0.91, 4, "War zone instability")

        elif r == 17 and not self.space:
            self.space = True
            self.money -= 500000000
            self.show_event("Space Program Disaster!",
                "You created a space program. On the first launch, the rocket explodes and kills everyone on board. Pay $500,000,000 in damages.")
            self.apply_market_effect(["Space"], 0.75, 5, "Space disaster")
            self.apply_market_effect(["Technology", "Defense"], 0.93, 3, "Space sector contagion")

        elif r == 18:
            self.money += 5000000
            self.show_event("Political Endorsement!",
                "You 'accidentally' did the salute of a hated Austrian politician in public. The president loved it and hired you into the government. +$5,000,000")
            self.apply_market_effect(["Finance", "Defense"], 1.05, 2, "Government contracts")

        elif r == 19:
            self.money -= 10000000
            self.show_event("Lawsuit Fail!",
                "You sued a local news outlet for talking badly about you — but forgot about free speech. Lose $10,000,000.")
            self.apply_market_effect(["Entertainment"], 0.94, 2, "Media coverage backlash")

        self.market.money = self.money

    # -----------------------------
    # EVENT POPUP
    # -----------------------------

    def show_event(self, title, text):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg="#0e1117")
        popup.geometry("420x210")
        popup.grab_set()
        popup.resizable(False, False)

        tk.Label(
            popup, text=title,
            font=("Arial", 13, "bold"), bg="#0e1117", fg="#ff4444"
        ).pack(pady=(18, 6))

        tk.Label(
            popup, text=text,
            font=("Arial", 10), bg="#0e1117", fg="white",
            wraplength=380, justify="center"
        ).pack(pady=6, padx=20)

        tk.Button(
            popup, text="OK",
            bg="#1e2130", fg="#00ff90", relief="flat",
            font=("Arial", 10), padx=24, pady=4,
            command=popup.destroy
        ).pack(pady=12)

        self.update_status()

    # -----------------------------
    # REVOLUTION EVENT (accept / decline)
    # -----------------------------

    def show_revolution_event(self):
        popup = tk.Toplevel(self.root)
        popup.title("Socialist Revolution!")
        popup.configure(bg="#0e1117")
        popup.geometry("420x230")
        popup.grab_set()
        popup.resizable(False, False)

        tk.Label(
            popup, text="Socialist Revolution!",
            font=("Arial", 13, "bold"), bg="#0e1117", fg="#ff4444"
        ).pack(pady=(18, 6))

        tk.Label(
            popup,
            text="While you were on vacation a socialist revolution erupted.\nYou are forced to split your money with the people.\nAccept, or face the consequences...",
            font=("Arial", 10), bg="#0e1117", fg="white",
            wraplength=380, justify="center"
        ).pack(pady=6, padx=20)

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
            self.show_event("Game Over", "You refused the revolution. The people came for you. Nobody attended your funeral.")

        tk.Button(
            btn_frame, text="Accept",
            bg="#1e2130", fg="#00ff90", relief="flat",
            font=("Arial", 10), padx=18, pady=4,
            command=accept
        ).pack(side="left", padx=12)

        tk.Button(
            btn_frame, text="Decline (Risk Death)",
            bg="#1e2130", fg="#ff4444", relief="flat",
            font=("Arial", 10), padx=18, pady=4,
            command=decline
        ).pack(side="left", padx=12)

    # -----------------------------
    # APPLY MARKET EFFECT HELPER
    # -----------------------------

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

    # -----------------------------
    # NYT SUBSCRIPTION TICK
    # -----------------------------

    def subscription_tick(self):
        if not self.subscription or not self.running:
            return
        self.money -= 1
        self.market.money = self.money
        self.update_status()
        self.root.after(1000, self.subscription_tick)

    # -----------------------------
    # WORK
    # -----------------------------

    def work(self):
        gain = random.randint(1000, 50000)
        self.money += gain
        self.market.money = self.money
        self.log_event(f"You worked and earned ${gain:,}")
        self.update_status()

    # -----------------------------
    # CASINO
    # -----------------------------

    def casino(self):
        bet = random.randint(1000, 50000)
        c1, c2, c3 = random.randint(0,9), random.randint(0,9), random.randint(0,9)
        self.log_event(f"Rolled {c1}-{c2}-{c3}")
        if c1 == c2 == c3:
            win = bet * 100
            self.money += win
            self.log_event(f"JACKPOT ${win:,}")
        else:
            self.money -= bet
            self.log_event(f"Lost ${bet:,}")
        self.market.money = self.money
        self.update_status()

    # -----------------------------
    # DAILY STOCK PRICE MOVEMENT
    # -----------------------------

    def update_stock_prices(self):
        for name, data in self.market.stocks.items():
            if data["returns"]:
                idx = data["return_index"] % len(data["returns"])
                change = 1 + data["returns"][idx]
                data["return_index"] += 1
            else:
                change = random.uniform(0.92, 1.08)

            # Apply any active market effects for this stock's category
            cat = data.get("category", "Custom")
            for effect in self.market_effects:
                if "ALL" in effect["categories"] or cat in effect["categories"]:
                    change *= effect["multiplier"]

            data["price"] = max(0.01, data["price"] * change)
            data["history"].append(data["price"])

        # Tick down effects and log expiry
        for effect in self.market_effects:
            effect["days_left"] -= 1
            if effect["days_left"] == 0:
                self.log_event(f"Market stabilising: {effect['label']} effect has ended.")
        self.market_effects = [e for e in self.market_effects if e["days_left"] > 0]

    # -----------------------------
    # STOCK MARKET WINDOW
    # -----------------------------

    def open_stock_market(self):

        self.stock_window = tk.Toplevel(self.root)
        self.stock_window.title("Stock Market")
        self.stock_window.configure(bg="#0e1117")
        self.stock_window.geometry("680x700")

        tk.Label(
            self.stock_window, text="Stock Market",
            font=("Arial", 16), bg="#0e1117", fg="white"
        ).pack(pady=8)

        # Category filter buttons
        cat_outer = tk.Frame(self.stock_window, bg="#0e1117")
        cat_outer.pack(fill="x", padx=10, pady=4)

        for cat in ["All"] + list(STOCK_CATEGORIES.keys()) + ["Custom"]:
            tk.Button(
                cat_outer, text=cat,
                bg="#1e2130", fg="#00ff90",
                activebackground="#00ff90", activeforeground="#0e1117",
                font=("Arial", 8), relief="flat", padx=6, pady=3,
                command=lambda c=cat: self.set_category(c)
            ).pack(side="left", padx=2)

        # Scrollable stock list
        list_frame = tk.Frame(self.stock_window, bg="#0e1117")
        list_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self._canvas = tk.Canvas(list_frame, bg="#0e1117", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self._canvas.yview)

        self.stock_frame = tk.Frame(self._canvas, bg="#0e1117")
        self.stock_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )

        self._canvas.create_window((0, 0), window=self.stock_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind_all("<MouseWheel>", lambda e: self._canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.refresh_market()

        # Create custom stock
        tk.Label(self.stock_window, text="Create Custom Stock", bg="#0e1117", fg="white").pack(pady=(8, 2))

        entry_frame = tk.Frame(self.stock_window, bg="#0e1117")
        entry_frame.pack(pady=4)

        self.stock_name  = tk.Entry(entry_frame, width=10)
        self.stock_price = tk.Entry(entry_frame, width=8)
        self.stock_name.insert(0,  "Name")
        self.stock_price.insert(0, "Price")

        self.custom_category_var = tk.StringVar(value="Custom")
        category_dropdown = ttk.Combobox(
            entry_frame,
            textvariable=self.custom_category_var,
            values=list(STOCK_CATEGORIES.keys()) + ["Custom"],
            width=12, state="readonly"
        )

        self.stock_name.pack(side="left", padx=4)
        self.stock_price.pack(side="left", padx=4)
        category_dropdown.pack(side="left", padx=4)
        tk.Button(entry_frame, text="Create", command=self.create_stock).pack(side="left", padx=4)

    # -----------------------------
    # CATEGORY FILTER
    # -----------------------------

    def set_category(self, category):
        self.current_category = category
        self.refresh_market()

    # -----------------------------
    # REBUILD STOCK WIDGETS
    # -----------------------------

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

            tk.Label(
                row, text=f"[{cat}]",
                width=12, anchor="w",
                fg="#555577", bg="#0e1117",
                font=("Arial", 8)
            ).pack(side="left")

            label = tk.Label(
                row,
                text=self._stock_text(name, data),
                width=36, anchor="w",
                fg="#00ff90", bg="#0e1117",
                font=("Arial", 10)
            )
            label.pack(side="left")
            label.bind("<Button-1>", lambda e, s=name: self.show_stock_graph(s))
            self.stock_labels[name] = label

            tk.Button(
                row, text="Buy",
                bg="#1e2130", fg="white", relief="flat",
                command=lambda s=name: self.buy_stock(s)
            ).pack(side="left", padx=2)

            tk.Button(
                row, text="Sell",
                bg="#1e2130", fg="white", relief="flat",
                command=lambda s=name: self.sell_stock(s)
            ).pack(side="left", padx=2)

    # -----------------------------
    # UPDATE LABEL TEXT ONLY (fast path for realtime)
    # -----------------------------

    def _stock_text(self, name, data):
        return f"{name}   ${data['price']:,.2f}   Shares: {data['shares']}"

    def update_market_labels(self):
        for name, label in self.stock_labels.items():
            if name in self.market.stocks:
                try:
                    label.config(text=self._stock_text(name, self.market.stocks[name]))
                except tk.TclError:
                    pass

    # -----------------------------
    # GRAPH
    # -----------------------------

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

    # -----------------------------
    # BUY / SELL
    # -----------------------------

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

    # -----------------------------
    # CREATE CUSTOM STOCK
    # -----------------------------

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

        category = self.custom_category_var.get()
        result = self.market.create_stock(name, price, category)
        self.log_event(result)
        self.refresh_market()

# -----------------------------
# RUN GAME
# -----------------------------

root = tk.Tk()
game = DebtClicker(root)
root.mainloop()
