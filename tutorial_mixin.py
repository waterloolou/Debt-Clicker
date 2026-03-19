import tkinter as tk
from tkinter import scrolledtext
import random


_STEPS = [
    {
        "title": "Welcome to Debt Clicker",
        "subtitle": "A quick guided tour of your empire.",
        "body": (
            "You play as a corrupt billionaire trying to survive as long as possible.\n\n"
            "Every day your wealth drains, rivals attack, and events threaten your empire.\n\n"
            "Your goal: stay alive. Manage your MONEY, HAPPINESS, PUBLIC OPINION, "
            "and TRANSGRESSIONS to avoid a catastrophic end.\n\n"
            "Let's walk through each system."
        ),
        "sim": None,
        "color": "#ff2222",
    },
    {
        "title": "Daily Drain & Work",
        "subtitle": "Money doesn't sit still.",
        "body": (
            "Every day a percentage of your balance drains away — upkeep, staff, bribes, lifestyle.\n\n"
            "At large balances ($100M+) you lose 0.6–1.6% per day. If you idle with no active "
            "operations, an extra 0.5% idle tax is added.\n\n"
            "The WORK button earns you a small amount ($1K–$50K) to stay afloat early on, "
            "but you'll need bigger income sources fast.\n\n"
            "Tip: Get resource operations running as early as possible."
        ),
        "sim": "drain",
        "color": "#ff8800",
    },
    {
        "title": "World Map & Resources",
        "subtitle": "Where your real money comes from.",
        "body": (
            "Open the WORLD MAP to find countries with Oil, Gas, Minerals, or Agriculture.\n\n"
            "Each country offers three actions:\n"
            "  • Bribe — cheapest, short-term income\n"
            "  • Coup  — medium cost, longer income\n"
            "  • Bomb  — most expensive, max income, +transgressions\n\n"
            "Once you take an action, that country pays you daily income for a set number of days.\n\n"
            "⚠  Rivals will try to seize the same countries — check your Rivals panel daily."
        ),
        "sim": "resource",
        "color": "#00aa44",
    },
    {
        "title": "Happiness & Public Opinion",
        "subtitle": "Keep your image — or die.",
        "body": (
            "HAPPINESS drops 1 point per day naturally. If it hits 0, you get a 1-day warning, "
            "then the game ends.\n\n"
            "PUBLIC OPINION works the same — it starts at 50 and decays when you take aggressive "
            "actions. Rivals can smear you to crash it.\n\n"
            "Ways to recover:\n"
            "  • Lobby → 'Buy a Senator [Image]' — expensive but effective\n"
            "  • Positive random events (charities, press coverage)\n"
            "  • Stock market — selling at a gain boosts happiness\n\n"
            "Stay above 0 on both or face consequences."
        ),
        "sim": "stats",
        "color": "#cc44ff",
    },
    {
        "title": "Transgressions",
        "subtitle": "Your crime score. Keep it under 100.",
        "body": (
            "TRANSGRESSIONS track your cumulative illegal activity. Bombing countries, "
            "black market purchases, and rival tip-offs all increase it.\n\n"
            "At 100 transgressions, you get a 1-day warning then the game ends in arrest.\n\n"
            "Ways to reduce transgressions:\n"
            "  • Lobby → 'Buy a Senator [Records]' (-25)\n"
            "  • Lobby → 'Full Records Expunge' (resets to 0, costs $150M)\n"
            "  • Natural decay: -0.4/day when wanted level < 2\n\n"
            "⚠  Wanted level rises automatically as transgressions grow."
        ),
        "sim": "transgress",
        "color": "#ff4444",
    },
    {
        "title": "The Lobby",
        "subtitle": "Buying influence — legally ambiguous.",
        "body": (
            "The LOBBY lets you purchase political influence to manage your public image or "
            "criminal record — but NOT both at once.\n\n"
            "Each tier targets one stat:\n"
            "  • Favorable Coverage  → +15 opinion  ($3M)\n"
            "  • Buy a Senator [Image] → +30 opinion  ($40M)\n"
            "  • Buy a Senator [Records] → -25 transgressions  ($40M)\n"
            "  • Presidential Rehabilitation → opinion set to 80  ($150M)\n"
            "  • Full Records Expunge → transgressions reset to 0  ($150M)\n\n"
            "Use the Lobby proactively — waiting until you're at 0 opinion is too late."
        ),
        "sim": None,
        "color": "#1e90ff",
    },
    {
        "title": "The Stock Market",
        "subtitle": "Gamble with a graph.",
        "body": (
            "The STOCK MARKET shows live-ish price feeds for categories like Tech, Energy, "
            "and Defense.\n\n"
            "Your own actions affect the market — bombing a country spikes Energy and Defense stocks.\n\n"
            "You can:\n"
            "  • Buy shares in any category\n"
            "  • Sell at a profit for cash + happiness bonus\n"
            "  • Watch your portfolio grow or collapse with the market\n\n"
            "Tip: Buy Energy before you Bomb a country — your own action will pump the price."
        ),
        "sim": None,
        "color": "#00ccff",
    },
    {
        "title": "The Casino",
        "subtitle": "High risk, high reward.",
        "body": (
            "The CASINO has three games:\n\n"
            "  🔫 Russian Roulette — 1-in-6 death chance. Survive to double your bet.\n\n"
            "  🎰 Slot Machine — Match 3 symbols. JACKPOT 777 pays 100x your bet.\n"
            "     Bet is capped at 20% of your balance ($30M max).\n\n"
            "  🂡 Poker — 5-card draw. Bet → see hand → hold cards → draw.\n"
            "     NEW: Pay 1% of balance to PEEK at one card before you bet!\n\n"
            "⚠  Roulette can end your run instantly. Use it sparingly."
        ),
        "sim": None,
        "color": "#ffdd44",
    },
    {
        "title": "Rivals",
        "subtitle": "They're hunting the same countries.",
        "body": (
            "Three AI rivals (Viktor Drago, Chen Wei, Elizabeth Harlow) compete with you:\n\n"
            "  • They seize resource countries — 15% chance per day\n"
            "  • They grow their wealth 1–5% daily\n"
            "  • They ATTACK you directly 8% chance per day:\n"
            "      - Smear campaign → opinion hit\n"
            "      - Regulatory tip-off → transgressions spike\n"
            "      - Lawsuit → money + transgressions\n"
            "      - Operation sabotage → destroys your active ops\n\n"
            "  • If you bomb their territory → IMMEDIATE retaliation\n\n"
            "Buy Out rivals from the world map (2x cost) to reclaim countries."
        ),
        "sim": "rival_attack",
        "color": "#cc0044",
    },
    {
        "title": "Alliances",
        "subtitle": "Choose your allies wisely.",
        "body": (
            "Alliances give you passive bonuses and protection:\n\n"
            "  🌍 G7 — 15% action cost discount, blocks smear attacks (30%)\n"
            "  🐉 BRICS — 20% income boost, blocks sabotage (25%)\n"
            "  🕵  Five Eyes — spy intel on rivals, blocks regulatory attacks (35%)\n"
            "  💼 WEF — market bonuses, blocks lawsuit attacks (30%)\n"
            "  ☢  SCO — military discount, blocks all attacks (20% general)\n\n"
            "Alliances also intercept rival attacks — a blocked attack shows a popup "
            "from your alliance instead of taking damage.\n\n"
            "You can only be in one alliance at a time."
        ),
        "sim": None,
        "color": "#44aaff",
    },
    {
        "title": "Black Market",
        "subtitle": "Illegal, but effective.",
        "body": (
            "The BLACK MARKET sells high-risk, high-reward items:\n\n"
            "  • Insider Tips — instant stock profit\n"
            "  • Money Laundering — cleans dirty money\n"
            "  • Organ Trafficking — large cash, high transgressions\n"
            "  • Nuclear Materials — extreme income, extreme risk\n\n"
            "Each item has a 4-day cooldown after purchase — you can't spam them.\n\n"
            "⚠  High-transgression items will accelerate your wanted level. "
            "Balance black market use with regular lobby cleanups."
        ),
        "sim": None,
        "color": "#880088",
    },
    {
        "title": "Island Map & Epstein's Island",
        "subtitle": "Your offshore empire.",
        "body": (
            "The ISLAND MAP lets you purchase private islands for daily income:\n\n"
            "  • Each island costs millions and generates passive income\n"
            "  • You can zoom/pan the map (scroll wheel + right-click drag)\n"
            "  • Caribbean and Pacific view buttons for quick navigation\n\n"
            "Little Saint James (Jeffrey Epstein's island) is available for $45M.\n\n"
            "  • If you OWN the island: Epstein events let you FRAME rivals —\n"
            "    invite them, then expose them. They lose money and reputation.\n"
            "  • If you DON'T own it: you may receive an invite — "
            "    accept for happiness/money, but risk exposure."
        ),
        "sim": None,
        "color": "#00aa88",
    },
    {
        "title": "Death Screens & Infamy",
        "subtitle": "How your reign ends.",
        "body": (
            "You can die five ways — each has a unique end screen:\n\n"
            "  💸 Broke — balance hits zero\n"
            "  😔 Unhappy — happiness reaches 0 (1-day warning given)\n"
            "  📰 Disgraced — public opinion reaches 0 (1-day warning)\n"
            "  ⚖  Arrested — transgressions hit 100 (1-day warning)\n"
            "  🔫 Roulette — lost Russian Roulette\n\n"
            "Your final score includes your net worth and your INFAMY TITLE, "
            "earned based on your transgression history:\n"
            "  'Gentleman' → 'Schemer' → 'Oligarch' → 'Crime Lord' → 'Global Menace'"
        ),
        "sim": None,
        "color": "#ff2222",
    },
    {
        "title": "Multiplayer",
        "subtitle": "Play against real people.",
        "body": (
            "In MULTIPLAYER mode:\n\n"
            "  • Choose USA, China, or Russia (superpowers only)\n"
            "  • Up to 3 players in a lobby\n"
            "  • Rivals panel shows REAL player stats live\n"
            "  • Bombing a rival's home country starts a WAR:\n"
            "      - $1.5M/day tax + 1 transgression/day per active war\n"
            "  • In-game CHAT available\n"
            "  • WAR ROOM: buy militia and deploy attacks against rivals\n"
            "      - Spy, Raid, Assassinate, Sabotage, Blockade, Nuke\n\n"
            "Host by starting a server (python server.py), then others join via IP + lobby code."
        ),
        "sim": None,
        "color": "#1e90ff",
    },
    {
        "title": "You're Ready!",
        "subtitle": "Go build your corrupt empire.",
        "body": (
            "Quick survival tips:\n\n"
            "  ✅ Get resource operations running on Day 1\n"
            "  ✅ Join an alliance early for the cost discount\n"
            "  ✅ Watch your transgressions — lobby before hitting 80\n"
            "  ✅ Use the stock market to supplement income\n"
            "  ✅ Keep happiness above 10 at all times\n"
            "  ✅ Check the Rivals panel — buy out territories they steal\n"
            "  ✅ Use the Peek feature in Poker before big bets\n\n"
            "Good luck. You'll need it."
        ),
        "sim": None,
        "color": "#00ff90",
    },
]


class TutorialMixin:
    """Interactive step-by-step tutorial with a simulated game state."""

    def open_tutorial(self):
        self._tut_step = 0
        self._tut_sim_money    = 500_000_000
        self._tut_sim_happiness = 65
        self._tut_sim_opinion   = 50
        self._tut_sim_trans     = 12

        win = tk.Toplevel(self.root)
        win.title("Tutorial — Debt Clicker")
        win.configure(bg="#0e1117")
        win.geometry("660x580")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        self._tut_win = win

        # Top bar
        top = tk.Frame(win, bg="#0e1117")
        top.pack(fill="x", padx=20, pady=(18, 0))

        self._tut_step_label = tk.Label(top, text="", font=("Arial", 9),
                                        bg="#0e1117", fg="#555")
        self._tut_step_label.pack(side="right")

        self._tut_color_bar = tk.Frame(win, height=4, bg="#ff2222")
        self._tut_color_bar.pack(fill="x")

        self._tut_title = tk.Label(win, text="", font=("Impact", 24),
                                   bg="#0e1117", fg="#ff2222")
        self._tut_title.pack(pady=(12, 0))

        self._tut_subtitle = tk.Label(win, text="", font=("Arial", 10, "italic"),
                                      bg="#0e1117", fg="#888")
        self._tut_subtitle.pack()

        # Simulated HUD
        hud = tk.Frame(win, bg="#1e2130", padx=12, pady=8)
        hud.pack(fill="x", padx=20, pady=10)

        self._tut_hud_money   = tk.Label(hud, text="", font=("Arial", 10, "bold"),
                                         bg="#1e2130", fg="#00ff90")
        self._tut_hud_money.pack(side="left", padx=10)
        self._tut_hud_happy   = tk.Label(hud, text="", font=("Arial", 10),
                                         bg="#1e2130", fg="#ffdd44")
        self._tut_hud_happy.pack(side="left", padx=10)
        self._tut_hud_opinion = tk.Label(hud, text="", font=("Arial", 10),
                                         bg="#1e2130", fg="#44aaff")
        self._tut_hud_opinion.pack(side="left", padx=10)
        self._tut_hud_trans   = tk.Label(hud, text="", font=("Arial", 10),
                                         bg="#1e2130", fg="#ff4444")
        self._tut_hud_trans.pack(side="left", padx=10)

        # Body text
        body_frame = tk.Frame(win, bg="#0e1117")
        body_frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self._tut_body = scrolledtext.ScrolledText(
            body_frame, font=("Arial", 11), bg="#0e1117", fg="white",
            relief="flat", wrap="word", height=10, state="disabled",
            cursor="arrow", borderwidth=0,
        )
        self._tut_body.pack(fill="both", expand=True)

        # Simulation output box
        self._tut_sim_frame = tk.Frame(win, bg="#111122", padx=10, pady=6)
        self._tut_sim_label = tk.Label(self._tut_sim_frame, text="",
                                       font=("Courier", 9), bg="#111122", fg="#aaffaa",
                                       justify="left", wraplength=580)
        self._tut_sim_label.pack(anchor="w")

        # Navigation buttons
        nav = tk.Frame(win, bg="#0e1117")
        nav.pack(pady=10)

        self._tut_prev_btn = tk.Button(nav, text="← Back", font=("Arial", 10),
                                       bg="#1e2130", fg="#aaa", relief="flat",
                                       padx=16, pady=6,
                                       command=self._tut_prev)
        self._tut_prev_btn.pack(side="left", padx=8)

        self._tut_next_btn = tk.Button(nav, text="Next →", font=("Arial", 11, "bold"),
                                       bg="#ff2222", fg="white", relief="flat",
                                       padx=20, pady=6,
                                       command=self._tut_next)
        self._tut_next_btn.pack(side="left", padx=8)

        tk.Button(nav, text="Skip Tutorial", font=("Arial", 9),
                  bg="#0e1117", fg="#444", relief="flat",
                  padx=10, pady=6,
                  command=win.destroy).pack(side="left", padx=16)

        self._tut_render()

    def _tut_render(self):
        step = _STEPS[self._tut_step]
        total = len(_STEPS)
        color = step["color"]

        self._tut_color_bar.config(bg=color)
        self._tut_title.config(text=step["title"], fg=color)
        self._tut_subtitle.config(text=step["subtitle"])
        self._tut_step_label.config(text=f"Step {self._tut_step + 1} / {total}")

        self._tut_body.config(state="normal")
        self._tut_body.delete("1.0", "end")
        self._tut_body.insert("end", step["body"])
        self._tut_body.config(state="disabled")

        # Update simulated HUD
        self._tut_hud_money.config(
            text=f"💰 ${self._tut_sim_money:,.0f}")
        self._tut_hud_happy.config(
            text=f"😊 {self._tut_sim_happiness}%")
        self._tut_hud_opinion.config(
            text=f"📰 {self._tut_sim_opinion}%")
        self._tut_hud_trans.config(
            text=f"⚖  {self._tut_sim_trans} transgressions")

        # Run simulation snippet
        self._tut_sim_frame.pack_forget()
        sim = step.get("sim")
        if sim:
            result = self._tut_run_sim(sim)
            self._tut_sim_label.config(text=result)
            self._tut_sim_frame.pack(fill="x", padx=20, pady=(0, 6))

        # Nav button states
        self._tut_prev_btn.config(state="normal" if self._tut_step > 0 else "disabled")
        is_last = self._tut_step == len(_STEPS) - 1
        self._tut_next_btn.config(
            text="Close  ✓" if is_last else "Next →",
            bg="#00aa44" if is_last else "#ff2222",
            command=self._tut_win.destroy if is_last else self._tut_next,
        )

    def _tut_run_sim(self, sim_type):
        """Run a mini simulation and return a log string showing the result."""
        lines = []
        if sim_type == "drain":
            drain_pct = random.uniform(0.006, 0.016)
            drain = int(self._tut_sim_money * drain_pct)
            self._tut_sim_money -= drain
            lines.append(f"[Day simulation]  Daily drain: -{drain_pct*100:.2f}%")
            lines.append(f"  Money: ${self._tut_sim_money + drain:,.0f}  →  ${self._tut_sim_money:,.0f}")
            lines.append(f"  (Idle tax would add another 0.5% if no operations running)")

        elif sim_type == "resource":
            income = random.randint(800_000, 3_000_000)
            cost   = random.randint(10_000_000, 50_000_000)
            days   = random.randint(20, 60)
            self._tut_sim_money -= cost
            lines.append(f"[Simulated: Bomb → Saudi Arabia (Oil)]")
            lines.append(f"  Cost: -${cost:,.0f}")
            lines.append(f"  Income: +${income:,.0f}/day  for {days} days")
            lines.append(f"  Total return: +${income * days:,.0f}  (net: +${income*days - cost:,.0f})")
            lines.append(f"  Transgressions: +8    Wanted level raised.")

        elif sim_type == "stats":
            self._tut_sim_happiness = max(0, self._tut_sim_happiness - 1)
            opinion_hit = random.randint(3, 8)
            self._tut_sim_opinion = max(0, self._tut_sim_opinion - opinion_hit)
            lines.append(f"[Day tick]")
            lines.append(f"  Happiness: -{1}  →  {self._tut_sim_happiness}%")
            lines.append(f"  Rival smear campaign: opinion -{opinion_hit}%  →  {self._tut_sim_opinion}%")
            if self._tut_sim_opinion < 20:
                lines.append(f"  ⚠  WARNING: Opinion is critically low!")

        elif sim_type == "transgress":
            hit = random.randint(8, 18)
            self._tut_sim_trans = min(100, self._tut_sim_trans + hit)
            lines.append(f"[Black market purchase: Organ Trafficking]")
            lines.append(f"  Transgressions: +{hit}  →  {self._tut_sim_trans}")
            if self._tut_sim_trans >= 80:
                lines.append(f"  ⚠  DANGER ZONE — Lobby NOW or face arrest in {100 - self._tut_sim_trans} points")
            else:
                lobby_cost = 40_000_000
                lines.append(f"  Lobby cost to clear 25 points: ${lobby_cost:,.0f}")

        elif sim_type == "rival_attack":
            rival = random.choice(["Viktor Drago", "Chen Wei", "Elizabeth Harlow"])
            attack = random.choice(["smear", "lawsuit", "sabotage"])
            if attack == "smear":
                hit = random.randint(5, 15)
                self._tut_sim_opinion = max(0, self._tut_sim_opinion - hit)
                lines.append(f"[RIVAL ATTACK from {rival}]")
                lines.append(f"  Smear campaign — Opinion: -{hit}%  →  {self._tut_sim_opinion}%")
            elif attack == "lawsuit":
                fine = int(self._tut_sim_money * random.uniform(0.02, 0.05))
                trans = random.randint(5, 12)
                self._tut_sim_money -= fine
                self._tut_sim_trans = min(100, self._tut_sim_trans + trans)
                lines.append(f"[RIVAL ATTACK from {rival}]")
                lines.append(f"  Lawsuit filed — Money: -${fine:,.0f}  |  Transgressions: +{trans}")
            else:
                income_lost = random.randint(500_000, 2_000_000)
                self._tut_sim_money -= income_lost
                lines.append(f"[RIVAL ATTACK from {rival}]")
                lines.append(f"  Operation sabotaged — Lost: ${income_lost:,.0f} from your oil ops")
            lines.append(f"  (Alliance membership can BLOCK this type of attack)")

        return "\n".join(lines)

    def _tut_next(self):
        if self._tut_step < len(_STEPS) - 1:
            self._tut_step += 1
            self._tut_render()

    def _tut_prev(self):
        if self._tut_step > 0:
            self._tut_step -= 1
            self._tut_render()
