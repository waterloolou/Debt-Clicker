"""
Debt Clicker — Multiplayer Mixin
Provides lobby UI, state broadcasting, and incoming-message handling.
"""

import tkinter as tk
import random
import string

from network_client import NetworkClient
from rivals_mixin import RIVAL_DEFS


# Colours assigned to multiplayer rivals (cycles if more than available)
_MP_COLORS = [r["color"] for r in RIVAL_DEFS] + [
    "#0099ff", "#00cc88", "#ff6600", "#cc0099",
]


def _random_lobby_code():
    return "".join(random.choices(string.ascii_uppercase, k=4))


class MultiplayerMixin:
    """
    Mixin for DebtClicker that adds multiplayer support.

    Depends on self.root, self.username, self.country, self.rivals,
    self.is_multiplayer, self.net_client, and standard game methods.
    """

    # ──────────────────────────────────────────────────────────────────────────
    # 1.  Lobby Window
    # ──────────────────────────────────────────────────────────────────────────

    def open_multiplayer_lobby(self):
        """Open the multiplayer lobby Toplevel."""
        win = tk.Toplevel(self.root)
        win.title("Multiplayer Lobby")
        win.configure(bg="#0e1117")
        win.geometry("420x520")
        win.resizable(False, False)
        win.grab_set()

        # Keep a reference so we can close it from a callback
        self._lobby_win = win

        # ── Title ────────────────────────────────────────────────────────────
        tk.Label(win, text="MULTIPLAYER",
                 font=("Impact", 26), bg="#0e1117", fg="#1e90ff").pack(pady=(20, 2))
        tk.Label(win, text="Join a lobby with up to 3 players.",
                 font=("Arial", 9), bg="#0e1117", fg="#555").pack(pady=(0, 12))

        # ── Server host ──────────────────────────────────────────────────────
        tk.Label(win, text="Server host:", font=("Arial", 10),
                 bg="#0e1117", fg="#aaaaaa").pack(anchor="w", padx=30)
        host_var = tk.StringVar(value="localhost")
        tk.Entry(win, textvariable=host_var, font=("Arial", 11), width=28,
                 bg="#1e2130", fg="white", insertbackground="white",
                 relief="flat", justify="center").pack(pady=(2, 10), ipady=5)

        # ── Lobby code ───────────────────────────────────────────────────────
        tk.Label(win, text="Lobby code (4 letters):", font=("Arial", 10),
                 bg="#0e1117", fg="#aaaaaa").pack(anchor="w", padx=30)

        code_var = tk.StringVar(value=_random_lobby_code())

        def _enforce_code(*_):
            val = code_var.get().upper().replace(" ", "")[:4]
            # Only allow letters
            val = "".join(c for c in val if c.isalpha())
            code_var.set(val)

        code_entry = tk.Entry(win, textvariable=code_var, font=("Arial", 14, "bold"),
                              width=8, bg="#1e2130", fg="#1e90ff",
                              insertbackground="white", relief="flat",
                              justify="center")
        code_entry.pack(pady=(2, 6), ipady=6)
        code_var.trace_add("write", _enforce_code)

        tk.Button(win, text="New Code", font=("Arial", 8),
                  bg="#151820", fg="#555",
                  activebackground="#1e2130", relief="flat",
                  command=lambda: code_var.set(_random_lobby_code())
                  ).pack(pady=(0, 12))

        # ── Status label ─────────────────────────────────────────────────────
        status_var = tk.StringVar(value="Enter a lobby code and press Join.")
        status_lbl = tk.Label(win, textvariable=status_var,
                              font=("Arial", 10), bg="#0e1117", fg="#aaaaaa",
                              wraplength=360)
        status_lbl.pack(pady=(0, 8))

        # ── Player list ──────────────────────────────────────────────────────
        tk.Label(win, text="Players in lobby:", font=("Arial", 9),
                 bg="#0e1117", fg="#555").pack(anchor="w", padx=30)

        players_frame = tk.Frame(win, bg="#111520", width=360, height=100)
        players_frame.pack(padx=30, pady=(4, 12), fill="x")
        players_frame.pack_propagate(False)
        self._lobby_players_frame = players_frame

        # ── Buttons ──────────────────────────────────────────────────────────
        btn_row = tk.Frame(win, bg="#0e1117")
        btn_row.pack(pady=8)

        join_btn = tk.Button(btn_row, text="Join Lobby",
                             font=("Arial", 11, "bold"),
                             bg="#1e4080", fg="white",
                             activebackground="#2a5090", relief="flat",
                             padx=22, pady=8)
        join_btn.pack(side="left", padx=8)

        leave_btn = tk.Button(btn_row, text="Leave",
                              font=("Arial", 11),
                              bg="#2a1010", fg="#ff4444",
                              activebackground="#3a1515", relief="flat",
                              padx=22, pady=8,
                              command=lambda: self._lobby_leave(win))
        leave_btn.pack(side="left", padx=8)

        # ── Wire up join ─────────────────────────────────────────────────────
        def _on_join():
            host = host_var.get().strip()
            code = code_var.get().strip().upper()
            if len(code) != 4:
                status_var.set("Lobby code must be exactly 4 letters.")
                status_lbl.config(fg="#ff4444")
                return
            if not host:
                status_var.set("Please enter a server host.")
                status_lbl.config(fg="#ff4444")
                return
            join_btn.config(state="disabled")
            status_var.set("Connecting...")
            status_lbl.config(fg="#ffaa00")
            win.update_idletasks()
            self._lobby_connect(host, code, status_var, status_lbl, join_btn, win)

        join_btn.config(command=_on_join)

        # Clean up on window close
        win.protocol("WM_DELETE_WINDOW", lambda: self._lobby_leave(win))

    def _update_lobby_players(self, names):
        """Rebuild the player list display in the lobby window."""
        frame = getattr(self, "_lobby_players_frame", None)
        if frame is None or not frame.winfo_exists():
            return
        for w in frame.winfo_children():
            w.destroy()
        colors = ["#00ff90", "#ff9900", "#1e90ff"]
        for i, name in enumerate(names):
            color = colors[i % len(colors)]
            tk.Label(frame, text=f"  {name}",
                     font=("Arial", 10, "bold"), bg="#111520", fg=color,
                     anchor="w").pack(fill="x", padx=6, pady=2)

    def _lobby_connect(self, host, code, status_var, status_lbl, join_btn, win):
        """Attempt TCP connection and send join message."""
        import threading

        def _do_connect():
            try:
                client = NetworkClient()
                client.connect(host, port=5555)
            except Exception as e:
                self.root.after(0, lambda: (
                    status_var.set(f"Connection failed: {e}"),
                    status_lbl.config(fg="#ff4444"),
                    join_btn.config(state="normal"),
                ))
                return

            self.net_client = client

            # Register incoming message handler
            client.add_callback(
                lambda msg: self.root.after(0, lambda m=msg: self._handle_network_message(m))
            )

            # Store lobby context on self for use in callbacks
            self._mp_status_var  = status_var
            self._mp_status_lbl  = status_lbl
            self._mp_join_btn    = join_btn
            self._mp_lobby_win   = win
            self._mp_lobby_code  = code

            # Send join
            client.send({
                "type":     "join",
                "lobby_id": code,
                "name":     self.username,
                "country":  self.country,
            })

        threading.Thread(target=_do_connect, daemon=True).start()

    def _lobby_leave(self, win=None):
        """Leave / close the lobby."""
        if self.net_client and self.net_client.connected:
            self.net_client.send({"type": "leave"})
            self.net_client.disconnect()
        self.net_client = None
        target = win or getattr(self, "_lobby_win", None)
        if target and target.winfo_exists():
            try:
                target.destroy()
            except Exception:
                pass

    # ──────────────────────────────────────────────────────────────────────────
    # 2.  Start Multiplayer Game
    # ──────────────────────────────────────────────────────────────────────────

    def _start_multiplayer_game(self, players):
        """
        Called when the server sends game_start.
        players is a list of dicts: [{"name": ...}, ...]
        """
        self.is_multiplayer = True

        # Build rivals dict from the other players (not ourselves)
        self.rivals = {}
        color_idx = 0
        for p in players:
            name = p.get("name", "Unknown")
            if name == self.username:
                continue
            color = _MP_COLORS[color_idx % len(_MP_COLORS)]
            color_idx += 1
            self.rivals[name] = {
                "money":          0,
                "days":           0,
                "happiness":      50,
                "public_opinion": 75,
                "transgressions": 0,
                "country":        p.get("country", ""),
                "color":          color,
                "disconnected":   False,
                # Keep an empty controls dict so existing rival-control
                # logic (is_rival_controlled, etc.) doesn't crash.
                "controls":       {},
            }

        # Close lobby window if still open
        lobby_win = getattr(self, "_mp_lobby_win", None) or getattr(self, "_lobby_win", None)
        if lobby_win and lobby_win.winfo_exists():
            try:
                lobby_win.destroy()
            except Exception:
                pass

        # Start the game (skip init_rivals — rivals already set above)
        self.show_screen("game")
        self._start_game_skip_rivals()

    def _start_game_skip_rivals(self):
        """
        Like start_game() but does NOT call init_rivals(),
        because multiplayer rivals are already populated.
        """
        import threading as _threading
        self.money   = 100_000_000
        self.days    = 0
        self.running = True
        self.market.money = self.money
        self._init_flags_keep_rivals()
        legacy = self._load_legacy()
        if legacy > 0:
            self.money += legacy
            self.market.money = self.money
            self.log_event(f"Legacy bonus applied: +${legacy:,}")
        # rivals already set — do NOT call init_rivals()
        self.clock_seconds = 0
        self.log_event(f"Welcome, {self.username}. Multiplayer match starting...")
        names = ", ".join(self.rivals.keys())
        self.log_event(f"Opponents: {names}")
        self.log_event("Fetching live stock data for all markets...")
        self.update_status()
        _threading.Thread(target=self.fetch_real_stock_data, daemon=True).start()

    def _init_flags_keep_rivals(self):
        """
        Re-initialise game flags without overwriting self.rivals.
        """
        saved_rivals = self.rivals
        self._init_flags()
        self.rivals = saved_rivals
        self.is_multiplayer = True

    # ──────────────────────────────────────────────────────────────────────────
    # 3.  Outgoing state broadcast
    # ──────────────────────────────────────────────────────────────────────────

    def _send_game_state(self):
        """Send current game state to the server for broadcast."""
        if not self.net_client or not self.net_client.connected:
            return
        self.net_client.send({
            "type": "state",
            "state": {
                "money":          int(self.money),
                "days":           self.days,
                "happiness":      round(self.happiness, 1),
                "public_opinion": round(self.public_opinion, 1),
                "transgressions": round(self.transgressions, 1),
                "country":        self.country,
                "militia":        getattr(self, "militia", 0),
            },
        })

    # ──────────────────────────────────────────────────────────────────────────
    # 4.  Incoming message handler
    # ──────────────────────────────────────────────────────────────────────────

    def _handle_network_message(self, msg):
        """
        Processes messages from the server.
        Always called via root.after(0, ...) so it runs on the main thread.
        """
        mtype = msg.get("type")

        # ── Lobby messages ────────────────────────────────────────────────────
        if mtype == "lobby_joined":
            count   = msg.get("player_count", 1)
            maximum = msg.get("max", 3)
            players = msg.get("players", [])
            sv  = getattr(self, "_mp_status_var", None)
            slbl = getattr(self, "_mp_status_lbl", None)
            if sv:
                sv.set(f"Waiting for players ({count}/{maximum})...")
                if slbl:
                    slbl.config(fg="#00ff90")
            self._update_lobby_players(players)

        elif mtype == "player_joined":
            count   = msg.get("player_count", 1)
            players = msg.get("players", [])
            sv   = getattr(self, "_mp_status_var", None)
            slbl = getattr(self, "_mp_status_lbl", None)
            if sv:
                sv.set(f"Waiting for players ({count}/3)...")
                if slbl:
                    slbl.config(fg="#00ff90")
            self._update_lobby_players(players)

        elif mtype == "game_start":
            players = msg.get("players", [])
            sv   = getattr(self, "_mp_status_var", None)
            slbl = getattr(self, "_mp_status_lbl", None)
            if sv:
                sv.set("Game starting!")
                if slbl:
                    slbl.config(fg="#00ff90")
            # Small delay so user sees the message
            self.root.after(600, lambda: self._start_multiplayer_game(players))

        elif mtype == "error":
            err  = msg.get("msg", "Unknown error")
            sv   = getattr(self, "_mp_status_var", None)
            slbl = getattr(self, "_mp_status_lbl", None)
            btn  = getattr(self, "_mp_join_btn", None)
            if sv:
                sv.set(f"Error: {err}")
                if slbl:
                    slbl.config(fg="#ff4444")
            if btn:
                btn.config(state="normal")

        # ── In-game messages ──────────────────────────────────────────────────
        elif mtype == "player_update":
            name  = msg.get("name")
            state = msg.get("state", {})
            if name and name in self.rivals:
                self.rivals[name].update({
                    "money":          state.get("money",          self.rivals[name].get("money", 0)),
                    "days":           state.get("days",           self.rivals[name].get("days", 0)),
                    "happiness":      state.get("happiness",      self.rivals[name].get("happiness", 50)),
                    "public_opinion": state.get("public_opinion", self.rivals[name].get("public_opinion", 75)),
                    "transgressions": state.get("transgressions", self.rivals[name].get("transgressions", 0)),
                    "country":        state.get("country",        self.rivals[name].get("country", "")),
                    "militia":        state.get("militia",        self.rivals[name].get("militia", 0)),
                })

        elif mtype == "player_left":
            name = msg.get("name")
            if name and name in self.rivals:
                self.rivals[name]["disconnected"] = True
                self.log_event(f"[MULTIPLAYER] {name} has left the game.")

        elif mtype == "chat":
            name = msg.get("name", "?")
            text = msg.get("text", "")
            # Append to chat window if open
            self._append_chat(name, text)
            # Also put a brief notice in the game log
            self.log_event(f"💬 {name}: {text}")

        elif mtype == "war":
            attacker       = msg.get("attacker", "?")
            target_country = msg.get("target_country", "?")
            victim         = msg.get("victim", "")
            # Am I the victim?
            if victim == self.username:
                damage = 10_000_000
                self.money -= damage
                self.market.money = self.money
                self.add_transgression(20, 15)
                if attacker not in getattr(self, "active_wars", {}):
                    self.active_wars[attacker] = 15
                self.log_event(
                    f"⚔️  WAR DECLARED! {attacker} bombed {target_country}. "
                    f"You lose ${damage:,} and face a $1.5M/day war tax for 15 days!")
                self._add_ticker(
                    f"WAR: {attacker} launches military strike on {target_country}!")
                self.update_status()
            elif attacker != self.username:
                self.log_event(
                    f"⚔️  [{attacker}] declared war on [{victim}] — {target_country} bombed.")

        elif mtype == "war_action":
            attacker  = msg.get("attacker", "?")
            action_id = msg.get("action_id", "")
            target    = msg.get("target", "")
            meta      = msg.get("meta", {})
            if target == self.username:
                self.receive_war_action(attacker, action_id, meta)

        elif mtype == "disconnected":
            self.log_event("[MULTIPLAYER] Disconnected from server.")
            self.is_multiplayer = False
            if self.net_client:
                self.net_client.disconnect()
                self.net_client = None

    # ──────────────────────────────────────────────────────────────────────────
    # 5.  War declaration
    # ──────────────────────────────────────────────────────────────────────────

    def _declare_war_on_player(self, rival_name, country):
        """Called when you bomb a country owned by rival_name."""
        if rival_name in getattr(self, "active_wars", {}):
            return   # already at war

        self.active_wars[rival_name] = 15
        extra_trans = 20
        self.add_transgression(extra_trans, 15)
        self.log_event(
            f"⚔️  You bombed {country} — the home country of {rival_name}! "
            f"War declared. +$1.5M/day war tax for 15 days.")
        self._add_ticker(f"WAR: You have declared war on {rival_name}!")

        if self.net_client and self.net_client.connected:
            self.net_client.send({
                "type":           "war",
                "target_country": country,
                "victim":         rival_name,
            })
        self.update_status()

    # ──────────────────────────────────────────────────────────────────────────
    # 6.  Chat window
    # ──────────────────────────────────────────────────────────────────────────

    def open_chat_window(self):
        """Open (or focus) the multiplayer chat window."""
        if not getattr(self, "is_multiplayer", False):
            self.log_event("Chat is only available in multiplayer.")
            return

        # If already open, just focus it
        existing = getattr(self, "_chat_win", None)
        if existing and existing.winfo_exists():
            existing.lift()
            return

        win = tk.Toplevel(self.root)
        win.title("💬 Multiplayer Chat")
        win.configure(bg="#0e1117")
        win.geometry("360x440")
        win.resizable(False, True)
        self._chat_win = win

        tk.Label(win, text="💬  CHAT",
                 font=("Impact", 16), bg="#0e1117", fg="#1e90ff").pack(pady=(10, 4))

        # ── Message display ───────────────────────────────────────────
        from tkinter import scrolledtext
        self._chat_display = scrolledtext.ScrolledText(
            win, state="disabled", height=18,
            bg="#0a0d13", fg="#dddddd",
            font=("Consolas", 9), relief="flat",
            insertbackground="white", wrap="word")
        self._chat_display.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        # colour tags for each player
        self._chat_display.tag_configure("self_name",  foreground="#00ff90", font=("Consolas", 9, "bold"))
        self._chat_display.tag_configure("other_name", foreground="#ff9900", font=("Consolas", 9, "bold"))
        self._chat_display.tag_configure("system",     foreground="#555555", font=("Consolas", 8, "italic"))

        # ── Input row ────────────────────────────────────────────────
        inp_row = tk.Frame(win, bg="#0e1117")
        inp_row.pack(fill="x", padx=10, pady=(0, 10))

        msg_var = tk.StringVar()
        entry = tk.Entry(inp_row, textvariable=msg_var, font=("Arial", 10),
                         bg="#1e2130", fg="white", insertbackground="white",
                         relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))

        def _send(*_):
            text = msg_var.get().strip()
            if not text:
                return
            msg_var.set("")
            if self.net_client and self.net_client.connected:
                self.net_client.send({"type": "chat", "text": text})
            else:
                self.log_event("Chat: not connected.")

        entry.bind("<Return>", _send)
        tk.Button(inp_row, text="➤", font=("Arial", 11, "bold"),
                  bg="#1e4080", fg="white", relief="flat",
                  padx=10, pady=4, command=_send).pack(side="right")

        entry.focus_set()

    def _append_chat(self, sender, text):
        """Add a message to the chat display (if window is open)."""
        win = getattr(self, "_chat_win", None)
        disp = getattr(self, "_chat_display", None)
        if not win or not win.winfo_exists() or not disp:
            return
        disp.config(state="normal")
        tag = "self_name" if sender == self.username else "other_name"
        disp.insert("end", f"{sender}: ", tag)
        disp.insert("end", f"{text}\n")
        disp.see("end")
        disp.config(state="disabled")
