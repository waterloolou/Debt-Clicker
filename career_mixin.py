"""
career_mixin.py — Cross-run career stats and unlockable achievement badges.

Persisted locally in career.json. Complements the local/global leaderboards
with a permanent record of what you've pulled off across every run.
"""

import tkinter as tk
import json
import os

CAREER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "career.json")

BADGES = [
    {"id": "first_blood", "name": "First Blood",       "icon": "🩸",
     "desc": "Complete your first run."},
    {"id": "survivor_50", "name": "Half-Century",       "icon": "📅",
     "desc": "Survive 50 years in a single run."},
    {"id": "centurion",   "name": "Centurion",          "icon": "👑",
     "desc": "Reach the 100-year World Domination win."},
    {"id": "untouchable", "name": "Untouchable",        "icon": "🕊️",
     "desc": "Survive 20+ years while keeping transgressions at or below 10."},
    {"id": "kingpin",     "name": "Kingpin",            "icon": "☠️",
     "desc": "End a run with 90+ transgressions."},
    {"id": "market_maker","name": "Market Maker",       "icon": "📈",
     "desc": "Reach a net worth of $500,000,000 or more."},
    {"id": "warlord",     "name": "Warlord",            "icon": "⚔️",
     "desc": "Simultaneously control 5+ resource-rich countries."},
    {"id": "world_leader","name": "World Leader",       "icon": "🏛️",
     "desc": "Win a presidential election."},
]


def _load_career():
    try:
        with open(CAREER_FILE) as f:
            data = json.load(f)
    except Exception:
        data = {}
    data.setdefault("games_played", 0)
    data.setdefault("best_days", 0)
    data.setdefault("badges", [])
    return data


def _save_career(data):
    try:
        with open(CAREER_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


class CareerMixin:
    """Tracks lifetime stats and unlocks achievement badges across runs."""

    def _record_career_run(self):
        """Called once per completed run (from _show_end_screen) — updates
        career.json and returns a list of newly-unlocked badge dicts."""
        data = _load_career()
        data["games_played"] += 1
        data["best_days"] = max(data["best_days"], self.days)

        earned = set(data["badges"])
        newly = []

        peak_net_worth = max(getattr(self, "net_worth_history", [0]) or [0])
        checks = {
            "first_blood": True,
            "survivor_50": self.days >= 50,
            "centurion":   getattr(self, "won_game", False),
            "untouchable": self.days >= 20 and self.transgressions <= 10,
            "kingpin":     self.transgressions >= 90,
            "market_maker": peak_net_worth >= 500_000_000,
            "warlord":     len(getattr(self, "bombed_countries", set())) >= 5,
            "world_leader": getattr(self, "ever_president", False),
        }
        for badge in BADGES:
            if checks.get(badge["id"]) and badge["id"] not in earned:
                earned.add(badge["id"])
                newly.append(badge)

        data["badges"] = sorted(earned)
        _save_career(data)
        return newly

    def _show_badge_popup(self, badges):
        if not badges:
            return
        popup = tk.Toplevel(self.root)
        popup.title("Badge Unlocked")
        popup.configure(bg="#0e1117")
        popup.geometry("420x120" if len(badges) == 1 else "420x260")
        popup.resizable(False, False)
        popup.lift()
        popup.focus_force()

        tk.Frame(popup, bg="#ffd700", height=5).pack(fill="x")
        tk.Label(popup, text="🏅 NEW CAREER BADGE" + ("S" if len(badges) > 1 else ""),
                 font=("Impact", 16), bg="#0e1117", fg="#ffd700").pack(pady=(12, 6))
        for badge in badges:
            tk.Label(popup, text=f"{badge['icon']}  {badge['name']}  —  {badge['desc']}",
                     font=("Arial", 9), bg="#0e1117", fg="white",
                     wraplength=380, justify="left").pack(pady=2, padx=16, anchor="w")
        tk.Button(popup, text="Nice", font=("Arial", 10, "bold"),
                  bg="#ffd700", fg="black", relief="flat", padx=20, pady=5,
                  command=popup.destroy).pack(pady=(10, 12))
        popup.after(8000, lambda: popup.destroy() if popup.winfo_exists() else None)

    def open_career_window(self):
        data = _load_career()
        win = tk.Toplevel(self.root)
        win.title("Career")
        win.configure(bg="#0e1117")
        win.geometry("480x560")
        win.resizable(False, False)

        tk.Frame(win, bg="#ffd700", height=5).pack(fill="x")
        tk.Label(win, text="CAREER", font=("Impact", 26),
                 bg="#0e1117", fg="#ffd700").pack(pady=(16, 4))
        tk.Label(win,
                 text=f"Games played: {data['games_played']}   |   Best run: {data['best_days']} years",
                 font=("Arial", 10), bg="#0e1117", fg="#aaaaaa").pack(pady=(0, 10))

        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=(0, 8))

        earned = set(data["badges"])
        for badge in BADGES:
            got = badge["id"] in earned
            row = tk.Frame(win, bg="#1e2130" if got else "#131722", padx=14, pady=8)
            row.pack(fill="x", padx=20, pady=3)
            icon_color = "#ffd700" if got else "#333"
            tk.Label(row, text=badge["icon"], font=("Arial", 16),
                     bg=row["bg"], fg=icon_color).pack(side="left", padx=(0, 10))
            info = tk.Frame(row, bg=row["bg"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=badge["name"] if got else "???",
                     font=("Arial", 10, "bold"), bg=row["bg"],
                     fg="white" if got else "#555").pack(anchor="w")
            tk.Label(info, text=badge["desc"] if got else "Locked",
                     font=("Arial", 8), bg=row["bg"],
                     fg="#888" if got else "#444").pack(anchor="w")

        tk.Button(win, text="Back", font=("Arial", 10), bg="#1e2130", fg="white",
                  activebackground="#2e3140", relief="flat", padx=20, pady=6,
                  command=win.destroy).pack(pady=14)
        tk.Frame(win, bg="#ffd700", height=5).pack(fill="x", side="bottom")
