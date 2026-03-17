import tkinter as tk

LOAN_OPTIONS = [
    {"label": "Quick Loan",     "amount": 10_000_000,  "rate": 0.08, "days": 30},
    {"label": "Mid-Size Loan",  "amount": 50_000_000,  "rate": 0.06, "days": 30},
    {"label": "Corporate Bond", "amount": 200_000_000, "rate": 0.04, "days": 30},
]


class DebtMixin:
    """Loan system — take on debt with daily compounding interest."""

    def open_debt_window(self):
        win = tk.Toplevel(self.root)
        win.title("Debt & Loans")
        win.configure(bg="#0e1117")
        win.geometry("500x520")
        win.resizable(False, False)

        tk.Label(win, text="DEBT & LOANS",
                 font=("Impact", 24), bg="#0e1117", fg="#ff6600").pack(pady=(18, 2))

        total_owed = sum(l["remaining"] for l in getattr(self, "loans", []))
        debt_color = "#ff4444" if total_owed > 0 else "#00ff90"
        tk.Label(win, text=f"Total Owed: ${total_owed:,.0f}",
                 font=("Arial", 11, "bold"), bg="#0e1117", fg=debt_color).pack(pady=(0, 4))

        # ── Scrollable content area ───────────────────────────────────
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

        def _wheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _wheel)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ── Active loans ──────────────────────────────────────────────
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
                urgency = "#ff4444" if loan["days_left"] <= 5 else "white"
                tk.Label(row,
                         text=f"Loan #{i+1}: ${loan['remaining']:,.0f}  |  "
                              f"{loan['rate']*100:.0f}%/day  |  {loan['days_left']} days left",
                         font=("Arial", 9), bg="#1e2130", fg=urgency).pack(side="left")

                def repay(idx=i, w=win):
                    l = self.loans[idx]
                    if self.money < l["remaining"]:
                        self.log_event(f"Not enough to repay (need ${l['remaining']:,.0f})")
                        return
                    self.money -= l["remaining"]
                    self.market.money = self.money
                    self.log_event(f"Repaid loan: ${l['remaining']:,.0f}")
                    self.loans.pop(idx)
                    self.update_status()
                    w.destroy()
                    self.open_debt_window()

                tk.Button(row, text="Repay",
                          font=("Arial", 9), bg="#ff4444", fg="white",
                          relief="flat", padx=8, pady=3,
                          command=repay).pack(side="right")

        # ── New loans ─────────────────────────────────────────────────
        tk.Frame(inner, bg="#333", height=1).pack(fill="x", padx=24, pady=8)
        tk.Label(inner, text="New Loans", font=("Arial", 10, "bold"),
                 bg="#0e1117", fg="#aaaaaa").pack(pady=(0, 4))

        for opt in LOAN_OPTIONS:
            row = tk.Frame(inner, bg="#1e2130", pady=8, padx=12)
            row.pack(fill="x", padx=16, pady=4)

            info = tk.Frame(row, bg="#1e2130")
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=opt["label"],
                     font=("Arial", 11, "bold"), bg="#1e2130", fg="white",
                     anchor="w").pack(anchor="w")
            tk.Label(info,
                     text=f"Borrow ${opt['amount']:,}  |  {opt['rate']*100:.0f}% daily interest  |  {opt['days']}-day term",
                     font=("Arial", 8), bg="#1e2130", fg="#888888",
                     anchor="w").pack(anchor="w")

            def take(o=opt, w=win):
                if not hasattr(self, "loans"):
                    self.loans = []
                self.money += o["amount"]
                self.market.money = self.money
                self.loans.append({
                    "amount":    o["amount"],
                    "remaining": float(o["amount"]),
                    "rate":      o["rate"],
                    "days_left": o["days"],
                })
                self.update_status()
                self.log_event(f"Took loan: +${o['amount']:,} at {o['rate']*100:.0f}%/day for {o['days']} days")
                self._add_ticker("MARKETS: New corporate debt issuance detected...")
                w.destroy()
                self.open_debt_window()

            tk.Button(row, text="Borrow",
                      font=("Arial", 10, "bold"), bg="#ff6600", fg="white",
                      relief="flat", padx=14, pady=5,
                      command=take).pack(side="right")

    def process_loans(self):
        """Called daily — compound interest and check for defaults."""
        if not getattr(self, "loans", []):
            return
        new_loans = []
        for loan in self.loans:
            interest = loan["remaining"] * loan["rate"]
            loan["remaining"] += interest
            loan["days_left"] -= 1
            if loan["days_left"] <= 0:
                if self.money >= loan["remaining"]:
                    self.money -= loan["remaining"]
                    self.market.money = self.money
                    self.log_event(f"Loan auto-repaid: ${loan['remaining']:,.0f}")
                else:
                    penalty = self.money * 0.5
                    self.money -= penalty
                    self.market.money = self.money
                    self.log_event(f"LOAN DEFAULT! Lost ${penalty:,.0f} — 50% of remaining funds.")
                    self.add_transgression(15, 10)
                    self._add_ticker("BREAKING: Debt default — creditors seize assets!")
            else:
                new_loans.append(loan)
                if loan["days_left"] in (1, 5, 10):
                    self.log_event(f"Loan warning: ${loan['remaining']:,.0f} due in {loan['days_left']} day(s)")
        self.loans = new_loans
