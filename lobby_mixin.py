import tkinter as tk

LOBBY_TIERS = [
    {"id": "bribe_official", "name": "Bribe Local Official",
     "desc": "Grease a few palms. Reduces transgressions by 10.",
     "cost": 500_000, "once": False,
     "effect": {"transgression": -10}},
    {"id": "control_narrative", "name": "Control the Narrative",
     "desc": "Plant stories in local media. +20 Public Opinion.",
     "cost": 5_000_000, "once": False,
     "effect": {"opinion": 20}},
    {"id": "buy_congressman", "name": "Buy a Congressman",
     "desc": "Capitol Hill speed dial. -20 transgressions, +15 Public Opinion.",
     "cost": 15_000_000, "once": False,
     "effect": {"transgression": -20, "opinion": 15}},
    {"id": "senate_immunity", "name": "Senate Immunity Deal",
     "desc": "Next bad random event is completely blocked. One use.",
     "cost": 40_000_000, "once": True,
     "effect": {"immunity": 1}},
    {"id": "presidential_pardon", "name": "Presidential Pardon",
     "desc": "Clean slate. Reset transgressions to 0, +30 Public Opinion.",
     "cost": 100_000_000, "once": False,
     "effect": {"transgression": -999, "opinion": 30}},
]


class LobbyMixin:
    """Lobby window — spend money to influence politicians."""

    def open_lobby(self):
        win = tk.Toplevel(self.root)
        win.title("Lobby System")
        win.configure(bg="#0e1117")
        win.geometry("500x480")
        win.resizable(False, False)

        tk.Label(win, text="LOBBY SYSTEM",
                 font=("Impact", 24), bg="#0e1117", fg="#ffaa00").pack(pady=(18, 2))
        tk.Label(win, text="Influence politicians. Shape the narrative.",
                 font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))

        for tier in LOBBY_TIERS:
            self._build_lobby_row(win, tier)

    def _build_lobby_row(self, win, tier):
        already_used = (tier["once"] and tier["id"] == "senate_immunity"
                        and getattr(self, "lobby_immunity", False))

        row = tk.Frame(win, bg="#1e2130", pady=8, padx=12)
        row.pack(fill="x", padx=16, pady=4)

        info = tk.Frame(row, bg="#1e2130")
        info.pack(side="left", fill="both", expand=True)

        name_fg = "#555" if already_used else "white"
        tk.Label(info, text=tier["name"], font=("Arial", 11, "bold"),
                 bg="#1e2130", fg=name_fg, anchor="w").pack(anchor="w")
        tk.Label(info, text=tier["desc"], font=("Arial", 8),
                 bg="#1e2130", fg="#888888", anchor="w",
                 wraplength=300, justify="left").pack(anchor="w")
        tk.Label(info, text=f"Cost: ${tier['cost']:,}", font=("Arial", 8),
                 bg="#1e2130", fg="#555577", anchor="w").pack(anchor="w", pady=(2, 0))

        def do_buy(t=tier, w=win):
            if t["once"] and t["id"] == "senate_immunity" and getattr(self, "lobby_immunity", False):
                return
            if self.money < t["cost"]:
                self.log_event(f"Can't afford {t['name']} (${t['cost']:,})")
                return
            self.money -= t["cost"]
            self.market.money = self.money
            eff = t["effect"]
            if "transgression" in eff:
                self.transgressions = max(0, min(100, self.transgressions + eff["transgression"]))
            if "opinion" in eff:
                self.public_opinion = max(0, min(100, self.public_opinion + eff["opinion"]))
            if "immunity" in eff:
                self.lobby_immunity = True
                self.log_event("Senate Immunity active — next bad event is blocked.")
            self._update_bars()
            self.update_status()
            self.log_event(f"Lobby: {t['name']} — ${t['cost']:,} spent.")
            self._add_ticker("BREAKING: Political sources confirm lobbying activity...")
            w.destroy()
            self.open_lobby()

        state = "disabled" if already_used else "normal"
        tk.Button(row, text="USED" if already_used else "Buy",
                  font=("Arial", 10, "bold"), bg="#333" if already_used else "#ffaa00",
                  fg="#555" if already_used else "black",
                  relief="flat", padx=14, pady=5,
                  state=state, command=do_buy).pack(side="right")
