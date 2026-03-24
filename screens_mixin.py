import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import random

from constants import LEADERBOARD_FILE, GLOBAL_LB_URL, STOCK_CATEGORIES, CATEGORY_PRICE_RANGES

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

        tk.Button(bottom_row, text="Load Game",
                  font=("Arial", 10), bg="#1e4060", fg="#4499ff",
                  activebackground="#2e5070", relief="flat",
                  padx=20, pady=5,
                  command=self.open_load_menu).pack(side="left", padx=8)

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

        tk.Button(bottom_row, text="Tutorial",
                  font=("Arial", 10), bg="#1e4020", fg="#aaffaa",
                  activebackground="#2e5030", relief="flat",
                  padx=20, pady=5,
                  command=self.open_tutorial).pack(side="left", padx=8)

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
                ("Survive", "You start with $100,000,000. Every game day (60 real seconds) you lose money through daily drain, upkeep, and fines. Your goal is to stay solvent as long as possible."),
                ("Death Conditions", "You die if your money hits $0, Happiness reaches 0, Public Opinion reaches 0, or Transgressions reaches 100. Each of these gives you a 1-day warning popup before killing you — use it to fix the problem."),
                ("End Screens", "Each death cause has its own themed end screen. Your Infamy Title is shown next to your score on the leaderboard."),
            ]),
            ("SINGLE PLAYER vs MULTIPLAYER", "#1e90ff", [
                ("Single Player", "Play against three AI rival billionaires: Viktor Drago, Chen Wei, and Elizabeth Harlow. Events fire every day. You can choose any country."),
                ("Multiplayer", "Join a lobby with up to 3 human players. Rivals are the other real players. Multiplayer is restricted to USA, China, and Russia only. The host starts the game when all players are ready."),
                ("Lobby Code", "When hosting, share the 4-letter lobby code with your friends. They enter it on the multiplayer screen to join your game."),
                ("In-Game Chat", "Click the Chat button during a multiplayer game to open a live chat window. Messages are colour-coded per player. Press Enter to send."),
            ]),
            ("WORK", "#00ff90", [
                ("Work Button", "Click Work on the main screen to earn a small amount of money instantly. A reliable way to generate income without risk."),
            ]),
            ("CASINO", "#ffdd44", [
                ("Russian Roulette", "Bet money for a 5-in-6 chance to double it. If you lose, the game ends immediately — permanently."),
                ("Slot Machine", "Spin 3 reels with coloured symbols (Cherry, Diamond, Seven, Bell, Star, Bar). Match symbols to multiply your bet. A full match is a jackpot. Flashing lights and win sounds play on a win. Max bet is 20% of your balance (capped at $30M)."),
                ("Poker", "5-card draw against the house. Set your bet first, then press Deal — your hand is revealed face-down. Press Draw to swap up to 3 cards, then the final hand is evaluated. Win multipliers: Pair ×1.5, Two Pair ×2, Trips ×3, Straight ×4, Flush ×5, Full House ×8, Quads ×20, Straight Flush ×50, Royal Flush ×100. Max bet is 20% of your balance."),
            ]),
            ("STOCK MARKET", "#0099ff", [
                ("Buying & Selling", "Buy and sell shares across 70+ stocks in 10 categories. Prices update every real second using live data (or simulated if offline)."),
                ("Price History", "Click any stock name to open a full price history graph."),
                ("Custom Stocks", "Create your own stock with a custom name, price, and category."),
                ("Pump & Dump", "Spend $5M to pump a stock you own by 25% (+8 transgressions). Then Dump to sell all shares at 1.5× price and crash it by 45% (+12 transgressions)."),
                ("Market Effects", "Events and world operations temporarily boost or crash entire categories. Watch the event log for active effects."),
            ]),
            ("ASSETS", "#ffaa00", [
                ("Luxury Purchases", "Buy supercars, a private jet, megayacht, doomsday bunker, private army, and more. Each has daily upkeep."),
                ("Passive Income", "Media Empire, Oil Rig, and Space Program generate daily income offsetting upkeep."),
                ("Special Effects", "Bunker skips pandemics. Offshore account halves tax fraud losses. Private army detects FBI agents. Each asset is worth buying for the right run."),
                ("Private Islands", "Open the Island Map to browse and purchase 19 real private islands worldwide — including Little Saint James ($45M). Each earns daily revenue."),
            ]),
            ("WORLD MAP", "#cc8800", [
                ("Resources", "Select Oil, Diamonds, Minerals, Agriculture, Technology, or Finance from the dropdown. Highlighted countries have reserves you can seize."),
                ("Bomb", "Aggressive option. Full cost, full income, full duration. +20 transgressions, -20 opinion. 30% sanction chance."),
                ("Stage a Coup", "Subtle option. 35% cost, 60% income, 70% duration. +10 transgressions, -8 opinion."),
                ("Sanctions", "Bombed countries may sanction you for up to 15 days — $500K/day fine. Sanctions stack."),
                ("Rival Territory", "If a rival controls a country you want, you can buy them out for 2× the normal action cost. Bombing a rival's territory triggers immediate retaliation."),
            ]),
            ("ISLAND MAP", "#00ccaa", [
                ("Zoom & Pan", "Scroll to zoom in/out. Right-click and drag to pan. Use the Caribbean and Pacific buttons to jump to key regions."),
                ("Purchasing", "Click an island dot to view its price, daily income, and upkeep. Click Buy if you can afford it."),
                ("Little Saint James", "Jeffrey Epstein's former island. $45M purchase, $250K/day upkeep, $600K/day income. Owning it changes how the Epstein event works."),
            ]),
            ("ALLIANCE SYSTEM", "#4499ff", [
                ("Join an Alliance", "Spend $50M to ally with USA, Russia, or China for 30 days. Alliances expire and must be renewed."),
                ("Cost Discounts", "USA alliance: 30% off Western countries. Russia: 30% off Eastern/Central Europe and Central Asia. China: 30% off Asia-Pacific."),
                ("Attack Interception", "Your alliance intelligence service has a chance to block incoming rival attacks (smear campaigns, lawsuits, sabotage). The block chance varies by alliance and attack type."),
                ("Territory Sharing", "Allied nations are less likely to sanction you after operations."),
                ("Multiplayer", "In multiplayer, alliances affect which countries you get discounts in — even when rivals are real players."),
            ]),
            ("LOBBY SYSTEM", "#ffaa00", [
                ("How It Works", "Each lobby action changes only ONE stat — either transgressions or public opinion, never both. Actions are expensive — this is a last resort, not a daily routine."),
                ("Bribe a Local Official", "$2M — reduces transgressions by 8."),
                ("Control the Narrative", "$8M — boosts public opinion by 15."),
                ("Buy a Senator [Records]", "$40M — reduces transgressions by 25."),
                ("Buy a Senator [Image]", "$40M — boosts public opinion by 30."),
                ("Senate Immunity", "$60M — blocks your next bad random event entirely. One use."),
                ("Full Records Expunge", "$150M — resets transgressions to 0."),
                ("Presidential Rehabilitation", "$150M — resets public opinion to 80."),
            ]),
            ("BLACK MARKET", "#ff2222", [
                ("Cooldowns", "Each black market item has a 4-day cooldown after purchase. The button shows remaining days when on cooldown."),
                ("Stolen Corporate Data", "+$8M | +12 transgressions"),
                ("Arms Smuggling", "+$10M | +18 transgressions"),
                ("Laundered Cash", "+$20M | +20 transgressions"),
                ("Forged Documents", "-$3M | -15 transgressions"),
                ("Organ Trafficking", "+$25M | +30 transgressions — the darkest trade"),
            ]),
            ("DEBT & LOANS", "#ff6600", [
                ("Taking Loans", "Borrow $10M (8%/day), $50M (6%/day), or $200M (4%/day) for a 30-day term."),
                ("Interest", "Compounds daily. Loans expiring within 5 days are shown in red as a warning."),
                ("Repaying", "Repay manually anytime, or loans auto-repay at expiry if you have funds."),
                ("Default", "Can't repay at expiry? You lose 50% of your money and gain 15 transgressions."),
            ]),
            ("RIVALS", "#cc44ff", [
                ("Single Player AI", "Viktor Drago, Chen Wei, and Elizabeth Harlow grow their wealth by 1–5%/day and have a 15% daily chance of seizing an unoccupied country. They hold territory for longer than before."),
                ("Direct Attacks", "Every day, each rival has an 8% chance of launching a targeted attack on you: Smear Campaign (−Opinion), Regulatory Tip-Off (+Transgressions), Sabotage (destroys an operation or steals money), Staff Poaching (−Happiness), or Lawsuit (−Money and +Transgressions). A popup alerts you to every attack."),
                ("Retaliation", "If you bomb a country a rival controls, they immediately retaliate with a Legal Injunction, PR Blitz, or Operation Seizure."),
                ("Alliance Shield", "Your active alliance may intercept a rival's attack before it lands. A popup confirms the block with no damage taken."),
                ("Buy Out", "Pay 2× normal action cost to remove a rival from a country they control."),
                ("Multiplayer Rivals", "In multiplayer, the Rivals window shows live stats of real opponents — money, country, happiness, opinion, and transgressions."),
            ]),
            ("WAR ROOM & MILITIA", "#ff4400", [
                ("Multiplayer Only", "The War Room is available in multiplayer games only. Use it to build a private military force and deploy attacks against rival players."),
                ("Buying Militia", "Four tiers: Mercenary Squad (15 units, $30M), PMC Battalion (40 units, $80M), Special Forces (75 units, $180M), Elite Strike Force (120 units, $280M). Units accumulate."),
                ("War Actions", "Spy (5 units) — view a rival's full stats. Raid (15 units) — steal 5–12% of their money. Assassinate (12 units) — destroy one of their operations. Sabotage (20 units) — crash their public opinion and happiness. Blockade (25 units) — block their resource income for 3 days. Nuke (100 units) — catastrophic: halve their money and spike transgressions."),
                ("Defense", "Every 20 militia units you own reduces incoming attack damage by 10%, up to 50% reduction."),
                ("War Declaration", "Bombing a rival's home country in multiplayer triggers a formal war — both sides pay $1.5M/day in war tax for 15 days."),
            ]),
            ("EPSTEIN EVENT", "#9900cc", [
                ("The Invitation", "Jeffrey Epstein may text you an iMessage-style invitation to Little Saint James. Accept for a big happiness boost and cash settlement — but there's risk."),
                ("Getting Caught", "After accepting the invite, there's a daily chance you're exposed. If caught, a Breaking News popup fires and your public opinion and transgressions take a severe hit."),
                ("Owning the Island", "If you own Little Saint James, you won't receive invitations — instead, you can invite a rival to the island and frame them. Their reputation crashes and yours stays clean."),
            ]),
            ("STAT BARS", "#888888", [
                ("Happiness", "Decays by 1/day. Rises when you spend on assets, islands, or lobby actions. Hitting 0 triggers a 1-day warning — fix it or the game ends."),
                ("Public Opinion", "Slowly recovers by 0.5/day. Damaged by transgressions and rival attacks. Hitting 0 triggers a 1-day warning."),
                ("Transgressions", "Accumulates with every illegal action. Naturally decays by 0.4/day when your Wanted Level is below 2. Use Lobby or Forged Documents to clean it. Hitting 100 triggers a 1-day warning."),
            ]),
            ("INFAMY TIERS", "#ff9900", [
                ("Tier 0 — Nobody", "0–19 transgressions. Clean record."),
                ("Tier 1 — Shady", "20–39 transgressions. People are starting to talk."),
                ("Tier 2 — Crime Lord", "40–59 transgressions. Serious heat."),
                ("Tier 3 — War Criminal", "60–79 transgressions. International warrants."),
                ("Tier 4 — Antichrist", "80–99 transgressions. You are the villain."),
                ("Tier 5 — ENDGAME", "100 transgressions. The end is near."),
            ]),
            ("WANTED LEVEL", "#ff4444", [
                ("Clean", "0–19 transgressions. No attention."),
                ("Media Attention", "20–39 — press coverage. Daily fine: $500K."),
                ("Senate Investigation", "40–59 — congressional probe. Daily fine: $1M."),
                ("FBI Target", "60–79 — federal investigation. Daily fine: $1.5M."),
                ("Interpol Red Notice", "80+ — global manhunt. Daily fine: $2M."),
            ]),
            ("WAR EVENTS", "#ff2222", [
                ("Trigger", "Public opinion hitting 5 or below triggers a country declaring war on you."),
                ("Consequences", "Lose $30M–$80M, gain 30 transgressions, 15-day sanctions, markets crash."),
                ("Recovery", "After a war event, public opinion resets to 15."),
            ]),
            ("RANDOM EVENTS", "#888888", [
                ("Frequency", "One or two random events fire at the end of every game day. Most are harmful. A few are lucky breaks."),
                ("Notable Events", "Gold Digger (lose half your money), Epstein text invite, Space Disaster ($500M loss), Pandemic, Ponzi Scheme Exposed, and 30+ more."),
                ("Asset Protection", "Certain assets protect against specific events. Buy the right gear before disaster hits."),
                ("Senate Immunity", "Spend $60M in the Lobby to block your next bad event entirely."),
            ]),
            ("LEGACY SYSTEM", "#aaaaaa", [
                ("Carry-Over Bonus", "Survive 10+ days and a cash bonus is saved when your empire collapses."),
                ("Next Run", "+$300K per day survived, capped at $50M. Applied automatically to your starting money next game."),
                ("Persistence", "Stored in legacy.json. Persists between sessions."),
            ]),
            ("NEWS TICKER", "#ffaa00", [
                ("Scrolling Headlines", "The gold bar below the stat bars reports every major event in real time — market moves, wars, rival actions, sanctions, and more."),
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

        # ── Top bar: money (left) + clock + day (right) ────────
        top = tk.Frame(frame, bg="#0e1117")
        top.pack(fill="x", padx=20, pady=(16, 6))

        self.money_label = tk.Label(top, text="Money: $100,000,000",
                                    font=self._font_money, bg="#0e1117", fg="#00ff90")
        self.money_label.pack(side="left")

        right_top = tk.Frame(top, bg="#0e1117")
        right_top.pack(side="right")

        self.day_label = tk.Label(right_top, text="Day 0",
                                  font=self._font_day, bg="#0e1117", fg="#aaaaaa")
        self.day_label.pack(side="right", padx=(8, 0))

        self.clock_canvas = tk.Canvas(right_top, width=52, height=52,
                                      bg="#0e1117", highlightthickness=0)
        self.clock_canvas.pack(side="right")
        self._draw_clock()

        # ── Primary action buttons ──────────────────────────────
        btn_frame = tk.Frame(frame, bg="#0e1117")
        btn_frame.pack(pady=(0, 4))

        for text, cmd in [
            ("Work",         self.work),
            ("Casino",       self.open_casino),
            ("Stock Market", self.open_stock_market),
            ("Assets",       self.open_assets),
            ("World Map",    self.open_world_map),
            ("🏭 Factory",   self.open_factory_window),
        ]:
            tk.Button(btn_frame, text=text,
                      font=self._font_btn_pri, bg="#1e2130", fg="white",
                      activebackground="#2e3140", relief="flat",
                      padx=18, pady=7,
                      command=cmd).pack(side="left", padx=6)

        # ── Secondary action buttons ────────────────────────────
        btn_frame2 = tk.Frame(frame, bg="#0e1117")
        btn_frame2.pack(pady=(0, 6))

        for text, cmd in [
            ("Lobby",        self.open_lobby),
            ("Black Market", self.open_black_market),
            ("Debt",         self.open_debt_window),
            ("Rivals",       self.open_rivals_window),
            ("Net Worth",    self.open_net_worth_graph),
            ("Alliance",     self.open_alliance_window),
            ("💬 Chat",      self.open_chat_window),
            ("⚔️ War Room",  self.open_war_room),
            ("💾 Save",      self.open_save_menu),
        ]:
            tk.Button(btn_frame2, text=text,
                      font=self._font_btn_sec, bg="#151820", fg="#aaaaaa",
                      activebackground="#2e3140", relief="flat",
                      padx=12, pady=5,
                      command=cmd).pack(side="left", padx=4)

        # ── Stat bars ───────────────────────────────────────────
        bars_frame = tk.Frame(frame, bg="#0e1117")
        bars_frame.pack(fill="x", padx=16, pady=(0, 4))

        def _make_bar(parent, label, init_val, color):
            col = tk.Frame(parent, bg="#0e1117")
            col.pack(side="left", expand=True, fill="x", padx=6)

            hdr = tk.Frame(col, bg="#0e1117")
            hdr.pack(fill="x")
            tk.Label(hdr, text=label, font=self._font_stat,
                     bg="#0e1117", fg="#888").pack(side="left")
            val_lbl = tk.Label(hdr, text=str(init_val),
                               font=self._font_stat, bg="#0e1117", fg=color)
            val_lbl.pack(side="right")

            track = tk.Frame(col, bg="#1a1a2e", height=14)
            track.pack(fill="x")
            track.pack_propagate(False)
            fill = tk.Frame(track, bg=color, height=14)
            fill.place(relx=0, rely=0, relheight=1, relwidth=max(0.001, init_val / 100))
            return fill, val_lbl

        self._bar_happy_fill,   self._bar_happy_lbl   = _make_bar(bars_frame, "Happiness",       50, "#00ff90")
        self._bar_opinion_fill, self._bar_opinion_lbl = _make_bar(bars_frame, "Public Opinion",   75, "#4499ff")
        self._bar_trans_fill,   self._bar_trans_lbl   = _make_bar(bars_frame, "Transgressions",    0, "#ff9900")

        # ── Infamy + Wanted status line ─────────────────────────
        status2 = tk.Frame(frame, bg="#0e1117")
        status2.pack(fill="x", padx=16, pady=(2, 2))
        self._infamy_label = tk.Label(status2, text="TIER 0: Nobody",
                                      font=("Arial", 8, "bold"), bg="#0e1117", fg="#555")
        self._infamy_label.pack(side="left")
        self._wanted_label = tk.Label(status2, text="Wanted: Clean",
                                      font=("Arial", 8, "bold"), bg="#0e1117", fg="#555")
        self._wanted_label.pack(side="right")

        # ── News ticker (centered, scrolling) ──────────────────
        ticker_frame = tk.Frame(frame, bg="#1a1a0a", height=24)
        ticker_frame.pack(fill="x", pady=(2, 0))
        ticker_frame.pack_propagate(False)
        self._ticker_label = tk.Label(ticker_frame, text="",
                                      font=self._font_ticker, bg="#1a1a0a", fg="#ffaa00",
                                      anchor="center")
        self._ticker_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._ticker_text = "  DEBT CLICKER NEWS  |  Your empire begins its descent...  "
        self._ticker_pos  = 0
        self._ticker_queue = []
        self._scroll_ticker()

        # ── Event log ──────────────────────────────────────────
        self.log = scrolledtext.ScrolledText(frame, height=20, state="disabled",
                                             bg="#0a0d13", fg="#cccccc",
                                             font=self._font_log, relief="flat",
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

    def _submit_global_score(self):
        """Non-blocking POST to the multiplayer server's leaderboard endpoint."""
        import threading, urllib.request
        from constants import GLOBAL_LB_URL
        def _post():
            try:
                import json as _json
                payload = _json.dumps({
                    "name":    self.username,
                    "days":    self.days,
                    "country": getattr(self, "country", ""),
                }).encode()
                req = urllib.request.Request(
                    GLOBAL_LB_URL,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                urllib.request.urlopen(req, timeout=4)
            except Exception:
                pass   # server offline — silent fail
        threading.Thread(target=_post, daemon=True).start()

    def _show_end_screen(self):
        self._save_legacy()
        rank, total = self._save_score()
        self._submit_global_score()

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
                 font=("Impact", 36), bg="#0e1117", fg="#ff2222").pack(pady=(40, 6))

        # Tab bar
        tab_bar = tk.Frame(frame, bg="#0e1117")
        tab_bar.pack()
        self._lb_tab = tk.StringVar(value="local")

        def _switch(tab):
            self._lb_tab.set(tab)
            if tab == "local":
                local_btn.config(bg="#ff2222", fg="white")
                global_btn.config(bg="#1e2130", fg="#aaa")
                self._populate_leaderboard()
            else:
                local_btn.config(bg="#1e2130", fg="#aaa")
                global_btn.config(bg="#4499ff", fg="white")
                self._populate_global_leaderboard()

        local_btn = tk.Button(tab_bar, text="Local", font=("Arial", 11, "bold"),
                              bg="#ff2222", fg="white", relief="flat", padx=24, pady=6,
                              command=lambda: _switch("local"))
        local_btn.pack(side="left", padx=4)

        global_btn = tk.Button(tab_bar, text="Global", font=("Arial", 11, "bold"),
                               bg="#1e2130", fg="#aaa", relief="flat", padx=24, pady=6,
                               command=lambda: _switch("global"))
        global_btn.pack(side="left", padx=4)

        self.lb_frame = tk.Frame(frame, bg="#0e1117")
        self.lb_frame.pack(fill="both", expand=True, padx=40, pady=(12, 0))

        tk.Button(frame, text="Back",
                  font=("Arial", 11), bg="#1e2130", fg="white",
                  activebackground="#2e3140", relief="flat",
                  padx=20, pady=6,
                  command=lambda: self.show_screen("start")).pack(pady=16)

        return frame

    def _render_lb_entries(self, entries, show_country=False):
        for w in self.lb_frame.winfo_children():
            w.destroy()
        if not entries:
            tk.Label(self.lb_frame, text="No scores yet. Be the first!",
                     font=("Arial", 12), bg="#0e1117", fg="#aaaaaa").pack(pady=20)
            return
        medals = ["🥇", "🥈", "🥉"]
        for i, entry in enumerate(entries[:10]):
            row = tk.Frame(self.lb_frame, bg="#1e2130")
            row.pack(fill="x", pady=3, ipady=6)
            rank_text = medals[i] if i < 3 else f"#{i+1}"
            tk.Label(row, text=rank_text, font=("Arial", 13), bg="#1e2130",
                     fg="#ffdd44", width=4).pack(side="left", padx=10)
            name_text = entry["name"]
            if show_country and entry.get("country"):
                name_text += f"  ({entry['country']})"
            tk.Label(row, text=name_text, font=("Arial", 12), bg="#1e2130",
                     fg="white", width=28, anchor="w").pack(side="left")
            tk.Label(row, text=f"{entry['days']} days",
                     font=("Arial", 12, "bold"), bg="#1e2130",
                     fg="#00ff90").pack(side="right", padx=16)

    def _populate_leaderboard(self):
        entries = self._load_leaderboard()
        self._render_lb_entries(entries, show_country=False)

    def _populate_global_leaderboard(self):
        import threading, urllib.request
        for w in self.lb_frame.winfo_children():
            w.destroy()
        status = tk.Label(self.lb_frame, text="Fetching global scores…",
                          font=("Arial", 11), bg="#0e1117", fg="#aaaaaa")
        status.pack(pady=20)

        def _fetch():
            try:
                with urllib.request.urlopen(GLOBAL_LB_URL, timeout=4) as r:
                    import json as _json
                    data = _json.loads(r.read())
                self.root.after(0, lambda: self._render_lb_entries(data, show_country=True))
            except Exception:
                self.root.after(0, lambda: [
                    status.config(text="Server offline — global leaderboard unavailable.",
                                  fg="#ff4444")
                ])
        threading.Thread(target=_fetch, daemon=True).start()

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

        # Scroll: show a 100-char centered window into the text
        base = self._ticker_text + "     "
        display = base * 3
        pos = self._ticker_pos % len(base)
        snippet = display[pos:pos + 100]
        try:
            self._ticker_label.config(text=snippet)
        except Exception:
            return
        self._ticker_pos += 1
        self.root.after(75, self._scroll_ticker)

    def _add_ticker(self, text):
        """Add a headline to the news ticker queue."""
        if hasattr(self, "_ticker_queue"):
            self._ticker_queue.append(text)
