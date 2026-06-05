"""
messages_mixin.py — In-game inbox with Gmail-style UI and notification sound.
"""
import tkinter as tk
from tkinter import ttk
import threading


def _play_notification_sound():
    """Play a soft notification chime using Windows built-in sounds."""
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass


# Sender profiles keyed by category
_SENDERS = {
    "gambling":    ("🎰", "Casino Security"),
    "stocks":      ("📈", "SEC Compliance"),
    "work":        ("💼", "HR Department"),
    "bombing":     ("💣", "Pentagon Memo"),
    "election":    ("🏛", "Federal Elections"),
    "scandal":     ("📰", "Breaking News"),
    "legal":       ("⚖️",  "Legal Affairs"),
    "financial":   ("🏦", "Finance Ministry"),
    "personal":    ("👤", "Personal"),
    "revolution":  ("✊", "The People"),
    "health":      ("🏥", "Healthcare"),
    "environment": ("🌍", "Environmental Agency"),
    "groq":        ("🧠", "Groq Executive Orders"),
    "rival":       ("⚔️",  "Rival Intel"),
    "event":       ("📬", "World Events"),
}


class MessagesMixin:

    # =========================================================
    # INBOX DATA
    # =========================================================

    def add_message(self, title: str, body: str, category: str = "event"):
        """Add a message to the inbox and trigger a notification."""
        if not hasattr(self, "inbox"):
            self.inbox = []
        emoji, sender = _SENDERS.get(category, ("📬", "World Events"))
        self.inbox.insert(0, {
            "title":   title,
            "body":    body,
            "sender":  sender,
            "emoji":   emoji,
            "category": category,
            "year":    getattr(self, "days", 0),
            "read":    False,
        })
        threading.Thread(target=_play_notification_sound, daemon=True).start()
        self.root.after(0, self._update_inbox_badge)

    def _unread_count(self) -> int:
        return sum(1 for m in getattr(self, "inbox", []) if not m["read"])

    def _update_inbox_badge(self):
        """Refresh the green badge count on the inbox button."""
        if not hasattr(self, "_inbox_badge"):
            return
        n = self._unread_count()
        if n > 0:
            self._inbox_badge.config(text=str(n), bg="#00cc44")
            self._inbox_badge.place(relx=1.0, rely=0.0, anchor="ne", x=4, y=-4)
        else:
            self._inbox_badge.place_forget()

    # =========================================================
    # INBOX BUTTON (call from top bar builder)
    # =========================================================

    def _build_inbox_button(self, parent) -> tk.Frame:
        """Return a frame containing the inbox button + badge. Pack it yourself."""
        container = tk.Frame(parent, bg="#0e1117")

        btn = tk.Button(
            container, text="✉",
            font=("Arial", 16), bg="#0e1117", fg="#aaaaaa",
            activebackground="#0e1117", activeforeground="#00ff90",
            relief="flat", bd=0, cursor="hand2",
            command=self.open_inbox,
        )
        btn.pack()

        self._inbox_badge = tk.Label(
            container, text="", font=("Arial", 7, "bold"),
            bg="#00cc44", fg="white",
            width=2, height=1, relief="flat",
        )
        # Badge starts hidden; _update_inbox_badge shows it when needed
        return container

    # =========================================================
    # GMAIL-STYLE INBOX WINDOW
    # =========================================================

    def open_inbox(self):
        win = tk.Toplevel(self.root)
        win.title("Inbox")
        win.configure(bg="#0e1117")
        win.geometry("960x720")
        win.resizable(True, True)

        # ── Header ────────────────────────────────────────────
        hdr = tk.Frame(win, bg="#1a1a2e")
        hdr.pack(fill="x")
        tk.Label(hdr, text="  ✉  Inbox", font=("Arial", 13, "bold"),
                 bg="#1a1a2e", fg="white").pack(side="left", pady=10, padx=8)
        unread_lbl = tk.Label(hdr, text="", font=("Arial", 9),
                              bg="#1a1a2e", fg="#00cc44")
        unread_lbl.pack(side="left", pady=10)
        tk.Button(hdr, text="Mark all read",
                  font=("Arial", 9), bg="#1a1a2e", fg="#888888",
                  activebackground="#2a2a3e", relief="flat",
                  command=lambda: self._mark_all_read(win, msg_frame, unread_lbl)
                  ).pack(side="right", padx=12, pady=8)

        tk.Frame(win, bg="#2a2a3e", height=1).pack(fill="x")

        # ── Scrollable message list ────────────────────────────
        outer = tk.Frame(win, bg="#0e1117")
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg="#0e1117", highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        msg_frame = tk.Frame(canvas, bg="#0e1117")
        msg_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=msg_frame, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._render_inbox(msg_frame, unread_lbl, win)

    def _render_inbox(self, msg_frame, unread_lbl, win):
        for w in msg_frame.winfo_children():
            w.destroy()

        inbox = getattr(self, "inbox", [])
        n = self._unread_count()
        unread_lbl.config(text=f"  {n} unread" if n else "  All read")

        if not inbox:
            tk.Label(msg_frame, text="No messages yet.",
                     font=("Arial", 11), bg="#0e1117", fg="#555555"
                     ).pack(pady=40)
            return

        for i, msg in enumerate(inbox):
            unread = not msg["read"]
            row_bg = "#111820" if unread else "#0e1117"
            row = tk.Frame(msg_frame, bg=row_bg, cursor="hand2")
            row.pack(fill="x", padx=0, pady=0)
            tk.Frame(msg_frame, bg="#1e2130", height=1).pack(fill="x")

            # Unread dot
            dot_color = "#00cc44" if unread else row_bg
            tk.Label(row, text="●", font=("Arial", 8),
                     bg=row_bg, fg=dot_color, width=2).pack(side="left", padx=(6, 0))

            # Sender emoji
            tk.Label(row, text=msg["emoji"], font=("Arial", 22),
                     bg=row_bg, width=3).pack(side="left", padx=(4, 8), pady=10)

            # Middle: sender + subject + preview
            mid = tk.Frame(row, bg=row_bg)
            mid.pack(side="left", fill="both", expand=True, pady=8)

            weight = "bold" if unread else "normal"
            fg_main = "white" if unread else "#888888"

            sender_row = tk.Frame(mid, bg=row_bg)
            sender_row.pack(fill="x")
            tk.Label(sender_row, text=msg["sender"],
                     font=("Arial", 10, weight), bg=row_bg, fg=fg_main,
                     anchor="w").pack(side="left")

            tk.Label(mid, text=msg["title"],
                     font=("Arial", 9, weight), bg=row_bg, fg=fg_main,
                     anchor="w").pack(fill="x")

            preview = msg["body"][:140].replace("\n", " ") + ("…" if len(msg["body"]) > 140 else "")
            tk.Label(mid, text=preview,
                     font=("Arial", 8), bg=row_bg, fg="#555555",
                     anchor="w").pack(fill="x")

            # Year
            tk.Label(row, text=f"Yr {msg['year']}",
                     font=("Arial", 8), bg=row_bg, fg="#444444",
                     width=6).pack(side="right", padx=10)

            # Click to open
            def _open(e, m=msg, mf=msg_frame, ul=unread_lbl, w=win):
                m["read"] = True
                self._update_inbox_badge()
                self._show_message_detail(m)
                self._render_inbox(mf, ul, w)

            for widget in [row] + list(row.winfo_children()) + list(mid.winfo_children()):
                try:
                    widget.bind("<Button-1>", _open)
                except Exception:
                    pass

    def _show_message_detail(self, msg):
        win = tk.Toplevel(self.root)
        win.title(msg["title"])
        win.configure(bg="#0e1117")
        win.geometry("680x460")
        win.resizable(False, True)

        hdr = tk.Frame(win, bg="#111820")
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"{msg['emoji']}  {msg['sender']}",
                 font=("Arial", 12, "bold"), bg="#111820", fg="#aaaaaa"
                 ).pack(side="left", padx=16, pady=12)
        tk.Label(hdr, text=f"Year {msg['year']}",
                 font=("Arial", 9), bg="#111820", fg="#444444"
                 ).pack(side="right", padx=16)

        tk.Label(win, text=msg["title"],
                 font=("Arial", 14, "bold"), bg="#0e1117", fg="#ff4444",
                 wraplength=640, justify="left").pack(anchor="w", padx=20, pady=(16, 6))

        tk.Label(win, text=msg["body"],
                 font=("Arial", 11), bg="#0e1117", fg="white",
                 wraplength=640, justify="left").pack(anchor="w", padx=20, pady=(0, 12))

        tk.Button(win, text="Close", font=("Arial", 10),
                  bg="#1e2130", fg="#aaaaaa", relief="flat",
                  padx=20, pady=4, command=win.destroy).pack(pady=10)

    def _mark_all_read(self, win, msg_frame, unread_lbl):
        for m in getattr(self, "inbox", []):
            m["read"] = True
        self._update_inbox_badge()
        self._render_inbox(msg_frame, unread_lbl, win)
