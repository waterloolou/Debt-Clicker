import tkinter as tk
from tkinter import scrolledtext
import random
import threading
import matplotlib.pyplot as plt
import yfinance as yf

# -----------------------------
# STOCK CATEGORIES
# -----------------------------

STOCK_CATEGORIES = {
    "AI": {
        "NVIDIA":       "NVDA",
        "AMD":          "AMD",
        "Palantir":     "PLTR",
        "C3.ai":        "AI",
        "Super Micro":  "SMCI",
        "Arm Holdings": "ARM",
        "SoundHound":   "SOUN",
    },
    "Technology": {
        "Apple":        "AAPL",
        "Microsoft":    "MSFT",
        "Google":       "GOOGL",
        "Meta":         "META",
        "Netflix":      "NFLX",
        "Oracle":       "ORCL",
        "IBM":          "IBM",
        "Qualcomm":     "QCOM",
        "Intel":        "INTC",
        "Salesforce":   "CRM",
        "Snowflake":    "SNOW",
        "Zoom":         "ZM",
    },
    "Energy": {
        "ExxonMobil":   "XOM",
        "Chevron":      "CVX",
        "Shell":        "SHEL",
        "BP":           "BP",
        "ConocoPhillips":"COP",
        "NextEra":      "NEE",
        "Enphase":      "ENPH",
        "SolarEdge":    "SEDG",
        "Schlumberger": "SLB",
    },
    "Finance": {
        "JPMorgan":     "JPM",
        "Goldman Sachs":"GS",
        "Bank of America":"BAC",
        "Morgan Stanley":"MS",
        "Visa":         "V",
        "Mastercard":   "MA",
        "Berkshire":    "BRK-B",
        "BlackRock":    "BLK",
        "Charles Schwab":"SCHW",
        "Coinbase":     "COIN",
        "PayPal":       "PYPL",
        "Robinhood":    "HOOD",
    },
    "Healthcare": {
        "Johnson & Johnson":"JNJ",
        "Pfizer":       "PFE",
        "UnitedHealth": "UNH",
        "Moderna":      "MRNA",
        "Eli Lilly":    "LLY",
        "Merck":        "MRK",
        "AbbVie":       "ABBV",
        "Intuitive Surgical":"ISRG",
    },
    "Retail": {
        "Amazon":       "AMZN",
        "Walmart":      "WMT",
        "Costco":       "COST",
        "Target":       "TGT",
        "McDonald's":   "MCD",
        "Starbucks":    "SBUX",
        "Nike":         "NKE",
        "Home Depot":   "HD",
        "eBay":         "EBAY",
    },
    "Automotive": {
        "Tesla":        "TSLA",
        "Ford":         "F",
        "GM":           "GM",
        "Rivian":       "RIVN",
        "Lucid":        "LCID",
        "Ferrari":      "RACE",
    },
    "Defense": {
        "Lockheed Martin":"LMT",
        "Boeing":       "BA",
        "Raytheon":     "RTX",
        "Northrop Grumman":"NOC",
        "General Dynamics":"GD",
        "L3Harris":     "LHX",
    },
    "Entertainment": {
        "Disney":       "DIS",
        "Spotify":      "SPOT",
        "Roblox":       "RBLX",
        "Warner Bros":  "WBD",
        "Live Nation":  "LYV",
        "Electronic Arts":"EA",
        "Take-Two":     "TTWO",
    },
    "Space": {
        "Rocket Lab":   "RKLB",
        "Virgin Galactic":"SPCE",
        "Intuitive Machines":"LUNR",
        "Redwire":      "RDW",
    },
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
            "price": price,
            "shares": 0,
            "history": [price],
            "category": category,
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

        self.market = StockMarket()
        self.market.money = self.money

        # Build ticker lookup from categories
        self.tickers = {}
        for category, stocks in STOCK_CATEGORIES.items():
            for name, ticker in stocks.items():
                self.tickers[name] = ticker
                self.market.create_stock(name, 100.0, category)

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

            close = raw["Close"] if "Close" in raw.columns.get_level_values(0) else raw

            loaded = 0

            for name, ticker in self.tickers.items():

                try:
                    series = close[ticker].dropna()

                    if series.empty:
                        continue

                    current_price = float(series.iloc[-1])
                    returns = series.pct_change().dropna().tolist()

                    self.market.stocks[name]["price"]        = current_price
                    self.market.stocks[name]["history"]      = [current_price]
                    self.market.stocks[name]["returns"]      = returns
                    self.market.stocks[name]["return_index"] = 0

                    loaded += 1

                except Exception:
                    pass

            self.root.after(0, lambda: self.log_event(f"Loaded {loaded} stocks. Good luck."))

        except Exception as e:
            self.root.after(0, lambda: self.log_event(f"Data fetch failed: {e}. Using simulated prices."))

        self.root.after(0, self.main_loop)

    # -----------------------------
    # MAIN LOOP
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

        lost = random.randint(100, 1000000)

        self.money -= lost
        self.market.money = self.money

        self.log_event(f"Lost ${lost:,}")

        self.update_status()

    # -----------------------------
    # RANDOM EVENTS
    # -----------------------------

    def random_events(self):

        r = random.randint(1, 20)

        if r == 1:
            self.money /= 2
            self.log_event("Divorce took half your fortune")

        if r == 2:
            self.money += 1000000
            self.log_event("A rich relative left you money")

        self.market.money = self.money

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

        c1 = random.randint(0, 9)
        c2 = random.randint(0, 9)
        c3 = random.randint(0, 9)

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
    # STOCK PRICE MOVEMENT
    # -----------------------------

    def update_stock_prices(self):

        for stock in self.market.stocks:

            data = self.market.stocks[stock]

            if "returns" in data and data["returns"]:
                idx = data["return_index"] % len(data["returns"])
                change = 1 + data["returns"][idx]
                data["return_index"] += 1
            else:
                change = random.uniform(0.92, 1.08)

            data["price"] *= change
            data["history"].append(data["price"])

    # -----------------------------
    # STOCK MARKET WINDOW
    # -----------------------------

    def open_stock_market(self):

        self.stock_window = tk.Toplevel(self.root)
        self.stock_window.title("Stock Market")
        self.stock_window.configure(bg="#0e1117")
        self.stock_window.geometry("660x700")

        tk.Label(
            self.stock_window, text="Stock Market",
            font=("Arial", 16), bg="#0e1117", fg="white"
        ).pack(pady=8)

        # Category filter buttons
        cat_outer = tk.Frame(self.stock_window, bg="#0e1117")
        cat_outer.pack(fill="x", padx=10, pady=4)

        categories = ["All"] + list(STOCK_CATEGORIES.keys()) + ["Custom"]

        for cat in categories:
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

        canvas = tk.Canvas(list_frame, bg="#0e1117", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)

        self.stock_frame = tk.Frame(canvas, bg="#0e1117")
        self.stock_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.stock_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self.refresh_market()

        # Create custom stock
        tk.Label(self.stock_window, text="Create Custom Stock", bg="#0e1117", fg="white").pack(pady=(8, 2))

        entry_frame = tk.Frame(self.stock_window, bg="#0e1117")
        entry_frame.pack()

        self.stock_name  = tk.Entry(entry_frame, width=12)
        self.stock_price = tk.Entry(entry_frame, width=10)
        self.stock_name.insert(0, "Name")
        self.stock_price.insert(0, "Price")

        self.stock_name.pack(side="left", padx=4)
        self.stock_price.pack(side="left", padx=4)

        tk.Button(entry_frame, text="Create", command=self.create_stock).pack(side="left", padx=4, pady=6)

    # -----------------------------
    # CATEGORY FILTER
    # -----------------------------

    def set_category(self, category):

        self.current_category = category
        self.refresh_market()

    # -----------------------------
    # REFRESH STOCK LIST
    # -----------------------------

    def refresh_market(self):

        for widget in self.stock_frame.winfo_children():
            widget.destroy()

        for name, data in self.market.stocks.items():

            cat = data.get("category", "Custom")

            if self.current_category != "All" and cat != self.current_category:
                continue

            row = tk.Frame(self.stock_frame, bg="#0e1117")
            row.pack(fill="x", pady=2, padx=4)

            cat_label = tk.Label(
                row, text=f"[{cat}]",
                width=12, anchor="w",
                fg="#888888", bg="#0e1117",
                font=("Arial", 8)
            )
            cat_label.pack(side="left")

            label = tk.Label(
                row,
                text=f"{name}   ${round(data['price'], 2)}   Shares: {data['shares']}",
                width=34, anchor="w",
                fg="#00ff90", bg="#0e1117",
                font=("Arial", 10)
            )
            label.pack(side="left")
            label.bind("<Button-1>", lambda e, s=name: self.show_stock_graph(s))

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
    # GRAPH
    # -----------------------------

    def show_stock_graph(self, stock):

        data = self.market.stocks[stock]["history"]

        plt.figure(figsize=(8, 4))
        plt.plot(data, color="#00ff90")
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

        name = self.stock_name.get()

        try:
            price = float(self.stock_price.get())
        except ValueError:
            self.log_event("Invalid price")
            return

        if price < 100:
            self.log_event("Stock must start at $100 or higher")
            return

        result = self.market.create_stock(name, price, category="Custom")
        self.log_event(result)
        self.refresh_market()

# -----------------------------
# RUN GAME
# -----------------------------

root = tk.Tk()
game = DebtClicker(root)
root.mainloop()
