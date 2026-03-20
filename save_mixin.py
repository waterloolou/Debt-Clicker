"""Save / Load system — 3 named slots stored as JSON files."""

import tkinter as tk
import json
import os
import time

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
NUM_SLOTS = 3


def _slot_path(slot: int) -> str:
    return os.path.join(SAVE_DIR, f"save_slot_{slot}.json")


# Fields persisted per save
_SAVE_FIELDS = [
    "username", "country", "money", "days",
    "happiness", "public_opinion", "transgressions", "wanted_level",
    "loans", "owned_assets", "oil_operations", "owned_islands",
    "alliance", "alliance_days", "alliance_tier",
    "sanctions", "militia", "blockaded_days",
    "advisor_cursed_days", "factories",
    "epstein", "epstein_visited", "epstein_catch_days",
    "subscription", "ponzi", "oil_spill", "carbon",
    "insider_trading", "pandemic", "lobby_immunity",
    "net_worth_history",
]


class SaveMixin:
    """Handles 3-slot save / load for mid-game persistence."""

    # ──────────────────────────────────────────────────────────────────────────
    # Core save / load
    # ──────────────────────────────────────────────────────────────────────────

    def save_game(self, slot: int):
        """Serialise current game state to a slot file."""
        data = {"saved_at": time.strftime("%Y-%m-%d %H:%M")}
        for field in _SAVE_FIELDS:
            val = getattr(self, field, None)
            # Convert sets to lists for JSON
            if isinstance(val, set):
                val = list(val)
            data[field] = val
        # Also save stock portfolio (shares owned per stock)
        data["stock_portfolio"] = {
            name: s["shares"]
            for name, s in self.market.stocks.items()
            if s.get("shares", 0) > 0
        }
        try:
            with open(_slot_path(slot), "w") as f:
                json.dump(data, f, indent=2)
            self.log_event(f"Game saved to slot {slot}.")
        except Exception as e:
            self.log_event(f"Save failed: {e}")

    def load_game(self, slot: int) -> bool:
        """Load game state from a slot file. Returns True on success."""
        path = _slot_path(slot)
        if not os.path.exists(path):
            return False
        try:
            with open(path) as f:
                data = json.load(f)
        except Exception:
            return False

        for field in _SAVE_FIELDS:
            if field not in data:
                continue
            val = data[field]
            # Restore sets
            if field in ("owned_assets", "owned_islands", "bombed_countries"):
                val = set(val) if isinstance(val, list) else (val or set())
            setattr(self, field, val)

        # Restore stock portfolio
        portfolio = data.get("stock_portfolio", {})
        for name, shares in portfolio.items():
            if name in self.market.stocks:
                self.market.stocks[name]["shares"] = shares

        self.market.money = self.money
        return True

    # ──────────────────────────────────────────────────────────────────────────
    # Slot metadata (for display)
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def get_slot_info(slot: int) -> dict | None:
        """Return summary dict for display, or None if slot is empty."""
        path = _slot_path(slot)
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                data = json.load(f)
            return {
                "name":     data.get("username", "Unknown"),
                "days":     data.get("days", 0),
                "money":    data.get("money", 0),
                "country":  data.get("country", ""),
                "saved_at": data.get("saved_at", ""),
            }
        except Exception:
            return None

    @staticmethod
    def delete_slot(slot: int):
        path = _slot_path(slot)
        if os.path.exists(path):
            os.remove(path)

    # ──────────────────────────────────────────────────────────────────────────
    # In-game save menu (accessible via Save button on game screen)
    # ──────────────────────────────────────────────────────────────────────────

    def open_save_menu(self):
        win = tk.Toplevel(self.root)
        win.title("Save Game")
        win.configure(bg="#0e1117")
        win.geometry("440x360")
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        tk.Label(win, text="SAVE GAME",
                 font=("Impact", 24), bg="#0e1117", fg="#00ff90").pack(pady=(18, 4))
        tk.Label(win, text="Choose a slot to save your current progress.",
                 font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))

        self._build_slot_cards(win, mode="save")

        tk.Button(win, text="Cancel", font=("Arial", 10), bg="#1e2130", fg="#aaa",
                  relief="flat", padx=20, pady=5,
                  command=win.destroy).pack(pady=(12, 0))

    def open_load_menu(self):
        """Load menu opened from the start screen."""
        win = tk.Toplevel(self.root)
        win.title("Load Game")
        win.configure(bg="#0e1117")
        win.geometry("440x400")
        win.resizable(False, False)
        win.lift()
        win.focus_force()

        tk.Label(win, text="LOAD GAME",
                 font=("Impact", 24), bg="#0e1117", fg="#4499ff").pack(pady=(18, 4))
        tk.Label(win, text="Select a save slot to continue your empire.",
                 font=("Arial", 9), bg="#0e1117", fg="#666").pack(pady=(0, 12))

        self._build_slot_cards(win, mode="load")

        tk.Button(win, text="Cancel", font=("Arial", 10), bg="#1e2130", fg="#aaa",
                  relief="flat", padx=20, pady=5,
                  command=win.destroy).pack(pady=(12, 0))

    def _build_slot_cards(self, win, mode: str):
        for slot in range(1, NUM_SLOTS + 1):
            info = self.get_slot_info(slot)
            card = tk.Frame(win, bg="#1e2130", pady=10, padx=16)
            card.pack(fill="x", padx=20, pady=4)

            # Slot label
            tk.Label(card, text=f"Slot {slot}",
                     font=("Arial", 10, "bold"), bg="#1e2130",
                     fg="#aaaaaa", width=6, anchor="w").pack(side="left")

            if info:
                # Filled slot
                desc = (f"{info['name']}  ·  Day {info['days']}  ·  "
                        f"${info['money']:,.0f}  [{info['saved_at']}]")
                tk.Label(card, text=desc, font=("Arial", 9),
                         bg="#1e2130", fg="white", anchor="w").pack(side="left", fill="x", expand=True)

                if mode == "save":
                    tk.Button(card, text="Overwrite",
                              font=("Arial", 9, "bold"), bg="#ff6600", fg="white",
                              relief="flat", padx=10, pady=3,
                              command=lambda s=slot, w=win: self._do_save(s, w)
                              ).pack(side="right", padx=4)
                else:
                    tk.Button(card, text="Load",
                              font=("Arial", 9, "bold"), bg="#4499ff", fg="white",
                              relief="flat", padx=10, pady=3,
                              command=lambda s=slot, w=win: self._do_load(s, w)
                              ).pack(side="right", padx=4)
                    tk.Button(card, text="Delete",
                              font=("Arial", 9), bg="#331111", fg="#ff4444",
                              relief="flat", padx=8, pady=3,
                              command=lambda s=slot, w=win: self._do_delete(s, w)
                              ).pack(side="right", padx=2)
            else:
                # Empty slot
                tk.Label(card, text="— Empty —", font=("Arial", 9),
                         bg="#1e2130", fg="#444", anchor="w").pack(side="left", fill="x", expand=True)
                if mode == "save":
                    tk.Button(card, text="Save Here",
                              font=("Arial", 9, "bold"), bg="#00aa44", fg="white",
                              relief="flat", padx=10, pady=3,
                              command=lambda s=slot, w=win: self._do_save(s, w)
                              ).pack(side="right")
                else:
                    tk.Label(card, text="(empty)", font=("Arial", 9),
                             bg="#1e2130", fg="#444").pack(side="right")

    def _do_save(self, slot: int, win):
        self.save_game(slot)
        win.destroy()

    def _do_load(self, slot: int, win):
        win.destroy()
        ok = self.load_game(slot)
        if ok:
            # Start the game from the loaded state
            self.running = True
            self.init_rivals()
            self.update_status()
            self.show_screen("game")
            self.log_event(f"Loaded save slot {slot}. Welcome back, {self.username}!")
            import threading
            threading.Thread(target=self.fetch_real_stock_data, daemon=True).start()
        else:
            self.log_event(f"Failed to load slot {slot}.")

    def _do_delete(self, slot: int, win):
        self.delete_slot(slot)
        win.destroy()
        self.open_load_menu()
