import tkinter as tk

BLACK_MARKET_ITEMS = [
    {"id": "stolen_data", "name": "Stolen Corporate Data",
     "desc": "Sell leaked CEO emails to rival corporations.",
     "gain": 8_000_000, "trans": 12, "opin": -8},
    {"id": "arms_smuggling", "name": "Arms Smuggling",
     "desc": "Sell surplus military hardware to the highest bidder.",
     "gain": 10_000_000, "trans": 18, "opin": -15},
    {"id": "laundered_cash", "name": "Laundered Cash",
     "desc": "Process dirty money through shell companies.",
     "gain": 20_000_000, "trans": 20, "opin": -18},
    {"id": "forged_docs", "name": "Forged Documents",
     "desc": "Buy a clean identity. Costs money but wipes records.",
     "gain": -3_000_000, "trans": -15, "opin": 0},
    {"id": "organ_trafficking", "name": "Organ Trafficking",
     "desc": "The darkest trade. Staggeringly profitable.",
     "gain": 25_000_000, "trans": 30, "opin": -25},
]


class BlackMarketMixin:
    """Black market — fast money at severe moral cost."""

    def open_black_market(self):
        win = tk.Toplevel(self.root)
        win.title("Black Market")
        win.configure(bg="#0e1117")
        win.geometry("500x480")
        win.resizable(False, False)

        tk.Label(win, text="BLACK MARKET",
                 font=("Impact", 24), bg="#0e1117", fg="#ff2222").pack(pady=(18, 2))
        tk.Label(win, text="High risk. Higher reward.",
                 font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))

        for item in BLACK_MARKET_ITEMS:
            self._build_bm_row(win, item)

    def _build_bm_row(self, win, item):
        row = tk.Frame(win, bg="#1e2130", pady=8, padx=12)
        row.pack(fill="x", padx=16, pady=4)

        info = tk.Frame(row, bg="#1e2130")
        info.pack(side="left", fill="both", expand=True)

        tk.Label(info, text=item["name"], font=("Arial", 11, "bold"),
                 bg="#1e2130", fg="white", anchor="w").pack(anchor="w")
        tk.Label(info, text=item["desc"], font=("Arial", 8),
                 bg="#1e2130", fg="#888888", anchor="w",
                 wraplength=280, justify="left").pack(anchor="w")

        gain = item["gain"]
        gain_color = "#00ff90" if gain > 0 else "#ff4444"
        gain_text  = f"+${gain:,}" if gain > 0 else f"-${abs(gain):,}"
        trans_text = f"+{item['trans']} transgression" if item["trans"] > 0 else f"{item['trans']} transgression"
        tk.Label(info,
                 text=f"{gain_text}  |  {trans_text}",
                 font=("Arial", 7), bg="#1e2130", fg=gain_color,
                 anchor="w").pack(anchor="w", pady=(2, 0))

        def do_deal(it=item, w=win):
            if it["gain"] < 0 and self.money < abs(it["gain"]):
                self.log_event(f"Can't afford {it['name']} (need ${abs(it['gain']):,})")
                return
            self.money += it["gain"]
            self.market.money = self.money
            if it["trans"] > 0:
                self.add_transgression(it["trans"], abs(it["opin"]) if it["opin"] < 0 else 0)
            elif it["trans"] < 0:
                self.transgressions = max(0, self.transgressions + it["trans"])
                self._update_bars()
            if it["opin"] > 0:
                self.public_opinion = min(100, self.public_opinion + it["opin"])
                self._update_bars()
            self.update_status()
            self.log_event(f"Black market: {it['name']} completed.")
            self._add_ticker("RUMOUR: Underground deal traced to offshore account...")
            w.destroy()

        btn_bg = "#ff2222" if gain > 0 else "#444466"
        btn_fg = "white"
        tk.Button(row, text="Deal",
                  font=("Arial", 10, "bold"), bg=btn_bg, fg=btn_fg,
                  relief="flat", padx=14, pady=5,
                  command=do_deal).pack(side="right")
