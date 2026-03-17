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

        for item in BLACK_MARKET_ITEMS:
            self._build_bm_row(inner, item)

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

        cooldowns = getattr(self, "_bm_cooldowns", {})
        cooldown_left = cooldowns.get(item["id"], 0)
        on_cooldown = cooldown_left > 0

        def do_deal(it=item, w=win):
            cd = getattr(self, "_bm_cooldowns", {})
            if cd.get(it["id"], 0) > 0:
                self.log_event(f"Black market: {it['name']} on cooldown ({cd[it['id']]} days).")
                return
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
            # Set 4-day cooldown
            if not hasattr(self, "_bm_cooldowns"):
                self._bm_cooldowns = {}
            self._bm_cooldowns[it["id"]] = 4
            self.update_status()
            self.log_event(f"Black market: {it['name']} completed. Available again in 4 days.")
            self._add_ticker("RUMOUR: Underground deal traced to offshore account...")
            w.destroy()

        if on_cooldown:
            btn_bg, btn_fg = "#222222", "#555555"
            btn_txt = f"{cooldown_left}d"
            btn_state = "disabled"
        elif gain > 0:
            btn_bg, btn_fg, btn_txt, btn_state = "#ff2222", "white", "Deal", "normal"
        else:
            btn_bg, btn_fg, btn_txt, btn_state = "#444466", "white", "Deal", "normal"

        tk.Button(row, text=btn_txt,
                  font=("Arial", 10, "bold"), bg=btn_bg, fg=btn_fg,
                  relief="flat", padx=14, pady=5,
                  state=btn_state, command=do_deal).pack(side="right")
