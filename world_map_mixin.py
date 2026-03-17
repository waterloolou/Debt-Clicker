"""world_map_mixin.py
Interactive world map — bomb or stage a coup in resource-rich countries.
"""

import tkinter as tk
import os
import threading
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import shapely.geometry

_SHAPEFILE_URL = (
    "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
)
_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "world_countries.gpkg"
)

# ---------------------------------------------------------------------------
# Resource catalogue
# ---------------------------------------------------------------------------
RESOURCE_DATA = {
    "Oil": {
        "clr": ("#3d2600", "#cc8800"),
        "market": ["Energy"],
        "countries": {
            "Kuwait":                   {"action_cost":   5_000_000, "income":   500_000, "days": 15, "reserves": "102 billion barrels"},
            "United Arab Emirates":     {"action_cost":   8_000_000, "income":   600_000, "days": 15, "reserves":  "97 billion barrels"},
            "Qatar":                    {"action_cost":   8_000_000, "income":   700_000, "days": 20, "reserves":  "25 billion barrels"},
            "Angola":                   {"action_cost":   8_000_000, "income":   600_000, "days": 15, "reserves":   "8 billion barrels"},
            "Libya":                    {"action_cost":  10_000_000, "income":   800_000, "days": 15, "reserves":  "48 billion barrels"},
            "Algeria":                  {"action_cost":  12_000_000, "income":   800_000, "days": 15, "reserves":  "12 billion barrels"},
            "Nigeria":                  {"action_cost":  15_000_000, "income": 1_000_000, "days": 20, "reserves":  "37 billion barrels"},
            "Norway":                   {"action_cost":  28_000_000, "income": 1_500_000, "days": 15, "reserves":   "8 billion barrels"},
            "Kazakhstan":               {"action_cost":  18_000_000, "income": 1_200_000, "days": 20, "reserves":  "30 billion barrels"},
            "Mexico":                   {"action_cost":  22_000_000, "income": 1_500_000, "days": 20, "reserves": "5.8 billion barrels"},
            "Brazil":                   {"action_cost":  20_000_000, "income": 1_300_000, "days": 20, "reserves":  "12 billion barrels"},
            "Venezuela":                {"action_cost":  25_000_000, "income": 2_000_000, "days": 20, "reserves": "304 billion barrels"},
            "Iraq":                     {"action_cost":  30_000_000, "income": 2_000_000, "days": 25, "reserves": "145 billion barrels"},
            "Iran":                     {"action_cost":  35_000_000, "income": 2_500_000, "days": 25, "reserves": "157 billion barrels"},
            "Canada":                   {"action_cost":  40_000_000, "income": 2_500_000, "days": 25, "reserves": "170 billion barrels"},
            "Saudi Arabia":             {"action_cost":  60_000_000, "income": 4_000_000, "days": 30, "reserves": "267 billion barrels"},
            "Russia":                   {"action_cost": 100_000_000, "income": 6_000_000, "days": 20, "reserves":  "80 billion barrels"},
            "United States of America": {"action_cost": 200_000_000, "income":10_000_000, "days": 30, "reserves": "297 billion barrels"},
        },
    },
    "Diamonds": {
        "clr": ("#0d0d2b", "#7777ff"),
        "market": ["Finance", "Entertainment"],
        "countries": {
            "Botswana":        {"action_cost":  15_000_000, "income":   900_000, "days": 20, "reserves": "25% of world supply"},
            "Russia":          {"action_cost":  80_000_000, "income": 3_000_000, "days": 25, "reserves": "23% of world supply"},
            "Canada":          {"action_cost":  30_000_000, "income": 1_200_000, "days": 20, "reserves": "15% of world supply"},
            "South Africa":    {"action_cost":  20_000_000, "income": 1_000_000, "days": 20, "reserves": "Famous Kimberley mines"},
            "Angola":          {"action_cost":  12_000_000, "income":   700_000, "days": 15, "reserves": "5th largest producer"},
            "Namibia":         {"action_cost":  10_000_000, "income":   600_000, "days": 15, "reserves": "Coastal diamond fields"},
            "Dem. Rep. Congo": {"action_cost":  18_000_000, "income": 1_100_000, "days": 20, "reserves": "Artisanal mining hotbed"},
            "Australia":       {"action_cost":  35_000_000, "income": 1_500_000, "days": 20, "reserves": "Argyle mine legacy"},
            "Zimbabwe":        {"action_cost":  10_000_000, "income":   700_000, "days": 15, "reserves": "Marange diamond fields"},
        },
    },
    "Minerals": {
        "clr": ("#0d2a2a", "#00ccaa"),
        "market": ["Technology", "Energy"],
        "countries": {
            "China":           {"action_cost": 150_000_000, "income": 8_000_000, "days": 30, "reserves": "60% of rare earth supply"},
            "Chile":           {"action_cost":  25_000_000, "income": 1_500_000, "days": 20, "reserves": "World's largest copper"},
            "Peru":            {"action_cost":  20_000_000, "income": 1_200_000, "days": 20, "reserves": "Silver, zinc, copper"},
            "Dem. Rep. Congo": {"action_cost":  18_000_000, "income": 1_300_000, "days": 20, "reserves": "60% of world cobalt"},
            "Australia":       {"action_cost":  35_000_000, "income": 2_000_000, "days": 25, "reserves": "Iron ore, lithium, nickel"},
            "Brazil":          {"action_cost":  25_000_000, "income": 1_500_000, "days": 20, "reserves": "Iron ore, niobium"},
            "Russia":          {"action_cost":  90_000_000, "income": 5_000_000, "days": 25, "reserves": "Nickel, palladium, gold"},
            "Kazakhstan":      {"action_cost":  20_000_000, "income": 1_200_000, "days": 20, "reserves": "Chromium, uranium, zinc"},
            "South Africa":    {"action_cost":  22_000_000, "income": 1_400_000, "days": 20, "reserves": "Platinum, gold, chromium"},
            "Indonesia":       {"action_cost":  20_000_000, "income": 1_300_000, "days": 20, "reserves": "Nickel, coal, tin"},
        },
    },
    "Agriculture": {
        "clr": ("#1a2200", "#88cc00"),
        "market": ["Retail"],
        "countries": {
            "United States of America": {"action_cost": 180_000_000, "income": 7_000_000, "days": 25, "reserves": "Corn Belt & Great Plains"},
            "Brazil":                   {"action_cost":  22_000_000, "income": 1_500_000, "days": 20, "reserves": "Amazon soy + sugarcane"},
            "Argentina":                {"action_cost":  15_000_000, "income": 1_000_000, "days": 15, "reserves": "Pampas breadbasket"},
            "Russia":                   {"action_cost":  85_000_000, "income": 4_000_000, "days": 20, "reserves": "World wheat superpower"},
            "Canada":                   {"action_cost":  38_000_000, "income": 2_000_000, "days": 20, "reserves": "Prairies wheat belt"},
            "Australia":                {"action_cost":  30_000_000, "income": 1_800_000, "days": 20, "reserves": "Grain and sheep"},
            "Ukraine":                  {"action_cost":  12_000_000, "income":   900_000, "days": 15, "reserves": "Breadbasket of Europe"},
            "India":                    {"action_cost":  30_000_000, "income": 2_000_000, "days": 20, "reserves": "Rice and wheat giant"},
            "China":                    {"action_cost": 130_000_000, "income": 6_000_000, "days": 25, "reserves": "World's largest food producer"},
            "France":                   {"action_cost":  45_000_000, "income": 2_500_000, "days": 20, "reserves": "EU's top farm exporter"},
        },
    },
    "Technology": {
        "clr": ("#001a33", "#0099ff"),
        "market": ["Technology", "AI"],
        "countries": {
            "United States of America": {"action_cost": 200_000_000, "income":12_000_000, "days": 30, "reserves": "Silicon Valley dominance"},
            "China":                    {"action_cost": 160_000_000, "income": 9_000_000, "days": 30, "reserves": "Factory of the world"},
            "Taiwan":                   {"action_cost":  50_000_000, "income": 4_000_000, "days": 25, "reserves": "TSMC chip dominance"},
            "South Korea":              {"action_cost":  55_000_000, "income": 4_000_000, "days": 25, "reserves": "Samsung + SK Hynix"},
            "Japan":                    {"action_cost":  70_000_000, "income": 5_000_000, "days": 25, "reserves": "Robotics and precision"},
            "Germany":                  {"action_cost":  60_000_000, "income": 4_500_000, "days": 25, "reserves": "Industrial automation"},
            "Netherlands":              {"action_cost":  45_000_000, "income": 3_000_000, "days": 20, "reserves": "ASML chip machines"},
            "India":                    {"action_cost":  35_000_000, "income": 2_500_000, "days": 20, "reserves": "Bangalore tech hub"},
        },
    },
    "Finance": {
        "clr": ("#1a1500", "#ccaa00"),
        "market": ["Finance"],
        "countries": {
            "United States of America": {"action_cost": 200_000_000, "income":15_000_000, "days": 30, "reserves": "Wall Street dominance"},
            "United Kingdom":           {"action_cost":  80_000_000, "income": 6_000_000, "days": 25, "reserves": "London financial hub"},
            "Switzerland":              {"action_cost":  60_000_000, "income": 5_000_000, "days": 25, "reserves": "Swiss bank secrecy"},
            "Luxembourg":               {"action_cost":  30_000_000, "income": 2_500_000, "days": 20, "reserves": "EU tax haven"},
            "Japan":                    {"action_cost":  65_000_000, "income": 5_000_000, "days": 25, "reserves": "Yen powerhouse"},
            "France":                   {"action_cost":  50_000_000, "income": 3_500_000, "days": 20, "reserves": "Paris Bourse"},
            "Germany":                  {"action_cost":  55_000_000, "income": 4_000_000, "days": 20, "reserves": "Frankfurt banking"},
            "Singapore":                {"action_cost":  50_000_000, "income": 4_000_000, "days": 25, "reserves": "Asian finance gateway"},
            "Russia":                   {"action_cost":  90_000_000, "income": 5_000_000, "days": 20, "reserves": "Sberbank empire"},
        },
    },
}

ACTIONS = {
    "Bomb": {
        "cost_mult":     1.0,
        "income_mult":   1.0,
        "days_mult":     1.0,
        "transgression": 20,
        "opinion":       20,
        "happiness":      5,
        "color":       "#ff2222",
        "past":        "Bombed",
        "tag":         "[BOMB]",
    },
    "Stage a Coup": {
        "cost_mult":     0.35,
        "income_mult":   0.6,
        "days_mult":     0.7,
        "transgression": 10,
        "opinion":        8,
        "happiness":      3,
        "color":       "#aa44ff",
        "past":        "Staged coup in",
        "tag":         "[COUP]",
    },
}

CLR_OCEAN    = "#0a1628"
CLR_LAND     = "#1a2a1a"
CLR_EDGE     = "#2e3e2e"
CLR_BOMBED   = "#3d0808"
CLR_BOMBED_E = "#ff3333"
CLR_COUP     = "#1a0a2e"
CLR_COUP_E   = "#aa44ff"
CLR_HOME     = "#003366"
CLR_HOME_E   = "#0066cc"


def _load_world():
    import geopandas as gpd
    if os.path.exists(_CACHE_FILE):
        return gpd.read_file(_CACHE_FILE)
    world = gpd.read_file(_SHAPEFILE_URL)
    world[["NAME", "geometry"]].to_file(_CACHE_FILE, driver="GPKG")
    return world


class WorldMapMixin:

    # =========================================================
    # OPEN MAP WINDOW
    # =========================================================

    def open_world_map(self):
        win = tk.Toplevel(self.root)
        win.title("World Map — Resource Operations")
        win.configure(bg=CLR_OCEAN)
        win.geometry("1020x620")
        win.resizable(True, True)

        header = tk.Frame(win, bg=CLR_OCEAN)
        header.pack(fill="x", padx=16, pady=(10, 0))
        tk.Label(header, text="WORLD RESOURCE OPERATIONS",
                 font=("Impact", 20), bg=CLR_OCEAN, fg="#ffaa00").pack(side="left")

        alliance_text = f"Alliance: {self.alliance} ({self.alliance_days}d)" if self.alliance else "Alliance: None"
        tk.Label(header, text=alliance_text,
                 font=("Arial", 9), bg=CLR_OCEAN, fg="#4499ff").pack(side="right", padx=10)

        sel = tk.Frame(header, bg=CLR_OCEAN)
        sel.pack(side="right")
        tk.Label(sel, text="Resource:", font=("Arial", 10),
                 bg=CLR_OCEAN, fg="#888").pack(side="left", padx=(0, 6))
        self._resource_var = tk.StringVar(value="Oil")
        menu = tk.OptionMenu(sel, self._resource_var, *RESOURCE_DATA.keys())
        menu.config(bg="#1e2130", fg="white", activebackground="#2e3140",
                    relief="flat", font=("Arial", 10), width=12, highlightthickness=0)
        menu["menu"].config(bg="#1e2130", fg="white",
                            activebackground="#2e3140", font=("Arial", 10))
        menu.pack(side="left")
        tk.Label(header, text="Bomb or stage a coup to seize resources.",
                 font=("Arial", 9), bg=CLR_OCEAN, fg="#555").pack(side="left", padx=14)

        loading = tk.Label(win, text="Loading map data...",
                           font=("Arial", 13), bg=CLR_OCEAN, fg="#888")
        loading.pack(expand=True)

        def _build():
            try:
                world = _load_world()
            except Exception as e:
                self.root.after(0, lambda: loading.config(
                    text=f"Map load failed: {e}", fg="#ff4444"))
                return
            self.root.after(0, lambda: _embed(world))

        def _embed(world):
            loading.destroy()
            fig, ax = plt.subplots(1, 1, figsize=(13, 6.2), facecolor=CLR_OCEAN)
            ax.set_facecolor(CLR_OCEAN)
            ax.set_axis_off()
            ax.set_xlim(-180, 180)
            ax.set_ylim(-90, 90)

            self._map_world = world
            self._render_map(ax, self._resource_var.get())

            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(4, 0))
            self._map_canvas = canvas

            self._map_legend_frame = tk.Frame(win, bg=CLR_OCEAN)
            self._map_legend_frame.pack(pady=4)
            self._rebuild_legend(self._resource_var.get())

            def _on_res_change(*_):
                res = self._resource_var.get()
                self._render_map(ax, res)
                canvas.draw()
                self._rebuild_legend(res)

            self._resource_var.trace_add("write", _on_res_change)
            fig.canvas.mpl_connect(
                "button_press_event",
                lambda e: self._on_map_click(e, world, ax, canvas))
            win.protocol("WM_DELETE_WINDOW",
                         lambda: [plt.close(fig), win.destroy()])

        threading.Thread(target=_build, daemon=True).start()

    # =========================================================
    # LEGEND
    # =========================================================

    def _rebuild_legend(self, resource):
        leg = self._map_legend_frame
        for w in leg.winfo_children():
            w.destroy()
        res_clr = RESOURCE_DATA[resource]["clr"][0]
        for color, label in [
            (res_clr,    f"{resource} reserves"),
            (CLR_BOMBED, "Bombed"),
            (CLR_COUP,   "Coup'd"),
            (CLR_HOME,   "Your country"),
            (CLR_LAND,   "No resource"),
        ]:
            dot = tk.Canvas(leg, width=12, height=12, bg=CLR_OCEAN, highlightthickness=0)
            dot.create_oval(1, 1, 11, 11, fill=color, outline="#555")
            dot.pack(side="left", padx=(10, 3))
            tk.Label(leg, text=label, font=("Arial", 8),
                     bg=CLR_OCEAN, fg="#888").pack(side="left", padx=(0, 14))
        # Rival legend entries
        for rival_name, rival in getattr(self, "rivals", {}).items():
            dot = tk.Canvas(leg, width=12, height=12, bg=CLR_OCEAN, highlightthickness=0)
            dot.create_oval(1, 1, 11, 11, fill=rival["color"], outline="#555")
            dot.pack(side="left", padx=(10, 3))
            tk.Label(leg, text=rival_name, font=("Arial", 8),
                     bg=CLR_OCEAN, fg=rival["color"]).pack(side="left", padx=(0, 14))

    # =========================================================
    # RENDER MAP
    # =========================================================

    def _render_map(self, ax, resource):
        ax.cla()
        ax.set_facecolor(CLR_OCEAN)
        ax.set_axis_off()
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)

        world    = self._map_world
        res_ctrs = RESOURCE_DATA[resource]["countries"]
        fill_clr, edge_clr = RESOURCE_DATA[resource]["clr"]

        home         = getattr(self, "country", "")
        action_taken = getattr(self, "action_taken", {})
        bombed_names = {c for c in self.bombed_countries
                        if action_taken.get(c, "Bomb") == "Bomb"}
        coup_names   = {c for c in self.bombed_countries
                        if action_taken.get(c) == "Stage a Coup"}

        home_mask     = world["NAME"] == home
        occupied_mask = world["NAME"].isin(self.bombed_countries)
        res_mask      = world["NAME"].isin(res_ctrs) & ~occupied_mask & ~home_mask
        other_mask    = ~world["NAME"].isin(res_ctrs) & ~occupied_mask & ~home_mask
        bombed_mask   = world["NAME"].isin(bombed_names)
        coup_mask     = world["NAME"].isin(coup_names)

        for df, clr, edge, lw in [
            (world[other_mask],  CLR_LAND,   CLR_EDGE,    0.35),
            (world[res_mask],    fill_clr,   edge_clr,    0.7),
            (world[bombed_mask], CLR_BOMBED, CLR_BOMBED_E, 0.8),
            (world[coup_mask],   CLR_COUP,   CLR_COUP_E,  0.8),
            (world[home_mask],   CLR_HOME,   CLR_HOME_E,  1.0),
        ]:
            if not df.empty:
                df.plot(ax=ax, color=clr, edgecolor=edge, linewidth=lw, aspect=None)

        for _, row in world[res_mask].iterrows():
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.plot(cx, cy, marker="o", color=edge_clr, markersize=5, zorder=5)
            ax.text(cx, cy - 2.5, row["NAME"], color=edge_clr, fontsize=5.5,
                    ha="center", va="top", zorder=6,
                    path_effects=[pe.withStroke(linewidth=1.5, foreground=CLR_OCEAN)])

        for _, row in world[occupied_mask].iterrows():
            name = row["NAME"]
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            is_coup = name in coup_names
            mc = CLR_COUP_E if is_coup else "#ff3333"
            ax.plot(cx, cy, marker="D" if is_coup else "*", color=mc,
                    markersize=7, zorder=5)
            suffix = " (COUP)" if is_coup else " (BOMBED)"
            ax.text(cx, cy - 3, name + suffix, color=mc, fontsize=5.5,
                    ha="center", va="top", zorder=6,
                    path_effects=[pe.withStroke(linewidth=1.5, foreground=CLR_OCEAN)])

        for _, row in world[home_mask].iterrows():
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.plot(cx, cy, marker="H", color=CLR_HOME_E, markersize=7, zorder=5)
            ax.text(cx, cy - 3, row["NAME"] + " (YOU)", color="#5599ff",
                    fontsize=5.5, ha="center", va="top", zorder=6,
                    path_effects=[pe.withStroke(linewidth=1.5, foreground=CLR_OCEAN)])

    # =========================================================
    # CLICK HANDLER
    # =========================================================

    def _on_map_click(self, event, world, ax, canvas):
        if event.inaxes != ax or event.xdata is None:
            return
        pt = shapely.geometry.Point(event.xdata, event.ydata)
        for _, row in world.iterrows():
            if row.geometry and row.geometry.contains(pt):
                name = row["NAME"]
                if name == getattr(self, "country", ""):
                    self._show_homeland_popup(name)
                    return
                if name in self.bombed_countries:
                    self._show_occupied_popup(name)
                    return
                res = self._resource_var.get()
                if name in RESOURCE_DATA[res]["countries"]:
                    self._show_action_popup(
                        name, RESOURCE_DATA[res]["countries"][name],
                        res, ax, canvas)
                return

    # =========================================================
    # HOMELAND POPUP
    # =========================================================

    def _show_homeland_popup(self, name):
        popup = tk.Toplevel(self.root)
        popup.title(name)
        popup.configure(bg="#0e1117")
        popup.geometry("380x180")
        popup.grab_set()
        popup.resizable(False, False)
        tk.Label(popup, text=f"Home: {name}",
                 font=("Arial", 14, "bold"), bg="#0e1117", fg="#5599ff").pack(pady=(20, 6))
        tk.Label(popup, text="This is your home country.\nYou can't attack where you're from.",
                 font=("Arial", 10), bg="#0e1117", fg="#aaaaaa", justify="center").pack(pady=4)
        tk.Button(popup, text="OK", bg="#1e2130", fg="white",
                  relief="flat", padx=20, pady=6,
                  command=popup.destroy).pack(pady=12)

    # =========================================================
    # OCCUPIED POPUP
    # =========================================================

    def _show_occupied_popup(self, name):
        popup = tk.Toplevel(self.root)
        popup.title(name)
        popup.configure(bg="#0e1117")
        popup.geometry("420x240")
        popup.grab_set()
        popup.resizable(False, False)

        action_taken = getattr(self, "action_taken", {})
        action   = action_taken.get(name, "Bomb")
        op       = next((o for o in self.oil_operations if o["country"] == name), None)
        income   = op["income"]    if op else 0
        days_rem = op["days_left"] if op else 0
        resource = op.get("resource", "?") if op else "?"
        status   = "Bombed" if action == "Bomb" else "Coup in progress"

        tk.Label(popup, text=name,
                 font=("Arial", 14, "bold"), bg="#0e1117", fg="#ffaa00").pack(pady=(18, 6))
        tk.Label(popup, text=f"Status: {status}  |  Resource: {resource}",
                 font=("Arial", 10), bg="#0e1117", fg="#888").pack()
        tk.Label(popup,
                 text=f"Income: ${income:,}/day\n{days_rem} day(s) remaining",
                 font=("Arial", 11, "bold"), bg="#0e1117", fg="#00ff90").pack(pady=8)
        tk.Button(popup, text="Close", bg="#1e2130", fg="white",
                  relief="flat", padx=20, pady=6,
                  command=popup.destroy).pack(pady=8)

    # =========================================================
    # ACTION POPUP  (Bomb vs Coup)
    # =========================================================

    def _show_action_popup(self, name, info, resource, ax, canvas):
        popup = tk.Toplevel(self.root)
        popup.title(name)
        popup.configure(bg="#0e1117")
        popup.geometry("500x400")
        popup.grab_set()
        popup.resizable(False, False)

        tk.Label(popup, text=name,
                 font=("Arial", 14, "bold"), bg="#0e1117", fg="#ffaa00").pack(pady=(16, 2))
        tk.Label(popup, text=f"{resource} — {info['reserves']}",
                 font=("Arial", 9, "italic"), bg="#0e1117", fg="#666").pack()

        # Check if rival controls this country
        rival = self.is_rival_controlled(resource, name)
        if rival:
            rival_color = self.rivals[rival]["color"]
            tk.Label(popup, text=f"Controlled by rival: {rival}",
                     font=("Arial", 9, "bold"), bg="#0e1117", fg=rival_color).pack()
            tk.Button(popup, text=f"Buy Out {rival} (2x cost)",
                      font=("Arial", 9), bg="#2a1a3a", fg=rival_color,
                      relief="flat", padx=10, pady=4,
                      command=lambda: [self.buyout_rival(resource, name, rival), popup.destroy()]
                      ).pack(pady=4)
            tk.Button(popup, text="Cancel", bg="#1e2130", fg="#aaaaaa",
                      relief="flat", padx=16, pady=5,
                      command=popup.destroy).pack(pady=4)
            return

        for label, val in [
            ("Base Income",   f"${info['income']:,}/day"),
            ("Duration",      f"{info['days']} days"),
            ("Total Revenue", f"${info['income'] * info['days']:,}"),
        ]:
            r = tk.Frame(popup, bg="#0e1117")
            r.pack(fill="x", padx=60, pady=1)
            tk.Label(r, text=label + ":", font=("Arial", 9),
                     bg="#0e1117", fg="#666", width=14, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=("Arial", 9, "bold"),
                     bg="#0e1117", fg="white").pack(side="left")

        tk.Frame(popup, bg="#333", height=1).pack(fill="x", padx=24, pady=10)

        btn_frame = tk.Frame(popup, bg="#0e1117")
        btn_frame.pack()

        for act_name, act in ACTIONS.items():
            cost   = int(info["action_cost"] * act["cost_mult"])
            income = int(info["income"]      * act["income_mult"])
            days   = int(info["days"]        * act["days_mult"])
            can    = self.money >= cost

            col = tk.Frame(btn_frame, bg="#151820", padx=14, pady=10)
            col.pack(side="left", padx=10)

            tk.Label(col, text=act_name, font=("Arial", 11, "bold"),
                     bg="#151820", fg=act["color"]).pack()
            tk.Label(col,
                     text=f"Cost:          ${cost:,}\n"
                          f"Income:        ${income:,}/day\n"
                          f"Duration:      {days} days\n"
                          f"Transgression: +{act['transgression']}\n"
                          f"Opinion hit:   -{act['opinion']}",
                     font=("Consolas", 8), bg="#151820", fg="#888",
                     justify="left").pack(pady=6)
            lbl = "Execute" if can else "Not enough money"
            tk.Button(col, text=lbl,
                      font=("Arial", 9, "bold"),
                      bg=act["color"] if can else "#2a1a1a",
                      fg="white", relief="flat", padx=10, pady=5,
                      state="normal" if can else "disabled",
                      command=lambda a=act_name: self._execute_action(
                          name, info, resource, a, popup, ax, canvas)
                      ).pack()

        tk.Button(popup, text="Cancel", bg="#1e2130", fg="#aaaaaa",
                  relief="flat", padx=16, pady=5,
                  command=popup.destroy).pack(pady=(12, 4))

    # =========================================================
    # EXECUTE ACTION
    # =========================================================

    def _execute_action(self, name, info, resource, action_name, popup, ax, canvas):
        act    = ACTIONS[action_name]
        discount = self.get_alliance_discount(name)
        cost   = int(info["action_cost"] * act["cost_mult"] * discount)
        income = int(info["income"]      * act["income_mult"])
        days   = int(info["days"]        * act["days_mult"])

        self.money -= cost
        self.market.money = self.money
        self.bombed_countries.add(name)
        if not hasattr(self, "action_taken"):
            self.action_taken = {}
        self.action_taken[name] = action_name

        self.oil_operations.append({
            "country":  name,
            "income":   income,
            "days_left": days,
            "resource": resource,
            "action":   action_name,
        })

        self.add_transgression(act["transgression"], act["opinion"])
        self.add_happiness(act["happiness"])
        self.update_status()
        self.log_event(
            f"{act['tag']} {act['past']} {name}!  "
            f"Cost: ${cost:,}  |  Income: ${income:,}/day x {days} days"
        )

        # Chance of sanction for bombing (not coup)
        if action_name == "Bomb":
            import random
            if random.random() < 0.3:
                self.apply_sanction(name, days=random.randint(5, 15))

        # Multiplayer: check if bombed country belongs to another player → war
        if action_name == "Bomb" and getattr(self, "is_multiplayer", False):
            for rival_name, rival in self.rivals.items():
                if rival.get("country", "") == name and not rival.get("disconnected"):
                    self._declare_war_on_player(rival_name, name)
                    break

        # Single player: AI rival retaliates immediately if you bombed their territory
        if action_name == "Bomb" and not getattr(self, "is_multiplayer", False):
            rival_name = self.is_rival_controlled(resource, name)
            if rival_name and rival_name in self.rivals:
                rival = self.rivals[rival_name]
                self.root.after(1500, lambda rn=rival_name, rv=rival:
                                self._rival_retaliate(rn, rv, name, resource))

        mkt_mult = 1.06 if action_name == "Bomb" else 1.04
        for cat in RESOURCE_DATA[resource]["market"]:
            self.apply_market_effect([cat], mkt_mult, 4, f"{action_name}: {name}")
        if action_name == "Bomb":
            self.apply_market_effect(["Defense"], 1.04, 3, f"Military op: {name}")

        popup.destroy()
        self._render_map(ax, self._resource_var.get())
        canvas.draw()

    # =========================================================
    # DAILY RESOURCE INCOME  (called from game.py main_loop)
    # =========================================================

    def process_resource_income(self):
        if not self.oil_operations:
            return
        if getattr(self, "blockaded_days", 0) > 0:
            self.log_event("⚓ Blockade active — resource income seized today.")
            # Still tick operations so they expire normally
            for op in self.oil_operations:
                op["days_left"] -= 1
            self.oil_operations = [o for o in self.oil_operations if o["days_left"] > 0]
            return
        total = sum(op["income"] for op in self.oil_operations)
        for op in self.oil_operations:
            op["days_left"] -= 1
        for op in [o for o in self.oil_operations if o["days_left"] <= 0]:
            resource = op.get("resource", "Oil")
            tag      = ACTIONS.get(op.get("action", "Bomb"), {}).get("tag", "")
            self.log_event(f"{tag} {resource} operation in {op['country']} has ended.")
            self.bombed_countries.discard(op["country"])
            getattr(self, "action_taken", {}).pop(op["country"], None)
            for cat in RESOURCE_DATA.get(resource, {}).get("market", []):
                self.apply_market_effect([cat], 0.97, 2,
                                         f"Operation ends: {op['country']}")
        self.oil_operations = [o for o in self.oil_operations if o["days_left"] > 0]
        if total:
            self.money += total
            self.market.money = self.money
            self.log_event(f"Resource income: +${total:,}/day")
