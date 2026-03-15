import tkinter as tk
from tkinter import scrolledtext
import json
import random

from constants import LEADERBOARD_FILE, STOCK_CATEGORIES, CATEGORY_PRICE_RANGES


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
                  command=lambda: [self._populate_leaderboard(),
                                   self.show_screen("leaderboard")]).pack(side="left", padx=12)

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
