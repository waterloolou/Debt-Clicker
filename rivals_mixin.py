import tkinter as tk
import random

RIVAL_DEFS = [
    {"name": "Viktor Drago",      "money": 95_000_000,  "color": "#cc0044"},
    {"name": "Chen Wei",          "money": 120_000_000, "color": "#cc6600"},
    {"name": "Elizabeth Harlow",  "money": 80_000_000,  "color": "#9900cc"},
]


class RivalsMixin:
    """AI rival billionaires who compete for the same resource countries."""

    def init_rivals(self):
        self.rivals = {
            r["name"]: {"money": r["money"], "controls": {}, "color": r["color"]}
            for r in RIVAL_DEFS
        }

    def process_rivals(self):
        if getattr(self, "is_multiplayer", False):
            return  # real player states come from network updates
        from world_map_mixin import RESOURCE_DATA
        for name, rival in self.rivals.items():
            # Rivals grow wealth more aggressively — 1–5% per day
            rival["money"] *= random.uniform(0.99, 1.05)

            # Seize a country (15% chance per day, up from 6%)
            if random.random() < 0.15:
                resource = random.choice(list(RESOURCE_DATA.keys()))
                countries = list(RESOURCE_DATA[resource]["countries"].keys())
                occupied_by_rivals = set()
                for rv in self.rivals.values():
                    occupied_by_rivals |= rv["controls"].get(resource, set())
                available = [c for c in countries
                             if c not in self.bombed_countries
                             and c != getattr(self, "country", "")
                             and c not in occupied_by_rivals]
                if available:
                    target = random.choice(available)
                    cost = RESOURCE_DATA[resource]["countries"][target]["action_cost"] * 0.4
                    if rival["money"] >= cost:
                        rival["money"] -= cost
                        rival["controls"].setdefault(resource, set()).add(target)
                        self.log_event(f"RIVAL: {name} seized {resource} ops in {target}!")
                        self._add_ticker(f"MARKETS: {name} acquires {resource} stake in {target}...")

            # Tick retaliation boost counter
            if getattr(self, "rival_retaliation_boost", 0) > 0:
                self.rival_retaliation_boost -= 1

            # Direct attack on the player (8% base, doubled during retaliation boost)
            base_chance = 0.16 if getattr(self, "rival_retaliation_boost", 0) > 0 else 0.08
            if random.random() < base_chance:
                self._rival_attack_player(name, rival)

            # Random release (slower — rivals hold territory longer)
            for res in list(rival["controls"].keys()):
                to_release = {c for c in rival["controls"][res] if random.random() < 0.01}
                rival["controls"][res] -= to_release

    def _rival_attack_player(self, name, rival):
        """A rival launches a targeted action against the player."""
        color  = rival.get("color", "#cc44ff")
        # Build available attack pool based on what player owns
        pool = ["smear", "lobby", "sabotage", "poach", "lawsuit"]
        if self.factories:
            pool.extend(["asset_strike", "smear_factories"])
        if self.oil_operations:
            pool.append("operation_seizure")
        attack = random.choice(pool)

        # Alliance may intercept the attack
        block_chance = self.get_alliance_block_chance(attack)
        if block_chance > 0 and random.random() < block_chance:
            ally_color = self._ALLIANCE_DATA[self.alliance]["color"]
            self.log_event(f"ALLIANCE: {self.alliance} intercepted {name}'s {attack} attack!")
            self._show_rival_attack_popup(
                f"{self.alliance} Intelligence", ally_color,
                "Attack Intercepted",
                f"Your {self.alliance} alliance blocked {name}'s {attack} operation.\n\nNo damage taken.")
            return

        if attack == "smear":
            # PR smear campaign — hits public opinion
            hit = random.randint(5, 15)
            self.public_opinion = max(0, self.public_opinion - hit)
            self.log_event(f"RIVAL: {name} funded a smear campaign against you! "
                           f"Public opinion -{hit}%")
            self._add_ticker(f"BREAKING: Anonymous sources question {self.username}'s ethics...")
            self._show_rival_attack_popup(name, color,
                f"Smear Campaign",
                f"{name} paid journalists to run hit pieces on you.\n\nPublic Opinion -{hit}%")

        elif attack == "lobby":
            # Lobby regulators — raises your transgressions
            hit = random.randint(8, 20)
            self.add_transgression(hit, 10)
            self.log_event(f"RIVAL: {name} tipped off regulators! Transgressions +{hit}")
            self._show_rival_attack_popup(name, color,
                "Regulatory Tip-Off",
                f"{name} gave your file to federal regulators.\n\nTransgressions +{hit}")

        elif attack == "sabotage":
            # Sabotage an active operation
            if self.oil_operations:
                op = random.choice(self.oil_operations)
                lost = op["income"] * random.randint(3, 7)
                self.money -= lost
                self.market.money = self.money
                self.log_event(f"RIVAL: {name} sabotaged your {op['resource']} operation "
                               f"in {op['country']}! Lost ${lost:,.0f}")
                self._show_rival_attack_popup(name, color,
                    "Operation Sabotaged",
                    f"{name} sent agents to disrupt your {op['resource']} "
                    f"operation in {op['country']}.\n\n-${lost:,.0f}")
            else:
                # No ops — just steal money directly
                stolen = int(self.money * random.uniform(0.01, 0.04))
                self.money -= stolen
                self.market.money = self.money
                self.log_event(f"RIVAL: {name} laundered money through your accounts! "
                               f"-${stolen:,}")
                self._show_rival_attack_popup(name, color,
                    "Financial Sabotage",
                    f"{name} ran a fraudulent wire through your shell accounts.\n\n"
                    f"-${stolen:,}")

        elif attack == "poach":
            # Poach your happiness (bribe your staff / personal attacks)
            hit = random.randint(5, 12)
            self.happiness = max(0, self.happiness - hit)
            self.log_event(f"RIVAL: {name} poached your key staff and spread rumors. "
                           f"Happiness -{hit}")
            self._show_rival_attack_popup(name, color,
                "Staff Poached",
                f"{name} headhunted your best people and fed gossip to tabloids.\n\n"
                f"Happiness -{hit}")

        elif attack == "lawsuit":
            # File a lawsuit — costs money and transgressions
            fine  = int(self.money * random.uniform(0.02, 0.06))
            trans = random.randint(5, 12)
            self.money -= fine
            self.market.money = self.money
            self.add_transgression(trans, 8)
            self.log_event(f"RIVAL: {name} filed a lawsuit against you! "
                           f"-${fine:,} | Transgressions +{trans}")
            self._show_rival_attack_popup(name, color,
                "Lawsuit Filed",
                f"{name}'s legal team has filed a federal lawsuit against you.\n\n"
                f"-${fine:,}  |  Transgressions +{trans}")

        elif attack == "asset_strike" and self.factories:
            fac = random.choice(self.factories)
            from factory_mixin import _FACTORY_BY_ID
            ftype = _FACTORY_BY_ID[fac["type_id"]]
            fac["on_strike"]   = True
            fac["strike_days"] = 3
            self.public_opinion = max(0, self.public_opinion - 8)
            self.log_event(f"RIVAL: {name} bribed your workers at {ftype['name']}! "
                           f"3-day strike. Opinion -8.")
            self._show_rival_attack_popup(name, color,
                "Factory Strike Instigated",
                f"{name} paid agitators to organise a strike at your {ftype['name']}.\n\n"
                f"3-day work stoppage  |  Public Opinion -8")

        elif attack == "operation_seizure" and self.oil_operations:
            op = random.choice(self.oil_operations)
            self.oil_operations.remove(op)
            self.bombed_countries.discard(op["country"])
            getattr(self, "action_taken", {}).pop(op["country"], None)
            self.log_event(f"RIVAL: {name} seized your {op['resource']} operation "
                           f"in {op['country']}! Operation lost.")
            self._show_rival_attack_popup(name, color,
                "Operation Seized",
                f"{name} deployed operatives and seized control of your\n"
                f"{op['resource']} operations in {op['country']}.\n\nOperation lost.")

        elif attack == "smear_factories" and self.factories:
            hit = random.randint(10, 20)
            self.public_opinion = max(0, self.public_opinion - hit)
            self.log_event(f"RIVAL: {name} ran a labour-violation campaign against your factories! "
                           f"Opinion -{hit}")
            self._show_rival_attack_popup(name, color,
                "Labour Smear Campaign",
                f"{name} leaked footage linking your factories to labour violations.\n\n"
                f"Public Opinion -{hit}")

        self.update_status()

    def _show_rival_attack_popup(self, rival_name, color, title, body):
        """Dramatic popup shown when a rival attacks you."""
        win = tk.Toplevel(self.root)
        win.title("Rival Action")
        win.configure(bg="#0e1117")
        win.geometry("400x240")
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        def _close(event=None):
            try:
                win.destroy()
            except tk.TclError:
                pass

        win.bind("<Return>", _close)
        win.bind("<Escape>", _close)
        win.protocol("WM_DELETE_WINDOW", _close)

        # Auto-dismiss after 12 seconds if not clicked
        win.after(12000, _close)

        tk.Frame(win, bg=color, height=6).pack(fill="x")
        tk.Label(win, text=f"⚠  {title.upper()}",
                 font=("Impact", 18), bg="#0e1117", fg=color).pack(pady=(14, 2))
        tk.Label(win, text=f"— {rival_name} —",
                 font=("Arial", 10, "italic"), bg="#0e1117", fg="#888").pack()
        tk.Label(win, text=body,
                 font=("Arial", 10), bg="#0e1117", fg="white",
                 wraplength=360, justify="center").pack(pady=10)
        tk.Button(win, text="Noted  [Enter]", font=("Arial", 10),
                  bg=color, fg="white", relief="flat", padx=20, pady=5,
                  command=_close).pack(pady=(0, 14))
        tk.Frame(win, bg=color, height=4).pack(fill="x")

    def open_rivals_window(self):
        is_mp = getattr(self, "is_multiplayer", False)

        win = tk.Toplevel(self.root)
        win.title("Rival Players" if is_mp else "Rival Billionaires")
        win.configure(bg="#0e1117")
        win.geometry("520x420")
        win.resizable(False, False)

        if is_mp:
            tk.Label(win, text="RIVAL PLAYERS",
                     font=("Impact", 22), bg="#0e1117", fg="#1e90ff").pack(pady=(18, 2))
            tk.Label(win, text="Real opponents — live stats from the network.",
                     font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))
        else:
            tk.Label(win, text="RIVAL BILLIONAIRES",
                     font=("Impact", 22), bg="#0e1117", fg="#cc44ff").pack(pady=(18, 2))
            tk.Label(win, text="They're hunting the same resources as you.",
                     font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))

        for name, rival in self.rivals.items():
            row = tk.Frame(win, bg="#1e2130", pady=10, padx=14)
            row.pack(fill="x", padx=16, pady=5)

            color = rival.get("color", "#aaaaaa")
            display_name = name
            if is_mp and rival.get("disconnected"):
                display_name = f"{name}  [DISCONNECTED]"
                color = "#555555"

            tk.Label(row, text=display_name, font=("Arial", 12, "bold"),
                     bg="#1e2130", fg=color).pack(anchor="w")
            tk.Label(row, text=f"Net worth: ${rival['money']:,.0f}",
                     font=("Arial", 9), bg="#1e2130", fg="#aaaaaa").pack(anchor="w")

            if is_mp:
                # Show real live stats for multiplayer rivals
                country       = rival.get("country", "—")
                days          = rival.get("days", 0)
                happiness     = rival.get("happiness", 0)
                opinion       = rival.get("public_opinion", 0)
                transgressions = rival.get("transgressions", 0)
                tk.Label(row,
                         text=(f"Country: {country}  |  Day {days}  |  "
                               f"Happiness: {int(happiness)}%  |  "
                               f"Opinion: {int(opinion)}%  |  "
                               f"Transgressions: {int(transgressions)}"),
                         font=("Arial", 8), bg="#1e2130", fg="#888888",
                         wraplength=460, justify="left").pack(anchor="w")
            else:
                controlled = []
                for res, ctries in rival.get("controls", {}).items():
                    for c in ctries:
                        controlled.append(f"{c} ({res})")

                if controlled:
                    tk.Label(row, text="Controls: " + ", ".join(controlled[:5]),
                             font=("Arial", 8), bg="#1e2130", fg="#888888",
                             wraplength=380, justify="left").pack(anchor="w")
                else:
                    tk.Label(row, text="Controls: nothing yet",
                             font=("Arial", 8), bg="#1e2130", fg="#555").pack(anchor="w")

    def _rival_retaliate(self, rival_name, rival, country, resource):
        """Immediate retaliation when player bombs a country a rival controls."""
        color = rival.get("color", "#cc44ff")
        retaliation = random.choice(["fine", "smear", "counter_op"])

        if retaliation == "fine":
            fine = int(self.money * random.uniform(0.03, 0.08))
            self.money -= fine
            self.market.money = self.money
            self.add_transgression(10, 8)
            self.log_event(f"RETALIATION: {rival_name} filed an injunction over {country}! "
                           f"-${fine:,} | Transgressions +10")
            self._show_rival_attack_popup(rival_name, color,
                "Retaliation: Legal Injunction",
                f"{rival_name} had lawyers waiting.\nYou seized their {resource} ops in {country}.\n\n"
                f"-${fine:,}  |  Transgressions +10")

        elif retaliation == "smear":
            opinion_hit = random.randint(10, 20)
            happiness_hit = random.randint(5, 10)
            self.public_opinion = max(0, self.public_opinion - opinion_hit)
            self.happiness      = max(0, self.happiness - happiness_hit)
            self.log_event(f"RETALIATION: {rival_name} launched a counter-PR blitz! "
                           f"Opinion -{opinion_hit} | Happiness -{happiness_hit}")
            self._show_rival_attack_popup(rival_name, color,
                "Retaliation: PR Blitz",
                f"{rival_name} is furious about {country}.\nThey've gone to every news outlet.\n\n"
                f"Opinion -{opinion_hit}  |  Happiness -{happiness_hit}")

        elif retaliation == "counter_op":
            # Rival seizes one of your active operations
            if self.oil_operations:
                op = random.choice(self.oil_operations)
                self.oil_operations.remove(op)
                self.log_event(f"RETALIATION: {rival_name} seized your {op['resource']} "
                               f"operation in {op['country']}!")
                self._show_rival_attack_popup(rival_name, color,
                    "Retaliation: Operation Seized",
                    f"{rival_name} counter-attacked your {op['resource']} "
                    f"operation in {op['country']}.\n\nOperation lost.")
            else:
                stolen = int(self.money * random.uniform(0.02, 0.05))
                self.money -= stolen
                self.market.money = self.money
                self.log_event(f"RETALIATION: {rival_name} hit your accounts — -${stolen:,}")
                self._show_rival_attack_popup(rival_name, color,
                    "Retaliation: Financial Strike",
                    f"{rival_name} couldn't seize your ops but hit your accounts.\n\n"
                    f"-${stolen:,}")

        self.update_status()

    def is_rival_controlled(self, resource, country):
        """Returns rival name if a rival controls this country, else None."""
        for name, rival in self.rivals.items():
            if country in rival["controls"].get(resource, set()):
                return name
        return None

    def buyout_rival(self, resource, country, rival_name):
        """Buy a rival out of a country for 2x the normal action cost."""
        from world_map_mixin import RESOURCE_DATA
        base_cost = RESOURCE_DATA[resource]["countries"][country]["action_cost"]
        buyout_cost = int(base_cost * 2)
        if self.money < buyout_cost:
            self.log_event(f"Need ${buyout_cost:,} to buy out {rival_name} from {country}")
            return False
        self.money -= buyout_cost
        self.market.money = self.money
        self.rivals[rival_name]["controls"].get(resource, set()).discard(country)
        self.log_event(f"Bought out {rival_name} from {country} ({resource}) for ${buyout_cost:,}")
        self._add_ticker(f"MARKETS: Hostile acquisition — {country} {resource} changes hands...")
        self.update_status()
        return True
