import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt

from constants import STOCK_CATEGORIES


class StockWindowMixin:
    """Stock market window, price updates, graphs, buy/sell, and custom stocks."""

    # =========================================================
    # STOCK PRICE MOVEMENT  (called every game day)
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
            tk.Button(row, text="Buy",  bg="#1e2130", fg="white", relief="flat",
                      command=lambda s=name: self.buy_stock(s)).pack(side="left", padx=2)
            tk.Button(row, text="Sell", bg="#1e2130", fg="white", relief="flat",
                      command=lambda s=name: self.sell_stock(s)).pack(side="left", padx=2)
            if data["shares"] > 0:
                tk.Button(row, text="Pump", bg="#004400", fg="#00ff90", relief="flat",
                          font=("Arial", 8),
                          command=lambda s=name: self.pump_stock(s)).pack(side="left", padx=1)
                tk.Button(row, text="Dump", bg="#440000", fg="#ff4444", relief="flat",
                          font=("Arial", 8),
                          command=lambda s=name: self.dump_stock(s)).pack(side="left", padx=1)

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

    def pump_stock(self, name):
        """Spend $5M to artificially inflate a stock you own."""
        cost = 5_000_000
        if self.money < cost:
            self.log_event(f"Need ${cost:,} to pump {name}")
            return
        self.money -= cost
        self.market.money = self.money
        data = self.market.stocks[name]
        data["price"] *= 1.25
        data["history"].append(data["price"])
        cat = data.get("category", "Custom")
        self.apply_market_effect([cat], 1.12, 3, f"Pump: {name}")
        self.add_transgression(8, 5)
        self.log_event(f"PUMP: Inflated {name} by 25%. Cost ${cost:,}. Transgression +8.")
        self._add_ticker(f"MARKETS: Unusual volume spike detected in {name}...")
        self.update_status()
        self.refresh_market()

    def dump_stock(self, name):
        """Sell all shares at 1.5x price, then crash the stock."""
        data = self.market.stocks[name]
        shares = data["shares"]
        if shares <= 0:
            self.log_event(f"No shares of {name} to dump")
            return
        sale_price = data["price"] * 1.5
        proceeds = int(sale_price * shares)
        self.money += proceeds
        self.market.money = self.money
        data["shares"] = 0
        data["price"] *= 0.55  # crash by 45%
        data["history"].append(data["price"])
        cat = data.get("category", "Custom")
        self.apply_market_effect([cat], 0.85, 4, f"Dump: {name}")
        self.add_transgression(12, 8)
        self.log_event(f"DUMP: Sold {shares} shares of {name} for ${proceeds:,} (1.5x). Stock crashed.")
        self._add_ticker(f"MARKETS: {name} in freefall — mass selloff detected...")
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
