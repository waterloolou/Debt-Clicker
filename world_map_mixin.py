"""world_map_mixin.py
Interactive world map using real country geometries (Natural Earth 110m).
Oil-producing countries can be bombed for daily income.
"""

import tkinter as tk
import os
import threading
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch
import shapely.geometry

_SHAPEFILE_URL = (
    "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
)
_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "world_countries.gpkg"
)

# ---------------------------------------------------------------------------
# Oil country data  — keys must match Natural Earth NAME field exactly
# ---------------------------------------------------------------------------
OIL_COUNTRIES = {
    "Kuwait":                    {"bomb_cost":  5_000_000, "oil_income":   500_000, "oil_days": 15, "reserves": "102 billion barrels"},
    "United Arab Emirates":      {"bomb_cost":  8_000_000, "oil_income":   600_000, "oil_days": 15, "reserves":  "97 billion barrels"},
    "Qatar":                     {"bomb_cost":  8_000_000, "oil_income":   700_000, "oil_days": 20, "reserves":  "25 billion barrels"},
    "Angola":                    {"bomb_cost":  8_000_000, "oil_income":   600_000, "oil_days": 15, "reserves":   "8 billion barrels"},
    "Libya":                     {"bomb_cost": 10_000_000, "oil_income":   800_000, "oil_days": 15, "reserves":  "48 billion barrels"},
    "Algeria":                   {"bomb_cost": 12_000_000, "oil_income":   800_000, "oil_days": 15, "reserves":  "12 billion barrels"},
    "Nigeria":                   {"bomb_cost": 15_000_000, "oil_income": 1_000_000, "oil_days": 20, "reserves":  "37 billion barrels"},
    "Norway":                    {"bomb_cost": 28_000_000, "oil_income": 1_500_000, "oil_days": 15, "reserves":   "8 billion barrels"},
    "Kazakhstan":                {"bomb_cost": 18_000_000, "oil_income": 1_200_000, "oil_days": 20, "reserves":  "30 billion barrels"},
    "Mexico":                    {"bomb_cost": 22_000_000, "oil_income": 1_500_000, "oil_days": 20, "reserves": "5.8 billion barrels"},
    "Brazil":                    {"bomb_cost": 20_000_000, "oil_income": 1_300_000, "oil_days": 20, "reserves":  "12 billion barrels"},
    "Venezuela":                 {"bomb_cost": 25_000_000, "oil_income": 2_000_000, "oil_days": 20, "reserves": "304 billion barrels"},
    "Iraq":                      {"bomb_cost": 30_000_000, "oil_income": 2_000_000, "oil_days": 25, "reserves": "145 billion barrels"},
    "Iran":                      {"bomb_cost": 35_000_000, "oil_income": 2_500_000, "oil_days": 25, "reserves": "157 billion barrels"},
    "Canada":                    {"bomb_cost": 40_000_000, "oil_income": 2_500_000, "oil_days": 25, "reserves": "170 billion barrels"},
    "Saudi Arabia":              {"bomb_cost": 60_000_000, "oil_income": 4_000_000, "oil_days": 30, "reserves": "267 billion barrels"},
    "Russia":                    {"bomb_cost":100_000_000, "oil_income": 6_000_000, "oil_days": 20, "reserves":  "80 billion barrels"},
    "United States of America":  {"bomb_cost":200_000_000, "oil_income":10_000_000, "oil_days": 30, "reserves": "297 billion barrels"},
}

# Colours
CLR_OCEAN   = "#0a1628"
CLR_LAND    = "#1a2a1a"
CLR_EDGE    = "#2e3e2e"
CLR_OIL     = "#3d2600"
CLR_OIL_E   = "#cc8800"
CLR_BOMBED  = "#3d0808"
CLR_BOMBED_E= "#ff3333"


def _load_world():
    """Load (and cache) the Natural Earth 110m countries GeoDataFrame."""
    import geopandas as gpd
    if os.path.exists(_CACHE_FILE):
        return gpd.read_file(_CACHE_FILE)
    world = gpd.read_file(_SHAPEFILE_URL)
    world[["NAME", "geometry"]].to_file(_CACHE_FILE, driver="GPKG")
    return world


class WorldMapMixin:
    """Interactive world map with oil-bombing mechanic."""

    # =========================================================
    # OPEN MAP WINDOW
    # =========================================================

    def open_world_map(self):
        win = tk.Toplevel(self.root)
        win.title("World Map — Oil Operations")
        win.configure(bg=CLR_OCEAN)
        win.geometry("1020x580")
        win.resizable(True, True)

        header = tk.Frame(win, bg=CLR_OCEAN)
        header.pack(fill="x", padx=16, pady=(10, 0))
        tk.Label(header, text="🌍  WORLD OIL OPERATIONS",
                 font=("Impact", 20), bg=CLR_OCEAN, fg="#ffaa00").pack(side="left")
        tk.Label(header,
                 text="Click an oil-rich country to bomb it and seize its reserves.",
                 font=("Arial", 9), bg=CLR_OCEAN, fg="#666666").pack(side="left", padx=16)

        # Loading placeholder
        loading = tk.Label(win, text="Loading map data...",
                           font=("Arial", 13), bg=CLR_OCEAN, fg="#888888")
        loading.pack(expand=True)

        def _build(w=win, l=loading):
            try:
                world = _load_world()
            except Exception as e:
                self.root.after(0, lambda: l.config(
                    text=f"Map load failed: {e}", fg="#ff4444"))
                return
            self.root.after(0, lambda: _embed(world, w, l))

        def _embed(world, w, l):
            l.destroy()
            fig, ax = plt.subplots(1, 1, figsize=(13, 6.2),
                                   facecolor=CLR_OCEAN)
            ax.set_facecolor(CLR_OCEAN)
            ax.set_axis_off()
            ax.set_xlim(-180, 180)
            ax.set_ylim(-90, 90)

            self._map_world = world
            self._render_map(ax)

            canvas = FigureCanvasTkAgg(fig, master=w)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True,
                                        padx=8, pady=(4, 0))

            # Legend
            leg = tk.Frame(w, bg=CLR_OCEAN)
            leg.pack(pady=4)
            for color, label in [(CLR_OIL, "Oil reserves"),
                                  (CLR_BOMBED, "Bombed / occupied"),
                                  (CLR_LAND, "No oil")]:
                dot = tk.Canvas(leg, width=12, height=12,
                                bg=CLR_OCEAN, highlightthickness=0)
                dot.create_oval(1, 1, 11, 11, fill=color, outline="#555")
                dot.pack(side="left", padx=(10, 3))
                tk.Label(leg, text=label, font=("Arial", 8),
                         bg=CLR_OCEAN, fg="#888888").pack(side="left", padx=(0, 14))

            self._map_fig    = fig
            self._map_ax     = ax
            self._map_canvas = canvas

            fig.canvas.mpl_connect(
                "button_press_event",
                lambda e: self._on_map_click(e, world, fig, ax, canvas, w)
            )
            w.protocol("WM_DELETE_WINDOW",
                       lambda: [plt.close(fig), w.destroy()])

        threading.Thread(target=_build, daemon=True).start()

    # =========================================================
    # RENDER ALL COUNTRIES
    # =========================================================

    def _render_map(self, ax):
        ax.cla()
        ax.set_facecolor(CLR_OCEAN)
        ax.set_axis_off()
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)

        world = self._map_world

        bombed_mask = world["NAME"].isin(self.bombed_countries)
        oil_mask    = world["NAME"].isin(OIL_COUNTRIES) & ~bombed_mask
        other_mask  = ~world["NAME"].isin(OIL_COUNTRIES) & ~bombed_mask

        for df, color, edge, lw in [
            (world[other_mask],  CLR_LAND,   CLR_EDGE,     0.35),
            (world[oil_mask],    CLR_OIL,    CLR_OIL_E,    0.7),
            (world[bombed_mask], CLR_BOMBED, CLR_BOMBED_E, 0.8),
        ]:
            if not df.empty:
                df.plot(ax=ax, color=color, edgecolor=edge, linewidth=lw, aspect=None)

        # Labels + markers
        for _, row in world[oil_mask | bombed_mask].iterrows():
            name   = row["NAME"]
            cx     = row.geometry.centroid.x
            cy     = row.geometry.centroid.y
            bombed = name in self.bombed_countries

            if bombed:
                ax.plot(cx, cy, marker="*", color="#ff3333",
                        markersize=7, zorder=5)
                ax.text(cx, cy - 3, name, color="#ff5555",
                        fontsize=5.5, ha="center", va="top", zorder=6,
                        path_effects=[pe.withStroke(linewidth=1.5,
                                                     foreground=CLR_OCEAN)])
            else:
                ax.plot(cx, cy, marker="o", color="#ffaa00",
                        markersize=5, zorder=5)
                ax.text(cx, cy - 2.5, name, color="#ffcc55",
                        fontsize=5.5, ha="center", va="top", zorder=6,
                        path_effects=[pe.withStroke(linewidth=1.5,
                                                     foreground=CLR_OCEAN)])

    # =========================================================
    # CLICK → FIND COUNTRY
    # =========================================================

    def _on_map_click(self, event, world, fig, ax, canvas, win):
        if event.inaxes != ax or event.xdata is None:
            return
        pt = shapely.geometry.Point(event.xdata, event.ydata)
        for _, row in world.iterrows():
            if row.geometry and row.geometry.contains(pt):
                name = row["NAME"]
                if name in OIL_COUNTRIES:
                    self._show_bomb_popup(name, OIL_COUNTRIES[name],
                                          fig, ax, canvas)
                return

    # =========================================================
    # BOMB POPUP
    # =========================================================

    def _show_bomb_popup(self, name, info, fig, ax, canvas):
        popup = tk.Toplevel(self.root)
        popup.title(name)
        popup.configure(bg="#0e1117")
        popup.geometry("420x310")
        popup.grab_set()
        popup.resizable(False, False)

        bombed = name in self.bombed_countries

        tk.Label(popup,
                 text=f"{'💥' if bombed else '🛢️'}  {name}",
                 font=("Arial", 14, "bold"),
                 bg="#0e1117", fg="#ffaa00").pack(pady=(18, 6))

        if bombed:
            remaining = next((op["days_left"] for op in self.oil_operations
                              if op["country"] == name), 0)
            tk.Label(popup, text="Already bombed — currently occupied.",
                     font=("Arial", 10), bg="#0e1117", fg="#ff4444").pack()
            tk.Label(popup,
                     text=f"Oil income: ${info['oil_income']:,}/day\n"
                          f"{remaining} day(s) remaining",
                     font=("Arial", 11, "bold"),
                     bg="#0e1117", fg="#00ff90").pack(pady=8)
            tk.Button(popup, text="Close", bg="#1e2130", fg="white",
                      relief="flat", padx=20, pady=6,
                      command=popup.destroy).pack(pady=10)
        else:
            rows = [
                ("Oil Reserves",  info["reserves"]),
                ("Bombing Cost",  f"${info['bomb_cost']:,}"),
                ("Daily Income",  f"${info['oil_income']:,}/day"),
                ("Duration",      f"{info['oil_days']} days"),
                ("Total Revenue", f"${info['oil_income'] * info['oil_days']:,}"),
            ]
            for lbl, val in rows:
                row = tk.Frame(popup, bg="#0e1117")
                row.pack(fill="x", padx=36, pady=2)
                tk.Label(row, text=lbl + ":", font=("Arial", 9),
                         bg="#0e1117", fg="#666666",
                         width=14, anchor="w").pack(side="left")
                tk.Label(row, text=val, font=("Arial", 9, "bold"),
                         bg="#0e1117", fg="white").pack(side="left")

            can_afford = self.money >= info["bomb_cost"]
            tk.Button(popup,
                      text=f"💣  BOMB IT  (-${info['bomb_cost']:,})"
                           if can_afford else "Not enough money",
                      font=("Arial", 11, "bold"),
                      bg="#ff2222" if can_afford else "#3a1a1a",
                      fg="white", relief="flat",
                      padx=16, pady=8,
                      state="normal" if can_afford else "disabled",
                      command=lambda: self._bomb_country(
                          name, info, popup, fig, ax, canvas)
                      ).pack(pady=(14, 4))

            tk.Button(popup, text="Cancel",
                      bg="#1e2130", fg="#aaaaaa", relief="flat",
                      padx=16, pady=6,
                      command=popup.destroy).pack()

    # =========================================================
    # EXECUTE BOMBING
    # =========================================================

    def _bomb_country(self, name, info, popup, fig, ax, canvas):
        self.money -= info["bomb_cost"]
        self.market.money = self.money
        self.bombed_countries.add(name)
        self.oil_operations.append({
            "country":   name,
            "income":    info["oil_income"],
            "days_left": info["oil_days"],
        })
        self.update_status()
        self.log_event(
            f"💣 Bombed {name}!  "
            f"Cost: ${info['bomb_cost']:,}  |  "
            f"Income: ${info['oil_income']:,}/day × {info['oil_days']} days"
        )
        self.apply_market_effect(["Energy"],  1.06, 4, f"Oil seizure: {name}")
        self.apply_market_effect(["Defense"], 1.04, 3, f"Military op: {name}")
        popup.destroy()
        self._render_map(ax)
        canvas.draw()

    # =========================================================
    # DAILY OIL INCOME  (called from game.py main_loop)
    # =========================================================

    def process_oil_income(self):
        if not self.oil_operations:
            return
        total = sum(op["income"] for op in self.oil_operations)
        for op in self.oil_operations:
            op["days_left"] -= 1
        for op in [o for o in self.oil_operations if o["days_left"] <= 0]:
            self.log_event(f"🛢️ Oil wells in {op['country']} have run dry.")
            self.apply_market_effect(["Energy"], 0.97, 2,
                                     f"Oil ends: {op['country']}")
        self.oil_operations = [o for o in self.oil_operations if o["days_left"] > 0]
        if total:
            self.money += total
            self.market.money = self.money
            self.log_event(f"🛢️ Oil income: +${total:,}/day")
