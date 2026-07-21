"""
cabinet_mixin.py — Presidential Cabinet of Advisors.

Advisors react to the executive orders and Groq power actions you sign while
in office. Keep them happy for passive perks; neglect or abuse your power and
they resign publicly, costing you opinion and dragging up your transgressions.
"""

import tkinter as tk
import random

ADVISOR_ROLES = [
    {"role": "Chief of Staff",     "names": ["Marcus Webb", "Diane Foster", "Trevor Kaine"],
     "color": "#4499ff",
     "desc": "Runs day-to-day operations. Hates emergency powers. Rewards a happy nation."},
    {"role": "Press Secretary",    "names": ["Nina Alvarez", "Colin Reyes", "Priya Sharma"],
     "color": "#ffaa00",
     "desc": "Manages your image. Loves propaganda in moderation. Hates censorship."},
    {"role": "Attorney General",   "names": ["Harold Voss", "Miriam Cole", "Desmond Okoye"],
     "color": "#cc44ff",
     "desc": "Oversees legal affairs. Loves pardons and amnesty. Hates cronyism."},
    {"role": "Treasury Secretary", "names": ["Elaine Brooks", "Raj Patel", "Wendell Ashford"],
     "color": "#00ff90",
     "desc": "Manages the budget. Loves tax cuts and infrastructure. Hates reckless spending."},
]

# Reaction deltas: {order/action key: {role: delta}}
_REACTIONS = {
    "daily_expense_multiplier":      {"Treasury Secretary": 8, "Chief of Staff": 3},
    "income_multiplier":             {"Treasury Secretary": 5},
    "transgression_decay_bonus":     {"Attorney General": 10, "Press Secretary": -5},
    "public_opinion_daily":          {"Press Secretary": 8},
    "loan_rate_multiplier":          {"Treasury Secretary": 6},
    "happiness_daily":               {"Chief of Staff": 5},
    "wanted_fine_reduction":         {"Attorney General": -8, "Press Secretary": -4},
    "declare_state_of_emergency":    {"Chief of Staff": -15, "Attorney General": -12},
    "censor_media":                  {"Press Secretary": -10, "Attorney General": -6},
    "launch_propaganda_campaign":    {"Press Secretary": 6},
    "appoint_loyalist_official":     {"Chief of Staff": 5, "Attorney General": -8},
    "impose_sanctions":              {"Treasury Secretary": -5},
    "pass_infrastructure_legislation": {"Treasury Secretary": 8, "Chief of Staff": 4},
    "pass_corporate_tax_cut":        {"Treasury Secretary": 10, "Press Secretary": -5},
}


class CabinetMixin:
    """Presidential cabinet — advisors who react to your use of power."""

    # =========================================================
    # LIFECYCLE
    # =========================================================

    def _form_cabinet(self):
        """Appoint a fresh cabinet at the start of a presidential term."""
        self.cabinet = {}
        for spec in ADVISOR_ROLES:
            self.cabinet[spec["role"]] = {
                "name":     random.choice(spec["names"]),
                "approval": 55,
                "color":    spec["color"],
                "vacant":   False,
                "vacant_days": 0,
            }

    def cabinet_react(self, action_key):
        """Adjust advisor approval in response to a signed order or Groq action."""
        if not getattr(self, "cabinet", None):
            return
        deltas = _REACTIONS.get(action_key)
        if not deltas:
            return
        for role, delta in deltas.items():
            seat = self.cabinet.get(role)
            if not seat or seat.get("vacant"):
                continue
            seat["approval"] = max(0, min(100, seat["approval"] + delta))

    # =========================================================
    # DAILY TICK  (called from main_loop, president mode only)
    # =========================================================

    def process_cabinet(self):
        if not getattr(self, "is_president", False) or not getattr(self, "cabinet", None):
            return
        for role, seat in list(self.cabinet.items()):
            if seat.get("vacant"):
                seat["vacant_days"] = seat.get("vacant_days", 0) + 1
                if seat["vacant_days"] >= 5:
                    spec = next(s for s in ADVISOR_ROLES if s["role"] == role)
                    self.cabinet[role] = {
                        "name": random.choice(spec["names"]), "approval": 50,
                        "color": spec["color"], "vacant": False, "vacant_days": 0,
                    }
                    self.log_event(f"CABINET: {self.cabinet[role]['name']} sworn in as {role}.")
                    self._add_ticker(f"POLITICS: New {role} confirmed by the Senate...")
                continue

            # Regress slowly toward neutral (50)
            if seat["approval"] > 50:
                seat["approval"] -= 1
            elif seat["approval"] < 50:
                seat["approval"] += 1

            # Resignation risk when deeply unhappy
            if seat["approval"] <= 15 and random.random() < 0.25:
                self._advisor_resigns(role, seat)
                continue

            # Passive perks for a loyal, high-approval advisor
            if seat["approval"] >= 85:
                self._apply_advisor_perk(role)

    def _apply_advisor_perk(self, role):
        if role == "Treasury Secretary":
            self.money += 500_000
            self.market.money = self.money
        elif role == "Chief of Staff":
            self.happiness = min(100, self.happiness + 1)
        elif role == "Attorney General":
            self.transgressions = max(0, self.transgressions - 1)
        elif role == "Press Secretary":
            self.public_opinion = min(100, self.public_opinion + 1)
        self._update_bars()

    def _advisor_resigns(self, role, seat):
        name = seat["name"]
        self.cabinet[role] = {"name": None, "approval": 0, "color": seat["color"],
                               "vacant": True, "vacant_days": 0}
        self.public_opinion = max(0, self.public_opinion - 8)
        self.add_transgression(5, 0)
        self.log_event(
            f"CABINET: {name} resigns as {role} — cites 'irreconcilable differences'. "
            f"Public Opinion -8.")
        self._add_ticker(f"BREAKING: {role} {name} resigns in protest...")
        self.add_message(
            f"🏛️ {role} Resigns",
            f"{name} has resigned as {role}, publicly citing your abuse of executive power.\n\n"
            f"Public Opinion -8\nTransgressions +5\n\n"
            f"The seat will remain vacant for several days before a replacement is confirmed.",
            category="election",
        )
        self.update_status()

    # =========================================================
    # WINDOW
    # =========================================================

    def open_cabinet_window(self):
        if getattr(self, "game_mode", "president") == "billionaire":
            self.log_event("Billionaires don't have a cabinet — they have lawyers.")
            return
        if not getattr(self, "is_president", False):
            self.log_event("You must be President to have a Cabinet. Win an election first.")
            return

        win = tk.Toplevel(self.root)
        win.title("Presidential Cabinet")
        win.configure(bg="#0e1117")
        win.geometry("520x560")
        win.resizable(False, False)

        tk.Frame(win, bg="#4499ff", height=5).pack(fill="x")
        tk.Label(win, text="PRESIDENTIAL CABINET",
                 font=("Impact", 22), bg="#0e1117", fg="#4499ff").pack(pady=(16, 2))
        tk.Label(win, text="Advisors react to your executive orders and Groq power actions.",
                 font=("Arial", 9), bg="#0e1117", fg="#666",
                 wraplength=460, justify="center").pack(pady=(0, 10))

        if not getattr(self, "cabinet", None):
            self._form_cabinet()

        for spec in ADVISOR_ROLES:
            role = spec["role"]
            seat = self.cabinet.get(role, {})
            color = spec["color"]

            card = tk.Frame(win, bg="#1e2130", padx=14, pady=10)
            card.pack(fill="x", padx=20, pady=5)

            hdr = tk.Frame(card, bg="#1e2130")
            hdr.pack(fill="x")
            if seat.get("vacant"):
                tk.Label(hdr, text=f"{role}  —  VACANT",
                         font=("Arial", 11, "bold"), bg="#1e2130", fg="#666").pack(side="left")
                tk.Label(card, text=f"Confirmation hearing in progress "
                                     f"({5 - seat.get('vacant_days', 0)} days)...",
                         font=("Arial", 8, "italic"), bg="#1e2130", fg="#555").pack(anchor="w", pady=(4, 0))
                continue

            tk.Label(hdr, text=f"{role}: {seat.get('name', '—')}",
                     font=("Arial", 11, "bold"), bg="#1e2130", fg=color).pack(side="left")
            approval = seat.get("approval", 50)
            app_color = "#00ff90" if approval >= 70 else ("#ffaa00" if approval >= 35 else "#ff4444")
            tk.Label(hdr, text=f"{approval}% approval",
                     font=("Arial", 9, "bold"), bg="#1e2130", fg=app_color).pack(side="right")

            track = tk.Frame(card, bg="#0a0d13", height=10)
            track.pack(fill="x", pady=(6, 4))
            fill = tk.Frame(track, bg=app_color, height=10)
            fill.place(relx=0, rely=0, relheight=1, relwidth=max(0.001, approval / 100))

            tk.Label(card, text=spec["desc"], font=("Arial", 8),
                     bg="#1e2130", fg="#888", wraplength=460, justify="left").pack(anchor="w")

            if approval >= 85:
                tk.Label(card, text="✓ Loyal — granting daily passive bonus",
                         font=("Arial", 8, "bold"), bg="#1e2130", fg="#00ff90").pack(anchor="w", pady=(4, 0))
            elif approval <= 15:
                tk.Label(card, text="⚠ At risk of resigning",
                         font=("Arial", 8, "bold"), bg="#1e2130", fg="#ff4444").pack(anchor="w", pady=(4, 0))

        tk.Frame(win, bg="#4499ff", height=5).pack(fill="x", side="bottom")
