import tkinter as tk

LOBBY_TIERS = [
    {"id": "bribe_official", "name": "Bribe Local Official",
     "desc": "Grease a few palms. Reduces transgressions by 8.",
     "cost": 4_000_000, "once": False,
     "effect": {"transgression": -8}},
    {"id": "control_narrative", "name": "Leak Positive Stories",
     "desc": "Plant flattering coverage in national media. +20 Public Opinion.",
     "cost": 12_000_000, "once": False,
     "effect": {"opinion": 20}},
    {"id": "buy_senator_trans", "name": "Buy a Senator  [Records]",
     "desc": "Have your criminal records quietly amended. -25 transgressions only.",
     "cost": 40_000_000, "once": False,
     "effect": {"transgression": -25}},
    {"id": "buy_senator_opin", "name": "Buy a Senator  [Image]",
     "desc": "Commission a full image rehabilitation campaign. +30 Public Opinion only.",
     "cost": 40_000_000, "once": False,
     "effect": {"opinion": 30}},
    {"id": "senate_immunity", "name": "Senate Immunity Deal",
     "desc": "Next bad random event is completely blocked. One use.",
     "cost": 60_000_000, "once": True,
     "effect": {"immunity": 1}},
    {"id": "full_expunge", "name": "Full Records Expunge",
     "desc": "Wipe your criminal record entirely. Transgressions reset to 0. No opinion benefit.",
     "cost": 150_000_000, "once": False,
     "effect": {"transgression": -999}},
    {"id": "presidential_rehab", "name": "Presidential Rehabilitation",
     "desc": "State-sponsored image rebuild. Public Opinion set to 80. No records benefit.",
     "cost": 150_000_000, "once": False,
     "effect": {"opinion": 999}},
]


class LobbyMixin:
    """Lobby window — spend money to influence politicians."""

    def open_lobby(self):
        win = tk.Toplevel(self.root)
        win.title("Lobby System")
        win.configure(bg="#0e1117")
        win.geometry("500x560")
        win.resizable(False, False)

        tk.Label(win, text="LOBBY SYSTEM",
                 font=("Impact", 24), bg="#0e1117", fg="#ffaa00").pack(pady=(18, 2))
        tk.Label(win, text="Influence politicians. Shape the narrative.",
                 font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 8))

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

        for tier in LOBBY_TIERS:
            self._build_lobby_row(inner, tier)

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

        def do_buy(t=tier, btn_ref=[None]):
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
                if eff["opinion"] == 999:
                    self.public_opinion = min(100, max(self.public_opinion, 80))
                else:
                    self.public_opinion = max(0, min(100, self.public_opinion + eff["opinion"]))
            if "immunity" in eff:
                self.lobby_immunity = True
                self.log_event("Senate Immunity active — next bad event is blocked.")
                if btn_ref[0]:
                    btn_ref[0].config(text="USED", state="disabled", bg="#333", fg="#555")
            self._update_bars()
            self.update_status()
            self.log_event(f"Lobby: {t['name']} — ${t['cost']:,} spent.")
            self._add_ticker("BREAKING: Political sources confirm lobbying activity...")

        state = "disabled" if already_used else "normal"
        btn = tk.Button(row, text="USED" if already_used else "Buy",
                        font=("Arial", 10, "bold"), bg="#333" if already_used else "#ffaa00",
                        fg="#555" if already_used else "black",
                        relief="flat", padx=14, pady=5,
                        state=state, command=do_buy)
        btn.pack(side="right")
        do_buy.__defaults__[1][0] = btn  # store ref so senate immunity can update it
