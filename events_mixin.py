import tkinter as tk
import random


class EventsMixin:
    """Random events, popups, market effects, and the NYT subscription tick."""

    # =========================================================
    # RANDOM EVENTS
    # =========================================================

    def random_events(self):
        r = random.randint(1, 50)   # tighter range → bad events ~40 % more frequent

        # Senate immunity blocks one bad event
        if getattr(self, "lobby_immunity", False) and r not in (4, 10, 18):  # skip good events
            self.lobby_immunity = False
            self.log_event("Senate Immunity activated — bad event blocked!")
            self._add_ticker("POLITICS: Senate intervention blocks investigation...")
            return

        if r == 1 and self.family:
            self.family = False
            self.money /= 2
            self.show_event("Gold Digger!", "Oh no! Your spouse is a gold-digger and has taken HALF your money!")
            self.apply_market_effect(["Finance"], 0.93, 3, "Divorce scandal")

        elif r == 2:
            if "offshore" in self.owned_assets:
                self.money *= 0.65
                self.show_event("Tax Fraud!", "You filed a fraudulent tax report. The IRS found out — but your offshore account shielded half the damage. Lose 35%.")
            else:
                self.money *= 0.30
                self.show_event("Tax Fraud!", "You filed a fraudulent tax report. The IRS found out — lose 70% of your money!")
            self.apply_market_effect(["Finance"], 0.91, 2, "Tax fraud scandal")
            self.add_transgression(10, 8)

        elif r == 3 and self.company:
            self.money -= 50000
            self.show_event("Factory Incident!", "One of your child workers at your illegal factory got mutilated by machinery. Pay $50,000 to cover it up.")
            self.apply_market_effect(["Retail", "Automotive"], 0.94, 2, "Factory scandal")
            self.add_transgression(8, 6)

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

        elif r == 7 and not self.epstein and not self.epstein_visited:
            self._show_epstein_invite()

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
            self.add_transgression(10, 12)

        elif r == 14 and self.mansion:
            if "island" in self.owned_assets or self.owned_islands:
                self.show_event("Cuba Tries to Invade!", "Cuba eyed your island — but your sovereign territory kept them out. Your Private Island paid off.")
            else:
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
            self.add_transgression(18, 15)

        elif r == 17 and not self.space:
            self.space = True
            if "jet" in self.owned_assets and not self.jet_skip_used:
                self.jet_skip_used = True
                self.show_event("Space Program Disaster... Avoided!", "Your rocket exploded — but you were already airborne in your private jet to the Maldives. PR team handled it. You missed the whole thing.")
            else:
                self.money -= 500_000_000
                self.show_event("Space Program Disaster!", "You created a space program. On the first launch, the rocket explodes and kills everyone on board. Pay $500,000,000 in damages.")
                self.apply_market_effect(["Space"], 0.75, 5, "Space disaster")
                self.apply_market_effect(["Technology", "Defense"], 0.93, 3, "Space sector contagion")

        elif r == 18:
            self.money += 5000000
            self.show_event("Political Endorsement!", "You 'accidentally' did the salute of a hated Austrian politician in public. The president loved it and hired you into the government. +$5,000,000")
            self.apply_market_effect(["Finance", "Defense"], 1.05, 2, "Government contracts")

        elif r == 19:
            fine = 10_000_000 if "senator" not in self.owned_assets else 6_000_000
            self.money -= fine
            if "senator" in self.owned_assets:
                self.show_event("Lawsuit Fail!", f"You sued a local news outlet — forgot about free speech. Your senator got the fine down to ${fine:,}.")
            else:
                self.show_event("Lawsuit Fail!", "You sued a local news outlet for talking badly about you — but forgot about free speech. Lose $10,000,000.")
            self.apply_market_effect(["Entertainment"], 0.94, 2, "Media coverage backlash")

        elif r == 20 and not self.ponzi:
            self.ponzi = True
            self.money -= 20000000
            self.show_event("Ponzi Scheme Exposed!", "Your side Ponzi scheme was discovered by the SEC. 2,000 retirees lost their savings. You lost $20,000,000 in fines.")
            self.apply_market_effect(["Finance"], 0.90, 4, "Ponzi scheme collapse")
            self.add_transgression(15, 15)

        elif r == 21 and not self.oil_spill:
            self.oil_spill = True
            self.money -= 50000000
            self.show_event("Oil Spill!", "Your private tanker had a 'minor' accident off the coast. The ocean is now 40% oil. Pay $50,000,000 in cleanup costs.")
            self.apply_market_effect(["Energy"], 0.88, 5, "Oil spill disaster")
            self.add_transgression(12, 14)

        elif r == 22:
            self.money -= 10000000
            self.show_event("Crypto Rug Pull!", "You launched 'RichCoin' and immediately rug pulled it. Unfortunately you forgot you also invested $10,000,000 in it. Classic.")
            self.apply_market_effect(["Finance", "AI"], 0.93, 2, "Crypto collapse")
            self.add_transgression(8, 8)

        elif r == 23:
            if "media" in self.owned_assets:
                self.money -= 2_000_000
                self.show_event("Social Media Disaster!", "You tweeted your bank password — but your media empire buried the story within the hour. Damage control cost $2,000,000 instead of $8,000,000.")
            else:
                self.money -= 8_000_000
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
            self.add_transgression(10, 12)

        elif r == 26 and not self.insider_trading:
            self.insider_trading = True
            self.money -= 35000000
            self.show_event("Insider Trading!", "You got caught insider trading NVIDIA stock right before earnings. The SEC fined you $35,000,000. Worth it honestly.")
            self.apply_market_effect(["AI", "Finance"], 0.89, 4, "Insider trading scandal")
            self.add_transgression(12, 10)

        elif r == 27:
            if "army" in self.owned_assets:
                self.show_event("Hitman Mishap!", "You hired a hitman — but your private army ran a background check first. Turns out he was FBI. You thanked your mercenaries and sent him packing. No charge.")
            else:
                self.money -= 15_000_000
                self.show_event("Hitman Mishap!", "You hired a hitman to deal with a business rival. He was an undercover FBI agent. Pay $15,000,000 in legal fees. Your rival is fine.")
                self.apply_market_effect(["Defense"], 0.93, 2, "Criminal investigation")
            self.add_transgression(15, 10)

        elif r == 28:
            self.money -= 20000000
            self.show_event("Casino Money Laundering!", "You used a casino to launder money. Casinos report large cash transactions. The IRS called. Lose $20,000,000.")
            self.apply_market_effect(["Finance", "Entertainment"], 0.91, 3, "Money laundering probe")
            self.add_transgression(10, 8)

        elif r == 29:
            self.money -= 10000000
            self.show_event("Lobbyist Caught!", "Your lobbyist was filmed handing a suitcase of cash to a senator in broad daylight. Lose $10,000,000. The senator kept the money.")
            self.apply_market_effect(["Finance", "Defense"], 0.93, 2, "Political corruption scandal")

        elif r == 30:
            if "yacht" in self.owned_assets:
                self.money -= 800_000
                self.show_event("Drunk Captain!", "Your yacht captain crashed into a buoy after one too many cocktails. Minor hull damage — $800,000 repair. At least it wasn't the highway.")
            else:
                self.money -= 5_000_000
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
            self.add_transgression(10, 12)

        elif r == 34 and not self.pandemic:
            self.pandemic = True
            if "bunker" in self.owned_assets:
                self.show_event("Pandemic? What Pandemic?", "A global pandemic swept the world. You were safe in your doomsday bunker eating canned beans. No financial damage.")
            else:
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
    # EPSTEIN INVITE  (text-message style popup)
    # =========================================================

    def _show_epstein_invite(self):
        owns_island = "Little Saint James" in self.owned_islands

        popup = tk.Toplevel(self.root)
        popup.title("New Message")
        popup.configure(bg="#1c1c1e")
        popup.geometry("340x520")
        popup.resizable(False, False)

        # ── Status bar ───────────────────────────────────────────────────
        bar = tk.Frame(popup, bg="#1c1c1e")
        bar.pack(fill="x", padx=16, pady=(10, 0))
        tk.Label(bar, text="9:41 AM", font=("Arial", 11, "bold"),
                 bg="#1c1c1e", fg="white").pack(side="left")
        tk.Label(bar, text="● ● ●  WiFi  🔋", font=("Arial", 8),
                 bg="#1c1c1e", fg="white").pack(side="right")

        # ── Contact header ───────────────────────────────────────────────
        hdr = tk.Frame(popup, bg="#1c1c1e")
        hdr.pack(fill="x", padx=16, pady=(8, 4))

        av = tk.Canvas(hdr, width=40, height=40, bg="#1c1c1e", highlightthickness=0)
        av.create_oval(2, 2, 38, 38, fill="#5856d6", outline="")
        av.create_text(20, 20, text="JE", font=("Arial", 13, "bold"), fill="white")
        av.pack(side="left", padx=(0, 10))

        info = tk.Frame(hdr, bg="#1c1c1e")
        info.pack(side="left")
        tk.Label(info, text="Jeffrey Epstein", font=("Arial", 12, "bold"),
                 bg="#1c1c1e", fg="white").pack(anchor="w")
        tk.Label(info, text="+1 (340) 776-6330", font=("Arial", 8),
                 bg="#1c1c1e", fg="#8e8e93").pack(anchor="w")

        tk.Frame(popup, bg="#38383a", height=1).pack(fill="x")

        # ── Message bubbles ──────────────────────────────────────────────
        msg_frame = tk.Frame(popup, bg="#000000")
        msg_frame.pack(fill="both", expand=True, padx=0, pady=0)

        tk.Label(msg_frame, text="Today  9:38 AM", font=("Arial", 8),
                 bg="#000000", fg="#8e8e93").pack(pady=(12, 6))

        def _bubble(text, color="#1c8a1c", anchor="e", padx=(60, 12)):
            outer = tk.Frame(msg_frame, bg="#000000")
            outer.pack(fill="x", padx=padx, pady=3, anchor=anchor)
            lbl = tk.Label(outer, text=text, font=("Arial", 10),
                           bg=color, fg="white", wraplength=220,
                           justify="left", padx=12, pady=8)
            lbl.pack(side="right" if anchor == "e" else "left")

        if owns_island:
            _bubble("Hey, I heard you bought my old place 👀", "#1c8a1c", "e", (60, 12))
            _bubble("You own the island now.\nYou want to... invite someone?", "#1c8a1c", "e", (60, 12))
            _bubble("I know a few people who'd love to visit 😈", "#1c8a1c", "e", (60, 12))
        else:
            _bubble("Hey, heard you've been doing well 💰", "#1c8a1c", "e", (60, 12))
            _bubble("I'm having a little gathering at my island this weekend.", "#1c8a1c", "e", (60, 12))
            _bubble("Very private. Very exclusive.\nYou should come 😉", "#1c8a1c", "e", (60, 12))
            _bubble("There's a settlement in it for you.\n$3,000,000. Think about it.", "#1c8a1c", "e", (60, 12))

        tk.Label(msg_frame, text="Delivered", font=("Arial", 7),
                 bg="#000000", fg="#8e8e93").pack(anchor="e", padx=14)

        # ── Action buttons ───────────────────────────────────────────────
        tk.Frame(popup, bg="#38383a", height=1).pack(fill="x")
        btn_row = tk.Frame(popup, bg="#1c1c1e")
        btn_row.pack(fill="x", pady=10, padx=12)

        if owns_island:
            # Rival dropdown
            rival_names = list(self.rivals.keys()) if self.rivals else []
            if not rival_names:
                popup.destroy()
                return

            sel = tk.StringVar(value=rival_names[0])
            from tkinter import ttk
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("EP.TCombobox", fieldbackground="#2c2c2e",
                            background="#2c2c2e", foreground="white",
                            selectbackground="#2c2c2e")
            dd = ttk.Combobox(btn_row, textvariable=sel, values=rival_names,
                              state="readonly", width=18, style="EP.TCombobox")
            dd.pack(side="left", padx=(0, 8))

            def _frame_rival():
                target = sel.get()
                self._epstein_frame_rival(target)
                popup.destroy()

            tk.Button(btn_row, text="Invite & Frame 😈",
                      font=("Arial", 10, "bold"), bg="#ff3b30", fg="white",
                      relief="flat", padx=12, pady=6,
                      command=_frame_rival).pack(side="left", padx=4)
            tk.Button(btn_row, text="Ignore",
                      font=("Arial", 10), bg="#2c2c2e", fg="#8e8e93",
                      relief="flat", padx=12, pady=6,
                      command=popup.destroy).pack(side="left", padx=4)
        else:
            def _accept():
                self.happiness = min(100, self.happiness + 35)
                self.money += 3_000_000
                self.market.money = self.money
                self.epstein_visited = True
                self.epstein_catch_days = random.randint(4, 9)
                self.update_status()
                self.log_event("You accepted Epstein's invitation. Happiness way up. $3M richer.")
                self._add_ticker("SOCIETY: Prominent billionaire spotted at private Caribbean gathering...")
                popup.destroy()

            def _decline():
                self.log_event("You declined Epstein's invitation. Smart.")
                self.epstein = True   # mark as handled so it won't fire again
                popup.destroy()

            tk.Button(btn_row, text="Accept ✈️  (+$3M, +Happiness)",
                      font=("Arial", 10, "bold"), bg="#30d158", fg="white",
                      relief="flat", padx=12, pady=6,
                      command=_accept).pack(fill="x", pady=(0, 6))
            tk.Button(btn_row, text="Decline 🚫",
                      font=("Arial", 10), bg="#2c2c2e", fg="#8e8e93",
                      relief="flat", padx=12, pady=6,
                      command=_decline).pack(fill="x")

    def _epstein_frame_rival(self, rival_name):
        """Invite a rival to Little Saint James, then leak it to the press."""
        rival = self.rivals.get(rival_name)
        if not rival:
            return
        # Rival loses reputation (money hit + scandal flag)
        scandal_hit = int(rival["money"] * random.uniform(0.30, 0.50))
        rival["money"] = max(0, rival["money"] - scandal_hit)
        rival["scandal"] = True

        # Market hit in rival's name
        self.apply_market_effect(["Finance", "Entertainment"], 0.88, 5,
                                 f"{rival_name} Epstein scandal")
        # Player benefits — happiness, small payout, clean image
        self.happiness = min(100, self.happiness + 20)
        self.money += 5_000_000
        self.market.money = self.money
        self.epstein = True   # mark as handled

        self.log_event(f"You invited {rival_name} to Little Saint James and leaked it to the press. "
                       f"Their reputation is destroyed. +$5M.")
        self._add_ticker(f"SCANDAL: {rival_name} linked to disgraced financier's private island...")
        self.update_status()

    def check_epstein_caught(self):
        """Call this from main_loop each day."""
        if not getattr(self, "epstein_visited", False) or self.epstein:
            return
        self.epstein_catch_days -= 1
        if self.epstein_catch_days > 0:
            return
        # Time's up — 65 % chance of getting caught
        self.epstein = True
        self.epstein_visited = False
        if random.random() < 0.65:
            self._show_epstein_caught()
        else:
            self.log_event("Your visit to Epstein's island was never discovered. You got lucky.")
            self._add_ticker("CELEBRITY: Billionaire denies any connection to financier's island estate...")

    def _show_epstein_caught(self):
        self.add_transgression(35, 40)
        self.happiness = max(0, self.happiness - 20)
        self.apply_market_effect(["Entertainment", "Finance"], 0.82, 6, "Epstein scandal exposed")
        self._add_ticker("BREAKING: Billionaire EXPOSED — visited Epstein's island, sources confirm...")
        self.log_event("EXPOSED: Your Epstein island visit leaked to the press. "
                       "Transgressions +35, public opinion -40.")

        popup = tk.Toplevel(self.root)
        popup.title("BREAKING NEWS")
        popup.configure(bg="#0e1117")
        popup.geometry("420x280")
        popup.resizable(False, False)

        # Fake news chyron
        tk.Frame(popup, bg="#cc0000", height=6).pack(fill="x")
        tk.Label(popup, text="🔴  BREAKING NEWS",
                 font=("Impact", 14), bg="#cc0000", fg="white").pack(fill="x", pady=4)
        tk.Label(popup,
                 text="BILLIONAIRE LINKED TO EPSTEIN'S PRIVATE ISLAND",
                 font=("Impact", 13), bg="#111111", fg="#ffdd00",
                 wraplength=400).pack(fill="x", pady=6)
        tk.Label(popup,
                 text="Sources confirm you were among the guests at Little Saint James.\n"
                      "Public opinion in freefall. Congressional hearings scheduled.\n"
                      "Your lawyers are already charging by the hour.",
                 font=("Arial", 9), bg="#0e1117", fg="#aaaaaa",
                 wraplength=390, justify="center").pack(pady=10)
        tk.Frame(popup, bg="#cc0000", height=3).pack(fill="x")
        ticker = tk.Label(popup,
                          text="  LIVE  •  Public opinion -40  •  Transgressions +35  •  Markets crashing  •  LIVE  ",
                          font=("Arial", 8), bg="#cc0000", fg="white")
        ticker.pack(fill="x")
        tk.Button(popup, text="No comment.",
                  font=("Arial", 10, "bold"), bg="#1e2130", fg="white",
                  relief="flat", padx=20, pady=8,
                  command=popup.destroy).pack(pady=12)

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
    # NYT SUBSCRIPTION TICK
    # =========================================================

    def subscription_tick(self):
        if not self.subscription or not self.running:
            return
        self.money -= 1
        self.market.money = self.money
        self.update_status()
        self.root.after(1000, self.subscription_tick)
