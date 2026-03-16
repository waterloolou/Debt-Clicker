import tkinter as tk


ASSETS = [
    {
        "id":      "supercar",
        "icon":    "🏎️",
        "name":    "Supercar Collection",
        "desc":    "12 Lamborghinis you'll never actually drive.",
        "cost":    500_000,
        "upkeep":  5_000,
        "income":  0,
        "special": None,
    },
    {
        "id":      "penthouse",
        "icon":    "🏙️",
        "name":    "Luxury Penthouse",
        "desc":    "Top floor. Golden toilets. Neighbours hate you.",
        "cost":    2_000_000,
        "upkeep":  20_000,
        "income":  0,
        "special": None,
    },
    {
        "id":      "jet",
        "icon":    "✈️",
        "name":    "Private Jet",
        "desc":    "Carbon footprint of a small country. Worth it.",
        "cost":    8_000_000,
        "upkeep":  80_000,
        "income":  0,
        "special": None,
    },
    {
        "id":      "offshore",
        "icon":    "🏦",
        "name":    "Offshore Bank Account",
        "desc":    "The Cayman Islands say hi. Tax fraud events cost 50% less.",
        "cost":    10_000_000,
        "upkeep":  100_000,
        "income":  0,
        "special": "tax_shield",
    },
    {
        "id":      "yacht",
        "icon":    "🛥️",
        "name":    "Mega Yacht",
        "desc":    "Comes with a helipad and a smaller yacht.",
        "cost":    15_000_000,
        "upkeep":  150_000,
        "income":  0,
        "special": None,
    },
    {
        "id":      "senator",
        "icon":    "🤝",
        "name":    "Bribed Senator",
        "desc":    "On retainer. Lawsuits and fines cost 40% less.",
        "cost":    20_000_000,
        "upkeep":  500_000,
        "income":  0,
        "special": "legal_shield",
    },
    {
        "id":      "island",
        "icon":    "🏝️",
        "name":    "Private Island",
        "desc":    "Browse 18 real private islands worldwide. Each earns daily income.",
        "cost":    0,
        "upkeep":  0,
        "income":  0,
        "special": "island_map",
    },
    {
        "id":      "media",
        "icon":    "📺",
        "name":    "Media Empire",
        "desc":    "6 channels, all say what you pay. +$1.5M/day.",
        "cost":    40_000_000,
        "upkeep":  800_000,
        "income":  1_500_000,
        "special": "media_boost",
    },
    {
        "id":      "oil_rig",
        "icon":    "🛢️",
        "name":    "Offshore Oil Rig",
        "desc":    "Definitely up to code. Generates $2M/day.",
        "cost":    50_000_000,
        "upkeep":  1_000_000,
        "income":  2_000_000,
        "special": "energy_boost",
    },
    {
        "id":      "army",
        "icon":    "💂",
        "name":    "Private Army",
        "desc":    "2,000 mercenaries on speed dial. Defense stocks up.",
        "cost":    80_000_000,
        "upkeep":  2_000_000,
        "income":  0,
        "special": "defense_boost",
    },
    {
        "id":      "bunker",
        "icon":    "🏚️",
        "name":    "Doomsday Bunker",
        "desc":    "12 years of canned food. Pandemic events skip you.",
        "cost":    100_000_000,
        "upkeep":  1_000_000,
        "income":  0,
        "special": "pandemic_immune",
    },
    {
        "id":      "space",
        "icon":    "🚀",
        "name":    "Vanity Space Program",
        "desc":    "Your name on a rocket. +$3M/day from contracts.",
        "cost":    200_000_000,
        "upkeep":  5_000_000,
        "income":  3_000_000,
        "special": "space_boost",
    },
]

# Quick lookup by id
ASSET_BY_ID = {a["id"]: a for a in ASSETS}


class AssetsMixin:
    """Purchasable luxury/corrupt assets with daily upkeep, passive income, and event effects."""

    # =========================================================
    # ASSETS WINDOW
    # =========================================================

    def open_assets(self):
        win = tk.Toplevel(self.root)
        win.title("Assets")
        win.configure(bg="#0e1117")
        win.geometry("560x620")
        win.resizable(False, False)

        tk.Label(win, text="💰  ASSETS",
                 font=("Impact", 26), bg="#0e1117", fg="#ffdd44").pack(pady=(20, 4))
        tk.Label(win, text="Buy luxury items. Each costs upkeep every day.",
                 font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))

        # Scrollable list
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
        def _on_scroll(e):
            try:
                canvas.yview_scroll(-1*(e.delta//120), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _on_scroll)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        self._asset_buy_btns = {}

        for asset in ASSETS:
            self._build_asset_row(inner, asset, win)

    def _build_asset_row(self, parent, asset, win):
        owned = asset["id"] in self.owned_assets

        row = tk.Frame(parent, bg="#1e2130", pady=8, padx=12)
        row.pack(fill="x", pady=4)

        # Icon + name
        left = tk.Frame(row, bg="#1e2130")
        left.pack(side="left", fill="y")

        tk.Label(left, text=asset["icon"], font=("Arial", 28),
                 bg="#1e2130").pack(anchor="w")

        # Info
        info = tk.Frame(row, bg="#1e2130")
        info.pack(side="left", fill="both", expand=True, padx=10)

        name_color = "#00ff90" if owned else "white"
        tk.Label(info, text=asset["name"], font=("Arial", 11, "bold"),
                 bg="#1e2130", fg=name_color, anchor="w").pack(anchor="w")
        tk.Label(info, text=asset["desc"], font=("Arial", 8),
                 bg="#1e2130", fg="#888888", anchor="w", wraplength=280,
                 justify="left").pack(anchor="w")

        if asset["special"] != "island_map":
            stat_line = f"Cost: ${asset['cost']:,}   Upkeep: ${asset['upkeep']:,}/day"
            if asset["income"]:
                stat_line += f"   Income: +${asset['income']:,}/day"
            tk.Label(info, text=stat_line, font=("Arial", 7),
                     bg="#1e2130", fg="#555577", anchor="w").pack(anchor="w", pady=(2, 0))

        # Island entry gets a permanent Browse button
        right = tk.Frame(row, bg="#1e2130")
        right.pack(side="right")

        if asset["special"] == "island_map":
            n = len(self.owned_islands)
            lbl = f"Browse  ({n} owned)" if n else "Browse"
            tk.Button(right, text=lbl,
                      font=("Arial", 10, "bold"), bg="#ff9900", fg="white",
                      relief="flat", padx=14, pady=5,
                      command=lambda w=win: [w.destroy(), self.open_island_map()]
                      ).pack()
        elif owned:
            tk.Label(right, text="OWNED", font=("Arial", 9, "bold"),
                     bg="#1e2130", fg="#00ff90").pack()
        else:
            btn = tk.Button(right, text="Buy",
                            font=("Arial", 10, "bold"), bg="#ff2222", fg="white",
                            relief="flat", padx=14, pady=5,
                            command=lambda a=asset, w=win: self._buy_asset(a, w))
            btn.pack()
            self._asset_buy_btns[asset["id"]] = btn

    def _buy_asset(self, asset, win):
        if asset["id"] in self.owned_assets:
            return
        if self.money < asset["cost"]:
            self.log_event(f"Can't afford {asset['name']} (need ${asset['cost']:,})")
            return

        self.money -= asset["cost"]
        self.market.money = self.money
        self.owned_assets.add(asset["id"])
        self.add_happiness(max(3, min(20, asset["cost"] // 5_000_000)))
        self.update_status()
        self.log_event(f"Purchased {asset['icon']} {asset['name']} for ${asset['cost']:,}")

        # Apply immediate one-off market boosts for productive assets
        if asset["special"] == "energy_boost":
            self.apply_market_effect(["Energy"], 1.04, 3, f"{asset['name']} online")
        elif asset["special"] == "media_boost":
            self.apply_market_effect(["Entertainment"], 1.03, 3, f"{asset['name']} launch")
        elif asset["special"] == "defense_boost":
            self.apply_market_effect(["Defense"], 1.05, 3, f"{asset['name']} deployed")
        elif asset["special"] == "space_boost":
            self.apply_market_effect(["Space"], 1.06, 3, f"{asset['name']} announced")

        # Refresh window to show OWNED state
        win.destroy()
        self.open_assets()

    # =========================================================
    # DAILY ASSET TICK  (called from game.py lose_money)
    # =========================================================

    def apply_asset_costs(self):
        """Subtract daily upkeep and add daily income for all owned assets."""
        net = 0
        for aid in self.owned_assets:
            a = ASSET_BY_ID.get(aid)
            if a:
                net += a["income"] - a["upkeep"]
        if net != 0:
            self.money += net
            self.market.money = self.money
            if net > 0:
                self.log_event(f"Assets net: +${net:,}/day")
            else:
                self.log_event(f"Assets upkeep: -${abs(net):,}/day")
