"""island_map_mixin.py
Private island purchase map.
Real world background (geopandas) with clickable island markers.
"""

import tkinter as tk
import os
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

_SHAPEFILE_URL = (
    "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
)
_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "world_countries.gpkg"
)

# ---------------------------------------------------------------------------
# Island catalogue  — (lon, lat), ascending price
# ---------------------------------------------------------------------------
ISLANDS = [
    {
        "name":    "Sandy Cay",
        "loc":     "Bahamas",
        "lat":  26.8,  "lon": -77.4,
        "price":     500_000,
        "upkeep":      5_000,
        "income":      5_000,
        "desc":  "A tiny sandbar with 3 palm trees. Technically yours.",
    },
    {
        "name":    "Bird Island",
        "loc":     "Belize",
        "lat":  16.8,  "lon": -88.1,
        "price":     800_000,
        "upkeep":      8_000,
        "income":      8_000,
        "desc":  "Remote jungle island. Crocodiles included at no extra charge.",
    },
    {
        "name":    "Little Whale Cay",
        "loc":     "Bahamas",
        "lat":  25.5,  "lon": -77.8,
        "price":   2_000_000,
        "upkeep":     15_000,
        "income":     15_000,
        "desc":  "Private beach, villa, boat dock. No neighbours. Perfect.",
    },
    {
        "name":    "Bell Island",
        "loc":     "Canada",
        "lat":  49.6,  "lon": -126.0,
        "price":   3_000_000,
        "upkeep":     20_000,
        "income":     20_000,
        "desc":  "Rugged, green, cold. Very exclusive. Bring a jacket.",
    },
    {
        "name":    "Diapori",
        "loc":     "Greece",
        "lat":  39.8,  "lon": 25.5,
        "price":   4_000_000,
        "upkeep":     30_000,
        "income":     30_000,
        "desc":  "Aegean blue. Ancient ruins. Goats not included.",
    },
    {
        "name":    "Rangyai",
        "loc":     "Thailand",
        "lat":   8.8,  "lon":  99.4,
        "price":   5_000_000,
        "upkeep":     40_000,
        "income":     40_000,
        "desc":  "57 beach villas. Staff to guest ratio: 3:1.",
    },
    {
        "name":    "Thanda Island",
        "loc":     "Tanzania",
        "lat":  -8.6,  "lon":  39.6,
        "price":   8_000_000,
        "upkeep":     60_000,
        "income":     60_000,
        "desc":  "Eco-luxury off the Tanzanian coast. Whale sharks visit.",
    },
    {
        "name":    "Cayo Espanto",
        "loc":     "Belize",
        "lat":  17.2,  "lon": -87.8,
        "price":  15_000_000,
        "upkeep":    100_000,
        "income":    100_000,
        "desc":  "7 private villas. Exclusive use only. The sea is yours.",
    },
    {
        "name":    "Tagomago",
        "loc":     "Ibiza, Spain",
        "lat":  39.1,  "lon":   1.7,
        "price":  18_000_000,
        "upkeep":    120_000,
        "income":    120_000,
        "desc":  "Party island off Ibiza. 12 full-time staff. Helicopters welcome.",
    },
    {
        "name":    "Gladstone's Island",
        "loc":     "Australia",
        "lat": -23.5,  "lon": 151.3,
        "price":  12_000_000,
        "upkeep":     90_000,
        "income":     90_000,
        "desc":  "Great Barrier Reef. Turtles everywhere. Legally protected turtles.",
    },
    {
        "name":    "Nukutepipi",
        "loc":     "French Polynesia",
        "lat": -19.3,  "lon": -138.8,
        "price":  22_000_000,
        "upkeep":    150_000,
        "income":    150_000,
        "desc":  "24 over-water bungalows. Owned by a French billionaire. Now you.",
    },
    {
        "name":    "Vomo Island",
        "loc":     "Fiji",
        "lat": -17.4,  "lon": 177.0,
        "price":  28_000_000,
        "upkeep":    200_000,
        "income":    200_000,
        "desc":  "225 hectares of Fijian perfection. Manta rays come free.",
    },
    {
        "name":    "Musha Cay",
        "loc":     "Bahamas",
        "lat":  24.1,  "lon": -76.3,
        "price":  37_000_000,
        "upkeep":    300_000,
        "income":    300_000,
        "desc":  "David Copperfield's island. Magic tricks not included.",
    },
    {
        "name":    "Little Saint James",
        "loc":     "U.S. Virgin Islands",
        "lat":  18.30,  "lon": -64.83,
        "price":  45_000_000,
        "upkeep":    250_000,
        "income":    600_000,
        "desc":  "Epstein's infamous private island. Sold by the estate in 2023. "
                 "Tunnels included. Previous owner not included.",
    },
    {
        "name":    "North Island",
        "loc":     "Seychelles",
        "lat":  -4.4,  "lon":  55.2,
        "price":  50_000_000,
        "upkeep":    400_000,
        "income":    400_000,
        "desc":  "George Clooney honeymooned here. Now it's your turn.",
    },
    {
        "name":    "Laucala Island",
        "loc":     "Fiji",
        "lat": -16.7,  "lon": -179.7,
        "price":  75_000_000,
        "upkeep":    500_000,
        "income":    500_000,
        "desc":  "Forbes' most expensive island resort. 25 private villas.",
    },
    {
        "name":    "Necker Island",
        "loc":     "British Virgin Islands",
        "lat":  18.5,  "lon": -64.4,
        "price": 100_000_000,
        "upkeep":    800_000,
        "income":    800_000,
        "desc":  "Richard Branson's former playground. 30 guests max.",
    },
    {
        "name":    "Mustique",
        "loc":     "St. Vincent",
        "lat":  12.9,  "lon": -61.2,
        "price": 150_000_000,
        "upkeep":  1_200_000,
        "income":  1_200_000,
        "desc":  "Princess Margaret's favourite. Old money only. (Or new, if enough.)",
    },
    {
        "name":    "Lanai",
        "loc":     "Hawaii, USA",
        "lat":  20.8,  "lon": -156.9,
        "price": 300_000_000,
        "upkeep":  2_000_000,
        "income":  2_000_000,
        "desc":  "Larry Ellison bought it for $300M. He's selling. You're buying.",
    },
]

GREENLAND = {
    "name":    "Greenland",
    "loc":     "Kingdom of Denmark",
    "lat":  72.0,  "lon": -42.0,
    "price":  500_000_000,         # offer price shown on popup (always rejected, money NOT spent)
    "bomb_cost":    80_000_000,    # bomb price
    "upkeep":  5_000_000,
    "income":  8_000_000,
    "desc":  "World's largest island. Denmark says it's not for sale. "
             "They have said this many times. To many people.",
}

GREENLAND_REJECTIONS = [
    "\"Greenland is not for sale.\"  — Denmark, 2019",
    "\"Greenland is not for sale.\"  — Denmark, again, 2025",
    "\"Greenland is STILL not for sale. Please stop calling.\"  — Denmark, now",
    "\"We are blocking your number.\"  — Copenhagen, probably",
]

# Islands that belong to a specific playable country (can't buy your own)
HOMELAND_ISLANDS = {
    "Canada":                   ["Bell Island"],
    "United States of America": ["Lanai"],
    "Spain":                    ["Tagomago"],
    "Australia":                ["Gladstone's Island"],
    "United Kingdom":           ["Necker Island"],
    "France":                   ["Nukutepipi"],
    "Fiji":                     ["Vomo Island", "Laucala Island"],
}

_CLR_BG    = "#07111f"
_CLR_OCEAN = "#0a1e35"
_CLR_LAND  = "#162a1b"
_CLR_EDGE  = "#1e3622"
_CLR_AVAIL = "#ffcc00"
_CLR_OWNED = "#00ff90"
_CLR_CANT  = "#444444"


def _load_world():
    import geopandas as gpd
    if os.path.exists(_CACHE_FILE):
        return gpd.read_file(_CACHE_FILE)
    world = gpd.read_file(_SHAPEFILE_URL)
    world[["NAME", "geometry"]].to_file(_CACHE_FILE, driver="GPKG")
    return world


class IslandMapMixin:
    """Purchasable private island map."""

    # =========================================================
    # OPEN ISLAND MAP
    # =========================================================

    def open_island_map(self):
        win = tk.Toplevel(self.root)
        win.title("Private Islands")
        win.configure(bg=_CLR_BG)
        win.geometry("1080x620")
        win.resizable(True, True)

        # Header
        hdr = tk.Frame(win, bg=_CLR_BG)
        hdr.pack(fill="x", padx=16, pady=(10, 0))
        tk.Label(hdr, text="🏝️  PRIVATE ISLANDS",
                 font=("Impact", 20), bg=_CLR_BG, fg="#ffcc00").pack(side="left")
        tk.Label(hdr, text="Click an island to purchase it. Earn daily passive income.",
                 font=("Arial", 9), bg=_CLR_BG, fg="#555").pack(side="left", padx=14)

        # Loading placeholder
        loading = tk.Label(win, text="Loading map...",
                           font=("Arial", 13), bg=_CLR_BG, fg="#888")
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

            fig, ax = plt.subplots(1, 1, figsize=(13.5, 6.5), facecolor=_CLR_OCEAN)
            ax.set_facecolor(_CLR_OCEAN)
            ax.set_axis_off()
            ax.set_xlim(-180, 180)
            ax.set_ylim(-75, 80)

            self._island_world = world
            self._island_ax    = ax
            self._island_fig   = fig

            self._draw_island_map(ax, world)

            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(4, 0))
            self._island_canvas = canvas

            # ── Zoom / pan state ──────────────────────────────────────────
            _pan = {"active": False, "x0": 0.0, "y0": 0.0,
                    "xlim": (-180, 180), "ylim": (-75, 80)}

            def _zoom(event):
                if event.inaxes != ax or event.xdata is None:
                    return
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                scale = 0.70 if event.button == "up" else 1.43
                xc, yc = event.xdata, event.ydata
                ax.set_xlim(xc - (xc - xmin) * scale,
                            xc + (xmax - xc) * scale)
                ax.set_ylim(yc - (yc - ymin) * scale,
                            yc + (ymax - yc) * scale)
                canvas.draw_idle()

            def _press(event):
                if event.button == 3 and event.xdata is not None:
                    _pan.update({"active": True,
                                 "x0": event.xdata, "y0": event.ydata,
                                 "xlim": ax.get_xlim(),
                                 "ylim": ax.get_ylim()})

            def _motion(event):
                if _pan["active"] and event.xdata is not None:
                    dx = event.xdata - _pan["x0"]
                    dy = event.ydata - _pan["y0"]
                    ax.set_xlim(_pan["xlim"][0] - dx, _pan["xlim"][1] - dx)
                    ax.set_ylim(_pan["ylim"][0] - dy, _pan["ylim"][1] - dy)
                    canvas.draw_idle()

            def _release(event):
                if event.button == 3:
                    _pan["active"] = False

            fig.canvas.mpl_connect("scroll_event",         _zoom)
            fig.canvas.mpl_connect("button_press_event",   _press)
            fig.canvas.mpl_connect("motion_notify_event",  _motion)
            fig.canvas.mpl_connect("button_release_event", _release)
            # Left-click island selection (button 1 only)
            fig.canvas.mpl_connect(
                "button_press_event",
                lambda e: self._on_island_click(e, ax, canvas) if e.button == 1 else None)

            # ── Legend + controls ─────────────────────────────────────────
            leg = tk.Frame(win, bg=_CLR_BG)
            leg.pack(pady=4)
            for color, label in [(_CLR_AVAIL, "Available"),
                                  (_CLR_OWNED, "Owned"),
                                  (_CLR_CANT,  "Can't afford")]:
                d = tk.Canvas(leg, width=12, height=12,
                              bg=_CLR_BG, highlightthickness=0)
                d.create_oval(1, 1, 11, 11, fill=color, outline="#444")
                d.pack(side="left", padx=(10, 3))
                tk.Label(leg, text=label, font=("Arial", 8),
                         bg=_CLR_BG, fg="#888").pack(side="left", padx=(0, 12))

            self._island_owned_lbl = tk.Label(
                leg,
                text=self._island_status_text(),
                font=("Arial", 8, "bold"), bg=_CLR_BG, fg="#00ff90")
            self._island_owned_lbl.pack(side="left", padx=(20, 0))

            # Zoom shortcuts
            def _reset_view():
                ax.set_xlim(-180, 180)
                ax.set_ylim(-75, 80)
                canvas.draw_idle()

            def _view_caribbean():
                ax.set_xlim(-90, -55)
                ax.set_ylim(10, 30)
                canvas.draw_idle()

            def _view_pacific():
                ax.set_xlim(130, 200)
                ax.set_ylim(-30, 25)
                canvas.draw_idle()

            btn_cfg = dict(font=("Arial", 8), bg="#1e2130", fg="#aaaaaa",
                           relief="flat", padx=8, pady=3)
            tk.Label(leg, text="  View:", font=("Arial", 8),
                     bg=_CLR_BG, fg="#555").pack(side="left", padx=(16, 4))
            tk.Button(leg, text="World",     command=_reset_view,     **btn_cfg).pack(side="left", padx=2)
            tk.Button(leg, text="Caribbean", command=_view_caribbean, **btn_cfg).pack(side="left", padx=2)
            tk.Button(leg, text="Pacific",   command=_view_pacific,   **btn_cfg).pack(side="left", padx=2)
            tk.Label(leg, text="  scroll=zoom  right-drag=pan",
                     font=("Arial", 7), bg=_CLR_BG, fg="#333").pack(side="left", padx=(10, 0))

            win.protocol("WM_DELETE_WINDOW",
                         lambda: [plt.close(fig), win.destroy()])

        threading.Thread(target=_build, daemon=True).start()

    def _island_status_text(self):
        n = len(self.owned_islands)
        daily = sum(isl["income"] for isl in ISLANDS
                    if isl["name"] in self.owned_islands)
        return f"Owned: {n}   |   Daily income: ${daily:,}"

    # =========================================================
    # DRAW MAP
    # =========================================================

    def _draw_island_map(self, ax, world):
        ax.cla()
        ax.set_facecolor(_CLR_OCEAN)
        ax.set_axis_off()
        ax.set_xlim(-180, 180)
        ax.set_ylim(-75, 80)

        if not world.empty:
            world.plot(ax=ax, color=_CLR_LAND, edgecolor=_CLR_EDGE,
                       linewidth=0.4, aspect=None)

        # Greenland — special marker
        gl = GREENLAND
        if gl["name"] in self.owned_islands:
            ax.plot(gl["lon"], gl["lat"], marker="*", color=_CLR_OWNED,
                    markersize=16, zorder=7)
            ax.annotate("Greenland (YOURS)",
                        xy=(gl["lon"], gl["lat"]), xytext=(3, 5),
                        textcoords="offset points", fontsize=6, color=_CLR_OWNED,
                        zorder=8, path_effects=[pe.withStroke(linewidth=1.5, foreground=_CLR_OCEAN)])
        else:
            ax.plot(gl["lon"], gl["lat"], marker="D", color="#aaddff",
                    markersize=10, zorder=7)
            ax.annotate("Greenland (NOT FOR SALE)",
                        xy=(gl["lon"], gl["lat"]), xytext=(3, 5),
                        textcoords="offset points", fontsize=5.5, color="#aaddff",
                        zorder=8, path_effects=[pe.withStroke(linewidth=1.5, foreground=_CLR_OCEAN)])

        # Island markers
        home_country = getattr(self, "country", "")
        homeland_set = set(HOMELAND_ISLANDS.get(home_country, []))
        for isl in ISLANDS:
            owned      = isl["name"] in self.owned_islands
            can_afford = self.money >= isl["price"]
            is_homeland = isl["name"] in homeland_set

            if owned:
                color, marker, size, zorder = _CLR_OWNED, "★", 14, 6
            elif is_homeland:
                color, marker, size, zorder = "#3366aa",  "●", 8,  5
            elif can_afford:
                color, marker, size, zorder = _CLR_AVAIL, "●", 9,  5
            else:
                color, marker, size, zorder = _CLR_CANT,  "●", 7,  4

            ax.plot(isl["lon"], isl["lat"],
                    marker="o" if marker == "●" else "*",
                    color=color, markersize=size,
                    markeredgecolor="#000000" if owned else "none",
                    markeredgewidth=0.5,
                    zorder=zorder)

            # Label for owned or affordable
            if owned or can_afford:
                ax.annotate(
                    isl["name"],
                    xy=(isl["lon"], isl["lat"]),
                    xytext=(3, 4), textcoords="offset points",
                    fontsize=5.2, color=color, zorder=zorder + 1,
                    path_effects=[pe.withStroke(linewidth=1.4,
                                                foreground=_CLR_OCEAN)],
                )

    # =========================================================
    # CLICK DETECTION
    # =========================================================

    def _on_island_click(self, event, ax, canvas):
        if event.inaxes != ax or event.xdata is None:
            return

        # Scale hit radius with current zoom level
        xspan = ax.get_xlim()[1] - ax.get_xlim()[0]
        scale = (xspan / 360.0) ** 2   # shrinks as you zoom in
        gl_thresh  = max(4,  64  * scale)
        isl_thresh = max(1,  16  * scale)

        # Check Greenland first (large target)
        gl = GREENLAND
        gl_dist = (event.xdata - gl["lon"])**2 + (event.ydata - gl["lat"])**2
        if gl_dist < gl_thresh:
            self._show_greenland_popup(ax, canvas)
            return

        # Find closest regular island
        best, best_dist = None, float("inf")
        for isl in ISLANDS:
            dist = (event.xdata - isl["lon"])**2 + (event.ydata - isl["lat"])**2
            if dist < best_dist:
                best_dist = dist
                best = isl

        if best and best_dist < isl_thresh:
            self._show_island_popup(best, ax, canvas)

    # =========================================================
    # ISLAND POPUP
    # =========================================================

    def _show_island_popup(self, isl, ax, canvas):
        popup = tk.Toplevel(self.root)
        popup.title(isl["name"])
        popup.configure(bg="#0e1117")
        popup.grab_set()
        popup.resizable(False, False)

        owned = isl["name"] in self.owned_islands
        home_country = getattr(self, "country", "")
        is_homeland  = isl["name"] in HOMELAND_ISLANDS.get(home_country, [])

        if is_homeland and not owned:
            popup.geometry("400x220")
            tk.Label(popup, text=f"🏠  {isl['name']}",
                     font=("Arial", 14, "bold"), bg="#0e1117", fg="#5599ff").pack(pady=(20, 4))
            tk.Label(popup, text=isl["loc"],
                     font=("Arial", 9, "italic"), bg="#0e1117", fg="#555").pack()
            tk.Label(popup,
                     text="This island belongs to your home country.\nYou can't buy your own territory.",
                     font=("Arial", 10), bg="#0e1117", fg="#aaaaaa",
                     justify="center").pack(pady=10)
            tk.Button(popup, text="Close", bg="#1e2130", fg="white",
                      relief="flat", padx=20, pady=6,
                      command=popup.destroy).pack(pady=8)
            return

        popup.geometry("400x320")

        tk.Label(popup,
                 text=f"{'🌟' if owned else '🏝️'}  {isl['name']}",
                 font=("Arial", 14, "bold"),
                 bg="#0e1117", fg="#ffcc00").pack(pady=(18, 2))
        tk.Label(popup, text=isl["loc"],
                 font=("Arial", 9, "italic"), bg="#0e1117", fg="#666").pack()
        tk.Label(popup, text=isl["desc"],
                 font=("Arial", 9), bg="#0e1117", fg="#aaaaaa",
                 wraplength=360, justify="center").pack(pady=(6, 4))

        if owned:
            tk.Label(popup, text="✅  You own this island.",
                     font=("Arial", 11, "bold"), bg="#0e1117",
                     fg="#00ff90").pack(pady=8)
            tk.Label(popup,
                     text=f"Generating ${isl['income']:,}/day",
                     font=("Arial", 10), bg="#0e1117", fg="#00cc70").pack()
            tk.Button(popup, text="Close",
                      bg="#1e2130", fg="white", relief="flat",
                      padx=20, pady=6,
                      command=popup.destroy).pack(pady=14)
        else:
            rows = [
                ("Purchase Price", f"${isl['price']:,}"),
                ("Daily Upkeep",   f"${isl['upkeep']:,}"),
                ("Daily Income",   f"${isl['income']:,}"),
            ]
            for lbl, val in rows:
                row = tk.Frame(popup, bg="#0e1117")
                row.pack(fill="x", padx=40, pady=2)
                tk.Label(row, text=lbl + ":", font=("Arial", 9),
                         bg="#0e1117", fg="#666", width=14,
                         anchor="w").pack(side="left")
                tk.Label(row, text=val, font=("Arial", 9, "bold"),
                         bg="#0e1117", fg="white").pack(side="left")

            can_afford = self.money >= isl["price"]
            tk.Button(popup,
                      text=f"🏝️  Buy Island  (-${isl['price']:,})"
                           if can_afford else "Not enough money",
                      font=("Arial", 11, "bold"),
                      bg="#ff9900" if can_afford else "#2a2010",
                      fg="white", relief="flat",
                      padx=16, pady=8,
                      state="normal" if can_afford else "disabled",
                      command=lambda: self._buy_island(isl, popup, ax, canvas)
                      ).pack(pady=(10, 4))

            tk.Button(popup, text="Cancel",
                      bg="#1e2130", fg="#aaaaaa", relief="flat",
                      padx=16, pady=6,
                      command=popup.destroy).pack()

    # =========================================================
    # GREENLAND POPUP
    # =========================================================

    def _show_greenland_popup(self, ax, canvas):
        import random
        gl = GREENLAND
        popup = tk.Toplevel(self.root)
        popup.title("Greenland")
        popup.configure(bg="#0e1117")
        popup.resizable(False, False)

        if gl["name"] in self.owned_islands:
            popup.geometry("400x220")
            tk.Label(popup, text="🏔️  Greenland",
                     font=("Arial", 14, "bold"), bg="#0e1117", fg="#00ff90").pack(pady=(20, 6))
            tk.Label(popup, text="It's yours. Denmark is furious.\nGenerating $8,000,000/day.",
                     font=("Arial", 10), bg="#0e1117", fg="white", justify="center").pack()
            tk.Button(popup, text="Close", bg="#1e2130", fg="white",
                      relief="flat", padx=20, pady=6,
                      command=popup.destroy).pack(pady=16)
            return

        popup.geometry("460x340")
        tk.Label(popup, text="Greenland",
                 font=("Arial", 14, "bold"), bg="#0e1117", fg="#aaddff").pack(pady=(18, 2))
        tk.Label(popup, text="World's largest island. 56,000 people. Denmark's pride.",
                 font=("Arial", 9, "italic"), bg="#0e1117", fg="#555").pack()
        tk.Label(popup, text=gl["desc"],
                 font=("Arial", 9), bg="#0e1117", fg="#aaaaaa",
                 wraplength=400, justify="center").pack(pady=(8, 4))

        # Track how many times player has tried to buy (per popup session)
        attempt = [0]

        offer_lbl = tk.Label(popup, text="",
                             font=("Arial", 9, "italic"), bg="#0e1117", fg="#ff6666")
        offer_lbl.pack(pady=2)

        btn_row = tk.Frame(popup, bg="#0e1117")
        btn_row.pack(pady=8)

        can_bomb = self.money >= gl["bomb_cost"]

        def try_offer():
            # Diplomatic offer is free — Denmark always says no
            idx = min(attempt[0], len(GREENLAND_REJECTIONS) - 1)
            offer_lbl.config(text=GREENLAND_REJECTIONS[idx])
            self.log_event(f"Offered ${gl['price']:,} for Greenland. Denmark said no.")
            attempt[0] += 1
            # Re-check affordability in case player earned money since popup opened
            affordable = self.money >= gl["bomb_cost"]
            bomb_btn.config(
                bg="#ff2222" if affordable else "#3a1a1a",
                fg="white" if affordable else "#663333",
                state="normal" if affordable else "disabled"
            )

        offer_btn = tk.Button(btn_row,
                              text=f"Make an offer  (${gl['price']:,})",
                              font=("Arial", 10), bg="#1e4080", fg="white",
                              relief="flat", padx=12, pady=6,
                              command=try_offer)
        offer_btn.pack(side="left", padx=8)

        bomb_btn = tk.Button(btn_row,
                             text=f"Bomb it  (-${gl['bomb_cost']:,})",
                             font=("Arial", 10, "bold"),
                             bg="#ff2222" if can_bomb else "#3a1a1a",
                             fg="white" if can_bomb else "#663333",
                             relief="flat", padx=12, pady=6,
                             state="normal" if can_bomb else "disabled",
                             command=lambda: self._bomb_greenland(popup, ax, canvas))
        bomb_btn.pack(side="left", padx=8)

        tk.Button(btn_row, text="Cancel",
                  font=("Arial", 9), bg="#1e2130", fg="#aaaaaa",
                  relief="flat", padx=10, pady=6,
                  command=popup.destroy).pack(side="left", padx=8)

    def _bomb_greenland(self, popup, ax, canvas):
        gl = GREENLAND
        self.money -= gl["bomb_cost"]
        self.market.money = self.money
        self.owned_islands.add(gl["name"])
        self.add_transgression(25, 25)
        self.add_happiness(10)
        self.update_status()
        self.log_event(
            f"💣 Bombed Greenland. Denmark is livid. "
            f"Cost: ${gl['bomb_cost']:,}. "
            f"Income: ${gl['income']:,}/day."
        )
        self.apply_market_effect(["Defense"], 1.08, 5, "Greenland annexation")
        self.apply_market_effect(["Energy"],  1.05, 4, "Arctic oil access")
        popup.destroy()
        self._draw_island_map(ax, self._island_world)
        canvas.draw()
        if hasattr(self, "_island_owned_lbl"):
            self._island_owned_lbl.config(text=self._island_status_text())

    # =========================================================
    # PURCHASE ISLAND
    # =========================================================

    def _buy_island(self, isl, popup, ax, canvas):
        self.money -= isl["price"]
        self.market.money = self.money
        self.owned_islands.add(isl["name"])
        self.add_happiness(max(5, min(20, isl["price"] // 5_000_000)))
        self.update_status()
        self.log_event(
            f"🏝️ Purchased {isl['name']} ({isl['loc']}) "
            f"for ${isl['price']:,}. "
            f"Earning ${isl['income']:,}/day."
        )
        popup.destroy()
        self._draw_island_map(ax, self._island_world)
        canvas.draw()
        if hasattr(self, "_island_owned_lbl"):
            self._island_owned_lbl.config(text=self._island_status_text())

    # =========================================================
    # DAILY ISLAND INCOME  (called from game.py main_loop)
    # =========================================================

    def process_island_income(self):
        if not self.owned_islands:
            return
        all_islands = ISLANDS + [GREENLAND]
        total_income  = sum(i["income"]  for i in all_islands if i["name"] in self.owned_islands)
        total_upkeep  = sum(i["upkeep"]  for i in all_islands if i["name"] in self.owned_islands)
        net = total_income - total_upkeep
        if net != 0:
            self.money += net
            self.market.money = self.money
            sign = "+" if net >= 0 else ""
            self.log_event(f"🏝️ Islands net: {sign}${net:,}/day")
