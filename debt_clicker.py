import tkinter as tk
from tkinter import scrolledtext
import random
import threading
import matplotlib.pyplot as plt
import yfinance as yf

# -----------------------------
# STOCK MARKET SYSTEM
# -----------------------------

class StockMarket:

    def __init__(self):
        self.stocks = {}
        self.money = 0

    def create_stock(self, name, price):

        if price < 100:
            return "Starting price must be at least $100"

        self.stocks[name] = {
            "price": price,
            "shares": 0,
            "history": [price]
        }

        return f"{name} created at ${price}"

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

        self.market = StockMarket()
        self.market.money = self.money

        # Ticker mapping for real market data
        self.tickers = {
            "NVIDIA": "NVDA",
            "Microsoft": "MSFT",
            "Apple": "AAPL",
            "Amazon": "AMZN"
        }

        # Base stocks (prices updated on game start from real data)
        self.market.create_stock("NVIDIA", 200)
        self.market.create_stock("Microsoft", 500)
        self.market.create_stock("Apple", 270)
        self.market.create_stock("Amazon", 250)

        self.setup_gui()

    # -----------------------------
    # GUI
    # -----------------------------

    def setup_gui(self):

        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=10)

        self.money_label = tk.Label(self.status_frame, font=("Arial",14))
        self.money_label.pack()

        self.day_label = tk.Label(self.status_frame, font=("Arial",14))
        self.day_label.pack()

        action_frame = tk.Frame(self.root)
        action_frame.pack()

        tk.Button(action_frame,text="Start Game",command=self.start_game).pack(pady=5)
        tk.Button(action_frame,text="Work",command=self.work).pack(pady=5)
        tk.Button(action_frame,text="Casino",command=self.casino).pack(pady=5)
        tk.Button(action_frame,text="Stock Market",command=self.open_stock_market).pack(pady=5)

        self.log = scrolledtext.ScrolledText(self.root,height=20,state="disabled")
        self.log.pack(fill="both",expand=True)

        self.update_status()

    # -----------------------------
    # LOG
    # -----------------------------

    def log_event(self,msg):

        self.log.config(state="normal")
        self.log.insert(tk.END,msg+"\n")
        self.log.see(tk.END)
        self.log.config(state="disabled")

    # -----------------------------

    def update_status(self):

        self.money_label.config(text=f"Money: ${int(self.money)}")
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
        self.log_event("Fetching live stock data...")
        self.update_status()

        threading.Thread(target=self.fetch_real_stock_data, daemon=True).start()

    # -----------------------------
    # FETCH REAL STOCK DATA
    # -----------------------------

    def fetch_real_stock_data(self):

        for name, ticker in self.tickers.items():
            try:
                hist = yf.Ticker(ticker).history(period="1y")

                if not hist.empty:
                    current_price = hist["Close"].iloc[-1]
                    returns = hist["Close"].pct_change().dropna().tolist()

                    self.market.stocks[name]["price"] = current_price
                    self.market.stocks[name]["history"] = [current_price]
                    self.market.stocks[name]["returns"] = returns
                    self.market.stocks[name]["return_index"] = 0

                    self.root.after(0, lambda n=name, p=current_price:
                        self.log_event(f"Loaded {n} at ${round(p, 2)}"))

            except Exception as e:
                self.root.after(0, lambda n=name, err=e:
                    self.log_event(f"Could not load {n}: {err}"))

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

        self.root.after(5000,self.main_loop)

    # -----------------------------
    # DAILY MONEY LOSS
    # -----------------------------

    def lose_money(self):

        lost = random.randint(100,1000000)

        self.money -= lost
        self.market.money = self.money

        self.log_event(f"Lost ${lost}")

        self.update_status()

    # -----------------------------
    # RANDOM EVENTS
    # -----------------------------

    def random_events(self):

        r = random.randint(1,20)

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

        gain = random.randint(1000,50000)

        self.money += gain
        self.market.money = self.money

        self.log_event(f"You worked and earned ${gain}")

        self.update_status()

    # -----------------------------
    # CASINO
    # -----------------------------

    def casino(self):

        bet = random.randint(1000,50000)

        c1 = random.randint(0,9)
        c2 = random.randint(0,9)
        c3 = random.randint(0,9)

        self.log_event(f"Rolled {c1}-{c2}-{c3}")

        if c1 == c2 == c3:

            win = bet * 100
            self.money += win
            self.log_event(f"JACKPOT ${win}")

        else:

            self.money -= bet
            self.log_event(f"Lost ${bet}")

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

        tk.Label(self.stock_window,text="Market",font=("Arial",16),bg="#0e1117",fg="white").pack(pady=10)

        self.stock_frame = tk.Frame(self.stock_window,bg="#0e1117")
        self.stock_frame.pack()

        self.refresh_market()

        tk.Label(self.stock_window,text="Create Custom Stock",bg="#0e1117",fg="white").pack(pady=10)

        self.stock_name = tk.Entry(self.stock_window)
        self.stock_name.pack()

        self.stock_price = tk.Entry(self.stock_window)
        self.stock_price.pack()

        tk.Button(self.stock_window,text="Create",command=self.create_stock).pack(pady=5)

    # -----------------------------
    # REFRESH STOCK LIST
    # -----------------------------

    def refresh_market(self):

        for widget in self.stock_frame.winfo_children():
            widget.destroy()

        for name,data in self.market.stocks.items():

            row = tk.Frame(self.stock_frame,bg="#0e1117")
            row.pack(pady=3)

            label = tk.Label(
                row,
                text=f"{name}   ${round(data['price'],2)}   Shares:{data['shares']}",
                width=32,
                anchor="w",
                fg="#00ff90",
                bg="#0e1117",
                font=("Arial",11)
            )

            label.pack(side="left")

            label.bind("<Button-1>", lambda e,s=name: self.show_stock_graph(s))

            tk.Button(row,text="Buy",command=lambda s=name:self.buy_stock(s)).pack(side="left")
            tk.Button(row,text="Sell",command=lambda s=name:self.sell_stock(s)).pack(side="left")

    # -----------------------------
    # GRAPH
    # -----------------------------

    def show_stock_graph(self,stock):

        data = self.market.stocks[stock]["history"]

        plt.figure()

        plt.plot(data)

        plt.title(stock + " Price History")
        plt.xlabel("Days")
        plt.ylabel("Price")

        plt.show()

    # -----------------------------
    # BUY / SELL
    # -----------------------------

    def buy_stock(self,name):

        result = self.market.buy_stock(name,1)

        self.money = self.market.money

        self.log_event(result)

        self.update_status()
        self.refresh_market()

    def sell_stock(self,name):

        result = self.market.sell_stock(name,1)

        self.money = self.market.money

        self.log_event(result)

        self.update_status()
        self.refresh_market()

    # -----------------------------
    # CREATE STOCK
    # -----------------------------

    def create_stock(self):

        name = self.stock_name.get()

        try:
            price = float(self.stock_price.get())
        except:
            self.log_event("Invalid price")
            return

        if price < 100:

            self.log_event("Stock must start at $100 or higher")
            return

        result = self.market.create_stock(name,price)

        self.log_event(result)

        self.refresh_market()

# -----------------------------
# RUN GAME
# -----------------------------

root = tk.Tk()
game = DebtClicker(root)
root.mainloop()
