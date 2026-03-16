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
        from world_map_mixin import RESOURCE_DATA
        for name, rival in self.rivals.items():
            rival["money"] *= random.uniform(0.99, 1.03)
            if random.random() < 0.06:
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
            # Random release
            for res in list(rival["controls"].keys()):
                to_release = {c for c in rival["controls"][res] if random.random() < 0.025}
                rival["controls"][res] -= to_release

    def open_rivals_window(self):
        win = tk.Toplevel(self.root)
        win.title("Rival Billionaires")
        win.configure(bg="#0e1117")
        win.geometry("520x420")
        win.resizable(False, False)

        tk.Label(win, text="RIVAL BILLIONAIRES",
                 font=("Impact", 22), bg="#0e1117", fg="#cc44ff").pack(pady=(18, 2))
        tk.Label(win, text="They're hunting the same resources as you.",
                 font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))

        for name, rival in self.rivals.items():
            row = tk.Frame(win, bg="#1e2130", pady=10, padx=14)
            row.pack(fill="x", padx=16, pady=5)

            tk.Label(row, text=name, font=("Arial", 12, "bold"),
                     bg="#1e2130", fg=rival["color"]).pack(anchor="w")
            tk.Label(row, text=f"Net worth: ${rival['money']:,.0f}",
                     font=("Arial", 9), bg="#1e2130", fg="#aaaaaa").pack(anchor="w")

            controlled = []
            for res, ctries in rival["controls"].items():
                for c in ctries:
                    controlled.append(f"{c} ({res})")

            if controlled:
                tk.Label(row, text="Controls: " + ", ".join(controlled[:5]),
                         font=("Arial", 8), bg="#1e2130", fg="#888888",
                         wraplength=380, justify="left").pack(anchor="w")
            else:
                tk.Label(row, text="Controls: nothing yet",
                         font=("Arial", 8), bg="#1e2130", fg="#555").pack(anchor="w")

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
