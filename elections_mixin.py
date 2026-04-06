"""
elections_mixin.py — Presidential Elections & Executive Orders
"""

import tkinter as tk
import threading
import json
import random

ELECTION_THRESHOLD = 1_000_000_000   # $1B minimum net worth to run
TERM_LENGTH        = 4               # years per term
MAX_TERMS          = 2               # lifetime term limit

# Valid ranges for each executive order effect type.
# Values outside these are clamped before applying.
_EFFECT_RANGES = {
    "daily_expense_multiplier": (0.40, 0.95),
    "income_multiplier":         (1.10, 2.50),
    "transgression_decay_bonus": (1,    8),
    "public_opinion_daily":      (1,    10),
    "loan_rate_multiplier":      (0.30, 0.90),
    "happiness_daily":           (1,    8),
    "wanted_fine_reduction":     (0.30, 0.90),
}

# ── Rule-based executive order parser ──────────────────────────────────────

# Automatic rejection — orders containing these phrases are instantly denied.
_REJECT_WORDS = [
    "infinite", "unlimited", "no cost", "zero cost", "free money",
    "god mode", "always win", "never lose", "immortal", "invincible",
    "cheat", "hack", "exploit", "100% discount", "no expenses",
    "zero expenses", "maximum money", "all money", "infinite income",
    "instant win", "delete debt", "remove all fines",
]

# One entry per available effect type.
# keywords  — score +2 each when found in the order text
# dir_words — score +1 each (directional verbs confirming intent)
# direction — "reduce" → multiplier < 1.0 ;  "increase" → multiplier > 1.0
# integer   — True for whole-number bonus types (counts per year)
# default_pct — fallback magnitude when no number or qualifier is found
_EFFECT_RULES = [
    {
        "type":        "daily_expense_multiplier",
        "keywords":    ["expense", "expenses", "cost", "costs", "spending",
                        "budget", "operating", "overhead", "outgoing",
                        "expenditure", "outlay"],
        "dir_words":   ["reduce", "cut", "lower", "decrease", "slash",
                        "trim", "limit", "curtail"],
        "direction":   "reduce",
        "default_pct": 15,
        "range":       (0.40, 0.95),
        "desc_tmpl":   "{pct:.0f}% operating expense reduction",
    },
    {
        "type":        "income_multiplier",
        "keywords":    ["income", "revenue", "earnings", "profit", "yield",
                        "production", "output", "factory", "resource",
                        "industry", "trade", "export"],
        "dir_words":   ["increase", "boost", "raise", "grow", "enhance",
                        "improve", "maximise", "maximize"],
        "direction":   "increase",
        "default_pct": 20,
        "range":       (1.10, 2.50),
        "desc_tmpl":   "{pct:.0f}% income boost",
    },
    {
        "type":        "transgression_decay_bonus",
        "keywords":    ["crime", "criminal", "record", "transgression",
                        "corruption", "misconduct", "offence", "offense",
                        "legal", "amnesty", "pardon", "clemency",
                        "expunge", "rehabilitate", "rehabilitation"],
        "dir_words":   ["reduce", "clear", "clean", "expunge", "pardon",
                        "forgive", "amnesty", "decrease"],
        "direction":   "reduce",
        "default_pct": 30,
        "range":       (1, 8),
        "integer":     True,
        "desc_tmpl":   "Expedited record cleanup (+{val:.0f} decay/yr)",
    },
    {
        "type":        "public_opinion_daily",
        "keywords":    ["opinion", "approval", "image", "reputation",
                        "popularity", "public", "media", "press",
                        "propaganda", "support", "perception",
                        "narrative", "brand"],
        "dir_words":   ["improve", "boost", "raise", "increase", "enhance",
                        "rebuild", "restore"],
        "direction":   "increase",
        "default_pct": 25,
        "range":       (1, 10),
        "integer":     True,
        "desc_tmpl":   "National image programme (+{val:.0f} opinion/yr)",
    },
    {
        "type":        "loan_rate_multiplier",
        "keywords":    ["loan", "interest", "rate", "debt", "borrowing",
                        "credit", "lending", "mortgage", "bank",
                        "financing", "borrow"],
        "dir_words":   ["reduce", "lower", "cut", "cap", "decrease",
                        "slash", "limit"],
        "direction":   "reduce",
        "default_pct": 25,
        "range":       (0.30, 0.90),
        "desc_tmpl":   "{pct:.0f}% loan interest reduction",
    },
    {
        "type":        "happiness_daily",
        "keywords":    ["happiness", "morale", "welfare", "wellbeing",
                        "well-being", "satisfaction", "joy", "content",
                        "citizens", "people", "population", "workers",
                        "employees"],
        "dir_words":   ["improve", "boost", "raise", "increase", "enhance",
                        "fund", "invest", "support"],
        "direction":   "increase",
        "default_pct": 30,
        "range":       (1, 8),
        "integer":     True,
        "desc_tmpl":   "National wellbeing initiative (+{val:.0f} happiness/yr)",
    },
    {
        "type":        "wanted_fine_reduction",
        "keywords":    ["fine", "fines", "penalty", "penalties", "wanted",
                        "law enforcement", "police", "punishment",
                        "sanction", "fee", "fees", "citation"],
        "dir_words":   ["reduce", "lower", "cut", "cap", "decrease",
                        "slash", "limit", "waive"],
        "direction":   "reduce",
        "default_pct": 30,
        "range":       (0.30, 0.90),
        "desc_tmpl":   "{pct:.0f}% law enforcement fine reduction",
    },
]

# Qualitative intensity words mapped to approximate percentage of change.
_QUAL_MAGNITUDES = [
    (["tiny", "minor", "slight", "slightly", "small", "minimal", "little"], 10),
    (["modest", "moderate", "reasonable", "fair", "average", "some"],       20),
    (["significant", "notably", "considerable", "substantially"],            35),
    (["major", "large", "greatly", "heavily", "strong"],                     50),
    (["drastic", "drastically", "extreme", "massive", "enormous", "huge"],   65),
    (["double", "doubled", "twice", "two times", "2x"],                     100),
    (["triple", "tripled", "three times", "3x"],                            200),
    (["half", "halved", "by half"],                                          50),
]


def _parse_executive_order_gemini(text):
    """
    Gemini-powered executive order parser.
    Returns {"approved": bool, "reason": str, "effect": {...} or None}
    Falls back to the rule-based parser if the API key is missing or the
    call fails for any reason.
    """
    import os
    import urllib.request

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None   # signal to caller: fall back to rule-based

    effect_types = "\n".join(
        f'  - "{k}": allowed value range {lo}–{hi}'
        for k, (lo, hi) in _EFFECT_RANGES.items()
    )

    prompt = (
        "You are the Supreme Court of a fictional nation in a game called Debt Clicker.\n"
        "A player who is President has submitted this executive order:\n\n"
        f'"{text}"\n\n'
        "Evaluate it and respond with ONLY a JSON object — no markdown, no explanation — in this exact shape:\n"
        '{"approved": true/false, "reason": "<1-2 sentences>", '
        '"effect": {"type": "<type>", "value": <number>, "description": "<short label>"} or null}\n\n'
        "Available effect types and their allowed numeric ranges:\n"
        f"{effect_types}\n\n"
        "Rules:\n"
        "- Deny anything that would give an infinite, game-breaking, or unrealistic advantage.\n"
        "- Pick the single effect type that best matches the order's intent.\n"
        "- Scale the value to the magnitude described (e.g. 'slightly' → near the low end).\n"
        "- Keep the description label short (e.g. '20% income boost').\n"
        "- If the order is nonsensical or impossible to map, set approved to false and effect to null."
    )

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 256},
    }).encode()

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode())

    raw = body["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown code fences if Gemini wraps the JSON anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def _parse_executive_order(text):
    """
    Executive order parser.
    Tries Gemini first; falls back to the local rule-based parser if
    GEMINI_API_KEY is not set or the API call fails.
    Returns {"approved": bool, "reason": str, "effect": {...} or None}
    """
    try:
        result = _parse_executive_order_gemini(text)
        if result is not None:
            return result
    except Exception:
        pass   # fall through to rule-based

    # ── Rule-based fallback ───────────────────────────────────────────
    import re

    lower = text.lower()

    for bad in _REJECT_WORDS:
        if bad in lower:
            return {
                "approved": False,
                "reason": (f"Order references prohibited terms ('{bad}'). "
                           "Keep policies realistic and grounded."),
                "effect": None,
            }

    best_rule  = None
    best_score = 0

    for rule in _EFFECT_RULES:
        score = sum(2 for kw in rule["keywords"] if kw in lower)
        score += sum(1 for dw in rule["dir_words"] if dw in lower)
        if score > best_score:
            best_score = score
            best_rule  = rule

    if not best_rule or best_score < 2:
        return {
            "approved": False,
            "reason": (
                "Order doesn't clearly address a recognised policy area "
                "(expenses, income, loans, happiness, public opinion, "
                "transgressions, or fines). Please be more specific."),
            "effect": None,
        }

    pct = None

    m = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
    if m:
        pct = float(m.group(1))

    if pct is None:
        for words, magnitude in _QUAL_MAGNITUDES:
            if any(w in lower for w in words):
                pct = float(magnitude)
                break

    if pct is None:
        pct = float(best_rule["default_pct"])

    pct = max(1.0, min(pct, 200.0))

    lo, hi = best_rule["range"]

    if best_rule.get("integer"):
        raw = lo + (hi - lo) * (pct / 100.0)
        val = float(max(lo, min(hi, round(raw))))
    elif best_rule["direction"] == "reduce":
        val = max(lo, min(hi, round(1.0 - pct / 100.0, 3)))
    else:
        val = max(lo, min(hi, round(1.0 + pct / 100.0, 3)))

    desc = best_rule["desc_tmpl"].format(pct=pct, val=val)

    return {
        "approved": True,
        "reason":   f"Order approved — interpreted as a {desc.lower()}.",
        "effect": {
            "type":        best_rule["type"],
            "value":       val,
            "description": desc,
        },
    }


class ElectionsMixin:
    """Presidential election system and AI-powered executive orders."""

    # =========================================================
    # ELECTIONS WINDOW
    # =========================================================

    def open_elections_window(self):
        win = tk.Toplevel(self.root)
        win.title("Presidential Elections")
        win.configure(bg="#0e1117")
        win.geometry("540x640")
        win.resizable(False, False)

        tk.Frame(win, bg="#1a2244", height=5).pack(fill="x")
        tk.Label(win, text="PRESIDENTIAL ELECTIONS",
                 font=("Impact", 24), bg="#0e1117", fg="#4499ff").pack(pady=(14, 2))

        is_pres  = getattr(self, "is_president",      False)
        term     = getattr(self, "presidential_term", 0)
        years_in = getattr(self, "years_in_office",   0)

        if is_pres:
            status_txt = (f"STATUS: PRESIDENT  |  Term {term}/{MAX_TERMS}"
                          f"  |  {years_in} years remaining")
            status_col = "#00ff90"
        else:
            status_txt = f"STATUS: Civilian  |  Terms served: {term}/{MAX_TERMS}"
            status_col = "#aaaaaa"
        tk.Label(win, text=status_txt, font=("Arial", 10, "bold"),
                 bg="#0e1117", fg=status_col).pack(pady=(0, 4))

        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=6)

        # ── Candidacy requirements ────────────────────────────────────────
        tk.Label(win, text="CANDIDACY REQUIREMENTS",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg="#888").pack(anchor="w", padx=20)

        req_frame = tk.Frame(win, bg="#111820")
        req_frame.pack(fill="x", padx=16, pady=(4, 8))

        reqs = [
            ("Net worth ≥ $1,000,000,000",
             self.money >= ELECTION_THRESHOLD,
             f"${int(self.money):,}"),
            ("Not currently in office",
             not is_pres,
             "Already serving" if is_pres else "OK"),
            ("Terms remaining",
             term < MAX_TERMS,
             f"Max {MAX_TERMS} ({term} used)"),
        ]
        all_met = all(ok for _, ok, _ in reqs)

        for label, ok, detail in reqs:
            r = tk.Frame(req_frame, bg="#111820")
            r.pack(fill="x", padx=12, pady=3)
            tick = "✓" if ok else "✗"
            col  = "#00ff90" if ok else "#ff4444"
            tk.Label(r, text=f"{tick}  {label}", font=("Arial", 9, "bold"),
                     bg="#111820", fg=col, width=30, anchor="w").pack(side="left")
            tk.Label(r, text=detail, font=("Arial", 9),
                     bg="#111820", fg="#666", anchor="w").pack(side="left")

        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=6)

        # ── Win probability ───────────────────────────────────────────────
        tk.Label(win, text="WIN PROBABILITY",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg="#888").pack(anchor="w", padx=20)

        senators  = getattr(self, "senators_bribed", 0)
        win_pct   = self._calculate_win_probability()
        pct_col   = "#00ff90" if win_pct >= 60 else ("#ffaa00" if win_pct >= 40 else "#ff4444")

        prob_frame = tk.Frame(win, bg="#111820")
        prob_frame.pack(fill="x", padx=16, pady=(4, 6))

        for lbl, val in [
            ("Base chance (public opinion × 0.6)", f"{int(self.public_opinion * 0.6)}%"),
            (f"Senator influence ({senators}/6)",  f"+{min(senators * 5, 30)}%"),
            ("Happiness bonus (above 50)",         f"+{int(max(0, self.happiness - 50) * 0.2):.0f}%"),
        ]:
            r = tk.Frame(prob_frame, bg="#111820")
            r.pack(fill="x", padx=12, pady=2)
            tk.Label(r, text=lbl, font=("Arial", 9),
                     bg="#111820", fg="#888", width=32, anchor="w").pack(side="left")
            tk.Label(r, text=val, font=("Arial", 9, "bold"),
                     bg="#111820", fg="#ffaa00", anchor="w").pack(side="left")

        tk.Label(prob_frame, text=f"TOTAL WIN CHANCE:  {win_pct:.0f}%",
                 font=("Arial", 11, "bold"), bg="#111820", fg=pct_col).pack(pady=(6, 4))

        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=6)

        # ── Bribe senators ────────────────────────────────────────────────
        tk.Label(win, text="IMPROVE YOUR ODDS",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg="#888").pack(anchor="w", padx=20)

        bribe_cost = 40_000_000
        bribe_can  = self.money >= bribe_cost and senators < 6

        bribe_row = tk.Frame(win, bg="#111820")
        bribe_row.pack(fill="x", padx=16, pady=(4, 8))
        inner_r   = tk.Frame(bribe_row, bg="#111820")
        inner_r.pack(fill="x", padx=12, pady=6)

        tk.Label(inner_r,
                 text=f"Bribe a Senator  ($40M | +5% win chance | +5 transgression)  [{senators}/6]",
                 font=("Arial", 9), bg="#111820", fg="#888",
                 anchor="w").pack(side="left", fill="x", expand=True)

        def do_bribe(w=win):
            if self.money < bribe_cost:
                self.log_event("Can't afford senator bribe ($40M required)")
                return
            if getattr(self, "senators_bribed", 0) >= 6:
                self.log_event("Maximum 6 senators already bribed.")
                return
            self.money -= bribe_cost
            self.market.money = self.money
            self.senators_bribed = getattr(self, "senators_bribed", 0) + 1
            self.add_transgression(5, 3)
            self.update_status()
            self.log_event(
                f"Senator bribed — election win chance +5%. "
                f"Total: {self.senators_bribed} senators.")
            w.destroy()
            self.open_elections_window()

        tk.Button(inner_r, text="Bribe",
                  font=("Arial", 9, "bold"),
                  bg="#886600" if bribe_can else "#2a2a2a",
                  fg="white" if bribe_can else "#444",
                  relief="flat", padx=10, pady=4,
                  state="normal" if bribe_can else "disabled",
                  command=do_bribe).pack(side="right")

        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=6)

        # ── Run button ────────────────────────────────────────────────────
        def run_election(w=win):
            w.destroy()
            self._run_election()

        tk.Button(win,
                  text="🗳️  RUN FOR PRESIDENT",
                  font=("Arial", 14, "bold"),
                  bg="#1a2244" if all_met else "#151515",
                  fg="#4499ff" if all_met else "#333",
                  activebackground="#2a3254",
                  relief="flat", padx=24, pady=12,
                  state="normal" if all_met else "disabled",
                  command=run_election).pack(pady=8)

        if not all_met:
            tk.Label(win, text="Meet all requirements above to run for office.",
                     font=("Arial", 9, "italic"), bg="#0e1117", fg="#555").pack()

        tk.Frame(win, bg="#1a2244", height=5).pack(fill="x", side="bottom")

    def _calculate_win_probability(self):
        """Return win probability as a percentage (5–90)."""
        pct  = self.public_opinion * 0.6
        pct += min(getattr(self, "senators_bribed", 0) * 5, 30)
        pct += max(0, self.happiness - 50) * 0.2
        return max(5, min(90, pct))

    def _run_election(self):
        """Roll against win probability and show result popup."""
        win_chance = self._calculate_win_probability()
        roll       = random.uniform(0, 100)
        won        = roll <= win_chance

        if won:
            self.is_president      = True
            self.presidential_term = getattr(self, "presidential_term", 0) + 1
            self.years_in_office   = TERM_LENGTH
            if not hasattr(self, "executive_orders") or self.executive_orders is None:
                self.executive_orders = []
            color       = "#00ff90"
            result_text = "YOU WIN THE ELECTION!"
            flavor_text = (
                f"The people have spoken. You are now President of {self.country}.\n"
                f"You have {TERM_LENGTH} years to serve.\n"
                f"World Map access granted. Sign Executive Orders from the main panel.")
            self.log_event(
                f"ELECTED! President of {self.country}. "
                f"Term {self.presidential_term}/{MAX_TERMS}.")
            self._add_ticker(
                f"BREAKING: {self.username} wins presidential election in {self.country}!")
        else:
            color       = "#ff4444"
            result_text = "YOU LOST THE ELECTION"
            flavor_text = (
                f"The public wasn't convinced.\n"
                f"You rolled {roll:.0f} — needed ≤ {win_chance:.0f}.\n"
                f"Rebuild your image and try again.")
            self.log_event(
                f"Election lost. Rolled {roll:.0f}, needed {win_chance:.0f}. "
                f"Improve public opinion and try again.")

        popup = tk.Toplevel(self.root)
        popup.title("Election Result")
        popup.configure(bg="#0e1117")
        popup.geometry("440x300")
        popup.resizable(False, False)
        popup.grab_set()

        tk.Frame(popup, bg=color, height=5).pack(fill="x")
        tk.Label(popup, text="🗳️", font=("Arial", 36), bg="#0e1117").pack(pady=(16, 0))
        tk.Label(popup, text=result_text,
                 font=("Impact", 20), bg="#0e1117", fg=color).pack(pady=(4, 6))
        tk.Label(popup, text=flavor_text,
                 font=("Arial", 9), bg="#0e1117", fg="#aaaaaa",
                 wraplength=380, justify="center").pack(pady=4)
        tk.Frame(popup, bg=color, height=3).pack(fill="x", pady=(8, 0))
        tk.Button(popup, text="Close",
                  font=("Arial", 10, "bold"), bg=color, fg="black",
                  relief="flat", padx=20, pady=6,
                  command=popup.destroy).pack(pady=10)

        self.update_status()

    # =========================================================
    # TERM PROCESSING  (called once per year from main_loop)
    # =========================================================

    def process_presidential_term(self):
        """Tick presidential term counter; fire expiry popup when it hits zero."""
        if not getattr(self, "is_president", False):
            return
        self.years_in_office = max(0, getattr(self, "years_in_office", 0) - 1)
        if self.years_in_office <= 0:
            self._term_expired()

    def _term_expired(self):
        term = getattr(self, "presidential_term", 1)
        self.is_president    = False
        self.years_in_office = 0
        self.executive_orders = []

        self.log_event(f"Presidential term {term} has expired.")
        self._add_ticker(
            f"POLITICS: President {self.username} completes term {term}...")

        if term < MAX_TERMS:
            msg = (f"Term {term}/{MAX_TERMS} complete.\n\n"
                   f"You may run for re-election via the Elections tab\n"
                   f"to serve one final term.")
        else:
            msg = (f"You have served the maximum {MAX_TERMS} terms.\n\n"
                   f"You are now a civilian. "
                   f"World Map access and Executive Orders are revoked.")

        popup = tk.Toplevel(self.root)
        popup.title("Presidential Term Expired")
        popup.configure(bg="#0e1117")
        popup.geometry("400x260")
        popup.resizable(False, False)

        tk.Frame(popup, bg="#4499ff", height=5).pack(fill="x")
        tk.Label(popup, text="🏛️  TERM EXPIRED",
                 font=("Impact", 20), bg="#0e1117", fg="#4499ff").pack(pady=(14, 6))
        tk.Label(popup, text=msg,
                 font=("Arial", 10), bg="#0e1117", fg="#aaaaaa",
                 wraplength=360, justify="center").pack(pady=4)
        tk.Frame(popup, bg="#4499ff", height=3).pack(fill="x", pady=(10, 0))
        tk.Button(popup, text="Understood",
                  font=("Arial", 10, "bold"), bg="#4499ff", fg="black",
                  relief="flat", padx=20, pady=6,
                  command=popup.destroy).pack(pady=10)

        self.update_status()

    # =========================================================
    # EXECUTIVE ORDER PASSIVE EFFECTS  (called from main_loop)
    # =========================================================

    def apply_executive_order_effects(self):
        """Apply all active executive order bonuses once per year."""
        if not getattr(self, "is_president", False):
            return
        for order in getattr(self, "executive_orders", []):
            etype = order.get("type")
            val   = order.get("value", 0)

            if etype == "transgression_decay_bonus":
                self.transgressions = max(0, self.transgressions - val)

            elif etype == "public_opinion_daily":
                self.public_opinion = min(100, self.public_opinion + val)

            elif etype == "happiness_daily":
                self.happiness = min(100, self.happiness + val)

            elif etype == "daily_expense_multiplier":
                # Refund the fraction of expenses that the order saved
                estimated = self.money * 0.01
                refund = int(estimated * (1 - val))
                if refund > 0:
                    self.money += refund
                    self.market.money = self.money

            elif etype == "income_multiplier":
                # Bonus on top of already-processed resource income
                base = sum(op.get("income", 0)
                           for op in getattr(self, "oil_operations", []))
                bonus = int(base * (val - 1))
                if bonus > 0:
                    self.money += bonus
                    self.market.money = self.money

            elif etype == "wanted_fine_reduction":
                if self.wanted_level > 0:
                    base_fine = self.wanted_level * 500_000
                    refund = int(base_fine * (1 - val))
                    self.money += refund
                    self.market.money = self.money

        self._update_bars()

    # Helpers used by other mixins to read active exec order multipliers

    def get_executive_loan_rate_multiplier(self):
        mult = 1.0
        for o in getattr(self, "executive_orders", []):
            if o.get("type") == "loan_rate_multiplier":
                mult *= o["value"]
        return mult

    # =========================================================
    # EXECUTIVE ORDER WINDOW
    # =========================================================

    def open_executive_order_window(self):
        if not getattr(self, "is_president", False):
            self.log_event(
                "You must be President to sign Executive Orders. "
                "Win an election first.")
            return

        win = tk.Toplevel(self.root)
        win.title("Executive Orders")
        win.configure(bg="#0e1117")
        win.geometry("600x640")
        win.resizable(False, False)

        tk.Frame(win, bg="#884400", height=5).pack(fill="x")
        tk.Label(win, text="EXECUTIVE ORDERS",
                 font=("Impact", 24), bg="#0e1117", fg="#ffaa00").pack(pady=(14, 2))
        tk.Label(win,
                 text=(f"President {self.username}  |  "
                       f"Term {self.presidential_term}  |  "
                       f"{self.years_in_office} years remaining"),
                 font=("Arial", 9), bg="#0e1117", fg="#555").pack(pady=(0, 4))

        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=4)

        # ── Active orders ──────────────────────────────────────────────────
        tk.Label(win, text="ACTIVE ORDERS",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg="#888").pack(anchor="w", padx=20)

        orders = getattr(self, "executive_orders", [])
        if not orders:
            tk.Label(win, text="No executive orders signed yet.",
                     font=("Arial", 9), bg="#0e1117", fg="#555").pack(pady=4)
        else:
            for o in orders:
                row = tk.Frame(win, bg="#111820", pady=5, padx=12)
                row.pack(fill="x", padx=16, pady=2)
                tk.Label(row,
                         text=f"📜  {o.get('description', o['type'])}",
                         font=("Arial", 9, "bold"), bg="#111820", fg="#00ff90",
                         anchor="w").pack(side="left")
                tk.Label(row,
                         text=f"[{o['type']}  =  {o['value']}]",
                         font=("Arial", 8), bg="#111820", fg="#444",
                         anchor="w").pack(side="left", padx=6)

        tk.Frame(win, bg="#1e2130", height=1).pack(fill="x", padx=20, pady=8)

        # ── Draft new order ────────────────────────────────────────────────
        tk.Label(win, text="DRAFT A NEW ORDER",
                 font=("Arial", 10, "bold"), bg="#0e1117", fg="#888").pack(anchor="w", padx=20)

        if len(orders) >= 3:
            tk.Label(win,
                     text="Maximum 3 executive orders per term.",
                     font=("Arial", 9, "bold"), bg="#0e1117", fg="#ff4444").pack(pady=8)
        else:
            tk.Label(win,
                     text=("Describe your executive order in plain language.\n"
                           "The legal review board will assess it and translate it into a game effect."),
                     font=("Arial", 9), bg="#0e1117", fg="#666",
                     wraplength=540, justify="left").pack(anchor="w", padx=20, pady=(2, 2))

            for ex in [
                'e.g.  "I order a 15% reduction in government operating costs"',
                'e.g.  "I decree all loan interest rates be capped at 70% of normal"',
                'e.g.  "I mandate a national morale programme — daily happiness funding"',
            ]:
                tk.Label(win, text=ex, font=("Arial", 8, "italic"),
                         bg="#0e1117", fg="#444").pack(anchor="w", padx=24)

            order_text = tk.Text(win, height=4, width=68,
                                 bg="#1e2130", fg="white", font=("Arial", 10),
                                 insertbackground="white", relief="flat", wrap="word")
            order_text.pack(padx=20, pady=(6, 4))

            status_var = tk.StringVar(value="")
            status_lbl = tk.Label(win, textvariable=status_var,
                                  font=("Arial", 9), bg="#0e1117", fg="#aaaaaa",
                                  wraplength=540, justify="center")
            status_lbl.pack(pady=4)

            sign_btn = tk.Button(win,
                                 text="✍️  Sign Executive Order",
                                 font=("Arial", 12, "bold"),
                                 bg="#884400", fg="white",
                                 activebackground="#aa5500",
                                 relief="flat", padx=20, pady=8)
            sign_btn.pack(pady=6)

            def on_sign(w=win):
                text = order_text.get("1.0", tk.END).strip()
                if len(text) < 10:
                    status_var.set("Please write a more descriptive order.")
                    status_lbl.config(fg="#ff4444")
                    return
                sign_btn.config(state="disabled", text="Reviewing order...")
                status_var.set("Reviewing with the legal board...")
                status_lbl.config(fg="#ffaa00")
                win.update_idletasks()
                self._submit_executive_order(text, status_var, status_lbl, sign_btn, w)

            sign_btn.config(command=on_sign)

        tk.Frame(win, bg="#884400", height=5).pack(fill="x", side="bottom")

    # =========================================================
    # ORDER REVIEW  (background thread — local parser, no API needed)
    # =========================================================

    def _submit_executive_order(self, order_text, status_var, status_lbl, sign_btn, win):
        def _do_call():
            import time
            time.sleep(1.2)   # deliberate pause for review feel
            try:
                data = _parse_executive_order(order_text)
                self.root.after(
                    0, lambda: self._handle_order_response(
                        data, status_var, status_lbl, sign_btn, win))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._order_error(
                    f"Parser error: {err}", status_var, status_lbl, sign_btn))

        threading.Thread(target=_do_call, daemon=True).start()

    def _handle_order_response(self, data, status_var, status_lbl, sign_btn, win):
        approved = data.get("approved", False)
        reason   = data.get("reason", "No reason given.")
        effect   = data.get("effect")

        if not approved or not effect:
            status_var.set(f"DENIED: {reason}")
            status_lbl.config(fg="#ff4444")
            sign_btn.config(state="normal", text="✍️  Sign Executive Order")
            self.log_event(f"Executive Order DENIED: {reason}")
            return

        etype = effect.get("type", "")
        val   = float(effect.get("value", 1.0))
        desc  = effect.get("description", etype)

        if etype not in _EFFECT_RANGES:
            status_var.set(f"DENIED: Unrecognised effect type '{etype}'.")
            status_lbl.config(fg="#ff4444")
            sign_btn.config(state="normal", text="✍️  Sign Executive Order")
            return

        lo, hi = _EFFECT_RANGES[etype]
        val = max(lo, min(hi, val))   # safety clamp

        if not hasattr(self, "executive_orders") or self.executive_orders is None:
            self.executive_orders = []
        self.executive_orders.append({"type": etype, "value": val, "description": desc})

        status_var.set(f"SIGNED: {reason}")
        status_lbl.config(fg="#00ff90")
        self.log_event(f"Executive Order SIGNED: {desc}  [{etype} = {val}]")
        self._add_ticker(
            f"POLITICS: President {self.username} signs executive order — {desc}...")

        self.root.after(1400, lambda: (win.destroy(), self.open_executive_order_window()))

    def _order_error(self, msg, status_var, status_lbl, sign_btn):
        status_var.set(msg)
        status_lbl.config(fg="#ff4444")
        sign_btn.config(state="normal", text="✍️  Sign Executive Order")
