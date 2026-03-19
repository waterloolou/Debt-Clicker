import tkinter as tk
import random
import math
import threading
import sys
import struct
import wave
import io
import subprocess
import os

try:
    import winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False


def _make_wav(freqs_durs) -> bytes:
    """Generate a raw WAV file in memory from a list of (freq_hz, duration_ms) pairs."""
    sample_rate = 44100
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        for freq, dur_ms in freqs_durs:
            n = int(sample_rate * dur_ms / 1000)
            import math as _m
            frames = b''.join(
                struct.pack('<h', int(28000 * _m.sin(2 * _m.pi * freq * i / sample_rate)))
                for i in range(n)
            )
            w.writeframes(frames)
    return buf.getvalue()


def _play_sound(kind="win"):
    """Play a non-blocking win / jackpot / loss sound (cross-platform)."""
    SOUNDS = {
        "jackpot": [(880,80),(1100,80),(1320,80),(1100,60),(1320,60),(1760,300)],
        "win":     [(880,80),(1100,80),(1320,200)],
        "loss":    [(440,120),(330,200)],
    }
    freqs = SOUNDS.get(kind, SOUNDS["win"])

    def _run():
        if _HAS_WINSOUND:
            for f, d in freqs:
                winsound.Beep(f, d)
        elif sys.platform == "darwin":
            # macOS: write WAV to temp file, play with afplay
            try:
                wav = _make_wav(freqs)
                tmp = "/tmp/_dc_sound.wav"
                with open(tmp, "wb") as fh:
                    fh.write(wav)
                subprocess.run(["afplay", tmp],
                               check=False, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            except Exception:
                pass
        else:
            # Linux: try paplay (PulseAudio) then aplay (ALSA) then silence
            try:
                wav = _make_wav(freqs)
                tmp = "/tmp/_dc_sound.wav"
                with open(tmp, "wb") as fh:
                    fh.write(wav)
                for player in ("paplay", "aplay"):
                    if subprocess.run(["which", player],
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL).returncode == 0:
                        subprocess.run([player, tmp],
                                       check=False, stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                        break
            except Exception:
                pass

    threading.Thread(target=_run, daemon=True).start()


class CasinoMixin:
    """Casino lobby, Russian Roulette, Slot Machine, Poker, and Work."""

    # =========================================================
    # CASINO LOBBY
    # =========================================================

    def open_casino(self):
        win = tk.Toplevel(self.root)
        win.title("Casino")
        win.configure(bg="#0e1117")
        win.geometry("500x300")
        win.resizable(False, False)

        tk.Label(win, text="🎰  CASINO  🎰",
                 font=("Impact", 28), bg="#0e1117", fg="#ffdd44").pack(pady=(24, 18))

        cards_frame = tk.Frame(win, bg="#0e1117")
        cards_frame.pack()

        games = [
            ("🔫", "Russian\nRoulette", "1-in-6 chance of death.\nSurvive to double your bet.", self._open_russian_roulette),
            ("🎰", "Slot\nMachine",    "Spin 3 reels.\nMatch symbols to win big.",           self._open_slot_machine),
            ("🂡", "Poker",            "5-card draw.\nBet first, then see your hand.",        self._open_poker),
        ]

        for icon, title, desc, cmd in games:
            card = tk.Frame(cards_frame, bg="#1e2130", padx=14, pady=14)
            card.pack(side="left", padx=10)

            tk.Label(card, text=icon, font=("Arial", 32), bg="#1e2130").pack()
            tk.Label(card, text=title, font=("Arial", 11, "bold"),
                     bg="#1e2130", fg="white", justify="center").pack(pady=(4, 2))
            tk.Label(card, text=desc, font=("Arial", 8),
                     bg="#1e2130", fg="#888888", justify="center").pack()
            tk.Button(card, text="Play", font=("Arial", 10, "bold"),
                      bg="#ff2222", fg="white", relief="flat",
                      padx=16, pady=4,
                      command=lambda c=cmd, w=win: [w.destroy(), c()]).pack(pady=(10, 0))

    # =========================================================
    # RUSSIAN ROULETTE
    # =========================================================

    def _open_russian_roulette(self):
        win = tk.Toplevel(self.root)
        win.title("Russian Roulette")
        win.configure(bg="#0e1117")
        win.geometry("420x520")
        win.resizable(False, False)

        tk.Label(win, text="🔫 Russian Roulette",
                 font=("Impact", 22), bg="#0e1117", fg="#ff2222").pack(pady=(18, 4))
        tk.Label(win, text="1 bullet. 6 chambers. Are you feeling lucky?",
                 font=("Arial", 9), bg="#0e1117", fg="#888").pack(pady=(0, 12))

        canvas = tk.Canvas(win, width=220, height=220, bg="#0e1117", highlightthickness=0)
        canvas.pack()

        self._rr_bullet   = random.randint(0, 5)
        self._rr_fired    = False
        self._rr_canvas   = canvas
        self._rr_revealed = False
        self._rr_spinning = False
        win.protocol("WM_DELETE_WINDOW", lambda: [setattr(self, '_rr_spinning', False), win.destroy()])
        self._draw_rr_cylinder()

        bet_frame = tk.Frame(win, bg="#0e1117")
        bet_frame.pack(pady=10)
        tk.Label(bet_frame, text="Bet: $", font=("Arial", 11), bg="#0e1117", fg="white").pack(side="left")
        self._rr_bet_var = tk.StringVar(value="1000000")
        tk.Entry(bet_frame, textvariable=self._rr_bet_var, width=12,
                 bg="#1e2130", fg="white", font=("Arial", 11),
                 insertbackground="white", relief="flat").pack(side="left", ipady=4)

        self._rr_result = tk.Label(win, text="", font=("Arial", 11, "bold"),
                                   bg="#0e1117", fg="white")
        self._rr_result.pack(pady=6)

        btn_frame = tk.Frame(win, bg="#0e1117")
        btn_frame.pack()

        self._rr_spin_btn = tk.Button(btn_frame, text="🔄  Spin Cylinder",
                  font=("Arial", 10), bg="#1e2130", fg="white", relief="flat",
                  padx=14, pady=6, command=self._rr_spin)
        self._rr_spin_btn.pack(side="left", padx=8)

        self._rr_fire_btn = tk.Button(btn_frame, text="🔫  Fire",
                  font=("Arial", 10, "bold"), bg="#ff2222", fg="white", relief="flat",
                  padx=14, pady=6, command=lambda: self._rr_fire(win))
        self._rr_fire_btn.pack(side="left", padx=8)

    def _draw_rr_cylinder(self, reveal=False):
        c = self._rr_canvas
        c.delete("all")
        cx, cy, ring_r, cham_r = 110, 110, 70, 22

        c.create_oval(cx-ring_r-cham_r-8, cy-ring_r-cham_r-8,
                      cx+ring_r+cham_r+8, cy+ring_r+cham_r+8,
                      outline="#444", width=3, fill="#111")
        c.create_oval(cx-18, cy-18, cx+18, cy+18, fill="#555", outline="#888", width=2)

        for i in range(6):
            angle = math.radians(i * 60 - 90)
            x = cx + ring_r * math.cos(angle)
            y = cy + ring_r * math.sin(angle)
            if reveal and i == self._rr_bullet:
                fill, outline = "#ff2222", "#ff6666"
            elif reveal:
                fill, outline = "#2a2a2a", "#555"
            else:
                fill, outline = "#2a2a2a", "#666"
            c.create_oval(x-cham_r, y-cham_r, x+cham_r, y+cham_r,
                          fill=fill, outline=outline, width=2)
            if reveal and i == self._rr_bullet:
                c.create_text(x, y, text="💀", font=("Arial", 14))
            else:
                c.create_oval(x-8, y-8, x+8, y+8, fill="#333", outline="#555")

        c.create_polygon(cx-8, cy-ring_r-cham_r-12,
                         cx+8, cy-ring_r-cham_r-12,
                         cx,   cy-ring_r-cham_r-2,
                         fill="#ffdd44", outline="")

    def _rr_spin(self):
        self._rr_bullet   = random.randint(0, 5)
        self._rr_revealed = False
        self._rr_spinning = True
        self._rr_result.config(text="")
        self._animate_rr_spin(0)

    def _animate_rr_spin(self, step):
        if not self._rr_spinning:
            return
        try:
            if step < 12:
                c = self._rr_canvas
                c.delete("all")
                cx, cy, ring_r, cham_r = 110, 110, 70, 22
                c.create_oval(cx-ring_r-cham_r-8, cy-ring_r-cham_r-8,
                              cx+ring_r+cham_r+8, cy+ring_r+cham_r+8,
                              outline="#444", width=3, fill="#111")
                c.create_oval(cx-18, cy-18, cx+18, cy+18, fill="#555", outline="#888", width=2)
                offset = step * 5
                for i in range(6):
                    angle = math.radians(i * 60 - 90 + offset)
                    x = cx + ring_r * math.cos(angle)
                    y = cy + ring_r * math.sin(angle)
                    c.create_oval(x-cham_r, y-cham_r, x+cham_r, y+cham_r,
                                  fill="#2a2a2a", outline="#666", width=2)
                    c.create_oval(x-8, y-8, x+8, y+8, fill="#333", outline="#555")
                c.create_polygon(cx-8, cy-ring_r-cham_r-12,
                                 cx+8, cy-ring_r-cham_r-12,
                                 cx,   cy-ring_r-cham_r-2,
                                 fill="#ffdd44", outline="")
                delay = 40 + step * 15
                self.root.after(delay, lambda: self._animate_rr_spin(step + 1))
            else:
                self._rr_spinning = False
                self._draw_rr_cylinder()
                self._rr_result.config(text="Cylinder spun. Ready to fire.", fg="#aaaaaa")
        except tk.TclError:
            self._rr_spinning = False

    def _rr_fire(self, win):
        try:
            bet = float(self._rr_bet_var.get().replace(",", ""))
        except ValueError:
            self._rr_result.config(text="Invalid bet.", fg="#ff4444")
            return

        self._rr_spinning = False
        self._rr_spin_btn.config(state="disabled")
        self._rr_fire_btn.config(state="disabled")
        self._draw_rr_cylinder(reveal=True)

        if self._rr_bullet == 0:
            self._rr_result.config(text="💀 BANG. You're dead.", fg="#ff2222")
            self.log_event("You lost at Russian Roulette. RIP.")
            self.running = False
            self.death_cause = "roulette"
            def _die():
                win.destroy()
                self._show_end_screen()
            win.after(2000, _die)
        else:
            winnings = bet
            self.money += winnings
            self.market.money = self.money
            self.update_status()
            self._rr_result.config(text=f"✅ CLICK. You survived! +${winnings:,.0f}", fg="#00ff90")
            self.log_event(f"Survived Russian Roulette! +${winnings:,.0f}")
            win.after(2000, win.destroy)

    # =========================================================
    # SLOT MACHINE  (colored canvas symbols + win flash + sound)
    # =========================================================

    SLOT_SYMBOLS = ["cherry", "lemon", "orange", "grapes", "diamond", "seven"]
    SLOT_PAYOUTS = {
        ("seven",   "seven",   "seven"):   ("JACKPOT 777!",   100),
        ("diamond", "diamond", "diamond"): ("Triple Diamond!", 50),
        ("cherry",  "cherry",  "cherry"):  ("Triple Cherry!",  10),
        ("lemon",   "lemon",   "lemon"):   ("Triple Lemon!",   10),
        ("orange",  "orange",  "orange"):  ("Triple Orange!",  10),
        ("grapes",  "grapes",  "grapes"):  ("Triple Grapes!",  10),
    }

    def _draw_slot_symbol(self, canvas, symbol):
        """Draw a colorful slot symbol on a 90×110 canvas."""
        canvas.delete("all")
        W, H = 90, 110
        cx, cy = W // 2, H // 2

        if symbol == "seven":
            canvas.create_rectangle(4, 4, W-4, H-4, fill="#1a0000", outline="#ff2222", width=2)
            canvas.create_text(cx, cy+4, text="7", font=("Impact", 52, "bold"),
                               fill="#ff2222")
            canvas.create_text(cx, cy+4, text="7", font=("Impact", 52, "bold"),
                               fill="#ff2222")

        elif symbol == "diamond":
            pts = [cx, 12, W-10, cy, cx, H-12, 10, cy]
            canvas.create_polygon(pts, fill="#00ccff", outline="#aaeeff", width=2)
            # inner highlight
            inner = [cx, 24, W-22, cy, cx, H-24, 22, cy]
            canvas.create_polygon(inner, fill="#66eeff", outline="", stipple="")
            canvas.create_text(cx, cy, text="◆", font=("Arial", 18, "bold"), fill="white")

        elif symbol == "cherry":
            # stems
            canvas.create_line(cx-12, 38, cx-2, 22, fill="#226600", width=2)
            canvas.create_line(cx+12, 38, cx+2, 22, fill="#226600", width=2)
            canvas.create_line(cx-2, 22, cx+2, 22, fill="#226600", width=2)
            # left cherry
            canvas.create_oval(cx-28, 38, cx+4, H-18, fill="#cc0000", outline="#ff4444", width=2)
            canvas.create_oval(cx-24, 40, cx-8, 52, fill="#ff6666", outline="")
            # right cherry
            canvas.create_oval(cx-4, 38, cx+28, H-18, fill="#cc0000", outline="#ff4444", width=2)
            canvas.create_oval(cx+4, 40, cx+20, 52, fill="#ff6666", outline="")

        elif symbol == "lemon":
            canvas.create_oval(14, 20, W-14, H-20, fill="#eecc00", outline="#ffee44", width=2)
            # bumps
            canvas.create_oval(cx-6, 14, cx+6, 26, fill="#ddbb00", outline="#ffee44", width=1)
            canvas.create_oval(cx-6, H-26, cx+6, H-14, fill="#ddbb00", outline="#ffee44", width=1)
            # shine
            canvas.create_oval(22, 28, 40, 44, fill="#ffee88", outline="")

        elif symbol == "orange":
            canvas.create_oval(12, 14, W-12, H-14, fill="#ee7700", outline="#ffaa33", width=2)
            # leaf
            pts = [cx-4, 10, cx+14, 2, cx+8, 16]
            canvas.create_polygon(pts, fill="#228800", outline="#44aa00", width=1)
            # shine
            canvas.create_oval(20, 22, 40, 40, fill="#ffcc77", outline="")

        elif symbol == "grapes":
            # leaf
            canvas.create_oval(cx-14, 6, cx+14, 24, fill="#228822", outline="#44aa44", width=1)
            # stem
            canvas.create_line(cx, 20, cx, 30, fill="#664400", width=2)
            # grape cluster – 3 rows
            positions = [(cx, 38), (cx-14, 52), (cx+14, 52),
                         (cx-7, 66), (cx+7, 66), (cx, 80)]
            for gx, gy in positions:
                canvas.create_oval(gx-11, gy-11, gx+11, gy+11,
                                   fill="#8800cc", outline="#cc66ff", width=1)
                canvas.create_oval(gx-7, gy-9, gx-1, gy-3, fill="#cc88ff", outline="")

    def _open_slot_machine(self):
        win = tk.Toplevel(self.root)
        win.title("Slot Machine")
        win.configure(bg="#0e1117")
        win.geometry("440x520")
        win.resizable(False, False)
        self._slot_win = win

        tk.Label(win, text="🎰 Slot Machine",
                 font=("Impact", 22), bg="#0e1117", fg="#ffdd44").pack(pady=(18, 4))

        self._slot_reel_frame = tk.Frame(win, bg="#ffdd44", relief="ridge", bd=4)
        self._slot_reel_frame.pack(pady=12)

        inner = tk.Frame(self._slot_reel_frame, bg="#222")
        inner.pack(padx=4, pady=4)

        self._slot_canvases = []
        for i in range(3):
            c = tk.Canvas(inner, width=90, height=110,
                          bg="#111", highlightthickness=2, highlightbackground="#444")
            c.pack(side="left", padx=5, pady=6)
            self._slot_canvases.append(c)
            self._draw_slot_symbol(c, "cherry")

        bet_frame = tk.Frame(win, bg="#0e1117")
        bet_frame.pack(pady=8)
        tk.Label(bet_frame, text="Bet: $", font=("Arial", 11), bg="#0e1117", fg="white").pack(side="left")
        self._slot_bet_var = tk.StringVar(value="500000")
        tk.Entry(bet_frame, textvariable=self._slot_bet_var, width=12,
                 bg="#1e2130", fg="white", font=("Arial", 11),
                 insertbackground="white", relief="flat").pack(side="left", ipady=4)

        self._slot_result = tk.Label(win, text="Press SPIN to play!",
                                     font=("Arial", 12, "bold"), bg="#0e1117", fg="#aaaaaa")
        self._slot_result.pack(pady=8)

        self._slot_btn = tk.Button(win, text="🎰  SPIN",
                                   font=("Arial", 13, "bold"), bg="#ffdd44", fg="#111",
                                   activebackground="#ffcc00", relief="flat",
                                   padx=30, pady=8,
                                   command=lambda: self._spin_slots(win))
        self._slot_btn.pack()

    def _spin_slots(self, win):
        try:
            bet = float(self._slot_bet_var.get().replace(",", ""))
        except ValueError:
            self._slot_result.config(text="Invalid bet.", fg="#ff4444")
            return
        max_bet = min(30_000_000, self.money * 0.20)
        if bet > max_bet:
            self._slot_result.config(text=f"Max bet: ${max_bet:,.0f} (20% of balance)", fg="#ff4444")
            return
        if bet > self.money:
            self._slot_result.config(text="Not enough money.", fg="#ff4444")
            return

        self._slot_btn.config(state="disabled")
        self._slot_result.config(text="Spinning...", fg="#aaaaaa")
        final = [random.choice(self.SLOT_SYMBOLS) for _ in range(3)]
        self._animate_slots(final, 0, 28, bet, win)

    def _animate_slots(self, final, step, total, bet, win):
        if step < total:
            for c in self._slot_canvases:
                self._draw_slot_symbol(c, random.choice(self.SLOT_SYMBOLS))
            delay = max(30, 90 - step * 2)
            self.root.after(delay, lambda: self._animate_slots(final, step+1, total, bet, win))
        else:
            for c, sym in zip(self._slot_canvases, final):
                self._draw_slot_symbol(c, sym)
            self._evaluate_slots(tuple(final), bet)
            self._slot_btn.config(state="normal")

    def _evaluate_slots(self, result, bet):
        is_jackpot = False
        if result in self.SLOT_PAYOUTS:
            label, mult = self.SLOT_PAYOUTS[result]
            winnings = bet * mult
            self.money += winnings
            is_jackpot = mult >= 50
            color = "#ffdd44" if mult < 50 else "#ff2222"
            self._slot_result.config(text=f"{label}  +${winnings:,.0f}", fg=color)
            self.log_event(f"Slots: {label} +${winnings:,.0f}")
            _play_sound("jackpot" if is_jackpot else "win")
            self._flash_reels(6, is_jackpot)
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            winnings = bet * 2
            self.money += winnings
            self._slot_result.config(text=f"Two of a kind! +${winnings:,.0f}", fg="#00ff90")
            self.log_event(f"Slots: two of a kind +${winnings:,.0f}")
            _play_sound("win")
            self._flash_reels(4, False)
        else:
            self.money -= bet
            self._slot_result.config(text=f"No match. Lost ${bet:,.0f}", fg="#ff4444")
            self.log_event(f"Slots: no match, lost ${bet:,.0f}")
            _play_sound("loss")
        self.market.money = self.money
        self.update_status()

    def _flash_reels(self, times, jackpot):
        colors = (["#ffdd44", "#ff2222"] * (times * 2)) if jackpot else (["#ffdd44", "#00ff90"] * times)
        colors += ["#ffdd44"]   # end on gold

        def _step(idx=0):
            try:
                if idx >= len(colors):
                    return
                self._slot_reel_frame.config(bg=colors[idx])
                delay = 80 if jackpot else 120
                self.root.after(delay, lambda: _step(idx + 1))
            except tk.TclError:
                pass

        _step()

    # =========================================================
    # POKER (5-card draw)  —  Bet → Deal → Hold → Draw
    # =========================================================

    RANKS     = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    SUITS     = ['♠','♥','♦','♣']
    SUIT_COLORS = {'♠':'#222222','♣':'#222222','♥':'#cc0000','♦':'#cc0000'}
    RANK_VAL  = {r: i for i, r in enumerate(['2','3','4','5','6','7','8','9','10','J','Q','K','A'])}

    def _open_poker(self):
        win = tk.Toplevel(self.root)
        win.title("Poker - 5 Card Draw")
        win.configure(bg="#0e1117")
        win.geometry("520x560")
        win.resizable(False, False)

        tk.Label(win, text="🂡 5-Card Draw Poker",
                 font=("Impact", 22), bg="#0e1117", fg="#00ff90").pack(pady=(18, 4))
        tk.Label(win, text="Set your bet → Deal → Hold cards → Draw",
                 font=("Arial", 9), bg="#0e1117", fg="#888").pack()

        pay_frame = tk.Frame(win, bg="#0e1117")
        pay_frame.pack(pady=6)
        payouts = [("Royal Flush","250x"),("Straight Flush","50x"),("Four of a Kind","25x"),
                   ("Full House","9x"),("Flush","6x"),("Straight","4x"),
                   ("Three of a Kind","3x"),("Two Pair","2x"),("Jacks or Better","1x")]
        for i, (hand, mult) in enumerate(payouts):
            tk.Label(pay_frame, text=f"{hand}: {mult}", font=("Arial", 7),
                     bg="#0e1117", fg="#666666").grid(row=i // 3, column=i % 3, padx=8)

        card_frame = tk.Frame(win, bg="#0e1117")
        card_frame.pack(pady=12)

        self._poker_held     = [False] * 5
        self._poker_hand     = []
        self._poker_canvases = []
        self._poker_win      = win
        self._poker_phase    = "bet"   # "bet" | "hold"

        for i in range(5):
            c = tk.Canvas(card_frame, width=72, height=100,
                          bg="#1a2a3a", highlightthickness=2,
                          highlightbackground="#333", cursor="hand2")
            c.pack(side="left", padx=4)
            c.bind("<Button-1>", lambda e, idx=i: self._toggle_hold(idx))
            self._poker_canvases.append(c)
            self._draw_card_back(c)

        self._poker_hold_labels = []
        hold_frame = tk.Frame(win, bg="#0e1117")
        hold_frame.pack()
        for _ in range(5):
            lbl = tk.Label(hold_frame, text="", font=("Arial", 9, "bold"),
                           bg="#0e1117", fg="#ffdd44", width=8)
            lbl.pack(side="left", padx=4)
            self._poker_hold_labels.append(lbl)

        bet_frame = tk.Frame(win, bg="#0e1117")
        bet_frame.pack(pady=8)
        tk.Label(bet_frame, text="Bet: $", font=("Arial", 11), bg="#0e1117", fg="white").pack(side="left")
        self._poker_bet_var = tk.StringVar(value="1000000")
        self._poker_bet_entry = tk.Entry(bet_frame, textvariable=self._poker_bet_var, width=12,
                 bg="#1e2130", fg="white", font=("Arial", 11),
                 insertbackground="white", relief="flat")
        self._poker_bet_entry.pack(side="left", ipady=4)

        self._poker_result = tk.Label(win, text="Set your bet and click Deal.",
                                      font=("Arial", 12, "bold"), bg="#0e1117", fg="#aaaaaa")
        self._poker_result.pack(pady=4)

        btn_frame = tk.Frame(win, bg="#0e1117")
        btn_frame.pack()
        self._poker_deal_btn = tk.Button(btn_frame, text="Deal  ($)",
                                         font=("Arial", 11, "bold"), bg="#00aa44", fg="white",
                                         relief="flat", padx=18, pady=6,
                                         command=self._poker_deal)
        self._poker_deal_btn.pack(side="left", padx=8)
        self._poker_draw_btn = tk.Button(btn_frame, text="Draw",
                                         font=("Arial", 11, "bold"), bg="#1e2130", fg="#555555",
                                         relief="flat", padx=18, pady=6, state="disabled",
                                         command=self._poker_draw)
        self._poker_draw_btn.pack(side="left", padx=8)

        self._poker_deck = []

    def _draw_card_back(self, c):
        c.delete("all")
        c.configure(bg="#1a2a3a", highlightbackground="#333")
        c.create_rectangle(4, 4, 68, 96, fill="#1e3a5f", outline="#2255aa", width=1)
        # cross-hatch pattern
        for y in range(8, 96, 8):
            c.create_line(4, y, 68, y, fill="#1a3050", width=1)
        for x in range(8, 68, 8):
            c.create_line(x, 4, x, 96, fill="#1a3050", width=1)
        c.create_rectangle(8, 8, 64, 92, fill="", outline="#2255aa", width=1)

    def _poker_new_deck(self):
        self._poker_deck = [(r, s) for s in self.SUITS for r in self.RANKS]
        random.shuffle(self._poker_deck)

    def _poker_deal(self):
        try:
            bet = float(self._poker_bet_var.get().replace(",", ""))
        except ValueError:
            self._poker_result.config(text="Invalid bet.", fg="#ff4444")
            return
        if bet <= 0:
            self._poker_result.config(text="Bet must be > 0.", fg="#ff4444")
            return
        max_bet = min(30_000_000, self.money * 0.20)
        if bet > max_bet:
            self._poker_result.config(text=f"Max bet: ${max_bet:,.0f} (20% of balance)", fg="#ff4444")
            return
        if bet > self.money:
            self._poker_result.config(text="Not enough money.", fg="#ff4444")
            return

        # Deduct bet upfront
        self.money -= bet
        self.market.money = self.money
        self.update_status()

        self._poker_current_bet = bet
        self._poker_new_deck()
        self._poker_hand = [self._poker_deck.pop() for _ in range(5)]
        self._poker_held = [False] * 5
        self._poker_phase = "hold"

        self._poker_result.config(text="Select cards to HOLD, then click Draw.", fg="#aaaaaa")
        self._poker_deal_btn.config(state="disabled")
        self._poker_draw_btn.config(state="normal", bg="#00aa44", fg="white")
        self._poker_bet_entry.config(state="disabled")
        self._render_poker_cards()

    def _poker_draw(self):
        for i in range(5):
            if not self._poker_held[i]:
                self._poker_hand[i] = self._poker_deck.pop()
        self._poker_held = [False] * 5
        self._poker_phase = "bet"
        self._render_poker_cards()
        self._poker_deal_btn.config(state="normal", bg="#00aa44", fg="white")
        self._poker_draw_btn.config(state="disabled", bg="#1e2130", fg="#555555")
        self._poker_bet_entry.config(state="normal")
        self._evaluate_poker()

    def _toggle_hold(self, idx):
        if self._poker_phase != "hold":
            return
        self._poker_held[idx] = not self._poker_held[idx]
        self._render_poker_cards()

    def _render_poker_cards(self):
        for i, (rank, suit) in enumerate(self._poker_hand):
            c = self._poker_canvases[i]
            c.delete("all")
            held = self._poker_held[i]
            c.configure(bg="#fffde7" if held else "white",
                        highlightbackground="#ffdd44" if held else "#333")
            color = self.SUIT_COLORS[suit]
            c.create_text(8,  10, text=rank, anchor="nw", font=("Arial", 11, "bold"), fill=color)
            c.create_text(36, 50, text=suit, anchor="center", font=("Arial", 28), fill=color)
            c.create_text(64, 90, text=rank, anchor="se", font=("Arial", 11, "bold"), fill=color)
            self._poker_hold_labels[i].config(text="HOLD" if held else "")

    def _evaluate_poker(self):
        hand   = self._poker_hand
        ranks  = sorted([self.RANK_VAL[r] for r, s in hand], reverse=True)
        suits  = [s for r, s in hand]
        flush    = len(set(suits)) == 1
        straight = (ranks == list(range(ranks[0], ranks[0]-5, -1)) or
                    ranks == [12, 3, 2, 1, 0])
        counts_map = {}
        for rv in ranks:
            counts_map[rv] = counts_map.get(rv, 0) + 1
        counts = sorted(counts_map.values(), reverse=True)

        if flush and straight and ranks[0] == 12: name, mult = "Royal Flush! 👑",   250
        elif flush and straight:                   name, mult = "Straight Flush!",   50
        elif counts[0] == 4:                       name, mult = "Four of a Kind!",   25
        elif counts[:2] == [3, 2]:                 name, mult = "Full House!",        9
        elif flush:                                name, mult = "Flush!",             6
        elif straight:                             name, mult = "Straight!",          4
        elif counts[0] == 3:                       name, mult = "Three of a Kind!",   3
        elif counts[:2] == [2, 2]:                 name, mult = "Two Pair!",          2
        elif counts[0] == 2 and max(k for k, v in counts_map.items() if v == 2) >= 9:
                                                   name, mult = "Jacks or Better!",  1
        else:                                      name, mult = "High Card — no win", 0

        bet = self._poker_current_bet

        if mult > 0:
            # Return bet + winnings (bet was already deducted on Deal)
            payout = bet * (mult + 1)
            self.money += payout
            profit = bet * mult
            self._poker_result.config(text=f"{name}  +${profit:,.0f}", fg="#ffdd44")
            self.log_event(f"Poker: {name} +${profit:,.0f}")
        else:
            # Bet already deducted — nothing more to do
            self._poker_result.config(text=f"{name}  -${bet:,.0f}", fg="#ff4444")
            self.log_event(f"Poker: high card, lost ${bet:,.0f}")

        self.market.money = self.money
        self.update_status()

        # Reset cards to face-down for next round
        for c in self._poker_canvases:
            self._draw_card_back(c)
        for lbl in self._poker_hold_labels:
            lbl.config(text="")

    # =========================================================
    # WORK
    # =========================================================

    def work(self):
        gain = random.randint(1000, 50000)
        self.money += gain
        self.market.money = self.money
        self.log_event(f"You worked and earned ${gain:,}")
        self.update_status()
