import tkinter as tk

LOAN_OPTIONS = [
    {"label": "Emergency Cash",    "amount":    5_000_000, "rate": 0.030, "days":  4},
    {"label": "Personal Loan",     "amount":   25_000_000, "rate": 0.025, "days":  6},
    {"label": "Corporate Bond",    "amount":  100_000_000, "rate": 0.020, "days":  8},
    {"label": "Hedge Fund Line",   "amount":  300_000_000, "rate": 0.016, "days": 10},
    {"label": "Sovereign Debt",    "amount":  750_000_000, "rate": 0.012, "days": 14},
    {"label": "Bailout Package",   "amount": 2_000_000_000,"rate": 0.010, "days": 20},
]

# Banks ordered from most to least legitimate.
# min_score: credit score required to apply (300–850 range).
# rate_bonus: extra interest added on top of base loan rate.
# blacklist_on_default: True = one default permanently bans you from this bank.
# default_war: True = defaulting adds an extra heavy transgression hit.
BANKS = [
    {
        "name":                 "First National Bank",
        "tab":                  "🏦 First National",
        "icon":                 "🏦",
        "desc":                 "Conservative lender. Best rates available. Strict background check — no criminals.",
        "min_score":            700,
        "rate_bonus":           0.000,
        "color":                "#4499ff",
        "blacklist_on_default": True,
    },
    {
        "name":                 "Merchant Credit Corp",
        "tab":                  "🏢 Merchant",
        "icon":                 "🏢",
        "desc":                 "Mid-tier commercial lender. Tolerates minor offences at a small surcharge.",
        "min_score":            550,
        "rate_bonus":           0.004,
        "color":                "#00cc88",
        "blacklist_on_default": True,
    },
    {
        "name":                 "Offshore Capital Ltd",
        "tab":                  "🌍 Offshore",
        "icon":                 "🌍",
        "desc":                 "Offshore lender. No questions asked — for a noticeable premium.",
        "min_score":            400,
        "rate_bonus":           0.010,
        "color":                "#ffaa00",
        "blacklist_on_default": False,
    },
    {
        "name":                 "Shadow Finance",
        "tab":                  "🕶️ Shadow",
        "icon":                 "🕶️",
        "desc":                 "Operates in the grey zone. Anything goes, at a steep price.",
        "min_score":            250,
        "rate_bonus":           0.018,
        "color":                "#cc44ff",
        "blacklist_on_default": False,
    },
    {
        "name":                 "Cartel Bank",
        "tab":                  "💀 Cartel",
        "icon":                 "💀",
        "desc":                 "No credit check. No questions. Default and they will collect… differently.",
        "min_score":            0,
        "rate_bonus":           0.030,
        "color":                "#ff2222",
        "blacklist_on_default": False,
        "default_war":          True,
    },
]


class DebtMixin:
    """Loan system — take on debt with daily compounding interest and a credit history."""

    # =========================================================
    # CREDIT SCORE
    # =========================================================

    def _credit_score(self):
        """Return current credit score in the 300–850 range.

        Factors:
          • Transgressions drag the score down (-7 per point).
          • Each loan default costs -100.
          • Each successfully repaid loan earns +30.
        """
        score = 850
        score -= int(getattr(self, "transgressions", 0) * 7)
        score -= getattr(self, "loan_defaults",  0) * 100
        score += getattr(self, "loans_repaid",   0) * 30
        return max(300, min(850, score))

    def _credit_label(self, score):
        """Return (label_str, colour) for a given score."""
        if score >= 750: return "Excellent", "#00ff90"
        if score >= 650: return "Good",       "#66dd66"
        if score >= 550: return "Fair",       "#ffdd00"
        if score >= 400: return "Poor",       "#ff9900"
        return               "Very Poor",    "#ff4444"

    def _bank_accessible(self, bank):
        """Return (accessible: bool, reason: str) for a given bank dict."""
        bl = getattr(self, "bank_blacklist", set())
        if bank["name"] in bl:
            return False, "You are permanently blacklisted from this institution."
        score = self._credit_score()
        if score < bank["min_score"]:
            lbl, _ = self._credit_label(score)
            return False, (
                f"Application denied. Credit score too low "
                f"({score} — need {bank['min_score']}).\n"
                f"Your rating: {lbl}. Reduce transgressions or repay loans to recover."
            )
        return True, ""

    # =========================================================
    # DEBT WINDOW
    # =========================================================

    def open_debt_window(self):
        win = tk.Toplevel(self.root)
        win.title("Debt & Loans")
        win.configure(bg="#0e1117")
        win.geometry("620x700")
        win.resizable(False, False)

        # ── Header ───────────────────────────────────────────────────────────
        tk.Label(win, text="DEBT & LOANS",
                 font=("Impact", 24), bg="#0e1117", fg="#ff6600").pack(pady=(14, 2))

        # Credit score
        score       = self._credit_score()
        s_lbl, s_col = self._credit_label(score)
        sf = tk.Frame(win, bg="#0e1117")
        sf.pack(pady=(0, 2))
        tk.Label(sf, text="Credit Score: ",
                 font=("Arial", 11), bg="#0e1117", fg="#888").pack(side="left")
        tk.Label(sf, text=f"{score}  ({s_lbl})",
                 font=("Arial", 11, "bold"), bg="#0e1117", fg=s_col).pack(side="left")

        # Score bar
        bar_c = tk.Canvas(win, height=10, width=500, bg="#222", highlightthickness=0)
        bar_c.pack(pady=(0, 4))
        fill_w = int(500 * max(0, (score - 300) / 550))
        bar_c.create_rectangle(0, 0, fill_w, 10, fill=s_col, outline="")

        # Quick stats
        total_owed  = sum(l["remaining"] for l in getattr(self, "loans", []))
        debt_color  = "#ff4444" if total_owed > 0 else "#00ff90"
        defaults    = getattr(self, "loan_defaults", 0)
        repaid      = getattr(self, "loans_repaid",  0)

        qf = tk.Frame(win, bg="#0e1117")
        qf.pack(pady=(0, 2))
        tk.Label(qf, text=f"Owed: ${total_owed:,.0f}",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg=debt_color).pack(side="left", padx=12)
        tk.Label(qf, text=f"Defaults: {defaults}",
                 font=("Arial", 10), bg="#0e1117",
                 fg="#ff4444" if defaults > 0 else "#555").pack(side="left", padx=12)
        tk.Label(qf, text=f"Repaid: {repaid}",
                 font=("Arial", 10), bg="#0e1117",
                 fg="#00ff90" if repaid > 0 else "#555").pack(side="left", padx=12)

        max_loans = getattr(self, "max_loans", 1)
        active    = len(getattr(self, "loans", []))
        slots_col = "#ffaa00" if active >= max_loans else "#00ff90"
        tk.Label(win, text=f"Loan slots: {active}/{max_loans}  |  Upgrade slots to borrow simultaneously.",
                 font=("Arial", 9), bg="#0e1117", fg=slots_col).pack()
        tk.Label(win, text="⚠  Loans compound daily. Default: 25% balance penalty + 10 transgressions.",
                 font=("Arial", 8), bg="#0e1117", fg="#666").pack(pady=(0, 4))

        # ── Scrollable content ────────────────────────────────────────────────
        container = tk.Frame(win, bg="#0e1117")
        container.pack(fill="both", expand=True, padx=0, pady=(0, 10))

        canvas    = tk.Canvas(container, bg="#0e1117", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner     = tk.Frame(canvas, bg="#0e1117")

        inner.bind("<Configure>",
                   lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _wheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _wheel)
        win.bind("<Destroy>", lambda _: canvas.unbind_all("<MouseWheel>"))

        # ── Active loans ──────────────────────────────────────────────────────
        tk.Label(inner, text="Active Loans", font=("Arial", 10, "bold"),
                 bg="#0e1117", fg="#aaaaaa").pack(pady=(8, 2))

        loans = getattr(self, "loans", [])
        if not loans:
            tk.Label(inner, text="No active loans.", font=("Arial", 9),
                     bg="#0e1117", fg="#555").pack(pady=4)
        else:
            for i, loan in enumerate(loans):
                row = tk.Frame(inner, bg="#1e2130", pady=6, padx=12)
                row.pack(fill="x", padx=16, pady=2)
                urgency   = "#ff4444" if loan["days_left"] <= 5 else (
                            "#ffaa00" if loan["days_left"] <= 10 else "white")
                grace     = loan.get("grace_days", 0)
                extra     = f"  [GRACE: {grace}d]" if grace > 0 else ""
                bank_name = loan.get("bank", "")
                bank_tag  = f"  [{bank_name}]" if bank_name else ""
                tk.Label(row,
                         text=f"Loan #{i+1}{bank_tag}: ${loan['remaining']:,.0f}  |  "
                              f"{loan['rate']*100:.2f}%/day  |  {loan['days_left']}d left{extra}",
                         font=("Arial", 9), bg="#1e2130", fg=urgency,
                         anchor="w").pack(side="left")

                def repay(idx=i, w=win):
                    l = self.loans[idx]
                    if self.money < l["remaining"]:
                        self.log_event(f"Not enough to repay (need ${l['remaining']:,.0f})")
                        return
                    self.money -= l["remaining"]
                    self.market.money = self.money
                    self.loans_repaid = getattr(self, "loans_repaid", 0) + 1
                    self.log_event(f"Repaid loan: ${l['remaining']:,.0f}")
                    self.loans.pop(idx)
                    self.update_status()
                    w.destroy()
                    self.open_debt_window()

                tk.Button(row, text="Repay",
                          font=("Arial", 9), bg="#ff4444", fg="white",
                          relief="flat", padx=8, pady=3,
                          command=repay).pack(side="right")

        # ── Loan slot upgrades ────────────────────────────────────────────────
        tk.Frame(inner, bg="#333", height=1).pack(fill="x", padx=24, pady=8)
        tk.Label(inner, text="Loan Slot Upgrades", font=("Arial", 10, "bold"),
                 bg="#0e1117", fg="#aaaaaa").pack(pady=(0, 4))

        SLOT_UPGRADES = [
            {"slots": 2, "cost": 500_000_000,    "label": "Slot 2 — 2 simultaneous loans"},
            {"slots": 3, "cost": 2_000_000_000,  "label": "Slot 3 — 3 simultaneous loans"},
        ]
        for su in SLOT_UPGRADES:
            already = getattr(self, "max_loans", 1) >= su["slots"]
            su_row  = tk.Frame(inner, bg="#1a1f2e", pady=6, padx=12)
            su_row.pack(fill="x", padx=16, pady=2)
            tk.Label(su_row, text=su["label"] + ("  ✅ OWNED" if already else ""),
                     font=("Arial", 10), bg="#1a1f2e",
                     fg="#00ff90" if already else "white").pack(side="left")
            if not already:
                can = self.money >= su["cost"]

                def _buy_slot(s=su, w=win):
                    if self.money < s["cost"]:
                        self.log_event(f"Can't afford loan slot upgrade (${s['cost']:,})")
                        return
                    self.money -= s["cost"]
                    self.market.money = self.money
                    self.max_loans = s["slots"]
                    self.loan_slots_purchased += 1
                    self.log_event(f"Loan slot upgraded — now {s['slots']} simultaneous loans allowed.")
                    self.update_status()
                    w.destroy()
                    self.open_debt_window()

                tk.Button(su_row,
                          text=f"Buy — ${su['cost']:,.0f}",
                          font=("Arial", 9, "bold"),
                          bg="#886600" if can else "#2a2a2a",
                          fg="white" if can else "#555",
                          relief="flat", padx=10, pady=3,
                          state="normal" if can else "disabled",
                          command=_buy_slot).pack(side="right")

        # ── Apply for a loan — bank selection ─────────────────────────────────
        tk.Frame(inner, bg="#333", height=1).pack(fill="x", padx=24, pady=8)
        tk.Label(inner, text="Apply for a Loan", font=("Arial", 10, "bold"),
                 bg="#0e1117", fg="#aaaaaa").pack(pady=(0, 4))

        at_limit = len(getattr(self, "loans", [])) >= getattr(self, "max_loans", 1)
        if at_limit:
            tk.Label(inner,
                     text="⛔  Loan limit reached. Repay a loan or upgrade your slot capacity.",
                     font=("Arial", 9, "bold"), bg="#0e1117", fg="#ff4444").pack(pady=(0, 6))

        # Bank tab buttons
        tab_frame = tk.Frame(inner, bg="#0e1117")
        tab_frame.pack(fill="x", padx=16, pady=(0, 2))

        # Loan details area — rebuilt on every tab click
        detail_frame = tk.Frame(inner, bg="#0e1117")
        detail_frame.pack(fill="x")

        selected_bank = [BANKS[0]]

        def show_bank(bank, btn_map):
            # Update tab highlights
            for b, btn in btn_map:
                sel = b["name"] == bank["name"]
                btn.config(
                    bg=bank["color"] if sel else "#1e2130",
                    fg=("black" if bank["color"] in ("#ffaa00", "#00ff90") else "white") if sel else "#888",
                    relief="sunken" if sel else "flat",
                )
            selected_bank[0] = bank

            # Rebuild detail area
            for w in detail_frame.winfo_children():
                w.destroy()

            accessible, reason = self._bank_accessible(bank)

            # Bank header card
            hdr = tk.Frame(detail_frame, bg="#111820", pady=8, padx=14)
            hdr.pack(fill="x", padx=16, pady=(2, 4))
            tk.Label(hdr, text=f"{bank['icon']}  {bank['name']}",
                     font=("Arial", 12, "bold"), bg="#111820", fg=bank["color"]).pack(anchor="w")
            tk.Label(hdr, text=bank["desc"],
                     font=("Arial", 8), bg="#111820", fg="#666").pack(anchor="w")

            req_score = bank["min_score"]
            cur_score = self._credit_score()
            if req_score > 0:
                score_fg = "#00ff90" if cur_score >= req_score else "#ff4444"
                tk.Label(hdr,
                         text=f"Minimum credit score: {req_score}  |  Yours: {cur_score}",
                         font=("Arial", 8, "italic"), bg="#111820", fg=score_fg).pack(anchor="w")

            if bank["rate_bonus"] > 0:
                tk.Label(hdr,
                         text=f"Rate surcharge: +{bank['rate_bonus']*100:.1f}%/day on all loans",
                         font=("Arial", 8, "italic"), bg="#111820", fg="#ffaa00").pack(anchor="w")

            if bank.get("blacklist_on_default"):
                tk.Label(hdr, text="⚠  One default = permanent blacklist from this bank.",
                         font=("Arial", 7, "italic"), bg="#111820", fg="#ff6666").pack(anchor="w")
            if bank.get("default_war"):
                tk.Label(hdr, text="☠  Default here and the cartel will come for you (+20 transgression).",
                         font=("Arial", 7, "italic"), bg="#111820", fg="#ff2222").pack(anchor="w")

            # Denial message
            if not accessible:
                tk.Label(detail_frame, text=reason,
                         font=("Arial", 9, "bold"), bg="#0e1117", fg="#ff4444",
                         wraplength=540, justify="center").pack(pady=12)
                return

            # Loan options (hidden if at limit — buttons already blocked above)
            for opt in LOAN_OPTIONS:
                adj_rate = opt["rate"] + bank["rate_bonus"]
                total    = opt["amount"] * ((1 + adj_rate) ** opt["days"])
                row = tk.Frame(detail_frame, bg="#1e2130", pady=8, padx=12)
                row.pack(fill="x", padx=16, pady=3)

                info = tk.Frame(row, bg="#1e2130")
                info.pack(side="left", fill="both", expand=True)
                tk.Label(info, text=opt["label"],
                         font=("Arial", 11, "bold"), bg="#1e2130", fg="white",
                         anchor="w").pack(anchor="w")
                tk.Label(info,
                         text=f"Borrow ${opt['amount']:,}  |  {adj_rate*100:.2f}%/day  |  "
                              f"{opt['days']}-day term  |  Repay ≈ ${total:,.0f}",
                         font=("Arial", 8), bg="#1e2130", fg="#888", anchor="w").pack(anchor="w")

                exec_mult = getattr(self, "get_executive_loan_rate_multiplier",
                                    lambda: 1.0)()
                adj_rate  = adj_rate * exec_mult

                def take(o=opt, b=bank, adj=adj_rate, w=win):
                    if not hasattr(self, "loans"):
                        self.loans = []
                    if len(self.loans) >= getattr(self, "max_loans", 1):
                        self.log_event("⛔ Loan limit reached.")
                        return
                    ok, msg = self._bank_accessible(b)
                    if not ok:
                        self.log_event(f"Loan denied by {b['name']}: {msg}")
                        return
                    self.money += o["amount"]
                    self.market.money = self.money
                    self.loans.append({
                        "amount":     o["amount"],
                        "remaining":  float(o["amount"]),
                        "rate":       adj,
                        "days_left":  o["days"],
                        "grace_days": 0,
                        "bank":       b["name"],
                    })
                    self.update_status()
                    self.log_event(
                        f"[{b['name']}] Approved: +${o['amount']:,} at "
                        f"{adj*100:.2f}%/day for {o['days']} days")
                    self._add_ticker(f"MARKETS: New debt issued via {b['name']}...")
                    w.destroy()
                    self.open_debt_window()

                tk.Button(row, text="Apply",
                          font=("Arial", 10, "bold"),
                          bg="#555" if at_limit else bank["color"],
                          fg="#333" if at_limit else (
                              "black" if bank["color"] in ("#ffaa00", "#00ff90") else "white"),
                          relief="flat", padx=14, pady=5,
                          state="disabled" if at_limit else "normal",
                          command=take).pack(side="right")

        # Build tab buttons
        btn_map = []
        for bank in BANKS:
            accessible, _ = self._bank_accessible(bank)
            btn = tk.Button(
                tab_frame,
                text=bank["tab"],
                font=("Arial", 8),
                bg="#1e2130",
                fg="white" if accessible else "#444",
                activebackground=bank["color"],
                activeforeground="black",
                relief="flat", padx=6, pady=4,
            )
            btn.pack(side="left", padx=2, pady=2)
            btn_map.append((bank, btn))

        for bank, btn in btn_map:
            btn.config(command=lambda b=bank: show_bank(b, btn_map))

        # Open on first accessible bank (or first bank if all denied)
        default_bank = next((b for b in BANKS if self._bank_accessible(b)[0]), BANKS[0])
        show_bank(default_bank, btn_map)

    # =========================================================
    # DAILY LOAN PROCESSING
    # =========================================================

    def process_loans(self):
        """Called daily — compound interest and check for defaults."""
        if not getattr(self, "loans", []):
            return
        new_loans = []
        for loan in self.loans:
            loan["remaining"] += loan["remaining"] * loan["rate"]
            loan["days_left"] -= 1

            if loan["days_left"] <= 0:
                if self.money >= loan["remaining"]:
                    self.money -= loan["remaining"]
                    self.market.money = self.money
                    self.loans_repaid = getattr(self, "loans_repaid", 0) + 1
                    self.log_event(f"Loan auto-repaid: ${loan['remaining']:,.0f}")
                elif self.money > 0:
                    paid = self.money
                    loan["remaining"] -= paid
                    self.money = 0
                    self.market.money = 0
                    grace = loan.get("grace_days", 0)
                    if grace < 3:
                        loan["days_left"] = 3
                        loan["grace_days"] = grace + 1
                        new_loans.append(loan)
                        self.log_event(
                            f"Partial payment ${paid:,.0f} — "
                            f"${loan['remaining']:,.0f} still owed. Grace: {3 - grace} days.")
                    else:
                        self._apply_loan_default(loan)
                else:
                    self._apply_loan_default(loan)
            else:
                new_loans.append(loan)
                if loan["days_left"] in (1, 3, 7):
                    self.log_event(
                        f"Loan warning: ${loan['remaining']:,.0f} due in "
                        f"{loan['days_left']} day(s)")
        self.loans = new_loans

    def _apply_loan_default(self, loan):
        """Apply default penalties and update credit history for one loan."""
        penalty = max(0, self.money * 0.25)
        self.money -= penalty
        self.market.money = self.money

        self.loan_defaults = getattr(self, "loan_defaults", 0) + 1
        bank_name = loan.get("bank", "Unknown")

        self.log_event(
            f"LOAN DEFAULT ({bank_name})! Lost ${penalty:,.0f} (25% penalty). "
            f"${loan['remaining']:,.0f} written off. Credit score hit.")
        self.add_transgression(10, 8)
        self._add_ticker("BREAKING: Debt default — creditors seize assets!")

        # Blacklist from this bank if it has that policy
        bank_data = next((b for b in BANKS if b["name"] == bank_name), None)
        if bank_data:
            if bank_data.get("blacklist_on_default"):
                if not hasattr(self, "bank_blacklist"):
                    self.bank_blacklist = set()
                self.bank_blacklist.add(bank_name)
                self.log_event(f"BLACKLISTED: {bank_name} will never lend to you again.")
            if bank_data.get("default_war"):
                self.add_transgression(20, 20)
                self._add_ticker("WARNING: Cartel Bank collectors are looking for you...")
