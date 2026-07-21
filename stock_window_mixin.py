"""
stock_window_mixin.py — Robinhood-style stock market UI
"""
import tkinter as tk
from tkinter import ttk
import random

from constants import STOCK_CATEGORIES


def _draw_sparkline(canvas, history, w=80, h=32):
    """Draw a mini sparkline on a Canvas widget."""
    canvas.delete("all")
    pts = history[-40:] if len(history) > 40 else history
    if len(pts) < 2:
        return
    lo, hi = min(pts), max(pts)
    if lo == hi:
        hi = lo + 1
    pad = 3
    color = "#00c853" if pts[-1] >= pts[0] else "#ff4444"
    xs = [pad + i / (len(pts) - 1) * (w - 2 * pad) for i in range(len(pts))]
    ys = [pad + (1 - (p - lo) / (hi - lo)) * (h - 2 * pad) for p in pts]
    for i in range(len(xs) - 1):
        canvas.create_line(xs[i], ys[i], xs[i + 1], ys[i + 1],
                           fill=color, width=1.5, smooth=True)


def _draw_chart(canvas, history, w, h):
    """Draw a filled area chart on a Canvas widget."""
    canvas.delete("all")
    pts = history[-120:] if len(history) > 120 else history
    if len(pts) < 2:
        return
    lo, hi = min(pts), max(pts)
    if lo == hi:
        hi = lo + 1
    color = "#00c853" if pts[-1] >= pts[0] else "#ff4444"
    fill = "#0d2a16" if color == "#00c853" else "#2a0d0d"
    pad_x, pad_y = 8, 10
    xs = [pad_x + i / (len(pts) - 1) * (w - 2 * pad_x) for i in range(len(pts))]
    ys = [pad_y + (1 - (p - lo) / (hi - lo)) * (h - 2 * pad_y) for p in pts]
    poly = [xs[0], h] + [v for pair in zip(xs, ys) for v in pair] + [xs[-1], h]
    canvas.create_polygon(poly, fill=fill, outline="")
    for i in range(len(xs) - 1):
        canvas.create_line(xs[i], ys[i], xs[i + 1], ys[i + 1],
                           fill=color, width=2, smooth=True)
    canvas.create_text(pad_x, pad_y - 2, text=f"${hi:,.2f}",
                       font=("Arial", 7), fill="#444444", anchor="w")
    canvas.create_text(pad_x, h - 2, text=f"${lo:,.2f}",
                       font=("Arial", 7), fill="#444444", anchor="w")


class StockWindowMixin:
    """Robinhood-style stock market window."""

    # =========================================================
    # PRICE UPDATES  (called every game day)
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
    # MAIN WINDOW
    # =========================================================

    def open_stock_market(self):
        self.stock_window = tk.Toplevel(self.root)
        self.stock_window.title("Markets")
        self.stock_window.configure(bg="#0e1117")
        self.stock_window.geometry("740x800")
        self.stock_window.resizable(True, True)

        # ── Header ────────────────────────────────────────────
        hdr = tk.Frame(self.stock_window, bg="#0e1117")
        hdr.pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(hdr, text="Stocks", font=("Arial", 24, "bold"),
                 bg="#0e1117", fg="white").pack(anchor="w")
        self._portfolio_lbl = tk.Label(hdr, text="", font=("Arial", 12),
                                       bg="#0e1117", fg="#888888")
        self._portfolio_lbl.pack(anchor="w", pady=(2, 0))
        self._refresh_portfolio_label()

        tk.Frame(self.stock_window, bg="#1e2130", height=1).pack(fill="x", pady=(14, 0))

        # ── Search ────────────────────────────────────────────
        search_wrap = tk.Frame(self.stock_window, bg="#1e2130", padx=12, pady=7)
        search_wrap.pack(fill="x", padx=16, pady=(10, 4))
        tk.Label(search_wrap, text="⌕", font=("Arial", 12),
                 bg="#1e2130", fg="#555555").pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.refresh_market())
        tk.Entry(search_wrap, textvariable=self._search_var,
                 bg="#1e2130", fg="white", font=("Arial", 11),
                 insertbackground="white", relief="flat", bd=0
                 ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # ── Category pills ────────────────────────────────────
        pills = tk.Frame(self.stock_window, bg="#0e1117")
        pills.pack(fill="x", padx=16, pady=(6, 8))
        self._cat_btns = {}
        for cat in ["All"] + list(STOCK_CATEGORIES.keys()) + ["Custom"]:
            b = tk.Button(pills, text=cat, font=("Arial", 9), relief="flat",
                          padx=12, pady=5, cursor="hand2",
                          command=lambda c=cat: self._select_category(c))
            b.pack(side="left", padx=3)
            self._cat_btns[cat] = b
        self._select_category("All", render=False)

        tk.Frame(self.stock_window, bg="#1e2130", height=1).pack(fill="x")

        # ── Scrollable stock list ─────────────────────────────
        outer = tk.Frame(self.stock_window, bg="#0e1117")
        outer.pack(fill="both", expand=True)
        self._canvas = tk.Canvas(outer, bg="#0e1117", highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        self.stock_frame = tk.Frame(self._canvas, bg="#0e1117")
        self.stock_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.create_window((0, 0), window=self.stock_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # ── Create-stock footer ───────────────────────────────
        tk.Frame(self.stock_window, bg="#1e2130", height=1).pack(fill="x")
        self._build_create_bar(self.stock_window)

        self.refresh_market()

    # =========================================================
    # CATEGORY + PORTFOLIO HELPERS
    # =========================================================

    def _refresh_portfolio_label(self):
        if not hasattr(self, "_portfolio_lbl"):
            return
        total = sum(d["price"] * d["shares"]
                    for d in self.market.stocks.values() if d["shares"] > 0)
        txt = f"Portfolio  ${total:,.2f}" if total > 0 else "No positions held"
        self._portfolio_lbl.config(text=txt)

    def _select_category(self, cat, render=True):
        self.current_category = cat
        for name, btn in self._cat_btns.items():
            if name == cat:
                btn.config(bg="#00c853", fg="white")
            else:
                btn.config(bg="#1e2130", fg="#aaaaaa")
        if render:
            self.refresh_market()

    def set_category(self, category):
        self._select_category(category)

    # =========================================================
    # STOCK LIST
    # =========================================================

    def refresh_market(self):
        if not hasattr(self, "stock_frame") or not self.stock_frame.winfo_exists():
            return
        for w in self.stock_frame.winfo_children():
            w.destroy()
        self.stock_labels = {}

        query  = getattr(self, "_search_var", None)
        query  = query.get().strip().lower() if query else ""
        cat_f  = getattr(self, "current_category", "All")

        # Build the full candidate list
        all_rows = [
            (name, data)
            for name, data in self.market.stocks.items()
            if (cat_f == "All" or data.get("category", "Custom") == cat_f)
            and (not query or query in name.lower())
        ]

        # Limit to 5 per category — owned shares bubble to top within each group
        from collections import defaultdict
        by_cat = defaultdict(list)
        for name, data in all_rows:
            by_cat[data.get("category", "Custom")].append((name, data))

        rows = []
        for items in by_cat.values():
            items.sort(key=lambda x: (x[1]["shares"] == 0, x[0]))
            rows.extend(items[:5])

        # Sort final list: owned first, then by category + name
        rows.sort(key=lambda x: (x[1]["shares"] == 0, x[1].get("category", ""), x[0]))

        if not rows:
            tk.Label(self.stock_frame, text="No stocks match.",
                     font=("Arial", 11), bg="#0e1117", fg="#444444").pack(pady=30)
            return

        for name, data in rows:
            self._build_row(name, data)

        self._refresh_portfolio_label()

    def _build_row(self, name, data):
        history = data.get("history", [data["price"]])
        prev = history[-2] if len(history) >= 2 else data["price"]
        chg_pct = (data["price"] - prev) / prev * 100 if prev else 0
        pos = chg_pct >= 0
        chg_color = "#00c853" if pos else "#ff4444"
        arrow = "▲" if pos else "▼"
        owned = data["shares"] > 0

        row = tk.Frame(self.stock_frame, bg="#0e1117", cursor="hand2")
        row.pack(fill="x")

        inner = tk.Frame(row, bg="#0e1117", pady=12, padx=24)
        inner.pack(fill="x")

        # Left — name + meta
        left = tk.Frame(inner, bg="#0e1117", width=180)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Label(left, text=name, font=("Arial", 12, "bold"),
                 bg="#0e1117", fg="white", anchor="w").pack(anchor="w")
        sub = tk.Frame(left, bg="#0e1117")
        sub.pack(anchor="w")
        cat = data.get("category", "Custom")
        tk.Label(sub, text=cat, font=("Arial", 8),
                 bg="#0e1117", fg="#444444").pack(side="left")
        if owned:
            tk.Label(sub, text=f"  ·  {data['shares']} shares",
                     font=("Arial", 8, "bold"), bg="#0e1117", fg="#00c853").pack(side="left")

        # Middle — sparkline
        spark = tk.Canvas(inner, width=88, height=34,
                          bg="#0e1117", highlightthickness=0)
        spark.pack(side="left", padx=20)
        _draw_sparkline(spark, history, 88, 34)

        # Right — price + change
        right = tk.Frame(inner, bg="#0e1117")
        right.pack(side="right", fill="y")
        price_lbl = tk.Label(right, text=f"${data['price']:,.2f}",
                             font=("Arial", 12, "bold"), bg="#0e1117", fg="white",
                             anchor="e")
        price_lbl.pack(anchor="e")
        chg_lbl = tk.Label(right, text=f"{arrow} {abs(chg_pct):.2f}%",
                           font=("Arial", 9), bg="#0e1117", fg=chg_color,
                           anchor="e")
        chg_lbl.pack(anchor="e")

        tk.Frame(self.stock_frame, bg="#1a1f2e", height=1).pack(fill="x", padx=24)

        # Click anywhere on the row → detail window
        def _click(e, n=name):
            self._open_detail(n)

        for w in [row, inner, left, sub, spark, right] \
                + left.winfo_children() + sub.winfo_children() \
                + right.winfo_children():
            try:
                w.bind("<Button-1>", _click)
            except Exception:
                pass

        # Store widgets for lightweight in-place updates
        self.stock_labels[name] = {"price_lbl": price_lbl, "chg_lbl": chg_lbl, "spark": spark}

    def update_market_labels(self):
        """Update price/change labels and sparklines in-place — no widget rebuild."""
        if not hasattr(self, "stock_labels") or not self.stock_labels:
            return
        for name, widgets in list(self.stock_labels.items()):
            data = self.market.stocks.get(name)
            if not data:
                continue
            history = data.get("history", [data["price"]])
            prev = history[-2] if len(history) >= 2 else data["price"]
            chg_pct = (data["price"] - prev) / prev * 100 if prev else 0
            pos = chg_pct >= 0
            chg_color = "#00c853" if pos else "#ff4444"
            arrow = "▲" if pos else "▼"
            try:
                widgets["price_lbl"].config(text=f"${data['price']:,.2f}")
                widgets["chg_lbl"].config(
                    text=f"{arrow} {abs(chg_pct):.2f}%", fg=chg_color)
                _draw_sparkline(widgets["spark"], history, 88, 34)
            except (tk.TclError, KeyError):
                pass

    # =========================================================
    # DETAIL WINDOW
    # =========================================================

    def _open_detail(self, name):
        data = self.market.stocks.get(name)
        if not data:
            return

        win = tk.Toplevel(self.root)
        win.title(name)
        win.configure(bg="#0e1117")
        win.geometry("520x660")
        win.resizable(False, True)

        history = data.get("history", [data["price"]])
        prev = history[-2] if len(history) >= 2 else data["price"]
        chg_pct = (data["price"] - prev) / prev * 100 if prev else 0
        chg_abs = data["price"] - prev
        pos = chg_pct >= 0
        chg_color = "#00c853" if pos else "#ff4444"
        arrow = "▲" if pos else "▼"

        # ── Name + price ──────────────────────────────────────
        tk.Frame(win, bg="#0e1117", height=18).pack()
        tk.Label(win, text=name, font=("Arial", 20, "bold"),
                 bg="#0e1117", fg="white").pack(anchor="w", padx=24)
        cat = data.get("category", "Custom")
        tk.Label(win, text=cat, font=("Arial", 10),
                 bg="#0e1117", fg="#444444").pack(anchor="w", padx=24)
        tk.Frame(win, bg="#0e1117", height=8).pack()
        tk.Label(win, text=f"${data['price']:,.4f}",
                 font=("Arial", 30, "bold"), bg="#0e1117", fg="white").pack(anchor="w", padx=24)
        sign = "+" if pos else ""
        tk.Label(win, text=f"{arrow} {sign}${abs(chg_abs):,.4f}  ({sign}{chg_pct:.2f}%)",
                 font=("Arial", 11), bg="#0e1117", fg=chg_color).pack(anchor="w", padx=26)

        # ── Chart ─────────────────────────────────────────────
        chart_c = tk.Canvas(win, width=472, height=160, bg="#0e1117", highlightthickness=0)
        chart_c.pack(padx=24, pady=(16, 0))
        _draw_chart(chart_c, history, 472, 160)

        # ── Position ──────────────────────────────────────────
        shares = data["shares"]
        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=(16, 10))
        if shares > 0:
            pos_frame = tk.Frame(win, bg="#0e1117")
            pos_frame.pack(fill="x", padx=24, pady=(0, 4))
            tk.Label(pos_frame, text="Your Position",
                     font=("Arial", 9, "bold"), bg="#0e1117", fg="#555555").pack(anchor="w")
            p_row = tk.Frame(pos_frame, bg="#0e1117")
            p_row.pack(fill="x", pady=(2, 0))
            tk.Label(p_row, text=f"{shares} shares",
                     font=("Arial", 11), bg="#0e1117", fg="white").pack(side="left")
            tk.Label(p_row, text=f"${shares * data['price']:,.2f}",
                     font=("Arial", 11, "bold"), bg="#0e1117", fg="#00c853").pack(side="right")
            tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=(10, 0))

        # ── Trade ─────────────────────────────────────────────
        trade = tk.Frame(win, bg="#0e1117")
        trade.pack(fill="x", padx=24, pady=14)
        tk.Label(trade, text="Quantity",
                 font=("Arial", 10), bg="#0e1117", fg="#555555").pack(anchor="w")

        qty_row = tk.Frame(trade, bg="#0e1117")
        qty_row.pack(fill="x", pady=(4, 10))
        qty_var = tk.StringVar(value="1")
        tk.Entry(qty_row, textvariable=qty_var, width=7,
                 bg="#1e2130", fg="white", font=("Arial", 14, "bold"),
                 insertbackground="white", relief="flat",
                 justify="center").pack(side="left", ipady=8, padx=(0, 12))
        total_lbl = tk.Label(qty_row, text=f"= ${data['price']:,.2f}",
                             font=("Arial", 11), bg="#0e1117", fg="#888888")
        total_lbl.pack(side="left")

        def _update_total(*_):
            try:
                total_lbl.config(text=f"= ${int(qty_var.get()) * data['price']:,.2f}")
            except ValueError:
                total_lbl.config(text="")

        qty_var.trace_add("write", _update_total)

        def _trade(action):
            try:
                qty = max(1, int(qty_var.get()))
            except ValueError:
                return
            for _ in range(qty):
                if action == "buy":
                    result = self.market.buy_stock(name, 1)
                else:
                    if self.market.stocks[name]["shares"] <= 0:
                        break
                    result = self.market.sell_stock(name, 1)
            self.money = self.market.money
            self.log_event(result)
            self.update_status()
            self.refresh_market()
            win.destroy()

        btn_row = tk.Frame(trade, bg="#0e1117")
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="Buy", font=("Arial", 13, "bold"),
                  bg="#00c853", fg="white", activebackground="#009940",
                  relief="flat", pady=10, cursor="hand2",
                  command=lambda: _trade("buy")
                  ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Button(btn_row, text="Sell", font=("Arial", 13, "bold"),
                  bg="#ff4444" if shares > 0 else "#1e2130",
                  fg="white" if shares > 0 else "#444444",
                  activebackground="#cc2222",
                  relief="flat", pady=10, cursor="hand2",
                  state="normal" if shares > 0 else "disabled",
                  command=lambda: _trade("sell")
                  ).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # ── Pump / Dump ────────────────────────────────────────
        if shares > 0:
            tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=(12, 8))
            tk.Label(win, text="Market Manipulation",
                     font=("Arial", 8, "bold"), bg="#0e1117", fg="#2a2a3a").pack(anchor="w", padx=24)
            mm_row = tk.Frame(win, bg="#0e1117")
            mm_row.pack(fill="x", padx=24, pady=(4, 0))

            def _pump_close():
                self.pump_stock(name)
                win.destroy()

            def _dump_close():
                self.dump_stock(name)
                win.destroy()

            tk.Button(mm_row, text="⬆  Pump  ($5M)", font=("Arial", 9),
                      bg="#0d2a16", fg="#00c853", activebackground="#1a4a1a",
                      relief="flat", pady=7, cursor="hand2",
                      command=_pump_close
                      ).pack(side="left", fill="x", expand=True, padx=(0, 4))
            tk.Button(mm_row, text="⬇  Dump  (all)", font=("Arial", 9),
                      bg="#2a0d0d", fg="#ff4444", activebackground="#4a1a1a",
                      relief="flat", pady=7, cursor="hand2",
                      command=_dump_close
                      ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        # ── Margin Desk (leveraged long/short bets) ─────────────
        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=(12, 8))
        tk.Label(win, text="Margin Desk — Leveraged Bet",
                 font=("Arial", 8, "bold"), bg="#0e1117", fg="#2a2a3a").pack(anchor="w", padx=24)

        open_bets = [b for b in getattr(self, "margin_bets", []) if b["stock"] == name]
        if open_bets:
            for b in open_bets:
                tk.Label(win,
                         text=(f"  {b['leverage']}x {b['direction'].upper()}  ·  "
                               f"${b['stake']:,.0f} stake  ·  {b['days_left']}d left"),
                         font=("Arial", 8), bg="#0e1117", fg="#ffaa00").pack(anchor="w", padx=24)

        mg = tk.Frame(win, bg="#0e1117")
        mg.pack(fill="x", padx=24, pady=(4, 10))

        dir_var = tk.StringVar(value="long")
        lev_var = tk.StringVar(value="2x")
        term_var = tk.StringVar(value="7d")
        stake_var = tk.StringVar(value="1000000")

        row1 = tk.Frame(mg, bg="#0e1117")
        row1.pack(fill="x", pady=(0, 4))
        ttk.Combobox(row1, values=["long", "short"], textvariable=dir_var,
                     state="readonly", width=7).pack(side="left", padx=(0, 4))
        ttk.Combobox(row1, values=[f"{x}x" for x in self.MARGIN_LEVERAGES], textvariable=lev_var,
                     state="readonly", width=5).pack(side="left", padx=4)
        ttk.Combobox(row1, values=[f"{x}d" for x in self.MARGIN_TERMS], textvariable=term_var,
                     state="readonly", width=5).pack(side="left", padx=4)
        tk.Entry(row1, textvariable=stake_var, width=12,
                 bg="#1e2130", fg="white", font=("Arial", 9),
                 insertbackground="white", relief="flat").pack(side="left", padx=4)

        def _place_bet(w=win):
            try:
                stake = float(stake_var.get())
                lev   = int(lev_var.get().rstrip("x"))
                term  = int(term_var.get().rstrip("d"))
            except ValueError:
                self.log_event("Invalid margin bet parameters.")
                return
            if self.place_margin_bet(name, dir_var.get(), stake, lev, term):
                w.destroy()

        tk.Button(mg, text="Place Leveraged Bet", font=("Arial", 9, "bold"),
                  bg="#1e3a6e", fg="white", activebackground="#2e4a7e",
                  relief="flat", padx=10, pady=6, cursor="hand2",
                  command=_place_bet).pack(fill="x", pady=(4, 0))
        tk.Label(mg, text="Long profits when price rises, short when it falls. "
                          "Higher leverage = bigger swings and more SEC scrutiny.",
                 font=("Arial", 7), bg="#0e1117", fg="#555",
                 wraplength=460, justify="left").pack(anchor="w", pady=(4, 0))

    # =========================================================
    # BUY / SELL / PUMP / DUMP
    # =========================================================

    def _trading_frozen(self):
        if getattr(self, "trading_frozen_days", 0) > 0:
            self.log_event(
                f"Trading frozen — SEC investigation in progress "
                f"({self.trading_frozen_days} days remaining).")
            return True
        return False

    def buy_stock(self, name):
        if self._trading_frozen():
            return
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
        """Spend $5M to artificially inflate a stock you own. Once per stock per year."""
        if self._trading_frozen():
            return
        cost = 5_000_000
        pumped_this_year = getattr(self, "_pumped_this_year", {})
        if pumped_this_year.get(name) == self.days:
            self.log_event(f"Already pumped {name} this year.")
            return
        if self.money < cost:
            self.log_event(f"Need ${cost:,} to pump {name}")
            return
        self.money -= cost
        self.market.money = self.money
        data = self.market.stocks[name]
        if not hasattr(self, "_pumped_this_year"):
            self._pumped_this_year = {}
        self._pumped_this_year[name] = self.days
        data["price"] *= 1.25
        data["history"].append(data["price"])
        cat = data.get("category", "Custom")
        self.apply_market_effect([cat], 1.12, 3, f"Pump: {name}")
        self.add_transgression(8, 5)
        self.sec_heat = min(150, getattr(self, "sec_heat", 0) + 10)
        self.log_event(f"PUMP: Inflated {name} by 25%. Cost ${cost:,}. Transgression +8. SEC Heat +10.")
        self._add_ticker(f"MARKETS: Unusual volume spike detected in {name}...")
        self.update_status()
        self.refresh_market()

    def dump_stock(self, name):
        """Sell all shares at 1.5x price, then crash the stock."""
        if self._trading_frozen():
            return
        data = self.market.stocks[name]
        shares = data["shares"]
        if shares <= 0:
            self.log_event(f"No shares of {name} to dump")
            return
        proceeds = int(data["price"] * 1.5 * shares)
        self.money += proceeds
        self.market.money = self.money
        data["shares"] = 0
        data["price"] *= 0.55
        data["history"].append(data["price"])
        cat = data.get("category", "Custom")
        self.apply_market_effect([cat], 0.85, 4, f"Dump: {name}")
        self.add_transgression(12, 8)
        self.sec_heat = min(150, getattr(self, "sec_heat", 0) + 12)
        self.log_event(f"DUMP: Sold {shares} shares of {name} for ${proceeds:,} (1.5x). Stock crashed. SEC Heat +12.")
        self._add_ticker(f"MARKETS: {name} in freefall — mass selloff detected...")
        self.update_status()
        self.refresh_market()

    # =========================================================
    # LEVERAGED MARGIN BETS  (long/short wagers settled after N days)
    # =========================================================

    MARGIN_LEVERAGES = [2, 5, 10]
    MARGIN_TERMS     = [3, 7, 14]

    def place_margin_bet(self, name, direction, stake, leverage, term_days):
        if self._trading_frozen():
            return False
        if stake <= 0 or self.money < stake:
            self.log_event(f"Need ${stake:,.0f} to open that margin position.")
            return False
        data = self.market.stocks.get(name)
        if not data:
            return False
        self.money -= stake
        self.market.money = self.money
        if not hasattr(self, "margin_bets") or self.margin_bets is None:
            self.margin_bets = []
        self.margin_bets.append({
            "stock": name, "direction": direction, "stake": stake,
            "leverage": leverage, "entry_price": data["price"],
            "days_left": term_days, "term": term_days,
        })
        if leverage >= 5:
            self.add_transgression(2, 0)
            self.sec_heat = min(150, getattr(self, "sec_heat", 0) + 3)
        self.log_event(
            f"MARGIN: Opened {leverage}x {direction.upper()} on {name} — "
            f"${stake:,.0f} stake, settles in {term_days} days.")
        self._add_ticker(f"MARKETS: Leveraged position opened on {name}...")
        self.update_status()
        return True

    def process_margin_bets(self):
        """Settle any margin bets whose term has expired. Called once per game day."""
        if not getattr(self, "margin_bets", None):
            return
        remaining = []
        for bet in self.margin_bets:
            bet["days_left"] -= 1
            if bet["days_left"] > 0:
                remaining.append(bet)
                continue
            data = self.market.stocks.get(bet["stock"])
            price_now = data["price"] if data else bet["entry_price"]
            pct_change = (price_now - bet["entry_price"]) / bet["entry_price"] if bet["entry_price"] else 0
            if bet["direction"] == "short":
                pct_change = -pct_change
            payout_mult = max(0.0, min(5.0, 1 + pct_change * bet["leverage"]))
            payout = bet["stake"] * payout_mult
            self.money += payout
            self.market.money = self.money
            profit = payout - bet["stake"]
            verb = "profited" if profit >= 0 else "lost"
            self.log_event(
                f"MARGIN SETTLED: {bet['leverage']}x {bet['direction'].upper()} on {bet['stock']} "
                f"{verb} ${abs(profit):,.0f} (payout ${payout:,.0f}).")
            if payout >= bet["stake"] * 2:
                self.sec_heat = min(150, getattr(self, "sec_heat", 0) + 5)
                self._add_ticker(f"MARKETS: Regulators note an unusually well-timed bet on {bet['stock']}...")
        self.margin_bets = remaining
        self.update_status()

    # =========================================================
    # SEC INVESTIGATION ARC  (called once per game day from main_loop)
    # =========================================================

    def process_sec_heat(self):
        heat = getattr(self, "sec_heat", 0)
        frozen = getattr(self, "trading_frozen_days", 0)

        if frozen > 0:
            self.trading_frozen_days -= 1
            if self.trading_frozen_days <= 0:
                self.log_event("SEC investigation concluded — trading privileges restored.")
                self._add_ticker("MARKETS: Trading freeze lifted — markets reopen for you...")

        # Slow daily decay when not actively manipulating markets
        self.sec_heat = max(0, heat - 2)

        if heat >= 100:
            fine = int(self.money * 0.15)
            self.money -= fine
            self.market.money = self.money
            self.add_transgression(20, 15)
            self.trading_frozen_days = 7
            self.sec_heat = 40
            self.warned_sec_heat = False
            self.log_event(
                f"🚨 SEC FORMAL CHARGES: Market manipulation case filed. "
                f"Fined ${fine:,} (15% of net worth). Trading frozen 7 days.")
            self._add_ticker("BREAKING: SEC files formal market manipulation charges...")
            self.add_message(
                "🚨 SEC Formal Investigation",
                f"The SEC has filed formal charges over your trading activity.\n\n"
                f"Fine: ${fine:,}\nTransgressions +20\nTrading frozen for 7 days.",
                category="stocks",
            )
        elif heat >= 60 and not getattr(self, "warned_sec_heat", False):
            self.warned_sec_heat = True
            self.log_event("⚠ SEC Compliance: Your trading pattern has triggered an internal inquiry.")
            self._add_ticker("MARKETS: SEC opens preliminary inquiry into unusual trading activity...")
            self.add_message(
                "⚠️ SEC Preliminary Inquiry",
                "Regulators have flagged your recent trading pattern for review.\n\n"
                "Cool off on pumps, dumps, and leveraged bets — "
                "further activity risks a formal investigation and a full trading freeze.",
                category="stocks",
            )
        elif heat < 60:
            self.warned_sec_heat = False

    def show_stock_graph(self, stock):
        self._open_detail(stock)

    # =========================================================
    # CREATE STOCK FOOTER
    # =========================================================

    def _build_create_bar(self, parent):
        bar = tk.Frame(parent, bg="#111820", pady=10)
        bar.pack(fill="x", side="bottom")
        tk.Label(bar, text="Create Stock", font=("Arial", 9, "bold"),
                 bg="#111820", fg="#555555").pack(anchor="w", padx=18)
        row = tk.Frame(bar, bg="#111820")
        row.pack(fill="x", padx=14, pady=(4, 0))

        self._cs_name = tk.Entry(row, width=10, bg="#1e2130", fg="white",
                                 font=("Arial", 10), insertbackground="white", relief="flat")
        self._cs_name.insert(0, "Ticker")
        self._cs_name.pack(side="left", padx=4, ipady=5)

        self._cs_price = tk.Entry(row, width=9, bg="#1e2130", fg="white",
                                  font=("Arial", 10), insertbackground="white", relief="flat")
        self._cs_price.insert(0, "Price")
        self._cs_price.pack(side="left", padx=4, ipady=5)

        self._cs_cat_var = tk.StringVar(value="Custom")
        ttk.Combobox(row, textvariable=self._cs_cat_var,
                     values=list(STOCK_CATEGORIES.keys()) + ["Custom"],
                     width=12, state="readonly").pack(side="left", padx=4)

        tk.Button(row, text="Create", font=("Arial", 10, "bold"),
                  bg="#00c853", fg="white", activebackground="#009940",
                  relief="flat", padx=14, pady=4,
                  command=self.create_stock).pack(side="left", padx=8)

    def create_stock(self):
        name = self._cs_name.get().strip()
        if not name or name == "Ticker":
            self.log_event("Enter a stock name")
            return
        try:
            price = float(self._cs_price.get())
        except ValueError:
            self.log_event("Invalid price")
            return
        if price < 1:
            self.log_event("Price must be at least $1")
            return
        result = self.market.create_stock(name, price, self._cs_cat_var.get())
        self.log_event(result)
        self.refresh_market()
