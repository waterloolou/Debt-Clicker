import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import random

from constants import LEADERBOARD_FILE, STOCK_CATEGORIES, CATEGORY_PRICE_RANGES

PLAYABLE_COUNTRIES = sorted([
    # Superpowers
    "United States of America", "Russia", "China",
    # Western-aligned
    "Canada", "Australia", "Japan", "South Korea",
    # Europe
    "Albania", "Austria", "Belarus", "Belgium",
    "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
    "Czech Republic", "Denmark", "Estonia", "Finland", "France",
    "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy",
    "Latvia", "Lithuania", "Luxembourg", "Moldova", "Montenegro",
    "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal",
    "Romania", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden",
    "Switzerland", "Ukraine", "United Kingdom",
])


class ScreensMixin:
    """Builds and manages all UI screens and the leaderboard."""

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

        tk.Label(frame, text="Select your country:", font=("Arial", 11),
                 bg="#0e1117", fg="white").pack()

        self.country_var = tk.StringVar()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                        fieldbackground="#1e2130", background="#1e2130",
                        foreground="white", selectbackground="#2e3140",
                        selectforeground="white", arrowcolor="white")
        self.country_combo = ttk.Combobox(frame, textvariable=self.country_var,
                                          values=PLAYABLE_COUNTRIES,
                                          state="readonly", width=24,
                                          font=("Arial", 11),
                                          style="Dark.TCombobox",
                                          justify="center")
        self.country_combo.pack(pady=6)

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
                  command=lambda: [self._populate_leaderboard(),
                                   self.show_screen("leaderboard")]).pack()

        return frame

    def _on_start_clicked(self):
        name = self.username_entry.get().strip()
        if not name:
            self.start_error.config(text="Please enter a name.")
            return
        country = self.country_var.get()
        if not country:
            self.start_error.config(text="Please select a country.")
            return
        self.start_error.config(text="")
        self.username = name
        self.country  = country
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
        self.day_label.pack(side="right", padx=(0, 8))

        self.clock_canvas = tk.Canvas(top, width=60, height=60,
                                      bg="#0e1117", highlightthickness=0)
        self.clock_canvas.pack(side="right")
        self._draw_clock()

        btn_frame = tk.Frame(frame, bg="#0e1117")
        btn_frame.pack(pady=6)

        for text, cmd in [
            ("Work",         self.work),
            ("Casino",       self.open_casino),
            ("Stock Market", self.open_stock_market),
            ("Assets",       self.open_assets),
            ("World Map",    self.open_world_map),
        ]:
            tk.Button(btn_frame, text=text,
                      font=("Arial", 10), bg="#1e2130", fg="white",
                      activebackground="#2e3140", relief="flat",
                      padx=14, pady=5,
                      command=cmd).pack(side="left", padx=6)

        btn_frame2 = tk.Frame(frame, bg="#0e1117")
        btn_frame2.pack(pady=(0, 4))

        for text, cmd in [
            ("Lobby",       self.open_lobby),
            ("Black Market",self.open_black_market),
            ("Debt",        self.open_debt_window),
            ("Rivals",      self.open_rivals_window),
            ("Net Worth",   self.open_net_worth_graph),
            ("Alliance",    self.open_alliance_window),
        ]:
            tk.Button(btn_frame2, text=text,
                      font=("Arial", 9), bg="#151820", fg="#aaaaaa",
                      activebackground="#2e3140", relief="flat",
                      padx=10, pady=4,
                      command=cmd).pack(side="left", padx=4)

        # ── Stat bars ──────────────────────────────────────────
        bars_frame = tk.Frame(frame, bg="#0e1117")
        bars_frame.pack(fill="x", padx=12, pady=(0, 4))

        def _make_bar(parent, label, init_val, color):
            col = tk.Frame(parent, bg="#0e1117")
            col.pack(side="left", expand=True, fill="x", padx=5)

            hdr = tk.Frame(col, bg="#0e1117")
            hdr.pack(fill="x")
            tk.Label(hdr, text=label, font=("Arial", 7),
                     bg="#0e1117", fg="#555").pack(side="left")
            val_lbl = tk.Label(hdr, text=str(init_val),
                               font=("Arial", 7, "bold"), bg="#0e1117", fg=color)
            val_lbl.pack(side="right")

            track = tk.Frame(col, bg="#1a1a2e", height=8)
            track.pack(fill="x")
            track.pack_propagate(False)
            fill = tk.Frame(track, bg=color, height=8)
            fill.place(relx=0, rely=0, relheight=1, relwidth=max(0.001, init_val / 100))
            return fill, val_lbl

        self._bar_happy_fill,  self._bar_happy_lbl  = _make_bar(bars_frame, "Happiness",      50, "#00ff90")
        self._bar_opinion_fill, self._bar_opinion_lbl = _make_bar(bars_frame, "Public Opinion", 75, "#4499ff")
        self._bar_trans_fill,  self._bar_trans_lbl  = _make_bar(bars_frame, "Transgressions",   0, "#ff9900")

        # Infamy + Wanted status line
        status2 = tk.Frame(frame, bg="#0e1117")
        status2.pack(fill="x", padx=12, pady=(0, 2))
        self._infamy_label  = tk.Label(status2, text="TIER 0: Nobody",
                                        font=("Arial", 7, "bold"), bg="#0e1117", fg="#555")
        self._infamy_label.pack(side="left")
        self._wanted_label  = tk.Label(status2, text="Wanted: Clean",
                                        font=("Arial", 7, "bold"), bg="#0e1117", fg="#555")
        self._wanted_label.pack(side="right")

        # News ticker
        ticker_frame = tk.Frame(frame, bg="#1a1a0a", height=18)
        ticker_frame.pack(fill="x", padx=0, pady=0)
        ticker_frame.pack_propagate(False)
        self._ticker_label = tk.Label(ticker_frame, text="  DEBT CLICKER NEWS  |  Your empire begins its descent...  ",
                                       font=("Consolas", 8), bg="#1a1a0a", fg="#ffaa00",
                                       anchor="w")
        self._ticker_label.pack(side="left", fill="y")
        self._ticker_text = "  DEBT CLICKER NEWS  |  Your empire begins its descent...  "
        self._ticker_pos  = 0
        self._ticker_queue = []
        self._scroll_ticker()

        self.log = scrolledtext.ScrolledText(frame, height=20, state="disabled",
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
                  command=lambda: [self._populate_leaderboard(),
                                   self.show_screen("leaderboard")]).pack(side="left", padx=12)

        return frame

    def _show_end_screen(self):
        self._save_legacy()
        rank, total = self._save_score()
        self.end_name_label.config(text=f"{self.username}'s empire has fallen.")
        self.end_days_label.config(text=f"Survived {self.days} days")
        if rank:
            self.end_rank_label.config(text=f"#{rank} on the leaderboard out of {total} players")
        else:
            self.end_rank_label.config(text="")
        self.show_screen("end")

    def _play_again(self):
        self.log.config(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.config(state="disabled")

        for category, stocks in STOCK_CATEGORIES.items():
            lo, hi = CATEGORY_PRICE_RANGES.get(category, (10, 500))
            for name in stocks:
                if name in self.market.stocks:
                    price = round(random.uniform(lo, hi), 2)
                    self.market.stocks[name].update({
                        "price":        price,
                        "shares":       0,
                        "history":      [price],
                        "returns":      [],
                        "return_index": 0,
                    })
        for name, data in self.market.stocks.items():
            if data.get("category") == "Custom":
                data["shares"] = 0
                data["history"] = [data["price"]]
                data["returns"] = []
                data["return_index"] = 0

        self.username_entry.delete(0, tk.END)
        self.country_var.set("")
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
                     font=("Arial", 12, "bold"), bg="#1e2130",
                     fg="#00ff90").pack(side="right", padx=16)

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
        self._update_bars()

    def _update_bars(self):
        if not hasattr(self, "_bar_happy_fill"):
            return

        h = getattr(self, "happiness",      50)
        o = getattr(self, "public_opinion", 75)
        t = getattr(self, "transgressions",  0)

        # Happiness colour: green → yellow → red
        if h > 60:   hc = "#00ff90"
        elif h > 30: hc = "#ffaa00"
        else:        hc = "#ff4444"
        self._bar_happy_fill.place(relwidth=max(0.001, min(1, h / 100)))
        self._bar_happy_fill.config(bg=hc)
        self._bar_happy_lbl.config(text=f"{int(h)}%", fg=hc)

        # Public opinion: blue → yellow → red
        if o > 60:   oc = "#4499ff"
        elif o > 30: oc = "#ffaa00"
        else:        oc = "#ff4444"
        self._bar_opinion_fill.place(relwidth=max(0.001, min(1, o / 100)))
        self._bar_opinion_fill.config(bg=oc)
        self._bar_opinion_lbl.config(text=f"{int(o)}%", fg=oc)

        # Transgressions: orange → deep red
        if t > 70:   tc = "#ff2222"
        elif t > 40: tc = "#ff6600"
        else:        tc = "#ff9900"
        self._bar_trans_fill.place(relwidth=max(0.001, min(1, t / 100)))
        self._bar_trans_fill.config(bg=tc)
        self._bar_trans_lbl.config(text=str(int(t)), fg=tc)

        # Update infamy + wanted labels
        if hasattr(self, "_infamy_label"):
            tier, title = self.get_infamy_tier()
            colors = ["#555", "#ffaa00", "#ff6600", "#ff2222", "#cc0000", "#880000"]
            self._infamy_label.config(text=f"TIER {tier}: {title}", fg=colors[tier])
        if hasattr(self, "_wanted_label"):
            labels = ["Clean", "Media Attention", "Senate Investigation", "FBI Target", "Interpol Red Notice"]
            wcolors = ["#555", "#ffdd44", "#ff9900", "#ff4444", "#ff0000"]
            wl = getattr(self, "wanted_level", 0)
            self._wanted_label.config(text=f"Wanted: {labels[wl]}", fg=wcolors[wl])

    # =========================================================
    # NEWS TICKER
    # =========================================================

    def _scroll_ticker(self):
        if not hasattr(self, "_ticker_label"):
            return
        try:
            self._ticker_label.winfo_exists()
        except Exception:
            return
        try:
            if not self._ticker_label.winfo_exists():
                return
        except Exception:
            return

        # Append queued items to ticker text
        while self._ticker_queue:
            self._ticker_text += "   |   " + self._ticker_queue.pop(0)

        # Scroll: show a 60-char window into the text
        display = (self._ticker_text + "   ") * 2
        pos = self._ticker_pos % len(self._ticker_text + "   ")
        snippet = display[pos:pos+80]
        try:
            self._ticker_label.config(text=snippet)
        except Exception:
            return
        self._ticker_pos += 1
        self.root.after(80, self._scroll_ticker)

    def _add_ticker(self, text):
        """Add a headline to the news ticker queue."""
        if hasattr(self, "_ticker_queue"):
            self._ticker_queue.append(text)
