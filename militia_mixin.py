"""
militia_mixin.py — Multiplayer War Room
Buy militia units, then unleash them on rival players.
"""

import tkinter as tk
import random

MILITIA_TIERS = [
    {"name": "Mercenary Squad",    "units": 15,  "cost":  30_000_000,
     "icon": "🔫",
     "desc": "A ragtag group of hired guns. Gets the job done."},
    {"name": "Private Army",       "units": 40,  "cost":  80_000_000,
     "icon": "⚔️",
     "desc": "Disciplined forces with real firepower."},
    {"name": "Military Contractor","units": 80,  "cost": 160_000_000,
     "icon": "🪖",
     "desc": "Ex-special forces. Black budget operations."},
    {"name": "Elite Strike Force", "units": 120, "cost": 280_000_000,
     "icon": "☢️",
     "desc": "State-level capabilities. Unlocks nuclear option."},
]

WAR_ACTIONS = [
    {"id": "spy",        "name": "🕵️  Spy Report",       "units": 5,
     "desc": "Reveal the target's full stats (money, ops, health)."},
    {"id": "raid",       "name": "💰  Raid Treasury",      "units": 15,
     "desc": "Steal 8–15 % of their cash reserves."},
    {"id": "assassinate","name": "🗡️  Hit Advisor",       "units": 12,
     "desc": "Force 2 bad events per day on them for 3 days."},
    {"id": "sabotage",   "name": "💥  Sabotage Ops",       "units": 20,
     "desc": "Wipe out one of their active resource operations."},
    {"id": "blockade",   "name": "⛵  Trade Blockade",     "units": 25,
     "desc": "Cut off all their resource income for 4 days."},
    {"id": "nuke",       "name": "☢️  Nuclear Strike",     "units": 100,
     "desc": "Obliterate 40 % of their fortune. Costs all elite units."},
]


class MilitiaMixin:
    """War Room — buy and deploy militia against rivals in multiplayer."""

    # =========================================================
    # OPEN WAR ROOM
    # =========================================================

    def open_war_room(self):
        if not getattr(self, "is_multiplayer", False):
            self.log_event("War Room is only available in multiplayer.")
            return

        win = tk.Toplevel(self.root)
        win.title("War Room")
        win.configure(bg="#0e1117")
        win.geometry("520x640")
        win.resizable(False, False)
        self._war_win = win

        # ── Header ──────────────────────────────────────────────────────
        tk.Frame(win, bg="#880000", height=5).pack(fill="x")
        tk.Label(win, text="⚔️  WAR ROOM",
                 font=("Impact", 26), bg="#0e1117", fg="#ff2222").pack(pady=(12, 0))

        self._militia_lbl = tk.Label(
            win, text=self._militia_status_text(),
            font=("Arial", 11, "bold"), bg="#0e1117", fg="#ffaa00")
        self._militia_lbl.pack(pady=(2, 8))

        # ── Scrollable body ──────────────────────────────────────────────
        container = tk.Frame(win, bg="#0e1117")
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg="#0e1117", highlightthickness=0)
        sb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#0e1117")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _wheel(ev):
            try:
                canvas.yview_scroll(int(-1 * (ev.delta / 120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _wheel)
        win.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # ── Buy militia ──────────────────────────────────────────────────
        tk.Label(inner, text="RECRUIT MILITIA",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg="#888").pack(
                     anchor="w", padx=16, pady=(8, 4))

        for tier in MILITIA_TIERS:
            self._build_militia_buy_row(inner, tier, win)

        tk.Frame(inner, bg="#333", height=1).pack(fill="x", padx=20, pady=10)

        # ── Deploy actions ───────────────────────────────────────────────
        tk.Label(inner, text="DEPLOY AGAINST RIVAL",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg="#888").pack(
                     anchor="w", padx=16, pady=(0, 4))

        rival_names = [n for n, r in self.rivals.items()
                       if not r.get("disconnected")]
        if not rival_names:
            tk.Label(inner, text="No active rivals.",
                     font=("Arial", 9), bg="#0e1117", fg="#555").pack(pady=8)
        else:
            sel_var = tk.StringVar(value=rival_names[0])
            target_row = tk.Frame(inner, bg="#0e1117")
            target_row.pack(fill="x", padx=16, pady=(0, 8))
            tk.Label(target_row, text="Target:", font=("Arial", 10),
                     bg="#0e1117", fg="#aaa").pack(side="left", padx=(0, 8))
            from tkinter import ttk
            style = ttk.Style()
            style.configure("War.TCombobox", fieldbackground="#1e2130",
                            background="#1e2130", foreground="white",
                            selectbackground="#2e3140")
            ttk.Combobox(target_row, textvariable=sel_var, values=rival_names,
                         state="readonly", width=20,
                         style="War.TCombobox").pack(side="left")

            for act in WAR_ACTIONS:
                self._build_war_action_row(inner, act, sel_var, win)

        tk.Frame(inner, bg="#880000", height=3).pack(fill="x", padx=20, pady=10)

        # Defense indicator
        defense_pct = min(50, (getattr(self, "militia", 0) // 20) * 10)
        tk.Label(inner,
                 text=f"🛡️  Passive defense: {defense_pct}% damage reduction "
                      f"({getattr(self, 'militia', 0)} units)",
                 font=("Arial", 9, "italic"), bg="#0e1117", fg="#555").pack(pady=(4, 12))

    def _militia_status_text(self):
        m = getattr(self, "militia", 0)
        blockaded = getattr(self, "blockaded_days", 0)
        cursed    = getattr(self, "advisor_cursed_days", 0)
        parts = [f"Militia: {m} units"]
        if blockaded > 0:
            parts.append(f"  🚫 BLOCKADED ({blockaded}d)")
        if cursed > 0:
            parts.append(f"  🗡️ ADVISOR HIT ({cursed}d)")
        return "  |  ".join(parts)

    def _build_militia_buy_row(self, parent, tier, win):
        can = self.money >= tier["cost"]
        row = tk.Frame(parent, bg="#1a1a2e", pady=8, padx=12)
        row.pack(fill="x", padx=16, pady=3)

        left = tk.Frame(row, bg="#1a1a2e")
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text=f"{tier['icon']}  {tier['name']}",
                 font=("Arial", 11, "bold"), bg="#1a1a2e",
                 fg="white" if can else "#555", anchor="w").pack(anchor="w")
        tk.Label(left, text=tier["desc"],
                 font=("Arial", 8), bg="#1a1a2e", fg="#888",
                 anchor="w").pack(anchor="w")
        tk.Label(left, text=f"+{tier['units']} units  |  ${tier['cost']:,}",
                 font=("Arial", 8), bg="#1a1a2e",
                 fg="#ffaa00" if can else "#444", anchor="w").pack(anchor="w")

        def _buy(t=tier, w=win):
            if self.money < t["cost"]:
                self.log_event(f"Can't afford {t['name']} (${t['cost']:,})")
                return
            self.money -= t["cost"]
            self.market.money = self.money
            self.militia = getattr(self, "militia", 0) + t["units"]
            self.update_status()
            self.log_event(f"⚔️ Recruited {t['name']}: +{t['units']} militia units "
                           f"(total: {self.militia})")
            w.destroy()
            self.open_war_room()

        tk.Button(row, text="Recruit",
                  font=("Arial", 10, "bold"),
                  bg="#880000" if can else "#1e1e1e",
                  fg="white" if can else "#444",
                  relief="flat", padx=12, pady=5,
                  state="normal" if can else "disabled",
                  command=_buy).pack(side="right")

    def _build_war_action_row(self, parent, act, sel_var, win):
        militia = getattr(self, "militia", 0)
        can     = militia >= act["units"]
        row = tk.Frame(parent, bg="#1e1a1a", pady=8, padx=12)
        row.pack(fill="x", padx=16, pady=3)

        left = tk.Frame(row, bg="#1e1a1a")
        left.pack(side="left", fill="both", expand=True)

        tk.Label(left, text=act["name"],
                 font=("Arial", 11, "bold"), bg="#1e1a1a",
                 fg="white" if can else "#555", anchor="w").pack(anchor="w")
        tk.Label(left, text=act["desc"],
                 font=("Arial", 8), bg="#1e1a1a", fg="#888",
                 anchor="w").pack(anchor="w")
        tk.Label(left, text=f"Costs {act['units']} militia units",
                 font=("Arial", 8), bg="#1e1a1a",
                 fg="#ff6666" if not can else "#888", anchor="w").pack(anchor="w")

        def _deploy(a=act, w=win):
            target = sel_var.get()
            if not target:
                return
            if getattr(self, "militia", 0) < a["units"]:
                self.log_event(f"Not enough militia for {a['name']} ({a['units']} required)")
                return
            self._execute_war_action(a, target)
            w.destroy()
            self.open_war_room()

        tk.Button(row, text="Deploy",
                  font=("Arial", 10, "bold"),
                  bg="#ff2222" if can else "#1e1e1e",
                  fg="white" if can else "#444",
                  relief="flat", padx=12, pady=5,
                  state="normal" if can else "disabled",
                  command=_deploy).pack(side="right")

    # =========================================================
    # EXECUTE WAR ACTION  (outgoing)
    # =========================================================

    def _execute_war_action(self, act, target_name):
        rival = self.rivals.get(target_name)
        if not rival:
            return

        self.militia = max(0, getattr(self, "militia", 0) - act["units"])

        # Spy is local only — no network needed
        if act["id"] == "spy":
            self._show_spy_report(target_name, rival)
            self.log_event(f"🕵️ Spy report on {target_name} obtained.")
            return

        # All other actions need network
        if not getattr(self, "net_client", None) or not self.net_client.connected:
            self.log_event("Not connected to server — can't deploy action.")
            return

        # Build metadata for the action
        atk_bonus = self.get_alliance_militia_bonus()  # 1.25 with Russia Strategic
        meta = {}
        if act["id"] == "raid":
            pct = random.uniform(0.08, 0.15) * atk_bonus
            meta["pct"] = round(pct, 4)
        elif act["id"] == "nuke":
            self.add_transgression(30, 25)
            self._add_ticker(f"⚠️  NUCLEAR STRIKE launched against {target_name}!")

        self.net_client.send({
            "type":      "war_action",
            "action_id": act["id"],
            "victim":    target_name,
            "meta":      meta,
        })
        self.log_event(f"⚔️ {act['name']} deployed against {target_name}.")
        self._add_ticker(f"MILITARY: Covert operation launched against rival...")
        self.update_status()

    # =========================================================
    # INCOMING WAR ACTION  (called from multiplayer_mixin handler)
    # =========================================================

    def receive_war_action(self, attacker_name, action_id, meta):
        """Apply an incoming war action to this player."""
        militia  = getattr(self, "militia", 0)
        # Defense reduction (each 20 units = 10% reduction, max 50%)
        defense  = min(0.50, (militia // 20) * 0.10)
        # Alliance strategic tier reduces all war damage by 30%
        war_reduction = self.get_alliance_war_reduction()
        defense = min(0.80, defense + (1 - war_reduction))  # stack militia + alliance
        # Consume some militia in defense
        if militia > 0:
            self.militia = max(0, militia - random.randint(2, 6))

        if action_id == "raid":
            pct     = meta.get("pct", 0.10) * (1 - defense)
            stolen  = int(self.money * pct)
            self.money -= stolen
            self.market.money = self.money
            self.log_event(
                f"💰 RAIDED by {attacker_name}! Lost ${stolen:,} "
                f"(defense reduced damage by {int(defense*100)}%)")
            self._show_attack_popup(
                "Treasury Raided!", attacker_name,
                f"They stole ${stolen:,.0f} from your reserves.\n"
                f"Your defense reduced it by {int(defense*100)}%.",
                "#ffaa00")

        elif action_id == "assassinate":
            days = 3
            self.advisor_cursed_days = getattr(self, "advisor_cursed_days", 0) + days
            self.log_event(f"🗡️ ADVISOR HIT by {attacker_name}! "
                           f"Double bad events for {days} days.")
            self._show_attack_popup(
                "Advisor Assassinated!", attacker_name,
                f"Your advisor is dead.\nYou'll suffer double bad events for {days} days.",
                "#cc0066")

        elif action_id == "sabotage":
            if self.oil_operations:
                op = random.choice(self.oil_operations)
                self.oil_operations.remove(op)
                self.bombed_countries.discard(op["country"])
                self.action_taken.pop(op["country"], None)
                self.log_event(
                    f"💥 SABOTAGE by {attacker_name}! "
                    f"Lost resource op in {op['country']}.")
                self._show_attack_popup(
                    "Operation Sabotaged!", attacker_name,
                    f"Your operation in {op['country']} was destroyed.",
                    "#ff6600")
            else:
                self.log_event(f"💥 Sabotage by {attacker_name} — no ops to destroy.")

        elif action_id == "blockade":
            days = max(1, int(4 * (1 - defense)))
            self.blockaded_days = getattr(self, "blockaded_days", 0) + days
            self.log_event(f"⛵ BLOCKADE by {attacker_name}! "
                           f"Resource income blocked for {days} days.")
            self._show_attack_popup(
                "Trade Blockaded!", attacker_name,
                f"All resource income blocked for {days} days.\n"
                f"Your defense reduced the duration by {int(defense*100)}%.",
                "#0077cc")

        elif action_id == "nuke":
            reduction = int(self.money * 0.40 * (1 - defense))
            self.money -= reduction
            self.market.money = self.money
            self.add_transgression(15, 20)
            self.apply_market_effect(
                ["ALL"], 0.85, 6, f"Nuclear strike by {attacker_name}")
            self.log_event(
                f"☢️ NUCLEAR STRIKE by {attacker_name}! "
                f"Lost ${reduction:,}. Markets in freefall.")
            self._show_attack_popup(
                "☢️ NUCLEAR STRIKE", attacker_name,
                f"They launched a nuclear strike.\nYou lost ${reduction:,.0f}.\n"
                f"Defense absorbed {int(defense*100)}%.",
                "#cc00ff")

        self.update_status()

    # =========================================================
    # SPY REPORT POPUP  (local)
    # =========================================================

    def _show_spy_report(self, name, rival):
        popup = tk.Toplevel(self.root)
        popup.title(f"Spy Report — {name}")
        popup.configure(bg="#0e1117")
        popup.geometry("360x320")
        popup.resizable(False, False)

        tk.Frame(popup, bg="#334400", height=4).pack(fill="x")
        tk.Label(popup, text=f"🕵️  SPY REPORT: {name}",
                 font=("Impact", 16), bg="#0e1117", fg="#aaff00").pack(pady=(12, 6))

        rows = [
            ("Country",       rival.get("country", "Unknown")),
            ("Money",         f"${rival.get('money', 0):,.0f}"),
            ("Day",           str(rival.get("days", "?"))),
            ("Happiness",     f"{rival.get('happiness', '?'):.0f}"),
            ("Public Opinion",f"{rival.get('public_opinion', '?'):.0f}"),
            ("Transgressions",f"{rival.get('transgressions', '?'):.0f}"),
            ("Militia",       str(rival.get("militia", "Unknown"))),
        ]
        for lbl, val in rows:
            r = tk.Frame(popup, bg="#111820")
            r.pack(fill="x", padx=24, pady=2)
            tk.Label(r, text=lbl + ":", font=("Arial", 9),
                     bg="#111820", fg="#666", width=16, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=("Arial", 9, "bold"),
                     bg="#111820", fg="white").pack(side="left")

        tk.Button(popup, text="Close",
                  font=("Arial", 10), bg="#1e2130", fg="white",
                  relief="flat", padx=20, pady=6,
                  command=popup.destroy).pack(pady=12)

    # =========================================================
    # INCOMING ATTACK POPUP
    # =========================================================

    def _show_attack_popup(self, title, attacker, body, color):
        popup = tk.Toplevel(self.root)
        popup.title("⚔️ Under Attack!")
        popup.configure(bg="#0e1117")
        popup.geometry("400x240")
        popup.resizable(False, False)

        tk.Frame(popup, bg=color, height=5).pack(fill="x")
        tk.Label(popup, text=f"⚔️  {title}",
                 font=("Impact", 18), bg="#0e1117", fg=color).pack(pady=(14, 4))
        tk.Label(popup, text=f"Attacked by: {attacker}",
                 font=("Arial", 9, "italic"), bg="#0e1117", fg="#888").pack()
        tk.Label(popup, text=body,
                 font=("Arial", 10), bg="#0e1117", fg="#dddddd",
                 wraplength=360, justify="center").pack(pady=10)
        tk.Frame(popup, bg=color, height=3).pack(fill="x")
        tk.Button(popup, text="Understood",
                  font=("Arial", 10, "bold"), bg=color, fg="white",
                  relief="flat", padx=20, pady=6,
                  command=popup.destroy).pack(pady=10)

    # =========================================================
    # DAILY MILITIA PROCESSING  (call from main_loop)
    # =========================================================

    def process_militia_effects(self):
        """Tick down blockade and advisor-curse counters."""
        if getattr(self, "blockaded_days", 0) > 0:
            self.blockaded_days -= 1
            if self.blockaded_days == 0:
                self.log_event("⛵ Trade blockade has lifted — resource income restored.")

        if getattr(self, "advisor_cursed_days", 0) > 0:
            self.advisor_cursed_days -= 1
            if self.advisor_cursed_days == 0:
                self.log_event("🗡️ Advisor curse has expired.")
            else:
                # Extra bad event
                self.random_events()
