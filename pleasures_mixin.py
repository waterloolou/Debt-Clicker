"""pleasures_mixin.py
Indulgences — repeatable activities that boost happiness with possible consequences.
"""

import tkinter as tk
import random

# Each entry:
#   icon, name, cost, happiness, desc,
#   risk: None = safe | dict with chance, title, text, money_loss, opinion, transgression
PLEASURES = [
    {
        "icon":      "🚬",
        "name":      "Smoking",
        "cost":      150_000,
        "happiness": 12,
        "desc":      "Hand-rolled Cuban. Your doctor has been trying to reach you.",
        "risk": {
            "chance":       0.35,
            "title":        "Your Lungs Filed a Complaint",
            "text":         "The x-ray technician went pale. Your doctor used the word "
                            "'catastrophic' then immediately asked for a raise. You paid "
                            "$12,000,000 to have the results classified. The cigars remain "
                            "on the desk.",
            "money":        -12_000_000,
            "opinion":      -5,
            "transgression": 0,
            "market":       ("Healthcare", 1.04, 2),
        },
    },
    {
        "icon":      "🥃",
        "name":      "Drinking",
        "cost":      250_000,
        "happiness": 18,
        "desc":      "18-year Scotch. You ordered three. It's 11am. It's fine.",
        "risk": {
            "chance":       0.40,
            "title":        "You Called the PM 'Champ'",
            "text":         "You gave an unscheduled speech at a state gala, called the "
                            "prime minister 'big guy', and challenged the French ambassador "
                            "to arm wrestle. PR spent $8,000,000 convincing the press "
                            "it was performance art.",
            "money":        -8_000_000,
            "opinion":      -8,
            "transgression": 4,
            "market":       ("Entertainment", 0.95, 2),
        },
    },
    {
        "icon":      "🚢",
        "name":      "Luxury Cruise",
        "cost":      3_000_000,
        "happiness": 30,
        "desc":      "14 days. 6 ports. Not a single email answered. Perfect.",
        "risk":      None,
    },
    {
        "icon":      "🦁",
        "name":      "Trophy Hunting",
        "cost":      6_000_000,
        "happiness": 35,
        "desc":      "Private reserve. Fully licensed. The lion did not get a vote.",
        "risk": {
            "chance":       0.55,
            "title":        "PETA Found the Photos",
            "text":         "Someone posted the victory photo. You're posing with a lion "
                            "and giving a thumbs up. PETA set up camp outside your building. "
                            "You paid $5,000,000 to relocate them. They went two doors down.",
            "money":        -5_000_000,
            "opinion":      -20,
            "transgression": 8,
            "market":       ("Entertainment", 0.93, 3),
        },
    },
    {
        "icon":      "🐆",
        "name":      "Exotic Pet",
        "cost":      5_000_000,
        "happiness": 28,
        "desc":      "A clouded leopard named Gerald. The staff were not consulted.",
        "risk": {
            "chance":       0.30,
            "title":        "Gerald Got Out",
            "text":         "Gerald escaped through the east wing. Three bodyguards quit "
                            "immediately. One fainted. Animal control charged $20,000,000 "
                            "for what they called 'emotional damages'. Gerald was found "
                            "napping on the helicopter.",
            "money":        -20_000_000,
            "opinion":      -10,
            "transgression": 5,
            "market":       None,
        },
    },
    {
        "icon":      "🎰",
        "name":      "Gambling Binge",
        "cost":      5_000_000,
        "happiness": 25,
        "desc":      "Private table in Monaco. You have a system. You don't.",
        "risk": {
            "chance":       0.60,
            "title":        "The System Did Not Work",
            "text":         "You were up $2M and then you weren't. You stayed for 'one more "
                            "hand' fourteen times. The dealer looked sorry for you. "
                            "You lost an extra $18,000,000. The system needs refinement.",
            "money":        -18_000_000,
            "opinion":      0,
            "transgression": 0,
            "market":       ("Finance", 0.96, 1),
        },
    },
    {
        "icon":      "🪂",
        "name":      "Skydiving",
        "cost":      500_000,
        "happiness": 20,
        "desc":      "13,000 feet. Certified instructor. He seemed confident enough.",
        "risk": {
            "chance":       0.20,
            "title":        "The Parachute Had Notes",
            "text":         "The chute opened late. Not catastrophically late — just "
                            "enough to introduce you to the ground faster than planned. "
                            "Three weeks in a private clinic, $15,000,000 in bills, and "
                            "a completely new perspective on gravity.",
            "money":        -15_000_000,
            "opinion":      0,
            "transgression": 0,
            "market":       ("Healthcare", 1.03, 1),
        },
    },
    {
        "icon":      "🍽️",
        "name":      "Fine Dining",
        "cost":      800_000,
        "happiness": 15,
        "desc":      "Three Michelin stars. The portion was the size of a cufflink. Exquisite.",
        "risk":      None,
    },
    {
        "icon":      "🎵",
        "name":      "Private Concert",
        "cost":      2_000_000,
        "happiness": 22,
        "desc":      "You hired a stadium band to play in your living room. They had thoughts.",
        "risk":      None,
    },
    {
        "icon":      "💉",
        "name":      "Cosmetic Surgery",
        "cost":      3_000_000,
        "happiness": 20,
        "desc":      "Minor adjustments. Nobody will notice. That's the plan anyway.",
        "risk": {
            "chance":       0.30,
            "title":        "The Surgeon Had a Sneezing Fit",
            "text":         "You went in for minor work. You came out looking like a "
                            "slightly different person — not worse, just not you. "
                            "Corrective surgery cost $10,000,000. The tabloids called "
                            "it a 'bold reinvention'. You did not.",
            "money":        -10_000_000,
            "opinion":      -12,
            "transgression": 0,
            "market":       ("Healthcare", 1.02, 1),
        },
    },
]


class PleasuresMixin:

    def open_pleasures(self):
        win = tk.Toplevel(self.root)
        win.title("Pleasures")
        win.configure(bg="#0e1117")
        win.geometry("580x640")
        win.resizable(False, True)

        tk.Label(win, text="INDULGENCES",
                 font=("Impact", 26), bg="#0e1117", fg="#ff6600").pack(pady=(20, 2))
        tk.Label(win, text="You've earned it. Probably.",
                 font=("Arial", 9), bg="#0e1117", fg="#555").pack(pady=(0, 10))

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

        def _wheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _wheel)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        for pleasure in PLEASURES:
            self._build_pleasure_row(inner, pleasure)

    def _build_pleasure_row(self, parent, p):
        row = tk.Frame(parent, bg="#1e2130", pady=10, padx=14)
        row.pack(fill="x", pady=4)

        # Icon
        tk.Label(row, text=p["icon"], font=("Arial", 28),
                 bg="#1e2130").pack(side="left", padx=(0, 12))

        # Info
        info = tk.Frame(row, bg="#1e2130")
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=p["name"], font=("Arial", 11, "bold"),
                 bg="#1e2130", fg="white", anchor="w").pack(anchor="w")
        tk.Label(info, text=p["desc"], font=("Arial", 8),
                 bg="#1e2130", fg="#888888", anchor="w").pack(anchor="w")

        detail = f"  +{p['happiness']} happiness  |  ${p['cost']:,}"
        tk.Label(info, text=detail, font=("Arial", 8),
                 bg="#1e2130", fg="#666666", anchor="w").pack(anchor="w")

        # Button
        can_afford = self.money >= p["cost"]
        btn = tk.Button(row, text="Indulge",
                        font=("Arial", 10, "bold"),
                        bg="#ff6600" if can_afford else "#2a2a2a",
                        fg="white" if can_afford else "#555",
                        relief="flat", padx=14, pady=6,
                        state="normal" if can_afford else "disabled",
                        command=lambda pl=p: self._indulge(pl))
        btn.pack(side="right")

    def _indulge(self, p):
        if self.money < p["cost"]:
            self.log_event(f"Can't afford {p['name']} (${p['cost']:,})")
            return

        self.money -= p["cost"]
        self.market.money = self.money
        self.happiness = min(100, self.happiness + p["happiness"])
        self.update_status()
        self.log_event(f"{p['icon']} Indulged in {p['name']}. +{p['happiness']} happiness. Cost: ${p['cost']:,}")

        risk = p["risk"]
        if risk and random.random() < risk["chance"]:
            # Bad outcome
            self.money += risk["money"]   # money is negative
            self.market.money = self.money
            if risk["opinion"]:
                self.public_opinion = max(0, min(100, self.public_opinion - risk["opinion"]))
            if risk["transgression"]:
                self.add_transgression(risk["transgression"], 0)
            if risk["market"]:
                cat, mult, days = risk["market"]
                self.apply_market_effect([cat], mult, days, risk["title"])
            self.happiness = max(0, self.happiness - p["happiness"] // 2)
            self.update_status()
            self.log_event(f"⚠ {risk['title']}: {risk['money']:,} financial hit.")
            self._show_pleasure_result(p["icon"], risk["title"], risk["text"], bad=True)
        else:
            # Clean outcome
            msg = self._pleasure_success_text(p["name"])
            self._show_pleasure_result(p["icon"], f"Enjoyed: {p['name']}", msg, bad=False)

    def _pleasure_success_text(self, name):
        msgs = {
            "Smoking":          "Exceptional cigar. Your lungs filed a formal objection. You ignored it.",
            "Drinking":         "Four bottles in, you solved geopolitics on a cocktail napkin. The napkin is gone. The problems remain.",
            "Luxury Cruise":    "Fourteen days of nothing. You returned tanned, rested, and briefly a decent person.",
            "Trophy Hunting":   "Successful hunt. The photo exists in exactly one location. For now.",
            "Exotic Pet":       "Gerald is settling in. Your head of security put in his two weeks. Worth it.",
            "Gambling Binge":   "You walked away up $5M and with a handshake from a man who definitely works for someone.",
            "Skydiving":        "Freefall from 13,000 feet. Instructor said you screamed the whole way. You disagree.",
            "Fine Dining":      "Seven courses. Each portion aggressive in its smallness. Somehow still the best meal of your life.",
            "Private Concert":  "The band played for three hours to an audience of one. They looked confused. You looked happy.",
            "Cosmetic Surgery": "Recovery was smooth. You look imperceptibly better. Your staff are saying nothing, which is suspicious.",
        }
        return msgs.get(name, "A thoroughly enjoyable indulgence. No further comment.")

    def _show_pleasure_result(self, icon, title, text, bad):
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg="#0e1117")
        popup.geometry("440x220")
        popup.grab_set()
        popup.resizable(False, False)

        hdr_clr = "#ff4444" if bad else "#00ff90"
        tk.Label(popup, text=f"{icon}  {title}",
                 font=("Arial", 13, "bold"), bg="#0e1117", fg=hdr_clr).pack(pady=(18, 6))
        tk.Label(popup, text=text, font=("Arial", 10),
                 bg="#0e1117", fg="white", wraplength=400,
                 justify="center").pack(pady=6, padx=20)
        tk.Button(popup, text="OK", bg="#1e2130", fg="#00ff90",
                  relief="flat", font=("Arial", 10), padx=24, pady=4,
                  command=popup.destroy).pack(pady=12)
