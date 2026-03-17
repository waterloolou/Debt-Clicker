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

        # ── Single-player / Multiplayer buttons ───────────────────────────
        game_btn_row = tk.Frame(frame, bg="#0e1117")
        game_btn_row.pack(pady=16)

        tk.Button(game_btn_row, text="Single Player",
                  font=("Arial", 13, "bold"), bg="#ff2222", fg="white",
                  activebackground="#cc0000", relief="flat",
                  padx=22, pady=8,
                  command=self._on_start_clicked).pack(side="left", padx=8)

        tk.Button(game_btn_row, text="Multiplayer",
                  font=("Arial", 12), bg="#1e4080", fg="white",
                  activebackground="#2a5090", relief="flat",
                  padx=22, pady=8,
                  command=self._on_multiplayer_clicked).pack(side="left", padx=8)

        bottom_row = tk.Frame(frame, bg="#0e1117")
        bottom_row.pack(pady=(0, 0))

        tk.Button(bottom_row, text="Leaderboard",
                  font=("Arial", 10), bg="#1e2130", fg="#aaaaaa",
                  activebackground="#2e3140", relief="flat",
                  padx=20, pady=5,
                  command=lambda: [self._populate_leaderboard(),
                                   self.show_screen("leaderboard")]).pack(side="left", padx=8)

        tk.Button(bottom_row, text="Wiki",
                  font=("Arial", 10), bg="#1e2130", fg="#aaaaaa",
                  activebackground="#2e3140", relief="flat",
                  padx=20, pady=5,
                  command=self._open_wiki).pack(side="left", padx=8)

        return frame

    # =========================================================
    # WIKI
    # =========================================================

    def _open_wiki(self):
        win = tk.Toplevel(self.root)
        win.title("Debt Clicker — Wiki")
        win.configure(bg="#0e1117")
        win.geometry("620x680")
        win.resizable(False, True)

        tk.Label(win, text="DEBT CLICKER WIKI",
                 font=("Impact", 28), bg="#0e1117", fg="#ff2222").pack(pady=(20, 4))
        tk.Label(win, text="Everything you need to know about your downfall.",
                 font=("Arial", 9), bg="#0e1117", fg="#555").pack(pady=(0, 10))

        # Scrollable content
        container = tk.Frame(win, bg="#0e1117")
        container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        canvas = tk.Canvas(container, bg="#0e1117", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#0e1117")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_scroll(e):
            try:
                canvas.yview_scroll(-1 * (e.delta // 120), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _on_scroll)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        SECTIONS = [
            ("GOAL", "#ff2222", [
                ("Survive", "You start with $100,000,000. Every game day (60 real seconds) you lose a random amount of money. Your goal is to stay solvent as long as possible. When you hit $0, it's over."),
            ]),
            ("WORK", "#00ff90", [
                ("Work Button", "Click Work on the main screen to earn a small amount of money instantly. Higher income variants unlock as you play."),
            ]),
            ("CASINO", "#ffdd44", [
                ("Russian Roulette", "Bet money for a 5-in-6 chance to double it. If you lose, the game ends immediately."),
                ("Slot Machine", "Spin 3 reels. Match symbols to multiply your bet. Higher matches pay more."),
                ("Poker", "5-card draw against the house. Best hand takes the pot."),
            ]),
            ("STOCK MARKET", "#0099ff", [
                ("Buying & Selling", "Buy and sell shares in real stocks across categories: AI, Technology, Energy, Finance, Healthcare, and more. Prices update every real second using live market data (or simulated if offline)."),
                ("Price History", "Click any stock name to open a graph of its price history."),
                ("Custom Stocks", "Create your own stock with a custom name, price, and category."),
                ("Pump", "Spend $5M to inflate a stock you own by 25%. Triggers a market boost but adds 8 transgressions."),
                ("Dump", "Sell all your shares at 1.5x current price, then crash the stock by 45%. Adds 12 transgressions."),
                ("Market Effects", "Events and world operations temporarily boost or crash entire stock categories. Watch the log for active effects."),
            ]),
            ("ASSETS", "#ffaa00", [
                ("Luxury Purchases", "Buy assets like supercars, a private jet, megayacht, or doomsday bunker. Each costs daily upkeep."),
                ("Passive Income", "Some assets (Media Empire, Oil Rig, Space Program) generate daily income that partially offsets upkeep."),
                ("Special Effects", "Certain assets protect you from specific events — the bunker skips pandemics, the offshore account halves tax fraud losses, the private army detects undercover FBI agents."),
                ("Private Islands", "Open the island sub-map to browse and buy 18 real private islands worldwide. Each earns daily income."),
            ]),
            ("WORLD MAP", "#cc8800", [
                ("Resources", "Select a resource type (Oil, Diamonds, Minerals, Agriculture, Technology, Finance) from the dropdown. Highlighted countries have reserves you can seize."),
                ("Bomb", "The aggressive option. Full cost, full income, full duration. Adds 20 transgressions and 20 opinion hit. 30% chance of triggering sanctions."),
                ("Stage a Coup", "The subtle option. 35% of the cost, 60% of the income, 70% of the duration. Adds 10 transgressions and 8 opinion hit."),
                ("Income", "Seized countries pay daily resource income for the operation's duration, then the occupation ends automatically."),
                ("Sanctions", "If a country sanctions you after a bombing, you pay $500K/day for up to 15 days. Sanctions stack."),
                ("Homeland", "You cannot attack your own country."),
            ]),
            ("ALLIANCE SYSTEM", "#4499ff", [
                ("Alliances", "Spend $50M to ally with USA, Russia, or China for 30 days."),
                ("Discounts", "USA: 30% off Western nations. Russia: 30% off Eastern/Central nations. China: 30% off Asia-Pacific nations."),
                ("Expiry", "Alliances expire after 30 days. You must re-sign and pay again."),
            ]),
            ("LOBBY SYSTEM", "#ffaa00", [
                ("Bribe Local Official", "$500K — reduces transgressions by 10."),
                ("Control the Narrative", "$5M — boosts public opinion by 20."),
                ("Buy a Congressman", "$15M — reduces transgressions by 20, boosts opinion by 15."),
                ("Senate Immunity", "$40M — blocks the next bad random event entirely. One use only."),
                ("Presidential Pardon", "$100M — resets transgressions to 0, boosts opinion by 30."),
            ]),
            ("BLACK MARKET", "#ff2222", [
                ("Stolen Corporate Data", "+$8M | +12 transgressions"),
                ("Arms Smuggling", "+$10M | +18 transgressions"),
                ("Laundered Cash", "+$20M | +20 transgressions"),
                ("Forged Documents", "-$3M | -15 transgressions (buy a clean record)"),
                ("Organ Trafficking", "+$25M | +30 transgressions — the darkest trade"),
            ]),
            ("DEBT & LOANS", "#ff6600", [
                ("Taking Loans", "Borrow $10M (8%/day), $50M (6%/day), or $200M (4%/day) for a 30-day term."),
                ("Interest", "Interest compounds daily on the remaining balance. The longer you wait, the more you owe."),
                ("Repaying", "Repay manually anytime, or loans auto-repay on expiry if you have the funds."),
                ("Default", "If you can't repay at expiry, you lose 50% of your remaining money and gain 15 transgressions."),
            ]),
            ("RIVALS", "#cc44ff", [
                ("Viktor Drago, Chen Wei, Elizabeth Harlow", "Three AI billionaires compete for the same resource countries as you. Each day they have a chance to seize an unoccupied country."),
                ("Rival Country", "If a rival controls a country you want, you can pay 2x the normal action cost to buy them out."),
                ("Tracking", "Open the Rivals window to see each rival's net worth and which countries they control."),
            ]),
            ("STAT BARS", "#888888", [
                ("Happiness", "Increases when you spend money (assets, islands, lobbying). Decays by 2 every day. Higher happiness has no direct penalty — but low happiness makes the game feel grim."),
                ("Public Opinion", "Decreases with transgressions. Slowly recovers by 0.5/day. If it hits 0 or below 5, a country declares war on you."),
                ("Transgressions", "Accumulates with every illegal or morally questionable action. Never decreases naturally — use Lobby or Forged Documents to clean it."),
            ]),
            ("INFAMY TIERS", "#ff9900", [
                ("Tier 0 — Nobody", "0–19 transgressions. Clean record."),
                ("Tier 1 — Shady", "20–39 transgressions. People are starting to talk."),
                ("Tier 2 — Crime Lord", "40–59 transgressions. Serious heat."),
                ("Tier 3 — War Criminal", "60–79 transgressions. International warrants."),
                ("Tier 4 — Antichrist", "80–99 transgressions. You are the villain."),
                ("Tier 5 — ENDGAME", "100 transgressions. Maximum infamy."),
            ]),
            ("WANTED LEVEL", "#ff4444", [
                ("Clean", "0–19 transgressions. No attention."),
                ("Media Attention", "20–39 — press coverage. Daily fine: $500K."),
                ("Senate Investigation", "40–59 — congressional probe. Daily fine: $1M."),
                ("FBI Target", "60–79 — federal investigation. Daily fine: $1.5M."),
                ("Interpol Red Notice", "80+ — global manhunt. Daily fine: $2M."),
            ]),
            ("WAR EVENTS", "#ff2222", [
                ("Trigger", "If your public opinion drops to 5 or below, a random country declares war on you."),
                ("Consequences", "Lose $30M–$80M instantly, gain 30 transgressions, receive 15-day sanctions from the attacker, and markets crash."),
                ("Recovery", "After a war event, public opinion resets to 15 to prevent immediate looping."),
            ]),
            ("RANDOM EVENTS", "#888888", [
                ("Frequency", "Every game day, one of 34 possible random events fires. Most are bad. A few are lucky windfalls."),
                ("Notable Events", "Gold Digger (lose half your money), Epstein Island (lose $10M), Space Disaster (lose $500M), Pandemic, Ponzi Scheme Exposed, and more."),
                ("Asset Protection", "Certain assets protect you from specific events. Buy the right gear before disaster strikes."),
                ("Senate Immunity", "Spend $40M in the Lobby to guarantee one bad event is completely skipped."),
            ]),
            ("LEGACY SYSTEM", "#aaaaaa", [
                ("Carry-Over Bonus", "If you survive 10+ days, a cash bonus is saved to disk when your empire collapses."),
                ("Next Run", "The bonus is automatically applied to your starting money in the next game (+$300K per day survived, capped at $50M)."),
                ("Persistence", "The bonus is stored in legacy.json in the game folder and persists between sessions."),
            ]),
            ("NEWS TICKER", "#ffaa00", [
                ("Scrolling Headlines", "The gold ticker bar below the stat bars shows recent major events as they happen — market moves, wars, rival activity, sanctions, and more."),
            ]),
        ]

        for section_title, color, entries in SECTIONS:
            # Section header
            hdr = tk.Frame(inner, bg=color, height=2)
            hdr.pack(fill="x", padx=8, pady=(14, 0))
            tk.Label(inner, text=section_title,
                     font=("Impact", 14), bg="#0e1117", fg=color,
                     anchor="w").pack(fill="x", padx=12, pady=(2, 4))

            for entry_title, entry_body in entries:
                entry_frame = tk.Frame(inner, bg="#111520", padx=12, pady=6)
                entry_frame.pack(fill="x", padx=8, pady=2)
                tk.Label(entry_frame, text=entry_title,
                         font=("Arial", 9, "bold"), bg="#111520", fg="white",
                         anchor="w").pack(anchor="w")
                tk.Label(entry_frame, text=entry_body,
                         font=("Arial", 8), bg="#111520", fg="#aaaaaa",
                         wraplength=540, justify="left", anchor="w").pack(anchor="w")

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

    _MP_SUPERPOWERS = {"United States of America", "China", "Russia"}

    def _on_multiplayer_clicked(self):
        """Validate name/country then open the multiplayer lobby."""
        name = self.username_entry.get().strip()
        if not name:
            self.start_error.config(text="Please enter a name.")
            return
        country = self.country_var.get()
        if not country:
            self.start_error.config(text="Please select a country.")
            return
        if country not in self._MP_SUPERPOWERS:
            self.start_error.config(
                text="Multiplayer: you must play as USA, China or Russia.")
            return
        self.start_error.config(text="")
        self.username = name
        self.country  = country
        self.open_multiplayer_lobby()

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
            ("💬 Chat",     self.open_chat_window),
            ("⚔️ War Room", self.open_war_room),
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

    # Maps death cause → (title, subtitle, accent_color, icon)
    _END_THEMES = {
        "broke": (
            "YOUR EMPIRE\nHAS COLLAPSED",
            "The banks took everything.\nYou're left with nothing but debt and regret.",
            "#ff2222", "💸",
        ),
        "happiness": (
            "YOU LOST THE\nWILL TO LIVE",
            "All the money in the world\ncouldn't fill the void. You simply... stopped.",
            "#ff9900", "😶",
        ),
        "opinion": (
            "HUNTED BY\nYOUR OWN PEOPLE",
            "The mob came for you.\nYour name became a curse. Nowhere to hide.",
            "#ff4466", "📉",
        ),
        "transgressions": (
            "BROUGHT TO\nJUSTICE",
            "Every crime. Every cover-up. Every lie.\nThe bill finally came due. Life in prison.",
            "#cc00ff", "⛓️",
        ),
        "roulette": (
            "BANG.",
            "You pulled the trigger.\nOne bullet. That was the one.",
            "#ff2222", "🔫",
        ),
    }

    def _build_end_screen(self):
        frame = tk.Frame(self.root, bg="#0e1117")

        self._end_top_bar   = tk.Frame(frame, bg="#ff2222", height=6)
        self._end_top_bar.pack(fill="x")

        self.end_icon_label = tk.Label(frame, text="💸",
                                       font=("Arial", 42), bg="#0e1117")
        self.end_icon_label.pack(pady=(24, 0))

        self.end_title_label = tk.Label(frame, text="YOUR EMPIRE\nHAS COLLAPSED",
                                        font=("Impact", 34), bg="#0e1117", fg="#ff2222",
                                        justify="center")
        self.end_title_label.pack(pady=(6, 4))

        self.end_flavor_label = tk.Label(frame, text="",
                                         font=("Arial", 10), bg="#0e1117", fg="#888888",
                                         justify="center")
        self.end_flavor_label.pack(pady=(0, 14))

        tk.Frame(frame, bg="#1e2130", height=1).pack(fill="x", padx=60)

        self.end_name_label = tk.Label(frame, text="",
                                       font=("Arial", 13), bg="#0e1117", fg="white")
        self.end_name_label.pack(pady=(12, 2))

        self.end_days_label = tk.Label(frame, text="",
                                       font=("Arial", 20, "bold"), bg="#0e1117", fg="#00ff90")
        self.end_days_label.pack(pady=2)

        self.end_infamy_label = tk.Label(frame, text="",
                                         font=("Arial", 10, "italic"), bg="#0e1117", fg="#aaaaaa")
        self.end_infamy_label.pack(pady=2)

        self.end_rank_label = tk.Label(frame, text="",
                                       font=("Arial", 10), bg="#0e1117", fg="#555555")
        self.end_rank_label.pack(pady=4)

        btn_frame = tk.Frame(frame, bg="#0e1117")
        btn_frame.pack(pady=18)

        self._end_play_btn = tk.Button(btn_frame, text="Play Again",
                  font=("Arial", 12, "bold"), bg="#ff2222", fg="white",
                  activebackground="#cc0000", relief="flat",
                  padx=22, pady=8,
                  command=self._play_again)
        self._end_play_btn.pack(side="left", padx=12)

        tk.Button(btn_frame, text="Leaderboard",
                  font=("Arial", 12), bg="#1e2130", fg="white",
                  activebackground="#2e3140", relief="flat",
                  padx=22, pady=8,
                  command=lambda: [self._populate_leaderboard(),
                                   self.show_screen("leaderboard")]).pack(side="left", padx=12)

        self._end_bot_bar = tk.Frame(frame, bg="#ff2222", height=6)
        self._end_bot_bar.pack(fill="x", side="bottom")

        return frame

    def _show_end_screen(self):
        self._save_legacy()
        rank, total = self._save_score()

        cause = getattr(self, "death_cause", "broke")
        title, flavor, color, icon = self._END_THEMES.get(cause, self._END_THEMES["broke"])

        # Apply theme colors
        self._end_top_bar.config(bg=color)
        self._end_bot_bar.config(bg=color)
        self._end_play_btn.config(bg=color, activebackground=color)
        self.end_icon_label.config(text=icon)
        self.end_title_label.config(text=title, fg=color)
        self.end_flavor_label.config(text=flavor)

        # Infamy title
        _, infamy_name = self.get_infamy_tier()
        self.end_name_label.config(
            text=f"{self.username}  —  \"{infamy_name}\"")
        self.end_days_label.config(text=f"Survived {self.days} days")
        self.end_infamy_label.config(
            text=f"Country: {getattr(self, 'country', '—')}  |  "
                 f"Transgressions: {self.transgressions}  |  "
                 f"Happiness: {int(self.happiness)}  |  "
                 f"Opinion: {int(self.public_opinion)}")
        if rank:
            self.end_rank_label.config(
                text=f"#{rank} on the leaderboard out of {total} players")
        else:
            self.end_rank_label.config(text="")

        self.show_screen("end")

    def _play_again(self):
        # Disconnect from any active multiplayer session
        if getattr(self, "net_client", None) and self.net_client.connected:
            self.net_client.disconnect()
        self.net_client = None
        self.is_multiplayer = False

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
