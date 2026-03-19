import tkinter as tk
import random

FACTORY_TYPES = [
    {
        "id": "steel_mill",
        "name": "Steel Mill",
        "icon": "🏭",
        "desc": "Heavy industry. Massive workforce, reliable output.",
        "price": 500_000_000,
        "income": 6_000_000,
        "base_wage_cost": 1_200_000,
        "workers": 500,
        "color": "#888888",
    },
    {
        "id": "oil_refinery",
        "name": "Oil Refinery",
        "icon": "🛢",
        "desc": "Refine crude into profit. Volatile but lucrative.",
        "price": 900_000_000,
        "income": 10_000_000,
        "base_wage_cost": 900_000,
        "workers": 300,
        "color": "#aa6600",
    },
    {
        "id": "tech_factory",
        "name": "Tech Manufacturing Plant",
        "icon": "💻",
        "desc": "Consumer electronics assembly. Skilled workforce required.",
        "price": 1_400_000_000,
        "income": 15_000_000,
        "base_wage_cost": 800_000,
        "workers": 200,
        "color": "#0088ff",
    },
    {
        "id": "pharma_plant",
        "name": "Pharmaceutical Plant",
        "icon": "💊",
        "desc": "Produce drugs (legally... mostly). High margins, high scrutiny.",
        "price": 1_800_000_000,
        "income": 20_000_000,
        "base_wage_cost": 700_000,
        "workers": 150,
        "color": "#00cc88",
    },
    {
        "id": "arms_factory",
        "name": "Arms Factory",
        "icon": "💣",
        "desc": "Defense contractor. Extreme income. Extreme consequences.",
        "price": 3_000_000_000,
        "income": 35_000_000,
        "base_wage_cost": 500_000,
        "workers": 100,
        "color": "#ff4444",
        "trans_per_day": 1,
    },
]

WORKER_TIERS = [
    {
        "id": "underpaid",
        "name": "Underpaid Labor",
        "wage_mult": 0.50,
        "income_mult": 0.80,
        "opinion_per_day": -3,
        "happiness_per_day": 0,
        "color": "#ff4444",
        "desc": "Half wages. Workers are miserable. Public will find out.",
    },
    {
        "id": "minimum",
        "name": "Minimum Wage",
        "wage_mult": 0.75,
        "income_mult": 0.90,
        "opinion_per_day": -1,
        "happiness_per_day": 0,
        "color": "#ff8800",
        "desc": "Technically legal. Barely. Slow opinion bleed.",
    },
    {
        "id": "standard",
        "name": "Standard Workers",
        "wage_mult": 1.00,
        "income_mult": 1.00,
        "opinion_per_day": 0,
        "happiness_per_day": 0,
        "color": "#aaaaaa",
        "desc": "Fair market rate. No bonuses, no backlash.",
    },
    {
        "id": "skilled",
        "name": "Skilled Workforce",
        "wage_mult": 1.40,
        "income_mult": 1.20,
        "opinion_per_day": 0.5,
        "happiness_per_day": 0.2,
        "color": "#44aaff",
        "desc": "Pay more, earn more. Good for PR.",
    },
    {
        "id": "unionized",
        "name": "Unionized Labor",
        "wage_mult": 1.80,
        "income_mult": 1.10,
        "opinion_per_day": 1.0,
        "happiness_per_day": 0.3,
        "color": "#ffaa00",
        "desc": "Strong union contract. Best public image. Cannot lower wages below this.",
    },
]

_WORKER_BY_ID = {w["id"]: w for w in WORKER_TIERS}
_FACTORY_BY_ID = {f["id"]: f for f in FACTORY_TYPES}


class FactoryMixin:
    """Factory purchasing, worker management, and daily income."""

    # =========================================================
    # OPEN FACTORY WINDOW
    # =========================================================

    def open_factory_window(self):
        win = tk.Toplevel(self.root)
        win.title("Factory Management")
        win.configure(bg="#0e1117")
        win.geometry("620x640")
        win.resizable(False, True)

        tk.Label(win, text="🏭  FACTORIES",
                 font=("Impact", 26), bg="#0e1117", fg="#ffaa00").pack(pady=(18, 2))
        tk.Label(win, text="Buy factories. Hire workers. Exploit accordingly.",
                 font=("Arial", 9), bg="#0e1117", fg="#555").pack(pady=(0, 8))

        container = tk.Frame(win, bg="#0e1117")
        container.pack(fill="both", expand=True, padx=0, pady=(0, 10))

        canvas = tk.Canvas(container, bg="#0e1117", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#0e1117")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _wheel(e):
            try:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _wheel)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ── Owned factories ──────────────────────────────────────
        if self.factories:
            tk.Label(inner, text="YOUR FACTORIES", font=("Impact", 14),
                     bg="#0e1117", fg="#ffaa00").pack(anchor="w", padx=16, pady=(8, 2))
            for fac in self.factories:
                self._build_owned_factory_row(inner, fac, win)
            tk.Frame(inner, bg="#333", height=1).pack(fill="x", padx=16, pady=10)

        # ── Buy new factories ────────────────────────────────────
        tk.Label(inner, text="BUY A FACTORY", font=("Impact", 14),
                 bg="#0e1117", fg="#888").pack(anchor="w", padx=16, pady=(4, 2))

        owned_ids = {f["type_id"] for f in self.factories}
        for ftype in FACTORY_TYPES:
            self._build_factory_buy_row(inner, ftype, ftype["id"] in owned_ids, win)

    def _build_owned_factory_row(self, parent, fac, win):
        ftype   = _FACTORY_BY_ID[fac["type_id"]]
        worker  = _WORKER_BY_ID[fac["worker_tier"]]
        color   = ftype["color"]

        daily_income = int(ftype["income"] * worker["income_mult"])
        daily_wages  = int(ftype["base_wage_cost"] * worker["wage_mult"])
        daily_net    = daily_income - daily_wages

        outer = tk.Frame(parent, bg="#1a1f2e", padx=12, pady=10)
        outer.pack(fill="x", padx=12, pady=4)
        tk.Frame(outer, bg=color, width=4).pack(side="left", fill="y", padx=(0, 10))

        info = tk.Frame(outer, bg="#1a1f2e")
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=f"{ftype['icon']}  {ftype['name']}",
                 font=("Arial", 12, "bold"), bg="#1a1f2e", fg=color).pack(anchor="w")

        stats_txt = (f"Workers: {ftype['workers']}  |  "
                     f"Income: ${daily_income:,.0f}/day  |  "
                     f"Wages: -${daily_wages:,.0f}/day  |  "
                     f"Net: ${daily_net:+,.0f}/day")
        tk.Label(info, text=stats_txt, font=("Arial", 8),
                 bg="#1a1f2e", fg="#aaaaaa").pack(anchor="w", pady=(2, 4))

        if fac.get("shutdown_days", 0) > 0:
            tk.Label(info,
                     text=f"🚫 SHUTDOWN — {fac['shutdown_days']} days remaining  (no income, wages still due)",
                     font=("Arial", 8, "bold"), bg="#1a1f2e", fg="#ff2222").pack(anchor="w")
        elif fac.get("on_strike"):
            tk.Label(info, text=f"🪧 ON STRIKE — {fac['strike_days']} days remaining  (income halted)",
                     font=("Arial", 8, "bold"), bg="#1a1f2e", fg="#ff4444").pack(anchor="w")
        elif fac.get("damaged_days", 0) > 0:
            tk.Label(info,
                     text=f"⚠️ DAMAGED — {fac['damaged_days']} days at 50% capacity  (repairs underway)",
                     font=("Arial", 8, "bold"), bg="#1a1f2e", fg="#ff8800").pack(anchor="w")

        # Worker tier buttons
        tier_row = tk.Frame(info, bg="#1a1f2e")
        tier_row.pack(anchor="w", pady=(4, 0))
        tk.Label(tier_row, text="Workers:", font=("Arial", 8),
                 bg="#1a1f2e", fg="#666").pack(side="left", padx=(0, 6))

        for wt in WORKER_TIERS:
            is_current = wt["id"] == fac["worker_tier"]
            # Can't go below unionized if unionized
            locked = (fac.get("unionized") and
                      WORKER_TIERS.index(wt) < WORKER_TIERS.index(_WORKER_BY_ID["unionized"]))
            def _set_tier(wid=wt["id"], f=fac, w=win):
                f["worker_tier"] = wid
                w.destroy()
                self.open_factory_window()

            tk.Button(tier_row, text=wt["name"],
                      font=("Arial", 8), relief="flat", padx=8, pady=3,
                      bg=wt["color"] if is_current else "#2a2f3e",
                      fg="black" if is_current else "#888",
                      state="disabled" if locked else "normal",
                      command=_set_tier).pack(side="left", padx=2)

        # Opinion/happiness effect preview
        eff_parts = []
        if worker["opinion_per_day"] != 0:
            sign = "+" if worker["opinion_per_day"] > 0 else ""
            eff_parts.append(f"Opinion {sign}{worker['opinion_per_day']:.1f}/day")
        if worker["happiness_per_day"] != 0:
            sign = "+" if worker["happiness_per_day"] > 0 else ""
            eff_parts.append(f"Happiness {sign}{worker['happiness_per_day']:.1f}/day")
        if ftype.get("trans_per_day"):
            eff_parts.append(f"+{ftype['trans_per_day']} transgressions/day")
        if eff_parts:
            tk.Label(info, text="  ".join(eff_parts),
                     font=("Arial", 8, "italic"), bg="#1a1f2e", fg="#777").pack(anchor="w", pady=(4, 0))

    def _build_factory_buy_row(self, parent, ftype, already_owned, win):
        color = ftype["color"] if not already_owned else "#444"

        row = tk.Frame(parent, bg="#111520", padx=12, pady=8)
        row.pack(fill="x", padx=12, pady=3)

        left = tk.Frame(row, bg="#111520")
        left.pack(side="left", fill="both", expand=True)

        title_txt = f"{ftype['icon']}  {ftype['name']}"
        if already_owned:
            title_txt += "  [OWNED]"
        tk.Label(left, text=title_txt, font=("Arial", 11, "bold"),
                 bg="#111520", fg=color).pack(anchor="w")
        tk.Label(left, text=ftype["desc"], font=("Arial", 8),
                 bg="#111520", fg="#666", wraplength=360, justify="left").pack(anchor="w")

        net = ftype["income"] - ftype["base_wage_cost"]
        extras = []
        if ftype.get("trans_per_day"):
            extras.append(f"+{ftype['trans_per_day']} trans/day")
        stats = (f"Price: ${ftype['price']:,.0f}  |  "
                 f"Gross income: ${ftype['income']:,.0f}/day  |  "
                 f"Workers: {ftype['workers']}  |  "
                 f"Net (std wages): ${net:+,.0f}/day"
                 + (f"  |  {', '.join(extras)}" if extras else ""))
        tk.Label(left, text=stats, font=("Arial", 7),
                 bg="#111520", fg="#555").pack(anchor="w", pady=(2, 0))

        def _buy(ft=ftype, w=win):
            if self.money < ft["price"]:
                self.log_event(f"Can't afford {ft['name']} (${ft['price']:,.0f})")
                return
            self.money -= ft["price"]
            self.market.money = self.money
            self.factories.append({
                "type_id":     ft["id"],
                "worker_tier": "standard",
                "on_strike":   False,
                "strike_days": 0,
                "unionized":   False,
                "days_owned":  0,
            })
            self.log_event(f"Purchased {ft['icon']} {ft['name']} for ${ft['price']:,.0f}!")
            self._add_ticker(f"MARKETS: {self.username} expands into manufacturing — {ft['name']} acquired.")
            self.update_status()
            w.destroy()
            self.open_factory_window()

        tk.Button(row,
                  text="OWNED" if already_owned else "Buy",
                  font=("Arial", 10, "bold"),
                  bg="#333" if already_owned else "#ffaa00",
                  fg="#555" if already_owned else "black",
                  relief="flat", padx=14, pady=5,
                  state="disabled" if already_owned else "normal",
                  command=_buy).pack(side="right")

    # =========================================================
    # DAILY FACTORY INCOME  (called from main_loop)
    # =========================================================

    def process_factory_income(self):
        if not self.factories:
            return
        total_income = 0
        total_wages  = 0
        for fac in self.factories:
            ftype  = _FACTORY_BY_ID[fac["type_id"]]
            worker = _WORKER_BY_ID[fac["worker_tier"]]

            fac["days_owned"] = fac.get("days_owned", 0) + 1

            # Tick shutdown (whistleblower / inspection closure)
            if fac.get("shutdown_days", 0) > 0:
                fac["shutdown_days"] -= 1
                if fac["shutdown_days"] == 0:
                    self.log_event(f"🏭 {ftype['name']} has reopened after forced shutdown.")
                # No income, still pay wages
                wages = int(ftype["base_wage_cost"] * worker["wage_mult"])
                total_wages += wages
                continue

            # Tick strike
            if fac.get("on_strike"):
                fac["strike_days"] = max(0, fac["strike_days"] - 1)
                if fac["strike_days"] == 0:
                    fac["on_strike"] = False
                    self.log_event(f"🏭 Strike at {ftype['name']} has ended — workers return.")
                wages = int(ftype["base_wage_cost"] * worker["wage_mult"])
                total_wages += wages
                continue

            # Tick damage (accident reduced capacity)
            income_mult_extra = 1.0
            if fac.get("damaged_days", 0) > 0:
                fac["damaged_days"] -= 1
                income_mult_extra = 0.5   # half output while damaged
                if fac["damaged_days"] == 0:
                    self.log_event(f"🏭 {ftype['name']} repairs complete — back to full capacity.")

            income = int(ftype["income"] * worker["income_mult"] * income_mult_extra)
            wages  = int(ftype["base_wage_cost"] * worker["wage_mult"])
            total_income += income
            total_wages  += wages

            # Opinion and happiness drift from worker tier
            if worker["opinion_per_day"] != 0:
                self.public_opinion = max(0, min(100,
                    self.public_opinion + worker["opinion_per_day"]))
            if worker["happiness_per_day"] != 0:
                self.happiness = max(0, min(100,
                    self.happiness + worker["happiness_per_day"]))

            # Arms factory transgression
            if ftype.get("trans_per_day"):
                self.add_transgression(ftype["trans_per_day"], 0)

        net = total_income - total_wages
        self.money += net
        self.market.money = self.money
        if self.factories:
            self.log_event(
                f"🏭 Factories: +${total_income:,.0f} income  "
                f"-${total_wages:,.0f} wages  =  ${net:+,.0f} net")

    # =========================================================
    # FACTORY EVENTS  (called from main_loop when factories owned)
    # =========================================================

    def check_factory_events(self):
        if not self.factories:
            return
        if random.random() > 0.18:   # ~18% chance per day
            return

        fac   = random.choice(self.factories)
        ftype = _FACTORY_BY_ID[fac["type_id"]]
        color = ftype["color"]
        event = random.choice(["strike", "accident", "whistleblower",
                               "record_profits", "union_drive", "inspection"])

        if event == "strike":
            if fac.get("on_strike"):
                return
            worker = _WORKER_BY_ID[fac["worker_tier"]]
            # Only underpaid/minimum wage workers strike
            if worker["id"] not in ("underpaid", "minimum"):
                event = "record_profits"   # fallback
            else:
                duration = random.randint(2, 5)
                fac["on_strike"]   = True
                fac["strike_days"] = duration
                self.public_opinion = max(0, self.public_opinion - 12)
                self.log_event(
                    f"🪧 STRIKE at {ftype['name']}! Workers walk out for {duration} days. "
                    f"Opinion -12. Raise wages to prevent future strikes.")
                self._show_factory_event(
                    ftype, color, "Workers' Strike",
                    f"Your {ftype['name']} workers have walked out.\n\n"
                    f"Production halted for {duration} days.\n"
                    f"Public Opinion -12\n\n"
                    f"Tip: Raise worker tier to prevent future strikes.")
                return

        if event == "accident":
            fine    = int(self.money * random.uniform(0.02, 0.06))
            trans   = random.randint(10, 20)
            dmg_days = random.randint(3, 7)
            self.money -= fine
            self.market.money = self.money
            self.add_transgression(trans, 10)
            self.public_opinion = max(0, self.public_opinion - 15)
            fac["damaged_days"] = dmg_days          # ← factory at 50% for N days
            self.log_event(
                f"💥 ACCIDENT at {ftype['name']}! Fine: -${fine:,.0f} | "
                f"Transgressions +{trans} | Opinion -15 | "
                f"Running at 50% capacity for {dmg_days} days")
            self._show_factory_event(
                ftype, "#ff2222", "Factory Accident",
                f"An explosion at your {ftype['name']} has made headlines.\n\n"
                f"-${fine:,.0f}  |  Transgressions +{trans}  |  Opinion -15\n\n"
                f"Factory running at 50% capacity for {dmg_days} days while repairs complete.")

        elif event == "whistleblower":
            trans     = random.randint(12, 25)
            shut_days = random.randint(2, 4)
            self.add_transgression(trans, 8)
            self.public_opinion = max(0, self.public_opinion - 18)
            fac["shutdown_days"] = shut_days        # ← factory closed for N days
            self.log_event(
                f"📢 WHISTLEBLOWER at {ftype['name']}! Safety violations exposed. "
                f"Transgressions +{trans} | Opinion -18 | "
                f"Factory shutdown for {shut_days} days")
            self._show_factory_event(
                ftype, "#cc44ff", "Whistleblower",
                f"A worker at your {ftype['name']} has gone to the press\n"
                f"with evidence of safety violations.\n\n"
                f"Transgressions +{trans}  |  Public Opinion -18\n\n"
                f"Regulators have ordered a {shut_days}-day shutdown.")

        elif event == "record_profits":
            bonus = int(ftype["income"] * random.uniform(0.5, 1.5))
            self.money += bonus
            self.market.money = self.money
            self.happiness = min(100, self.happiness + 5)
            self.log_event(
                f"📈 RECORD PROFITS at {ftype['name']}! Bonus: +${bonus:,.0f}")
            self._show_factory_event(
                ftype, "#00ff90", "Record Profits",
                f"Your {ftype['name']} has posted record quarterly results!\n\n"
                f"+${bonus:,.0f}  |  Happiness +5")

        elif event == "union_drive":
            if fac.get("unionized") or fac["worker_tier"] == "unionized":
                return
            self._show_union_drive(fac, ftype, color)

        elif event == "inspection":
            if self.transgressions < 30:
                return
            fine      = int(self.money * random.uniform(0.01, 0.03))
            shut_days = random.randint(1, 3) if self.transgressions > 60 else 0
            self.money -= fine
            self.market.money = self.money
            shut_txt = ""
            if shut_days:
                fac["shutdown_days"] = shut_days    # ← factory closed if bad enough
                shut_txt = f"\nFactory ordered closed for {shut_days} days."
            self.log_event(
                f"🔍 GOVERNMENT INSPECTION at {ftype['name']}! Fine: -${fine:,.0f}"
                + (f" | Shutdown {shut_days} days" if shut_days else ""))
            self._show_factory_event(
                ftype, "#ffaa00", "Government Inspection",
                f"Regulators have audited your {ftype['name']}.\n\n"
                f"Fine: -${fine:,.0f}{shut_txt}\n\n"
                f"(Reduce transgressions to avoid future inspections)")

        self.update_status()

    def _show_factory_event(self, ftype, color, title, body):
        win = tk.Toplevel(self.root)
        win.title("Factory Event")
        win.configure(bg="#0e1117")
        win.geometry("400x230")
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        def _close(e=None):
            try:
                win.destroy()
            except tk.TclError:
                pass

        win.bind("<Return>", _close)
        win.bind("<Escape>", _close)
        win.after(12000, _close)

        tk.Frame(win, bg=color, height=5).pack(fill="x")
        tk.Label(win, text=f"{ftype['icon']}  {title.upper()}",
                 font=("Impact", 18), bg="#0e1117", fg=color).pack(pady=(14, 2))
        tk.Label(win, text=f"— {ftype['name']} —",
                 font=("Arial", 9, "italic"), bg="#0e1117", fg="#888").pack()
        tk.Label(win, text=body, font=("Arial", 10), bg="#0e1117", fg="white",
                 wraplength=360, justify="center").pack(pady=10)
        tk.Button(win, text="Noted  [Enter]", font=("Arial", 10),
                  bg=color, fg="black" if color in ("#00ff90", "#ffaa00") else "white",
                  relief="flat", padx=20, pady=5, command=_close).pack(pady=(0, 14))
        tk.Frame(win, bg=color, height=4).pack(fill="x")

    def _show_union_drive(self, fac, ftype, color):
        win = tk.Toplevel(self.root)
        win.title("Union Drive")
        win.configure(bg="#0e1117")
        win.geometry("420x260")
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        tk.Frame(win, bg="#ffaa00", height=5).pack(fill="x")
        tk.Label(win, text=f"🟡  UNION DRIVE",
                 font=("Impact", 18), bg="#0e1117", fg="#ffaa00").pack(pady=(14, 2))
        tk.Label(win, text=f"— {ftype['name']} —",
                 font=("Arial", 9, "italic"), bg="#0e1117", fg="#888").pack()
        tk.Label(win,
                 text=(f"Workers at your {ftype['name']} are organizing.\n\n"
                       f"ACCEPT: Wages locked at Unionized tier (+80% cost, +1 opinion/day, "
                       f"can't cut wages later).\n"
                       f"REFUSE: Workers stay, but Opinion -20 and strike risk rises."),
                 font=("Arial", 10), bg="#0e1117", fg="white",
                 wraplength=380, justify="center").pack(pady=10)

        btn_row = tk.Frame(win, bg="#0e1117")
        btn_row.pack()

        def _accept():
            fac["worker_tier"] = "unionized"
            fac["unionized"]   = True
            self.public_opinion = min(100, self.public_opinion + 10)
            self.log_event(f"✅ Accepted union at {ftype['name']}. Workers now Unionized. Opinion +10.")
            win.destroy()
            self.update_status()

        def _refuse():
            self.public_opinion = max(0, self.public_opinion - 20)
            self.log_event(f"❌ Refused union at {ftype['name']}. Opinion -20. Strike risk elevated.")
            win.destroy()
            self.update_status()

        tk.Button(btn_row, text="Accept Union", font=("Arial", 10, "bold"),
                  bg="#ffaa00", fg="black", relief="flat", padx=16, pady=6,
                  command=_accept).pack(side="left", padx=8)
        tk.Button(btn_row, text="Refuse", font=("Arial", 10),
                  bg="#2a1a1a", fg="#ff4444", relief="flat", padx=16, pady=6,
                  command=_refuse).pack(side="left", padx=8)
