import tkinter as tk
import random


class EventsMixin:
    """Random events, popups, market effects, and the NYT subscription tick."""

    # =========================================================
    # RANDOM EVENTS
    # =========================================================

    def random_events(self):
        r = random.randint(1, 70)

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

        elif r == 3 and self.company:
            self.money -= 50000
            self.show_event("Factory Incident!", "One of your child workers at your illegal factory got mutilated by machinery. Pay $50,000 to cover it up.")
            self.apply_market_effect(["Retail", "Automotive"], 0.94, 2, "Factory scandal")

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

        elif r == 7 and not self.epstein:
            self.epstein = True
            self.money -= 10000000
            self.show_event("Island Discovered...", "Your ventures to Epstein's island have been discovered. Lose $10,000,000 to cover it up.")
            self.apply_market_effect(["Entertainment", "Finance"], 0.88, 4, "Epstein scandal")

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

        elif r == 14 and self.mansion:
            if "island" in self.owned_assets:
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

        elif r == 17 and not self.space:
            self.space = True
            self.money -= 500000000
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

        elif r == 21 and not self.oil_spill:
            self.oil_spill = True
            self.money -= 50000000
            self.show_event("Oil Spill!", "Your private tanker had a 'minor' accident off the coast. The ocean is now 40% oil. Pay $50,000,000 in cleanup costs.")
            self.apply_market_effect(["Energy"], 0.88, 5, "Oil spill disaster")

        elif r == 22:
            self.money -= 10000000
            self.show_event("Crypto Rug Pull!", "You launched 'RichCoin' and immediately rug pulled it. Unfortunately you forgot you also invested $10,000,000 in it. Classic.")
            self.apply_market_effect(["Finance", "AI"], 0.93, 2, "Crypto collapse")

        elif r == 23:
            self.money -= 8000000
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

        elif r == 26 and not self.insider_trading:
            self.insider_trading = True
            self.money -= 35000000
            self.show_event("Insider Trading!", "You got caught insider trading NVIDIA stock right before earnings. The SEC fined you $35,000,000. Worth it honestly.")
            self.apply_market_effect(["AI", "Finance"], 0.89, 4, "Insider trading scandal")

        elif r == 27:
            self.money -= 15000000
            self.show_event("Hitman Mishap!", "You hired a hitman to deal with a business rival. He was an undercover FBI agent. Pay $15,000,000 in legal fees. Your rival is fine.")
            self.apply_market_effect(["Defense"], 0.93, 2, "Criminal investigation")

        elif r == 28:
            self.money -= 20000000
            self.show_event("Casino Money Laundering!", "You used a casino to launder money. Casinos report large cash transactions. The IRS called. Lose $20,000,000.")
            self.apply_market_effect(["Finance", "Entertainment"], 0.91, 3, "Money laundering probe")

        elif r == 29:
            self.money -= 10000000
            self.show_event("Lobbyist Caught!", "Your lobbyist was filmed handing a suitcase of cash to a senator in broad daylight. Lose $10,000,000. The senator kept the money.")
            self.apply_market_effect(["Finance", "Defense"], 0.93, 2, "Political corruption scandal")

        elif r == 30:
            self.money -= 5000000
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
