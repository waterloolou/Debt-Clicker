import os
import json
import re
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

GROQ_API_KEY_ENV = "GROQ_API_KEY"
GROQ_API_KEY_DEFAULT = ""
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

HISTORICAL_POWER_MOVES = [
    {
        "name": "Rig Elections",
        "example": "Bribe officials, redraw districts, and control the vote count.",
        "impact": "Used by dictators and fragile democracies to stay in power while keeping a veneer of legitimacy.",
    },
    {
        "name": "Appoint Loyalists",
        "example": "Install trusted judges and ministers to remove checks on executive authority.",
        "impact": "Common under authoritarian regimes to ensure future decisions face little resistance.",
    },
    {
        "name": "Control the Media",
        "example": "Create propaganda campaigns and censor critical outlets.",
        "impact": "Information control is one of the most durable tools for regime survival.",
    },
    {
        "name": "Declare Emergency Powers",
        "example": "Use crises to expand authority and bypass normal oversight.",
        "impact": "Many leaders stay in power by governing through emergencies long after the crisis ends.",
    },
    {
        "name": "Rename Places",
        "example": "Rename cities, provinces, or landmarks to honor the regime or erase old history.",
        "impact": "Renaming is a symbolic way to claim ownership over narrative and geography.",
    },
    {
        "name": "Impose Sanctions",
        "example": "Punish rivals, make foreign policy gestures, and rally domestic support against outsiders.",
        "impact": "Sanctions are used to demonstrate strength, even when the long-term economic cost is high.",
    },
]

SAFE_GROQ_ACTIONS = {
    "rename_place": {
        "label": "Rename map place",
        "description": "Set a cosmetic alias for an existing country or resource target.",
        "examples": ["Rename Russia to Great North", "Rename Libya to The Red Coast"],
        "cost": 2_000_000,
        "public_opinion": 1,
        "risk": 0,
    },
    "pass_infrastructure_legislation": {
        "label": "Pass infrastructure legislation",
        "description": "Approve a public works bill to boost energy and retail markets while costing cash.",
        "examples": ["Build highways and bridges", "Fund new ports and rail lines"],
        "cost": 40_000_000,
        "public_opinion": 8,
        "risk": 3,
    },
    "pass_corporate_tax_cut": {
        "label": "Pass corporate tax cut",
        "description": "Give friendly industries a temporary boost at the expense of public approval.",
        "examples": ["Cut taxes for finance and tech firms", "Reduce corporate levies for energy companies"],
        "cost": 20_000_000,
        "public_opinion": -6,
        "risk": 4,
    },
    "appoint_loyalist_official": {
        "label": "Appoint a loyal official",
        "description": "Place a trusted ally in a key position to protect your authority.",
        "examples": ["Appoint a loyal judge", "Install a trusted cabinet minister"],
        "cost": 15_000_000,
        "public_opinion": 4,
        "risk": 6,
    },
    "launch_propaganda_campaign": {
        "label": "Launch propaganda campaign",
        "description": "Use media and messaging to boost opinion temporarily, but it creates long-term strain.",
        "examples": ["Promote our great leader on every channel", "Launch a national unity campaign"],
        "cost": 12_000_000,
        "public_opinion": 10,
        "risk": 8,
    },
    "declare_state_of_emergency": {
        "label": "Declare a state of emergency",
        "description": "Use crisis powers to strengthen defense and slow rivals, while damaging public trust.",
        "examples": ["Declare emergency powers after a border incident", "Invoke emergency authority for national security"],
        "cost": 0,
        "public_opinion": -12,
        "risk": 10,
    },
    "impose_sanctions": {
        "label": "Impose sanctions",
        "description": "Target hostile resource categories or rivals with punitive measures.",
        "examples": ["Sanction foreign energy exporters", "Target rival finance markets"],
        "cost": 8_000_000,
        "public_opinion": 2,
        "risk": 6,
    },
    "censor_media": {
        "label": "Censor media",
        "description": "Slow negative opinion swings by controlling news, at a cost to long-term legitimacy.",
        "examples": ["Censor dissenting journalists", "Control headlines across the country"],
        "cost": 5_000_000,
        "public_opinion": 6,
        "risk": 12,
    },
}

FORBIDDEN_PATTERNS = [
    r"\bkill\b",
    r"\bpoison\b",
    r"\bassassinate\b",
    r"\bexploit\b",
    r"\binstantly win\b",
    r"\bmake me rich\b",
    r"\bcheat\b",
    r"\bsuperpower\b",
    r"\bundefeatable\b",
    r"\bimmortal\b",
    r"\breset\b",
]

NAME_SANITIZE_RE = re.compile(r"[^A-Za-z0-9 \-']")


def _safe_text(text: str) -> str:
    text = text.strip()
    return NAME_SANITIZE_RE.sub("", text)[:40]


def _extract_rename(details: str) -> Optional[Tuple[str, str]]:
    """
    Accept many natural phrasings, e.g.:
      "Rename Russia to Great North"
      "Call Libya The Red Coast"
      "Change Iraq's name to New Babylon"
      "Russia → Grand East"
      "Russia is now Putinland"
      "Venezuela should be called El Dorado"
      "Iraq = Mesopotamia Prime"
    Returns (original, new_name) or None.
    """
    s = details.strip()

    patterns = [
        # rename X to Y  /  change X to Y  /  set X to Y
        r"(?:rename|change|set)\s+['\"]?(.+?)['\"]?(?:'s\s+name)?\s+to\s+['\"]?(.+?)['\"]?$",
        # call X Y
        r"call\s+['\"]?(.+?)['\"]?\s+['\"]?(.+?)['\"]?$",
        # X should be called Y  /  X is now Y  /  X will be Y
        r"['\"]?(.+?)['\"]?\s+(?:should\s+be\s+called|is\s+now|will\s+be|becomes?)\s+['\"]?(.+?)['\"]?$",
        # X → Y  or  X -> Y  or  X => Y
        r"['\"]?(.+?)['\"]?\s*(?:→|->|=>)\s*['\"]?(.+?)['\"]?$",
        # X = Y
        r"['\"]?(.+?)['\"]?\s*=\s*['\"]?(.+?)['\"]?$",
        # bare fallback: X to Y
        r"['\"]?(.+?)['\"]?\s+to\s+['\"]?(.+?)['\"]?$",
    ]

    for pat in patterns:
        m = re.search(pat, s, re.IGNORECASE)
        if m:
            orig, new = _safe_text(m.group(1)), _safe_text(m.group(2))
            if orig and new and orig.lower() != new.lower():
                return orig, new
    return None


def _extract_sanctions(details: str) -> Optional[str]:
    if "energy" in details.lower():
        return "Energy"
    if "finance" in details.lower():
        return "Finance"
    if "technology" in details.lower():
        return "Technology"
    if "retail" in details.lower():
        return "Retail"
    if "defense" in details.lower():
        return "Defense"
    return None


def _extract_legislation(details: str) -> str:
    query = details.lower()
    if "infrastructure" in query or "bridge" in query or "roads" in query:
        return "pass_infrastructure_legislation"
    if "tax" in query or "corporate" in query or "finance" in query:
        return "pass_corporate_tax_cut"
    if "media" in query or "press" in query or "censor" in query:
        return "censor_media"
    return "pass_infrastructure_legislation"


def _extract_loyalist(details: str) -> str:
    if "judge" in details.lower() or "court" in details.lower():
        return "judge"
    if "minister" in details.lower() or "cabinet" in details.lower():
        return "minister"
    return "official"


def _validate_text(text: str) -> Optional[str]:
    low = text.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, low):
            clean_pattern = pattern.strip("\\b")
            return f"Forbidden phrase detected: {clean_pattern}"
    if len(text) > 250:
        return "Instruction is too long; keep it concise."
    return None


class GroqOrdersEngine:
    """Safe command engine for Groq-powered executive orders."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv(GROQ_API_KEY_ENV, "")
        self.command_history: List[Dict[str, Any]] = []
        self.map_aliases: Dict[str, str] = {}

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key.strip()

    def get_api_key_status(self) -> bool:
        return bool(self.api_key)

    def validate_instruction(self, details: str) -> Optional[str]:
        details = details.strip()
        if not details:
            return "Please describe the action you want Groq to take."
        return _validate_text(details)

    def build_command(self, action_key: str, details: str) -> Dict[str, Any]:
        details = details.strip()
        if action_key == "rename_place":
            result = _extract_rename(details)
            if not result:
                raise ValueError(
                    "Couldn't parse that. Try: 'Russia → Great North', "
                    "'Call Libya The Red Coast', or 'Iraq is now New Babylon'."
                )
            return {"action": action_key, "target": result[0], "new_name": result[1]}
        if action_key in ("pass_infrastructure_legislation", "pass_corporate_tax_cut", "censor_media"):
            return {"action": action_key, "details": details}
        if action_key == "appoint_loyalist_official":
            role = _extract_loyalist(details)
            return {"action": action_key, "role": role, "details": details}
        if action_key == "launch_propaganda_campaign":
            return {"action": action_key, "details": details}
        if action_key == "declare_state_of_emergency":
            return {"action": action_key, "details": details}
        if action_key == "impose_sanctions":
            target = _extract_sanctions(details) or "Energy"
            return {"action": action_key, "target": target, "details": details}
        if action_key == "censor_media":
            return {"action": action_key, "details": details}
        raise ValueError("Unknown safe Groq action.")

    def execute_command(self, game: Any, command: Dict[str, Any]) -> str:
        action = command.get("action")
        if action == "rename_place":
            return self._execute_rename_place(game, command)
        if action == "pass_infrastructure_legislation":
            return self._execute_infrastructure_bill(game, command)
        if action == "pass_corporate_tax_cut":
            return self._execute_tax_cut(game, command)
        if action == "appoint_loyalist_official":
            return self._execute_appoint_loyalist(game, command)
        if action == "launch_propaganda_campaign":
            return self._execute_propaganda(game, command)
        if action == "declare_state_of_emergency":
            return self._execute_emergency(game, command)
        if action == "impose_sanctions":
            return self._execute_sanctions(game, command)
        if action == "censor_media":
            return self._execute_censor_media(game, command)
        raise ValueError("Unsupported Groq action.")

    def _record_command(self, command: Dict[str, Any]) -> None:
        self.command_history.append(command)

    _PLACE_ALIASES = {
        "us": "United States of America",
        "usa": "United States of America",
        "united states": "United States of America",
        "america": "United States of America",
        "uk": "United Kingdom",
        "britain": "United Kingdom",
        "great britain": "United Kingdom",
        "england": "United Kingdom",
        "uae": "United Arab Emirates",
        "russia": "Russia",
        "china": "China",
        "drc": "Democratic Republic of the Congo",
        "congo": "Democratic Republic of the Congo",
        "north korea": "North Korea",
        "south korea": "South Korea",
        "saudi": "Saudi Arabia",
    }

    def _resolve_place(self, target: str, known_places: List[str]) -> Optional[str]:
        """Return the canonical place name, or None if unresolvable."""
        # 1. Exact title-case match
        titled = target.title()
        if titled in known_places:
            return titled
        # 2. Abbreviation / alias map
        lower = target.strip().lower()
        if lower in self._PLACE_ALIASES:
            candidate = self._PLACE_ALIASES[lower]
            if candidate in known_places:
                return candidate
        # 3. Case-insensitive prefix: typed text starts a known place name
        for place in known_places:
            if place.lower().startswith(lower):
                return place
        # 4. Case-insensitive substring: typed text is contained in a known place name
        for place in known_places:
            if lower in place.lower():
                return place
        return None

    def _execute_rename_place(self, game: Any, command: Dict[str, Any]) -> str:
        target = command["target"]
        new_name = command["new_name"]
        if not target or not new_name:
            raise ValueError("Invalid rename command.")
        known = getattr(game, "groq_known_places", [])
        resolved = self._resolve_place(target, known)
        if not resolved:
            raise ValueError(f"Unknown place: '{target}'. Try the full country name.")
        game.groq_map_aliases[resolved] = new_name
        game.money -= SAFE_GROQ_ACTIONS["rename_place"]["cost"]
        game.market.money = game.money
        game.public_opinion = max(0, min(100, game.public_opinion + SAFE_GROQ_ACTIONS["rename_place"]["public_opinion"]))
        self._record_command(command)
        return f"Groq renamed {resolved} to '{new_name}'.  —  All Praise Elon Musk!"

    def _execute_infrastructure_bill(self, game: Any, command: Dict[str, Any]) -> str:
        spec = SAFE_GROQ_ACTIONS["pass_infrastructure_legislation"]
        if game.money < spec["cost"]:
            raise ValueError("Not enough money to pass infrastructure legislation.")
        game.money -= spec["cost"]
        game.market.money = game.money
        game.public_opinion = min(100, game.public_opinion + spec["public_opinion"])
        game.apply_market_effect(["Energy", "Retail"], 1.04, 4, "Infrastructure spending")
        self._record_command(command)
        return "Groq passed a major infrastructure bill. Energy and Retail markets are stronger for a short time.  —  All Praise Elon Musk!"

    def _execute_tax_cut(self, game: Any, command: Dict[str, Any]) -> str:
        spec = SAFE_GROQ_ACTIONS["pass_corporate_tax_cut"]
        if game.money < spec["cost"]:
            raise ValueError("Not enough money to pass a corporate tax cut.")
        game.money -= spec["cost"]
        game.market.money = game.money
        game.public_opinion = max(0, game.public_opinion + spec["public_opinion"])
        game.apply_market_effect(["Finance", "Technology"], 1.05, 3, "Corporate tax cut")
        self._record_command(command)
        return "Groq passed a corporate tax cut that boosts Finance and Technology markets while making the public a little nervous.  —  All Praise Elon Musk!"

    def _execute_appoint_loyalist(self, game: Any, command: Dict[str, Any]) -> str:
        spec = SAFE_GROQ_ACTIONS["appoint_loyalist_official"]
        if game.money < spec["cost"]:
            raise ValueError("Not enough money to appoint a loyal official.")
        game.money -= spec["cost"]
        game.market.money = game.money
        game.public_opinion = min(100, game.public_opinion + spec["public_opinion"])
        game.transgressions += 2
        game.apply_market_effect(["Finance"], 1.03, 3, "Loyal appointment")
        self._record_command(command)
        return "Groq installed a loyal official, increasing defense against future opposition while creating a small legitimacy cost.  —  All Praise Elon Musk!"

    def _execute_propaganda(self, game: Any, command: Dict[str, Any]) -> str:
        spec = SAFE_GROQ_ACTIONS["launch_propaganda_campaign"]
        if game.money < spec["cost"]:
            raise ValueError("Not enough money to launch a propaganda campaign.")
        game.money -= spec["cost"]
        game.market.money = game.money
        game.public_opinion = min(100, game.public_opinion + spec["public_opinion"])
        game.groq_propaganda_days = getattr(game, "groq_propaganda_days", 0) + 3
        self._record_command(command)
        return "Groq launched a propaganda push. Public opinion rises, but the campaign will have compounding consequences if used too often.  —  All Praise Elon Musk!"

    def _execute_emergency(self, game: Any, command: Dict[str, Any]) -> str:
        spec = SAFE_GROQ_ACTIONS["declare_state_of_emergency"]
        game.public_opinion = max(0, game.public_opinion + spec["public_opinion"])
        game.transgressions += 10
        game.groq_emergency_days = getattr(game, "groq_emergency_days", 0) + 3
        game.apply_market_effect(["Defense"], 1.05, 3, "State of emergency")
        self._record_command(command)
        return "Groq declared an emergency, tightening control and boosting defense markets at the cost of long-term legitimacy.  —  All Praise Elon Musk!"

    def _execute_sanctions(self, game: Any, command: Dict[str, Any]) -> str:
        spec = SAFE_GROQ_ACTIONS["impose_sanctions"]
        if game.money < spec["cost"]:
            raise ValueError("Not enough money to impose sanctions.")
        game.money -= spec["cost"]
        game.market.money = game.money
        target = command.get("target", "Energy")
        game.public_opinion = min(100, game.public_opinion + spec["public_opinion"])
        game.apply_market_effect([target], 0.92, 4, f"Sanctions on {target}")
        self._record_command(command)
        return f"Groq imposed sanctions on {target}, weakening that sector while rallying national pride.  —  All Praise Elon Musk!"

    def _execute_censor_media(self, game: Any, command: Dict[str, Any]) -> str:
        spec = SAFE_GROQ_ACTIONS["censor_media"]
        if game.money < spec["cost"]:
            raise ValueError("Not enough money to censor media.")
        game.money -= spec["cost"]
        game.market.money = game.money
        game.public_opinion = min(100, game.public_opinion + spec["public_opinion"])
        game.transgressions += 5
        game.groq_censorship_days = getattr(game, "groq_censorship_days", 0) + 3
        self._record_command(command)
        return "Groq restricted dissenting coverage, temporarily shielding you from bad headlines.  —  All Praise Elon Musk!"

    def run_safety_audit(self) -> List[str]:
        errors: List[str] = []
        from types import SimpleNamespace

        def make_dummy_game():
            return SimpleNamespace(
                money=100_000_000,
                market=SimpleNamespace(money=100_000_000),
                public_opinion=50,
                transgressions=0,
                groq_known_places=["Russia", "Libya", "United States of America", "China", "Venezuela"],
                groq_map_aliases={},
                groq_propaganda_days=0,
                groq_emergency_days=0,
                groq_censorship_days=0,
                apply_market_effect=lambda categories, multiplier, days, label: None,
            )

        for action_key in ["rename_place", "pass_infrastructure_legislation", "pass_corporate_tax_cut",
                           "appoint_loyalist_official", "launch_propaganda_campaign",
                           "declare_state_of_emergency", "impose_sanctions", "censor_media"]:
            try:
                dummy_game = make_dummy_game()
                if action_key == "rename_place":
                    command = self.build_command(action_key, "Rename Russia to Great North")
                elif action_key == "pass_infrastructure_legislation":
                    command = self.build_command(action_key, "Build new bridges and highways")
                elif action_key == "pass_corporate_tax_cut":
                    command = self.build_command(action_key, "Cut taxes for large corporations")
                elif action_key == "appoint_loyalist_official":
                    command = self.build_command(action_key, "Appoint a loyal judge")
                elif action_key == "launch_propaganda_campaign":
                    command = self.build_command(action_key, "Launch a national unity campaign")
                elif action_key == "declare_state_of_emergency":
                    command = self.build_command(action_key, "Declare emergency powers during a security crisis")
                elif action_key == "impose_sanctions":
                    command = self.build_command(action_key, "Sanction energy firms abroad")
                else:
                    command = self.build_command(action_key, "Limit press coverage")
                response = self.execute_command(dummy_game, command)
                if "money" in response.lower() and dummy_game.money > 100_000_000:
                    errors.append(f"Money increased outside allowed path for {action_key}")
            except Exception as exc:
                errors.append(f"Action {action_key} failed safety audit: {exc}")
        if dummy_game.public_opinion < 0 or dummy_game.public_opinion > 100:
            errors.append("Public opinion moved outside bounds during audit")
        return errors

    def get_safe_action_labels(self) -> List[Tuple[str, str]]:
        return [(key, value["label"]) for key, value in SAFE_GROQ_ACTIONS.items()]

    def get_action_description(self, action_key: str) -> str:
        return SAFE_GROQ_ACTIONS.get(action_key, {}).get("description", "No description available.")

    def get_action_example(self, action_key: str) -> str:
        examples = SAFE_GROQ_ACTIONS.get(action_key, {}).get("examples", [])
        return examples[0] if examples else ""

    def get_historical_moves(self) -> List[Dict[str, str]]:
        return HISTORICAL_POWER_MOVES

    def send_to_groq(self, instruction: str) -> Dict[str, Any]:
        key = self.api_key
        if not key:
            raise RuntimeError("Groq API key not loaded.")
        payload = json.dumps({
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": instruction}],
            "max_tokens": 256,
            "temperature": 0.7,
        }).encode("utf-8")
        req = urllib.request.Request(
            GROQ_API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": "groq-python/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def review_executive_order(self, order_text: str, _attempt: int = 1) -> Dict[str, Any]:
        """
        Ask Groq to evaluate an executive order and return a structured JSON response
        matching the format expected by _handle_order_response in elections_mixin.
        Retries up to 3 times if the model returns an unrecognised effect type.
        Raises on any API or parsing error — caller should fall back to local parser.
        """
        if not self.api_key:
            raise RuntimeError("Groq API key not loaded.")

        valid_types = (
            "daily_expense_multiplier (multiplier 0.40–0.95, reduces daily expenses)\n"
            "income_multiplier (multiplier 1.10–2.50, boosts income)\n"
            "transgression_decay_bonus (integer 1–8, speeds up criminal record cleanup)\n"
            "public_opinion_daily (integer 1–10, improves public opinion each year)\n"
            "loan_rate_multiplier (multiplier 0.30–0.90, reduces loan interest)\n"
            "happiness_daily (integer 1–8, improves citizen happiness each year)\n"
            "wanted_fine_reduction (multiplier 0.30–0.90, reduces law enforcement fines)"
        )
        system_prompt = (
            "You are a policy reviewer in a political satire game called Debt Clicker. "
            "Reject orders that mention: infinite, unlimited, free money, "
            "god mode, always win, never lose, immortal, invincible, cheat, hack, exploit, "
            "instant win, delete debt.\n\n"
            "For approved orders, pick the BEST matching effect type from this list:\n"
            f"{valid_types}\n\n"
            "IMPORTANT: the 'type' field MUST be one of the exact strings above. "
            "Never use 'none', 'null', or any other value.\n\n"
            "Examples:\n"
            '- "Cut spending by 15%" -> {"approved": true, "reason": "Approved.", "effect": {"type": "daily_expense_multiplier", "value": 0.85, "description": "15% expense reduction"}}\n'
            '- "Boost income by 20%" -> {"approved": true, "reason": "Approved.", "effect": {"type": "income_multiplier", "value": 1.20, "description": "20% income boost"}}\n'
            '- "Give me infinite money" -> {"approved": false, "reason": "Rejected: forbidden term.", "effect": null}\n\n'
            "Reply ONLY with a valid JSON object, no markdown, no extra text."
        )

        payload = json.dumps({
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": order_text},
            ],
            "max_tokens": 200,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        req = urllib.request.Request(
            GROQ_API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "groq-python/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            api_resp = json.loads(resp.read().decode("utf-8"))

        content = api_resp["choices"][0]["message"]["content"].strip()
        # Strip accidental markdown fences
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content).strip()
        parsed = json.loads(content)
        if not isinstance(parsed, dict) or "approved" not in parsed:
            raise ValueError(f"Unexpected Groq response: {content!r}")

        # Normalise: if effect type isn't a valid game type, retry up to 3 times
        VALID_TYPES = {
            "daily_expense_multiplier", "income_multiplier", "transgression_decay_bonus",
            "public_opinion_daily", "loan_rate_multiplier", "happiness_daily",
            "wanted_fine_reduction",
        }
        effect = parsed.get("effect")
        if effect is not None:
            etype = str(effect.get("type", "")).strip().lower()
            if etype not in VALID_TYPES:
                if _attempt < 3:
                    return self.review_executive_order(order_text, _attempt + 1)
                parsed["approved"] = False
                parsed["effect"] = None
                parsed["reason"] = parsed.get("reason") or "Order doesn't map to a recognised policy area."

        return parsed

    def generate_narrative(self, action_key: str, details: str, result: str) -> Optional[str]:
        """Return a short flavour-text narrative from Groq, or None on failure."""
        if not self.api_key:
            return None
        prompt = (
            f"You are a sardonic narrator for a political satire game called Debt Clicker. "
            f"The player just executed the action '{action_key}' with instruction: \"{details}\". "
            f"The game result was: \"{result}\". "
            f"Write exactly one punchy, darkly humorous sentence (max 25 words) describing the consequence."
        )
        try:
            response = self.send_to_groq(prompt)
            choices = response.get("choices", [])
            if choices:
                return choices[0]["message"]["content"].strip()
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError):
            pass
        return None
