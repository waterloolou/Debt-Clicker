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
CLR_ALLY     = "#002a1a"
CLR_ALLY_E   = "#00cc66"

# Crash multipliers applied to resource market category on seizure
RESOURCE_CRASH = {
    "Oil":         (["Energy"],                  0.88, 4),
    "Diamonds":    (["Finance", "Entertainment"], 0.90, 3),
    "Minerals":    (["Automotive", "Technology"], 0.87, 4),
    "Agriculture": (["Retail"],                  0.89, 3),
    "Technology":  (["Technology", "AI"],         0.86, 5),
    "Finance":     (["Finance"],                  0.85, 5),
}


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
        if not getattr(self, "is_president", False):
            self.log_event(
                "Access denied. You must be President to use the World Map. "
                "Win an election first via the Elections tab.")
            return
        win = tk.Toplevel(self.root)
        win.title("World Map — Resource Operations")
        win.configure(bg=CLR_OCEAN)
        win.geometry("1020x620")
        win.resizable(True, True)

        header = tk.Frame(win, bg=CLR_OCEAN)
        header.pack(fill="x", padx=16, pady=(10, 0))
        tk.Label(header, text="WORLD MAP",
                 font=("Impact", 20), bg=CLR_OCEAN, fg="#ffaa00").pack(side="left")
        alliance_text = f"Alliance: {self.alliance} ({self.alliance_days}d)" if self.alliance else "Alliance: None"
        tk.Label(header, text=alliance_text,
                 font=("Arial", 9), bg=CLR_OCEAN, fg="#4499ff").pack(side="right", padx=10)
        tk.Label(header,
                 text="Click any country to interact  •  Scroll to zoom  •  Right-drag to pan",
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
            self._render_map(ax)

            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(4, 0))
            self._map_canvas = canvas

            self._map_legend_frame = tk.Frame(win, bg=CLR_OCEAN)
            self._map_legend_frame.pack(pady=4)
            self._rebuild_legend()

            # ── Zoom (mouse scroll) ───────────────────────────────────
            def _on_scroll(event, _ax=ax, _cv=canvas):
                if event.inaxes != _ax or event.xdata is None:
                    return
                factor = 0.70 if event.button == "up" else 1.40
                xl, yl = _ax.get_xlim(), _ax.get_ylim()
                cx, cy = event.xdata, event.ydata
                _ax.set_xlim([cx + (x - cx) * factor for x in xl])
                _ax.set_ylim([cy + (y - cy) * factor for y in yl])
                _cv.draw_idle()

            # ── Pan (right-click drag) ────────────────────────────────
            _pan = {"x": None, "y": None}

            def _on_press(event, _ax=ax, _cv=canvas, _w=world):
                if event.button == 1:
                    self._on_map_click(event, _w, _ax, _cv)
                elif event.button == 3 and event.inaxes == _ax and event.xdata:
                    _pan["x"] = event.xdata
                    _pan["y"] = event.ydata

            def _on_motion(event, _ax=ax, _cv=canvas):
                if _pan["x"] is None or event.inaxes != _ax or event.xdata is None:
                    return
                dx = _pan["x"] - event.xdata
                dy = _pan["y"] - event.ydata
                _ax.set_xlim([x + dx for x in _ax.get_xlim()])
                _ax.set_ylim([y + dy for y in _ax.get_ylim()])
                _cv.draw_idle()

            def _on_release(event):
                if event.button == 3:
                    _pan["x"] = None
                    _pan["y"] = None

            fig.canvas.mpl_connect("scroll_event",         _on_scroll)
            fig.canvas.mpl_connect("button_press_event",   _on_press)
            fig.canvas.mpl_connect("motion_notify_event",  _on_motion)
            fig.canvas.mpl_connect("button_release_event", _on_release)
            win.protocol("WM_DELETE_WINDOW",
                         lambda: [plt.close(fig), win.destroy()])

            def _on_map_resize(e, _fig=fig, _cv=canvas):
                new_w = max(1, e.width  - 16)
                new_h = max(1, e.height - 80)
                _fig.set_size_inches(new_w / 96, new_h / 96, forward=True)
                _cv.draw_idle()
            win.bind("<Configure>", _on_map_resize)

        threading.Thread(target=_build, daemon=True).start()

    # =========================================================
    # LEGEND
    # =========================================================

    def _rebuild_legend(self):
        leg = self._map_legend_frame
        for w in leg.winfo_children():
            w.destroy()
        # One entry per resource type
        for res_name, res_data in RESOURCE_DATA.items():
            fill_clr, edge_clr = res_data["clr"]
            dot = tk.Canvas(leg, width=12, height=12, bg=CLR_OCEAN, highlightthickness=0)
            dot.create_oval(1, 1, 11, 11, fill=fill_clr, outline=edge_clr)
            dot.pack(side="left", padx=(8, 3))
            tk.Label(leg, text=res_name, font=("Arial", 8),
                     bg=CLR_OCEAN, fg=edge_clr).pack(side="left", padx=(0, 10))
        # Special states
        ally_label = f"Ally ({self.alliance})" if self.alliance else "Ally"
        for color, label in [
            (CLR_BOMBED, "Bombed"),
            (CLR_COUP,   "Coup'd"),
            (CLR_HOME,   "You"),
            (CLR_ALLY,   ally_label),
            (CLR_LAND,   "No resources"),
        ]:
            dot = tk.Canvas(leg, width=12, height=12, bg=CLR_OCEAN, highlightthickness=0)
            dot.create_oval(1, 1, 11, 11, fill=color, outline="#555")
            dot.pack(side="left", padx=(8, 3))
            tk.Label(leg, text=label, font=("Arial", 8),
                     bg=CLR_OCEAN, fg="#888").pack(side="left", padx=(0, 10))
        for rival_name, rival in getattr(self, "rivals", {}).items():
            dot = tk.Canvas(leg, width=12, height=12, bg=CLR_OCEAN, highlightthickness=0)
            dot.create_oval(1, 1, 11, 11, fill=rival["color"], outline="#555")
            dot.pack(side="left", padx=(8, 3))
            tk.Label(leg, text=rival_name, font=("Arial", 8),
                     bg=CLR_OCEAN, fg=rival["color"]).pack(side="left", padx=(0, 10))

    # =========================================================
    # RENDER MAP
    # =========================================================

    def _render_map(self, ax):
        # Preserve current zoom/pan before clearing
        prev_xl = ax.get_xlim()
        prev_yl = ax.get_ylim()
        ax.cla()
        ax.set_facecolor(CLR_OCEAN)
        ax.set_axis_off()
        # Restore zoom (default axes give (0,1) before first draw)
        if prev_xl == (0.0, 1.0):
            ax.set_xlim(-180, 180)
            ax.set_ylim(-90, 90)
        else:
            ax.set_xlim(prev_xl)
            ax.set_ylim(prev_yl)

        world        = self._map_world
        home         = getattr(self, "country", "")
        action_taken = getattr(self, "action_taken", {})
        bombed_names = {c for c in self.bombed_countries
                        if action_taken.get(c, "Bomb") == "Bomb"}
        coup_names   = {c for c in self.bombed_countries
                        if action_taken.get(c) == "Stage a Coup"}
        ally_countries = set()
        if self.alliance:
            ally_countries = self._ALLIANCE_DATA.get(
                self.alliance, {}).get("countries", set())

        home_mask     = world["NAME"] == home
        occupied_mask = world["NAME"].isin(self.bombed_countries)
        ally_mask     = world["NAME"].isin(ally_countries) & ~home_mask & ~occupied_mask
        bombed_mask   = world["NAME"].isin(bombed_names)
        coup_mask     = world["NAME"].isin(coup_names)

        # ── Color each country by its dominant resource (priority order) ──
        RESOURCE_PRIORITY = [
            "Finance", "Technology", "Oil", "Diamonds", "Minerals", "Agriculture"
        ]
        already_colored = set()
        for res_name in RESOURCE_PRIORITY:
            res_data  = RESOURCE_DATA[res_name]
            fill_clr, edge_clr = res_data["clr"]
            countries_here = (set(res_data["countries"].keys()) - already_colored)
            already_colored |= countries_here
            draw_mask = (world["NAME"].isin(countries_here)
                         & ~occupied_mask & ~home_mask & ~ally_mask)
            if not world[draw_mask].empty:
                world[draw_mask].plot(ax=ax, color=fill_clr, edgecolor=edge_clr,
                                      linewidth=0.55, aspect=None)

        # ── No-resource countries ─────────────────────────────────────
        no_res_mask = (~world["NAME"].isin(already_colored)
                       & ~occupied_mask & ~home_mask & ~ally_mask)
        if not world[no_res_mask].empty:
            world[no_res_mask].plot(ax=ax, color=CLR_LAND, edgecolor=CLR_EDGE,
                                    linewidth=0.3, aspect=None)

        # ── Special state overlays ────────────────────────────────────
        for df, clr, edge, lw in [
            (world[ally_mask],   CLR_ALLY,   CLR_ALLY_E,   0.9),
            (world[bombed_mask], CLR_BOMBED, CLR_BOMBED_E, 0.8),
            (world[coup_mask],   CLR_COUP,   CLR_COUP_E,   0.8),
            (world[home_mask],   CLR_HOME,   CLR_HOME_E,   1.0),
        ]:
            if not df.empty:
                df.plot(ax=ax, color=clr, edgecolor=edge, linewidth=lw, aspect=None)

        # ── Build lookup: country → (edge_color, suffix) for labels ──
        # Dominant resource edge color per country
        country_label_clr = {}
        for res_name in reversed(RESOURCE_PRIORITY):   # reverse so highest priority wins
            for cname in RESOURCE_DATA[res_name]["countries"]:
                country_label_clr[cname] = RESOURCE_DATA[res_name]["clr"][1]

        # ── Label ALL countries ───────────────────────────────────────
        for _, row in world.iterrows():
            cname = row["NAME"]
            if not row.geometry or row.geometry.is_empty:
                continue
            cx = row.geometry.centroid.x
            cy = row.geometry.centroid.y
            if cname == home:
                lclr, suffix = "#5599ff", " ★"
            elif cname in coup_names:
                lclr, suffix = CLR_COUP_E, " ✦"
            elif cname in bombed_names:
                lclr, suffix = "#ff4444", " ✦"
            elif cname in ally_countries:
                lclr, suffix = CLR_ALLY_E, " ♦"
            elif cname in country_label_clr:
                lclr, suffix = country_label_clr[cname], ""
            else:
                lclr, suffix = "#5a5a5a", ""
            ax.text(cx, cy, cname + suffix,
                    color=lclr, fontsize=4.2, ha="center", va="center",
                    zorder=6,
                    path_effects=[pe.withStroke(linewidth=1.0, foreground=CLR_OCEAN)])

        # ── Markers for special states ────────────────────────────────
        for _, row in world[occupied_mask].iterrows():
            cname = row["NAME"]
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            mc = CLR_COUP_E if cname in coup_names else "#ff4444"
            ax.plot(cx, cy, marker="D" if cname in coup_names else "*",
                    color=mc, markersize=6, zorder=7)

        for _, row in world[home_mask].iterrows():
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.plot(cx, cy, marker="H", color=CLR_HOME_E, markersize=7, zorder=7)

        for _, row in world[ally_mask].iterrows():
            cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
            ax.plot(cx, cy, marker="^", color=CLR_ALLY_E, markersize=3.5, zorder=7)

        # ── Rival territory markers ───────────────────────────────────
        for rival in getattr(self, "rivals", {}).values():
            all_controlled = set()
            for countries in rival.get("controls", {}).values():
                all_controlled |= set(countries)
            for cname in all_controlled:
                rmask = world["NAME"] == cname
                if not world[rmask].empty:
                    cx = world[rmask].iloc[0].geometry.centroid.x
                    cy = world[rmask].iloc[0].geometry.centroid.y
                    ax.plot(cx, cy, marker="s", color=rival["color"],
                            markersize=4.5, zorder=8, alpha=0.85)

    # =========================================================
    # CLICK HANDLER
    # =========================================================

    def _on_map_click(self, event, world, ax, canvas):
        if event.inaxes != ax or event.xdata is None:
            return
        pt = shapely.geometry.Point(event.xdata, event.ydata)
        for _, row in world.iterrows():
            if row.geometry and row.geometry.contains(pt):
                self._show_country_panel(row["NAME"], ax, canvas)
                return

    # =========================================================
    # COUNTRY PANEL  (universal — replaces homeland/occupied/action popups)
    # =========================================================

    def _show_country_panel(self, name, ax, canvas):
        """Comprehensive country info + action panel for any clicked country."""
        # Aggregate all resources this country has across all categories
        country_resources = [
            (res_name, res_data["countries"][name])
            for res_name, res_data in RESOURCE_DATA.items()
            if name in res_data["countries"]
        ]

        is_home      = name == getattr(self, "country", "")
        is_occupied  = name in self.bombed_countries
        action_taken = getattr(self, "action_taken", {})
        action_name  = action_taken.get(name, "Bomb")
        is_ally      = (bool(self.alliance) and
                        name in self._ALLIANCE_DATA.get(
                            self.alliance, {}).get("countries", set()))

        # Find rival controls per resource
        rival_controls = {}
        for res_name, _ in country_resources:
            rv = self.is_rival_controlled(res_name, name)
            if rv:
                rival_controls[res_name] = rv

        popup = tk.Toplevel(self.root)
        popup.title(name)
        popup.configure(bg="#0e1117")
        popup.geometry("560x520")
        popup.grab_set()
        popup.resizable(False, True)

        # ── Header ────────────────────────────────────────────────
        tk.Label(popup, text=name,
                 font=("Arial", 16, "bold"), bg="#0e1117", fg="#ffaa00").pack(pady=(16, 2))

        badge_row = tk.Frame(popup, bg="#0e1117")
        badge_row.pack(pady=(0, 4))
        if is_home:
            tk.Label(badge_row, text="🏠 YOUR HOME",
                     font=("Arial", 9, "bold"), bg="#003366",
                     fg="#5599ff", padx=8, pady=3).pack(side="left", padx=4)
        if is_ally:
            tk.Label(badge_row, text=f"🤝 ALLY — {self.alliance}",
                     font=("Arial", 9, "bold"), bg=CLR_ALLY,
                     fg=CLR_ALLY_E, padx=8, pady=3).pack(side="left", padx=4)
        if is_occupied:
            tag_color = CLR_COUP_E if action_name == "Stage a Coup" else CLR_BOMBED_E
            tag_text  = "COUP" if action_name == "Stage a Coup" else "BOMBED"
            tk.Label(badge_row, text=f"⚔ {tag_text} — ACTIVE OP",
                     font=("Arial", 9, "bold"), bg="#1a0808",
                     fg=tag_color, padx=8, pady=3).pack(side="left", padx=4)
        if name in self.sanctions:
            tk.Label(badge_row,
                     text=f"🚫 SANCTIONING YOU — {self.sanctions[name]}d left",
                     font=("Arial", 9, "bold"), bg="#2a0000",
                     fg="#ff4444", padx=8, pady=3).pack(side="left", padx=4)

        # Homeland — show info only, no actions
        if is_home:
            tk.Label(popup,
                     text="Your base of operations.\nNo operations can be performed here.",
                     font=("Arial", 10, "italic"), bg="#0e1117",
                     fg="#aaaaaa", justify="center").pack(pady=14)
            tk.Button(popup, text="Close", bg="#1e2130", fg="white",
                      relief="flat", padx=20, pady=6,
                      command=popup.destroy).pack(pady=6)
            return

        # ── Scrollable body ────────────────────────────────────────
        cont  = tk.Frame(popup, bg="#0e1117")
        cont.pack(fill="both", expand=True, padx=0, pady=(0, 8))
        sc    = tk.Canvas(cont, bg="#0e1117", highlightthickness=0)
        sb    = tk.Scrollbar(cont, orient="vertical", command=sc.yview)
        inner = tk.Frame(sc, bg="#0e1117")
        inner.bind("<Configure>",
                   lambda e: sc.configure(scrollregion=sc.bbox("all")))
        win_id = sc.create_window((0, 0), window=inner, anchor="nw")
        sc.configure(yscrollcommand=sb.set)
        sc.bind("<Configure>", lambda e: sc.itemconfig(win_id, width=e.width))
        sb.pack(side="right", fill="y")
        sc.pack(side="left", fill="both", expand=True)

        def _mw(e):
            try:
                sc.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except tk.TclError:
                pass
        sc.bind_all("<MouseWheel>", _mw)
        popup.bind("<Destroy>", lambda e: sc.unbind_all("<MouseWheel>"))

        # ── Active operation info ─────────────────────────────────
        if is_occupied:
            op = next((o for o in self.oil_operations if o["country"] == name), None)
            if op:
                clr  = CLR_COUP_E if action_name == "Stage a Coup" else CLR_BOMBED_E
                op_f = tk.Frame(inner, bg="#1a0a2e", padx=12, pady=10)
                op_f.pack(fill="x", padx=12, pady=(4, 0))
                tk.Label(op_f, text=f"ACTIVE OPERATION — {action_name.upper()}",
                         font=("Arial", 10, "bold"), bg="#1a0a2e", fg=clr).pack(anchor="w")
                tk.Label(op_f,
                         text=(f"Resource: {op.get('resource','?')}  |  "
                               f"${op['income']:,}/day  |  "
                               f"{op['days_left']} day(s) remaining"),
                         font=("Arial", 9), bg="#1a0a2e", fg="#aaaaaa").pack(anchor="w")

        # ── Resource operations ────────────────────────────────────
        if country_resources:
            tk.Label(inner, text="RESOURCE OPERATIONS",
                     font=("Impact", 13), bg="#0e1117", fg="#888888").pack(
                     anchor="w", padx=16, pady=(10, 2))

            for res_name, info in country_resources:
                res_clr = RESOURCE_DATA[res_name]["clr"][1]
                rv      = rival_controls.get(res_name)

                card = tk.Frame(inner, bg="#141920", padx=12, pady=10)
                card.pack(fill="x", padx=12, pady=3)
                tk.Frame(card, bg=res_clr, width=4).pack(
                    side="left", fill="y", padx=(0, 10))
                body = tk.Frame(card, bg="#141920")
                body.pack(side="left", fill="both", expand=True)

                tk.Label(body, text=res_name,
                         font=("Arial", 11, "bold"), bg="#141920",
                         fg=res_clr).pack(anchor="w")
                tk.Label(body, text=info["reserves"],
                         font=("Arial", 8, "italic"), bg="#141920",
                         fg="#666").pack(anchor="w")
                tk.Label(body,
                         text=(f"${info['income']:,}/day  ×  {info['days']} days"
                               f"  =  ${info['income'] * info['days']:,} total"),
                         font=("Arial", 8), bg="#141920",
                         fg="#888").pack(anchor="w", pady=(2, 4))

                if is_ally:
                    tk.Label(body, text="🤝 Allied nation — operations blocked.",
                             font=("Arial", 8, "italic"), bg="#141920",
                             fg=CLR_ALLY_E).pack(anchor="w")
                elif is_occupied:
                    tk.Label(body, text="✓ Operation already active in this country.",
                             font=("Arial", 8, "italic"), bg="#141920",
                             fg="#00ff90").pack(anchor="w")
                else:
                    if rv:
                        rc = self.rivals[rv]["color"]
                        tk.Label(body, text=f"⚠ Rival controlled: {rv}",
                                 font=("Arial", 8, "bold"), bg="#141920",
                                 fg=rc).pack(anchor="w", pady=(0, 4))
                    btn_r = tk.Frame(body, bg="#141920")
                    btn_r.pack(anchor="w")
                    disc = self.get_alliance_discount(name)
                    for aname, adef in ACTIONS.items():
                        cost = int(info["action_cost"] * adef["cost_mult"] * disc)
                        can  = self.money >= cost
                        tk.Button(btn_r,
                                  text=f"{aname}  ${cost:,}",
                                  font=("Arial", 9, "bold"),
                                  bg=adef["color"] if can else "#2a1a1a",
                                  fg="white", relief="flat",
                                  padx=10, pady=4,
                                  state="normal" if can else "disabled",
                                  command=lambda a=aname, i=info, r=res_name, p=popup:
                                      self._execute_action(name, i, r, a, p, ax, canvas)
                                  ).pack(side="left", padx=(0, 6))
                    if rv:
                        bo_cost = int(info["action_cost"] * 2)
                        can_bo  = self.money >= bo_cost
                        tk.Button(btn_r,
                                  text=f"Buy Out {rv}  ${bo_cost:,}",
                                  font=("Arial", 9),
                                  bg="#2a1a3a",
                                  fg=self.rivals[rv]["color"] if can_bo else "#555",
                                  relief="flat", padx=10, pady=4,
                                  state="normal" if can_bo else "disabled",
                                  command=lambda r=res_name, rv_=rv, p=popup:
                                      [self.buyout_rival(r, name, rv_), p.destroy()]
                                  ).pack(side="left", padx=(0, 6))
        else:
            tk.Label(inner, text="No major resource deposits identified.",
                     font=("Arial", 9, "italic"), bg="#0e1117",
                     fg="#555").pack(pady=6, padx=16, anchor="w")

        # ── Alternative operations ─────────────────────────────────
        tk.Frame(inner, bg="#333", height=1).pack(fill="x", padx=16, pady=8)
        tk.Label(inner, text="ALTERNATIVE OPERATIONS",
                 font=("Impact", 13), bg="#0e1117", fg="#888888").pack(
                 anchor="w", padx=16, pady=(0, 4))

        # Trade Route
        tr_f = tk.Frame(inner, bg="#141920", padx=12, pady=10)
        tr_f.pack(fill="x", padx=12, pady=3)
        tk.Label(tr_f, text="📦  Establish Trade Route",
                 font=("Arial", 10, "bold"), bg="#141920", fg="#00cc88").pack(anchor="w")
        tk.Label(tr_f,
                 text="Legal commerce deal.  $10M setup.  $500K/day for 15 days.  No penalties.",
                 font=("Arial", 8), bg="#141920", fg="#666").pack(anchor="w", pady=2)
        trade_active = any(o["country"] == name and o.get("resource") == "Trade"
                           for o in self.oil_operations)
        if trade_active:
            tk.Label(tr_f, text="✓ Trade route already active.",
                     font=("Arial", 8, "italic"), bg="#141920", fg="#00ff90").pack(anchor="w")
        elif is_ally:
            tk.Label(tr_f, text="✓ Alliance provides automatic trade benefits.",
                     font=("Arial", 8, "italic"), bg="#141920", fg=CLR_ALLY_E).pack(anchor="w")
        else:
            can_tr = self.money >= 10_000_000
            tk.Button(tr_f, text="Establish Trade Route  —  $10,000,000",
                      font=("Arial", 9, "bold"),
                      bg="#006644" if can_tr else "#2a2a2a",
                      fg="white" if can_tr else "#555",
                      relief="flat", padx=10, pady=4,
                      state="normal" if can_tr else "disabled",
                      command=lambda p=popup:
                          self._establish_trade_route(name, p, ax, canvas)
                      ).pack(anchor="w", pady=(4, 0))

        # Lift Sanctions
        if name in self.sanctions:
            san_days   = self.sanctions[name]
            bribe_cost = max(5_000_000, san_days * 3_000_000)
            ls_f = tk.Frame(inner, bg="#141920", padx=12, pady=10)
            ls_f.pack(fill="x", padx=12, pady=3)
            tk.Label(ls_f, text="🤝  Lift Sanctions",
                     font=("Arial", 10, "bold"), bg="#141920", fg="#ffaa00").pack(anchor="w")
            tk.Label(ls_f,
                     text=(f"Remove {name}'s active sanctions on you.  "
                           f"{san_days} day(s) remaining.  Cost: ${bribe_cost:,}"),
                     font=("Arial", 8), bg="#141920", fg="#666").pack(anchor="w", pady=2)
            can_ls = self.money >= bribe_cost
            tk.Button(ls_f,
                      text=f"Lift Sanctions  —  ${bribe_cost:,}",
                      font=("Arial", 9, "bold"),
                      bg="#886600" if can_ls else "#2a2a2a",
                      fg="white" if can_ls else "#555",
                      relief="flat", padx=10, pady=4,
                      state="normal" if can_ls else "disabled",
                      command=lambda bc=bribe_cost, p=popup:
                          self._lift_sanctions(name, bc, p)
                      ).pack(anchor="w", pady=(4, 0))

        # ── Covert Operations ─────────────────────────────────────────
        tk.Frame(inner, bg="#333", height=1).pack(fill="x", padx=16, pady=8)
        tk.Label(inner, text="COVERT OPERATIONS",
                 font=("Impact", 13), bg="#0e1117", fg="#888888").pack(
                 anchor="w", padx=16, pady=(0, 4))

        # Espionage
        esp_f = tk.Frame(inner, bg="#141920", padx=12, pady=10)
        esp_f.pack(fill="x", padx=12, pady=3)
        tk.Label(esp_f, text="🕵  Espionage Mission  —  $15M",
                 font=("Arial", 10, "bold"), bg="#141920", fg="#cc88ff").pack(anchor="w")
        tk.Label(esp_f,
                 text="If rival operates here: steal 3 days of their income + sabotage. +8 trans.\n"
                      "Otherwise: sell intel for $3–8M bonus.",
                 font=("Arial", 8), bg="#141920", fg="#666",
                 justify="left").pack(anchor="w", pady=2)
        can_esp = not is_home and self.money >= 15_000_000
        tk.Button(esp_f, text="Send Spy  —  $15,000,000",
                  font=("Arial", 9, "bold"),
                  bg="#4a1a6a" if can_esp else "#2a2a2a",
                  fg="white" if can_esp else "#555",
                  relief="flat", padx=10, pady=4,
                  state="normal" if can_esp else "disabled",
                  command=lambda p=popup:
                      self._espionage_mission(name, p, ax, canvas)
                  ).pack(anchor="w", pady=(4, 0))

        # Proxy War (only if rival controls a resource here)
        if rival_controls and not is_home:
            rv_str = ", ".join(set(rival_controls.values()))
            pw_f = tk.Frame(inner, bg="#141920", padx=12, pady=10)
            pw_f.pack(fill="x", padx=12, pady=3)
            tk.Label(pw_f, text="⚔  Proxy War  —  $60M",
                     font=("Arial", 10, "bold"), bg="#141920", fg="#ff6644").pack(anchor="w")
            tk.Label(pw_f,
                     text=f"Fund insurgents against {rv_str}'s operations here.\n"
                          f"Removes all rival control from this country. +20 trans, -8 opinion.",
                     font=("Arial", 8), bg="#141920", fg="#666",
                     justify="left").pack(anchor="w", pady=2)
            can_pw = self.money >= 60_000_000
            tk.Button(pw_f, text="Fund Proxy War  —  $60,000,000",
                      font=("Arial", 9, "bold"),
                      bg="#5a1a1a" if can_pw else "#2a2a2a",
                      fg="white" if can_pw else "#555",
                      relief="flat", padx=10, pady=4,
                      state="normal" if can_pw else "disabled",
                      command=lambda p=popup:
                          self._proxy_war(name, p, ax, canvas)
                      ).pack(anchor="w", pady=(4, 0))

        # Puppet Upgrade (only after a coup)
        if is_occupied and action_name == "Stage a Coup":
            pu_f = tk.Frame(inner, bg="#141920", padx=12, pady=10)
            pu_f.pack(fill="x", padx=12, pady=3)
            tk.Label(pu_f, text="👑  Install Puppet Government  —  $100M",
                     font=("Arial", 10, "bold"), bg="#141920", fg="#ffdd44").pack(anchor="w")
            tk.Label(pu_f,
                     text="Install loyal regime. +10 days on operation. Income doubled. +10 trans.",
                     font=("Arial", 8), bg="#141920", fg="#666").pack(anchor="w", pady=2)
            can_pu = self.money >= 100_000_000
            tk.Button(pu_f, text="Install Puppet  —  $100,000,000",
                      font=("Arial", 9, "bold"),
                      bg="#5a4a00" if can_pu else "#2a2a2a",
                      fg="white" if can_pu else "#555",
                      relief="flat", padx=10, pady=4,
                      state="normal" if can_pu else "disabled",
                      command=lambda p=popup:
                          self._install_puppet(name, p, ax, canvas)
                      ).pack(anchor="w", pady=(4, 0))

        # Arms Deal (non-ally, non-occupied, non-home)
        if not is_ally and not is_occupied and not is_home:
            ad_f = tk.Frame(inner, bg="#141920", padx=12, pady=10)
            ad_f.pack(fill="x", padx=12, pady=3)
            tk.Label(ad_f, text="🔫  Arms Deal  —  net +$10M profit",
                     font=("Arial", 10, "bold"), bg="#141920", fg="#ff4444").pack(anchor="w")
            tk.Label(ad_f,
                     text="Sell weapons. Requires $20M upfront. Returns $30M. +18 trans. Boosts Defense stocks.",
                     font=("Arial", 8), bg="#141920", fg="#666").pack(anchor="w", pady=2)
            can_ad = self.money >= 20_000_000
            tk.Button(ad_f, text="Deal Arms  —  $20M cost / $30M return",
                      font=("Arial", 9, "bold"),
                      bg="#5a0000" if can_ad else "#2a2a2a",
                      fg="white" if can_ad else "#555",
                      relief="flat", padx=10, pady=4,
                      state="normal" if can_ad else "disabled",
                      command=lambda p=popup:
                          self._arms_deal(name, p, ax, canvas)
                      ).pack(anchor="w", pady=(4, 0))

        # Foreign Aid (any country except home)
        if not is_home:
            fa_f = tk.Frame(inner, bg="#141920", padx=12, pady=10)
            fa_f.pack(fill="x", padx=12, pady=3)
            tk.Label(fa_f, text="🤲  Foreign Aid  —  $25M",
                     font=("Arial", 10, "bold"), bg="#141920", fg="#00cc88").pack(anchor="w")
            tk.Label(fa_f,
                     text="+10 public opinion. -8 transgressions. Reduces sanction risk from this country.",
                     font=("Arial", 8), bg="#141920", fg="#666").pack(anchor="w", pady=2)
            can_fa = self.money >= 25_000_000
            tk.Button(fa_f, text="Send Foreign Aid  —  $25,000,000",
                      font=("Arial", 9, "bold"),
                      bg="#004a30" if can_fa else "#2a2a2a",
                      fg="white" if can_fa else "#555",
                      relief="flat", padx=10, pady=4,
                      state="normal" if can_fa else "disabled",
                      command=lambda p=popup:
                          self._foreign_aid(name, p, ax, canvas)
                      ).pack(anchor="w", pady=(4, 0))

        tk.Button(popup, text="Close", bg="#1e2130", fg="white",
                  relief="flat", padx=20, pady=6,
                  command=popup.destroy).pack(pady=8)

    def _establish_trade_route(self, country, popup, ax, canvas):
        cost = 10_000_000
        if self.money < cost:
            self.log_event("Not enough funds to establish trade route.")
            return
        self.money -= cost
        self.market.money = self.money
        self.oil_operations.append({
            "country":   country,
            "income":    500_000,
            "days_left": 15,
            "resource":  "Trade",
            "action":    "Trade Route",
        })
        self.log_event(
            f"📦 Trade Route established with {country}. $500K/day for 15 days.")
        self._add_ticker(
            f"MARKETS: {self.username} expands commercial ties with {country}.")
        self.update_status()
        popup.destroy()
        self._render_map(ax)
        canvas.draw()

    def _lift_sanctions(self, country, cost, popup):
        if self.money < cost:
            self.log_event(f"Not enough to lift sanctions (${cost:,})")
            return
        self.money -= cost
        self.market.money = self.money
        del self.sanctions[country]
        self.log_event(f"🤝 Sanctions from {country} lifted. Cost: ${cost:,}")
        self.update_status()
        popup.destroy()

    # =========================================================
    # COVERT OPERATIONS
    # =========================================================

    def _espionage_mission(self, country, popup, ax, canvas):
        import random
        cost = 15_000_000
        if self.money < cost:
            self.log_event("Not enough funds for espionage mission ($15M).")
            return
        self.money -= cost
        self.market.money = self.money
        # Check if a rival controls a resource here
        rival_ops = [op for op in getattr(self, "oil_operations", [])
                     if op.get("country") == country
                     and op.get("action") in ("Bomb", "Coup", "Trade Route")]
        if rival_ops:
            # Steal income from rival intel
            stolen = random.randint(3_000_000, 8_000_000)
            self.money += stolen
            self.market.money = self.money
            self.log_event(
                f"🕵 Espionage in {country}: intercepted rival operations — "
                f"stole ${stolen:,} in intel value.")
        else:
            # Sell general intel
            bonus = random.randint(2_000_000, 6_000_000)
            self.money += bonus
            self.market.money = self.money
            self.log_event(
                f"🕵 Espionage in {country}: sold intelligence dossier for ${bonus:,}.")
        self.add_transgression(8, -3)
        self._add_ticker(f"INTELLIGENCE: Covert activity detected near {country}.")
        self.update_status()
        popup.destroy()
        self._render_map(ax)
        canvas.draw()

    def _proxy_war(self, country, popup, ax, canvas):
        cost = 60_000_000
        if self.money < cost:
            self.log_event("Not enough funds for proxy war ($60M).")
            return
        self.money -= cost
        self.market.money = self.money
        # Remove rival control (bombed status) from this country
        removed = country in self.bombed_countries
        self.bombed_countries.discard(country)
        if hasattr(self, "action_taken"):
            self.action_taken.pop(country, None)
        self.log_event(
            f"⚔ Proxy War in {country}: {'rival forces expelled' if removed else 'destabilization campaign launched'}. "
            f"Cost: $60M")
        self.add_transgression(20, -8)
        self._add_ticker(
            f"CONFLICT: Proxy forces escalate tensions in {country}.")
        self.update_status()
        popup.destroy()
        self._render_map(ax)
        canvas.draw()

    def _install_puppet(self, country, popup, ax, canvas):
        cost = 100_000_000
        if self.money < cost:
            self.log_event("Not enough funds to install puppet government ($100M).")
            return
        # Must have an active operation in this country
        ops_here = [op for op in getattr(self, "oil_operations", [])
                    if op.get("country") == country]
        if not ops_here:
            self.log_event(
                f"No active operations in {country}. "
                "Establish control first (Bomb/Coup/Trade Route).")
            return
        self.money -= cost
        self.market.money = self.money
        for op in ops_here:
            op["days_left"] = op.get("days_left", 0) + 10
            op["income"] = int(op["income"] * 2)
        self.log_event(
            f"🏛 Puppet government installed in {country}. "
            f"All operations: +10 days, income ×2. Cost: $100M")
        self.add_transgression(10, -5)
        self._add_ticker(
            f"POLITICS: Regime change reported in {country}.")
        self.update_status()
        popup.destroy()
        self._render_map(ax)
        canvas.draw()

    def _arms_deal(self, country, popup, ax, canvas):
        cost = 20_000_000
        returns = 30_000_000
        if self.money < cost:
            self.log_event("Not enough funds for arms deal ($20M).")
            return
        self.money -= cost
        self.money += returns
        self.market.money = self.money
        # Small defense sector boost
        if hasattr(self, "apply_market_effect"):
            self.apply_market_effect(["Defense"], 1.05, 3, "Arms Deal")
        self.log_event(
            f"🔫 Arms Deal with {country}: paid $20M, received $30M. "
            f"Net: +$10M. Defense stocks up +5% for 3 days.")
        self.add_transgression(18, -6)
        self._add_ticker(
            f"MARKETS: Defense sector rises after arms shipment to {country}.")
        self.update_status()
        popup.destroy()
        self._render_map(ax)
        canvas.draw()

    def _foreign_aid(self, country, popup, ax, canvas):
        cost = 25_000_000
        if self.money < cost:
            self.log_event("Not enough funds for foreign aid ($25M).")
            return
        self.money -= cost
        self.market.money = self.money
        self.log_event(
            f"🤝 Foreign Aid sent to {country}: $25M. "
            f"+10 public opinion, −8 transgressions.")
        self.add_transgression(-8, 10)
        self._add_ticker(
            f"DIPLOMACY: {self.username} sends humanitarian aid to {country}.")
        self.update_status()
        popup.destroy()
        self._render_map(ax)
        canvas.draw()

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

        # Crash the seized resource's market category (supply disruption)
        if resource in RESOURCE_CRASH:
            crash_cats, crash_mult, crash_days = RESOURCE_CRASH[resource]
            self.apply_market_effect(crash_cats, crash_mult, crash_days,
                                     f"Resource seizure: {name} {resource}")
            self.log_event(
                f"📉 {resource} seizure in {name} caused a market crash in "
                f"{', '.join(crash_cats)} stocks for {crash_days} days.")
        if action_name == "Bomb":
            self.apply_market_effect(["Defense"], 1.04, 3, f"Military op: {name}")

        popup.destroy()
        self._render_map(ax)
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
