"""
mobile/state.py — the entire game engine, with zero UI dependency.

Mirrors the rules implemented across the desktop Tkinter mixins, but is
plain Python: every place the desktop code would touch a widget, this
calls one of a small set of UI hooks (on_log, on_ticker, on_notify,
on_warning, on_status, on_game_over) that the Kivy layer wires up.
That split is what makes this importable on a phone.
"""

import json
import os
import random
import time
import urllib.request
import urllib.error

from market import StockMarket
from network_client import NetworkClient
from groq_integration import GroqOrdersEngine
from constants import STOCK_CATEGORIES, CATEGORY_PRICE_RANGES, LEADERBOARD_FILE, GLOBAL_LB_URL

import mobile.game_data as gd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CAREER_FILE = os.path.join(DATA_DIR, "career_mobile.json")
LEGACY_FILE = os.path.join(DATA_DIR, "legacy_mobile.json")
SAVE_FILE = os.path.join(DATA_DIR, "save_mobile.json")


def _noop(*_a, **_k):
    pass


class GameState:
    """Holds all game state and every daily-tick rule. UI-agnostic."""

    def __init__(self):
        # UI hooks — the Kivy app replaces these with real callbacks.
        self.on_log = _noop        # (msg: str)
        self.on_ticker = _noop     # (msg: str)
        self.on_notify = _noop     # (title, body, category)
        self.on_warning = _noop    # (title, body, action)
        self.on_status = _noop     # () — call after most mutations to refresh UI
        self.on_game_over = _noop  # () — called once running flips False

        self.market = StockMarket()
        self.net_client = NetworkClient()
        self.groq_engine = GroqOrdersEngine()

        self.tickers = {}
        for category, stocks in STOCK_CATEGORIES.items():
            lo, hi = CATEGORY_PRICE_RANGES.get(category, (10, 500))
            for name, ticker in stocks.items():
                self.tickers[name] = ticker
                self.market.create_stock(name, round(random.uniform(lo, hi), 2), category)

        self.username = ""
        self.country = ""
        self.game_mode = "president"
        self.is_multiplayer = False
        self.running = False
        self._reset_flags()

    # =====================================================================
    # LIFECYCLE
    # =====================================================================

    def _reset_flags(self):
        self.money = 100_000_000
        self.days = 0
        self.happiness = 50
        self.public_opinion = 75
        self.transgressions = 0
        self.wanted_level = 0
        self.won_game = False
        self.death_cause = "broke"

        self.warned_happiness = False
        self.warned_opinion = False
        self.warned_transgress = False
        self.warned_sec_heat = False
        self.warned_bm_heat = False

        self.loans = []
        self.max_loans = 1
        self.loan_defaults = 0
        self.loans_repaid = 0
        self.bank_blacklist = set()

        self.owned_assets = set()
        self.owned_islands = set()
        self.bombed_countries = set()
        self.oil_operations = []
        self.action_taken = {}

        self.alliance = None
        self.alliance_days = 0
        self.sanctions = {}

        self.rivals = {}
        self.rival_retaliation_boost = 0

        self.militia = 0
        self.active_wars = {}

        self.factories = []
        self.work_level = 0
        self._last_work_year = -1

        self.bm_heat = 0
        self.sec_heat = 0
        self.trading_frozen_days = 0
        self.margin_bets = []
        self.market_effects = []
        self._pumped_this_year = {}

        self.is_president = False
        self.presidential_term = 0
        self.years_in_office = 0
        self.senators_bribed = 0
        self.executive_orders = []
        self.cabinet = {}
        self.ever_president = False

        self.lobby_immunity = False
        self.pandemic = False
        self.revolution_used = False

        self.net_worth_history = []
        self.inbox = []
        self.event_log = []

        self.roulette_bullet = None
        self.slot_last = None
        self.poker_hand = []
        self.poker_hold = [False] * 5
        self.poker_bet = 0
        self.bj_deck = []
        self.bj_player = []
        self.bj_dealer = []
        self.bj_bet = 0

    def start_game(self, username, country, game_mode):
        self.username = username
        self.country = country
        self.game_mode = game_mode
        self._reset_flags()
        self.running = True

        if game_mode == "billionaire":
            self.money = 1_000_000_000
            self.factories = [
                {"type_id": "steel_mill", "worker_tier": "standard", "on_strike": False, "strike_days": 0},
                {"type_id": "oil_refinery", "worker_tier": "standard", "on_strike": False, "strike_days": 0},
                {"type_id": "tech_factory", "worker_tier": "standard", "on_strike": False, "strike_days": 0},
            ]
        else:
            self.money = 100_000_000

        self.market.money = self.money
        legacy = self._load_legacy()
        if legacy:
            self.money += legacy
            self.market.money = self.money
            self.on_log(f"Legacy bonus applied: +${legacy:,}")

        self._init_rivals()
        self.on_log(f"Welcome, {self.username}. Starting capital: ${self.money:,}")
        self.on_status()

    def _init_rivals(self):
        defs = gd.PRESIDENT_RIVAL_DEFS if self.game_mode == "president" else gd.RIVAL_DEFS
        self.rivals = {r["name"]: {"money": r["money"], "controls": {}} for r in defs}

    # =====================================================================
    # MASTER DAILY TICK  (call every 60s from the Kivy Clock)
    # =====================================================================

    def tick_day(self):
        if not self.running:
            return
        self.days += 1
        self._lose_money()
        self._update_stock_prices()
        self._process_resource_income()
        self._process_island_income()
        self._process_loans()
        self._process_rivals()
        self._process_sanctions()
        self._process_alliance_tick()
        self._process_wars()
        self._process_militia_effects()
        self._process_factory_income()
        self._check_factory_events()
        self._process_presidential_term()
        self._apply_executive_order_effects()
        self._process_cabinet()
        self._process_margin_bets()
        self._process_sec_heat()
        self._process_black_market_heat()
        self._update_wanted_level()
        self._track_net_worth()
        self._check_win_condition()
        self._check_critical_stats()
        if not self.running:
            return
        self._random_events()
        if random.random() < 0.45:
            self._random_events()
        if self.money <= 0:
            self.running = False
            self.death_cause = "broke"
            self.on_log("You lost everything.")
            self.on_game_over()
        self.on_status()

    def _lose_money(self):
        m = self.money
        if m < 1_000:          lost = random.randint(10, 100)
        elif m < 100_000:       lost = int(m * random.uniform(0.02, 0.06))
        elif m < 10_000_000:    lost = int(m * random.uniform(0.015, 0.045))
        elif m < 100_000_000:   lost = int(m * random.uniform(0.008, 0.022))
        else:                   lost = int(m * random.uniform(0.006, 0.016))
        idle = not self.oil_operations and not self.owned_islands
        if idle and m >= 1_000_000:
            lost += int(m * 0.005)
        self.money -= lost
        self.market.money = self.money
        self.on_log(f"Daily expenses: -${lost:,}")
        self._apply_asset_costs()
        self.happiness = max(0, self.happiness - 4)
        self.public_opinion = min(100, self.public_opinion + 0.3)
        if self.transgressions > 0 and self.wanted_level < 2:
            self.transgressions = max(0, self.transgressions - 0.4)

    def add_transgression(self, n, opinion_hit=None):
        self.transgressions = min(100, self.transgressions + n)
        hit = opinion_hit if opinion_hit is not None else n // 2
        self.public_opinion = max(0, self.public_opinion - hit)

    def add_happiness(self, n):
        self.happiness = min(100, self.happiness + n)

    def apply_market_effect(self, categories, multiplier, days, label):
        self.market_effects.append({"categories": categories, "multiplier": multiplier,
                                     "days_left": days, "label": label})

    def _update_stock_prices(self):
        for name, data in self.market.stocks.items():
            if data["returns"]:
                idx = data["return_index"] % len(data["returns"])
                change = 1 + data["returns"][idx]
                data["return_index"] += 1
            else:
                change = random.uniform(0.92, 1.08)
            cat = data.get("category", "Custom")
            for effect in self.market_effects:
                if "ALL" in effect["categories"] or cat in effect["categories"]:
                    change *= effect["multiplier"]
            data["price"] = max(0.01, data["price"] * change)
            data["history"].append(data["price"])
        for effect in self.market_effects:
            effect["days_left"] -= 1
        self.market_effects = [e for e in self.market_effects if e["days_left"] > 0]

    def get_infamy_tier(self):
        t = self.transgressions
        if t < 20: return 0, "Nobody"
        if t < 40: return 1, "Shady"
        if t < 60: return 2, "Crime Lord"
        if t < 80: return 3, "War Criminal"
        if t < 100: return 4, "Antichrist"
        return 5, "ENDGAME"

    def _update_wanted_level(self):
        t = self.transgressions
        level = 0 if t < 20 else 1 if t < 40 else 2 if t < 60 else 3 if t < 80 else 4
        if level != self.wanted_level:
            self.wanted_level = level
            labels = ["Clean", "Media Attention", "Senate Investigation", "FBI Target", "Interpol Red Notice"]
            self.on_log(f"Wanted level changed: {labels[level]}")
            self.on_ticker(f"BREAKING: {labels[level]} — threat level rising...")
        if self.wanted_level > 0:
            fine = self.wanted_level * 500_000
            self.money -= fine
            self.market.money = self.money

    def _track_net_worth(self):
        self.net_worth_history.append(int(self.money))

    # =====================================================================
    # WORLD MAP
    # =====================================================================

    def get_alliance_discount(self, country):
        if not self.alliance:
            return 1.0
        return gd.ALLIANCE_DATA[self.alliance]["discount"] if country in gd.ALLIANCE_DATA[self.alliance]["countries"] else 1.0

    def bomb_or_coup(self, country, resource, action_name):
        info = gd.RESOURCE_DATA[resource]["countries"][country]
        act = gd.ACTIONS[action_name]
        discount = self.get_alliance_discount(country)
        cost = int(info["action_cost"] * act["cost_mult"] * discount)
        if self.money < cost:
            self.on_log(f"Need ${cost:,} for this operation.")
            return False
        income = int(info["income"] * act["income_mult"])
        days = int(info["days"] * act["days_mult"])
        self.money -= cost
        self.market.money = self.money
        self.bombed_countries.add(country)
        self.action_taken[country] = action_name
        self.oil_operations.append({"country": country, "income": income, "days_left": days,
                                     "resource": resource, "action": action_name})
        self.add_transgression(act["transgression"], act["opinion"])
        self.add_happiness(act["happiness"])
        self.on_log(f"{act['tag']} {action_name} in {country}! Cost ${cost:,}, income ${income:,}/yr x{days}yr")

        if action_name == "Bomb" and random.random() < 0.3:
            self.apply_sanction(country, random.randint(5, 15))

        rival_name = self._is_rival_controlled(resource, country)
        if action_name == "Bomb" and rival_name:
            self._rival_retaliate(rival_name, country, resource)

        if resource in gd.RESOURCE_CRASH:
            self._insider_front_run(gd.RESOURCE_CRASH[resource][0])
            cats, mult, days_ = gd.RESOURCE_CRASH[resource]
            self.apply_market_effect(cats, mult, days_, f"Resource seizure: {country}")
        if action_name == "Bomb":
            self.apply_market_effect(["Defense"], 1.04, 3, "Military op")
        self.on_status()
        return True

    def _insider_front_run(self, crash_categories):
        dumped_value, dumped = 0, []
        for name, data in self.market.stocks.items():
            if data.get("category") not in crash_categories or data.get("shares", 0) <= 0:
                continue
            proceeds = data["shares"] * data["price"]
            self.money += proceeds
            self.market.money = self.money
            dumped_value += proceeds
            dumped.append(name)
            data["shares"] = 0
        if dumped:
            self.sec_heat = min(150, self.sec_heat + 15)
            self.add_transgression(10, 6)
            self.on_log(f"Insider trade: liquidated {', '.join(dumped)} for ${dumped_value:,.0f} pre-crash.")

    def apply_sanction(self, country, days=10):
        self.sanctions[country] = days
        self.on_log(f"SANCTIONED by {country} for {days} days!")
        self.on_ticker(f"BREAKING: {country} imposes economic sanctions...")

    def _process_sanctions(self):
        expired = [c for c, d in self.sanctions.items() if d <= 1]
        for c in expired:
            del self.sanctions[c]
        for c in list(self.sanctions.keys()):
            if c not in expired:
                self.sanctions[c] -= 1
                self.money -= 500_000
                self.market.money = self.money

    def _process_resource_income(self):
        if not self.oil_operations:
            return
        total = sum(op["income"] for op in self.oil_operations)
        for op in self.oil_operations:
            op["days_left"] -= 1
        for op in [o for o in self.oil_operations if o["days_left"] <= 0]:
            self.bombed_countries.discard(op["country"])
            self.action_taken.pop(op["country"], None)
        self.oil_operations = [o for o in self.oil_operations if o["days_left"] > 0]
        if total:
            self.money += total
            self.market.money = self.money

    def sign_alliance(self, ally):
        data = gd.ALLIANCE_DATA[ally]
        if self.money < data["cost"]:
            return False
        self.money -= data["cost"]
        self.market.money = self.money
        self.alliance = ally
        self.alliance_days = data["days"]
        self.on_log(f"Alliance signed with {ally} for {data['days']} days.")
        return True

    def _process_alliance_tick(self):
        if not self.alliance:
            return
        if self.wanted_level >= 3 and random.random() < 0.04 * (self.wanted_level - 2):
            self._alliance_betrayal()
            return
        data = gd.ALLIANCE_DATA[self.alliance]
        if self.alliance == "USA":
            self.money += 750_000
        elif self.alliance == "Russia":
            self.militia += 20
        elif self.alliance == "China":
            self.money += int(sum(op["income"] for op in self.oil_operations) * 0.15)
        self.market.money = self.money
        self.alliance_days -= 1
        if self.alliance_days <= 0:
            self.on_log(f"Alliance with {self.alliance} expired.")
            self.alliance = None

    def _alliance_betrayal(self):
        ally = self.alliance
        seized = int(self.money * random.uniform(0.05, 0.12))
        self.money -= seized
        self.market.money = self.money
        self.public_opinion = max(0, self.public_opinion - 15)
        self.alliance = None
        self.apply_sanction(ally, 20)
        self.on_log(f"BETRAYAL: {ally} cut ties and froze ${seized:,}.")
        self.on_notify(f"Alliance Betrayed: {ally}", f"{ally} froze ${seized:,} and sanctioned you.", "rival")

    # =====================================================================
    # ISLANDS
    # =====================================================================

    def buy_island(self, name):
        isl = next((i for i in gd.ISLANDS if i["name"] == name), None)
        if not isl or self.money < isl["price"]:
            return False
        self.money -= isl["price"]
        self.market.money = self.money
        self.owned_islands.add(name)
        self.on_log(f"Purchased {name} ({isl['loc']}) for ${isl['price']:,}")
        return True

    def _process_island_income(self):
        if not self.owned_islands:
            return
        total_income = total_upkeep = 0
        for name in self.owned_islands:
            isl = next((i for i in gd.ISLANDS if i["name"] == name), None)
            if isl:
                total_income += isl["income"]
                total_upkeep += isl["upkeep"]
        net = total_income - total_upkeep
        self.money += net
        self.market.money = self.money

    # =====================================================================
    # RIVALS
    # =====================================================================

    def _is_rival_controlled(self, resource, country):
        for name, rival in self.rivals.items():
            if country in rival["controls"].get(resource, set()):
                return name
        return None

    def _process_rivals(self):
        for name, rival in self.rivals.items():
            rival["money"] *= random.uniform(0.99, 1.05)
            if random.random() < 0.15:
                resource = random.choice(list(gd.RESOURCE_DATA.keys()))
                countries = list(gd.RESOURCE_DATA[resource]["countries"].keys())
                occupied = set()
                for rv in self.rivals.values():
                    occupied |= rv["controls"].get(resource, set())
                available = [c for c in countries if c not in self.bombed_countries
                             and c != self.country and c not in occupied]
                if available:
                    target = random.choice(available)
                    cost = gd.RESOURCE_DATA[resource]["countries"][target]["action_cost"] * 0.4
                    if rival["money"] >= cost:
                        rival["money"] -= cost
                        rival["controls"].setdefault(resource, set()).add(target)
                        self.on_ticker(f"MARKETS: {name} acquires {resource} stake in {target}...")

            if self.rival_retaliation_boost > 0:
                self.rival_retaliation_boost -= 1
            base_chance = 0.16 if self.rival_retaliation_boost > 0 else 0.08
            if random.random() < base_chance:
                self._rival_attack_player(name, rival)

            for res in list(rival["controls"].keys()):
                released = {c for c in rival["controls"][res] if random.random() < 0.01}
                rival["controls"][res] -= released
        self._process_rival_wars()

    def _process_rival_wars(self):
        names = list(self.rivals.keys())
        if len(names) < 2 or random.random() >= 0.12:
            return
        a_name, d_name = random.sample(names, 2)
        attacker, defender = self.rivals[a_name], self.rivals[d_name]
        contested = [(r, c) for r, cs in defender["controls"].items() for c in cs]
        if contested and random.random() < 0.6:
            resource, country = random.choice(contested)
            defender["controls"][resource].discard(country)
            attacker["controls"].setdefault(resource, set()).add(country)
            loss = defender["money"] * random.uniform(0.03, 0.10)
            defender["money"] -= loss
            attacker["money"] += loss * 0.5
            self.on_ticker(f"CONFLICT: {a_name} and {d_name} clash over {country}...")
        else:
            drain = defender["money"] * random.uniform(0.02, 0.06)
            defender["money"] -= drain
            attacker["money"] -= drain * 0.3

    def _rival_attack_player(self, name, rival):
        pool = ["smear", "lobby", "sabotage", "poach", "lawsuit"]
        attack = random.choice(pool)
        if attack == "smear":
            hit = random.randint(5, 15)
            self.public_opinion = max(0, self.public_opinion - hit)
            self.on_notify(f"{name}: Smear Campaign", f"Public Opinion -{hit}%", "rival")
        elif attack == "lobby":
            hit = random.randint(8, 20)
            self.add_transgression(hit, 10)
            self.on_notify(f"{name}: Regulatory Tip-Off", f"Transgressions +{hit}", "rival")
        elif attack == "sabotage":
            if self.oil_operations:
                op = random.choice(self.oil_operations)
                lost = op["income"] * random.randint(3, 7)
                self.money -= lost
                self.market.money = self.money
                self.on_notify(f"{name}: Operation Sabotaged", f"-${lost:,.0f}", "rival")
            else:
                stolen = int(self.money * random.uniform(0.01, 0.04))
                self.money -= stolen
                self.market.money = self.money
                self.on_notify(f"{name}: Financial Sabotage", f"-${stolen:,}", "rival")
        elif attack == "poach":
            hit = random.randint(5, 12)
            self.happiness = max(0, self.happiness - hit)
            self.on_notify(f"{name}: Staff Poached", f"Happiness -{hit}", "rival")
        elif attack == "lawsuit":
            fine = int(self.money * random.uniform(0.02, 0.06))
            trans = random.randint(5, 12)
            self.money -= fine
            self.market.money = self.money
            self.add_transgression(trans, 8)
            self.on_notify(f"{name}: Lawsuit Filed", f"-${fine:,} | Transgressions +{trans}", "rival")

    def _rival_retaliate(self, rival_name, country, resource):
        kind = random.choice(["fine", "smear", "counter_op"])
        if kind == "fine":
            fine = int(self.money * random.uniform(0.03, 0.08))
            self.money -= fine
            self.market.money = self.money
            self.add_transgression(10, 8)
            self.on_notify(f"Retaliation: {rival_name}", f"-${fine:,} | Transgressions +10", "rival")
        elif kind == "smear":
            oh, hh = random.randint(10, 20), random.randint(5, 10)
            self.public_opinion = max(0, self.public_opinion - oh)
            self.happiness = max(0, self.happiness - hh)
            self.on_notify(f"Retaliation: {rival_name}", f"Opinion -{oh} | Happiness -{hh}", "rival")
        elif kind == "counter_op" and self.oil_operations:
            op = random.choice(self.oil_operations)
            self.oil_operations.remove(op)
            self.on_notify(f"Retaliation: {rival_name}", f"Operation in {op['country']} seized.", "rival")

    def buyout_rival(self, resource, country, rival_name):
        base_cost = gd.RESOURCE_DATA[resource]["countries"][country]["action_cost"]
        cost = int(base_cost * 2)
        if self.money < cost:
            return False
        self.money -= cost
        self.market.money = self.money
        self.rivals[rival_name]["controls"].get(resource, set()).discard(country)
        return True

    def _process_wars(self):
        expired = [n for n, d in self.active_wars.items() if d <= 0]
        for n in expired:
            del self.active_wars[n]
        for n in list(self.active_wars):
            self.active_wars[n] -= 1
            self.money -= 1_500_000
            self.market.money = self.money
            self.add_transgression(1, 1)

    # =====================================================================
    # MILITIA / WAR ROOM (vs strongest AI rival — single-player equivalent)
    # =====================================================================

    def buy_militia(self, tier_idx):
        tier = gd.MILITIA_TIERS[tier_idx]
        if self.money < tier["cost"]:
            return False
        self.money -= tier["cost"]
        self.market.money = self.money
        self.militia += tier["units"]
        self.on_log(f"Recruited {tier['name']}: +{tier['units']} militia units.")
        return True

    def deploy_war_action(self, action_id, target_rival):
        act = next(a for a in gd.WAR_ACTIONS if a["id"] == action_id)
        if self.militia < act["units"]:
            return None
        self.militia -= act["units"]
        rival = self.rivals[target_rival]
        result = ""
        if action_id == "spy":
            result = f"{target_rival} net worth: ${rival['money']:,.0f}"
        elif action_id == "raid":
            pct = random.uniform(0.08, 0.15)
            stolen = rival["money"] * pct
            rival["money"] -= stolen
            self.money += stolen
            self.market.money = self.money
            result = f"Raided ${stolen:,.0f} from {target_rival}."
        elif action_id == "assassinate":
            self.rival_retaliation_boost = 3
            result = f"{target_rival}'s advisor hit — expect retaliation."
        elif action_id == "sabotage":
            result = f"Sabotaged one of {target_rival}'s operations."
        elif action_id == "blockade":
            result = f"{target_rival} blockaded for 4 days."
        elif action_id == "nuke":
            lost = rival["money"] * 0.40
            rival["money"] -= lost
            result = f"NUCLEAR STRIKE: {target_rival} lost ${lost:,.0f}!"
        self.on_log(f"[WAR ROOM] {result}")
        return result

    def _process_militia_effects(self):
        pass  # militia is a static stockpile between actions; nothing decays daily

    # =====================================================================
    # FACTORIES
    # =====================================================================

    def buy_factory(self, type_id):
        ftype = gd.FACTORY_BY_ID[type_id]
        if self.money < ftype["price"]:
            return False
        self.money -= ftype["price"]
        self.market.money = self.money
        self.factories.append({"type_id": type_id, "worker_tier": "standard",
                                "on_strike": False, "strike_days": 0})
        return True

    def set_worker_tier(self, factory_idx, tier_id):
        self.factories[factory_idx]["worker_tier"] = tier_id

    def _process_factory_income(self):
        if not self.factories:
            return
        total_income = total_wages = 0
        for fac in self.factories:
            ftype = gd.FACTORY_BY_ID[fac["type_id"]]
            tier = gd.WORKER_BY_ID[fac["worker_tier"]]
            if fac.get("on_strike"):
                fac["strike_days"] -= 1
                if fac["strike_days"] <= 0:
                    fac["on_strike"] = False
                continue
            income = ftype["income"] * tier["income_mult"]
            wages = ftype["base_wage_cost"] * tier["wage_mult"]
            total_income += income
            total_wages += wages
            self.public_opinion = max(0, min(100, self.public_opinion + tier["opinion_per_day"]))
            if ftype.get("trans_per_day"):
                self.add_transgression(ftype["trans_per_day"], 0)
        net = total_income - total_wages
        self.money += net
        self.market.money = self.money

    def _check_factory_events(self):
        for fac in self.factories:
            if fac.get("on_strike"):
                continue
            tier = gd.WORKER_BY_ID[fac["worker_tier"]]
            if random.random() < tier["strike_chance"] * 0.1:
                fac["on_strike"] = True
                fac["strike_days"] = 3
                ftype = gd.FACTORY_BY_ID[fac["type_id"]]
                self.on_notify(f"Strike at {ftype['name']}", "3-day work stoppage.", "financial")

    # =====================================================================
    # STOCK MARKET
    # =====================================================================

    def buy_stock(self, name, shares=1):
        if self.trading_frozen_days > 0:
            self.on_log("Trading frozen — SEC investigation in progress.")
            return
        result = self.market.buy_stock(name, shares)
        self.money = self.market.money
        self.on_log(result)

    def sell_stock(self, name, shares=1):
        result = self.market.sell_stock(name, shares)
        self.money = self.market.money
        self.on_log(result)

    def pump_stock(self, name):
        if self.trading_frozen_days > 0:
            return
        cost = 5_000_000
        if self._pumped_this_year.get(name) == self.days or self.money < cost:
            return
        self.money -= cost
        self.market.money = self.money
        data = self.market.stocks[name]
        self._pumped_this_year[name] = self.days
        data["price"] *= 1.25
        data["history"].append(data["price"])
        self.apply_market_effect([data.get("category", "Custom")], 1.12, 3, f"Pump: {name}")
        self.add_transgression(8, 5)
        self.sec_heat = min(150, self.sec_heat + 10)
        self.on_log(f"PUMP: Inflated {name} 25%. SEC Heat +10.")

    def dump_stock(self, name):
        if self.trading_frozen_days > 0:
            return
        data = self.market.stocks[name]
        shares = data["shares"]
        if shares <= 0:
            return
        proceeds = int(data["price"] * 1.5 * shares)
        self.money += proceeds
        self.market.money = self.money
        data["shares"] = 0
        data["price"] *= 0.55
        data["history"].append(data["price"])
        self.apply_market_effect([data.get("category", "Custom")], 0.85, 4, f"Dump: {name}")
        self.add_transgression(12, 8)
        self.sec_heat = min(150, self.sec_heat + 12)
        self.on_log(f"DUMP: Sold {shares} of {name} for ${proceeds:,}. SEC Heat +12.")

    def place_margin_bet(self, name, direction, stake, leverage, term_days):
        if self.trading_frozen_days > 0 or stake <= 0 or self.money < stake:
            return False
        data = self.market.stocks.get(name)
        if not data:
            return False
        self.money -= stake
        self.market.money = self.money
        self.margin_bets.append({"stock": name, "direction": direction, "stake": stake,
                                  "leverage": leverage, "entry_price": data["price"],
                                  "days_left": term_days})
        if leverage >= 5:
            self.add_transgression(2, 0)
            self.sec_heat = min(150, self.sec_heat + 3)
        return True

    def _process_margin_bets(self):
        remaining = []
        for bet in self.margin_bets:
            bet["days_left"] -= 1
            if bet["days_left"] > 0:
                remaining.append(bet)
                continue
            data = self.market.stocks.get(bet["stock"])
            price_now = data["price"] if data else bet["entry_price"]
            pct = (price_now - bet["entry_price"]) / bet["entry_price"] if bet["entry_price"] else 0
            if bet["direction"] == "short":
                pct = -pct
            payout_mult = max(0.0, min(5.0, 1 + pct * bet["leverage"]))
            payout = bet["stake"] * payout_mult
            self.money += payout
            self.market.money = self.money
            self.on_log(f"MARGIN SETTLED: {bet['stock']} payout ${payout:,.0f}")
            if payout >= bet["stake"] * 2:
                self.sec_heat = min(150, self.sec_heat + 5)
        self.margin_bets = remaining

    def _process_sec_heat(self):
        if self.trading_frozen_days > 0:
            self.trading_frozen_days -= 1
        self.sec_heat = max(0, self.sec_heat - 2)
        if self.sec_heat >= 100:
            fine = int(self.money * 0.15)
            self.money -= fine
            self.market.money = self.money
            self.add_transgression(20, 15)
            self.trading_frozen_days = 7
            self.sec_heat = 40
            self.warned_sec_heat = False
            self.on_notify("SEC Formal Investigation", f"Fined ${fine:,}. Trading frozen 7 days.", "stocks")
        elif self.sec_heat >= 60 and not self.warned_sec_heat:
            self.warned_sec_heat = True
            self.on_notify("SEC Preliminary Inquiry", "Cool off on pumps/dumps/leverage.", "stocks")
        elif self.sec_heat < 60:
            self.warned_sec_heat = False

    # =====================================================================
    # BLACK MARKET
    # =====================================================================

    def black_market_deal(self, item_id):
        item = next(i for i in gd.BLACK_MARKET_ITEMS if i["id"] == item_id)
        cd = getattr(self, "_bm_cooldowns", {})
        if cd.get(item_id, 0) > 0:
            return False
        if item["gain"] < 0 and self.money < abs(item["gain"]):
            return False
        self.money += item["gain"]
        self.market.money = self.money
        if item["trans"] > 0:
            self.add_transgression(item["trans"], abs(item["opin"]) if item["opin"] < 0 else 0)
        elif item["trans"] < 0:
            self.transgressions = max(0, self.transgressions + item["trans"])
        if item["opin"] > 0:
            self.public_opinion = min(100, self.public_opinion + item["opin"])
        if not hasattr(self, "_bm_cooldowns"):
            self._bm_cooldowns = {}
        self._bm_cooldowns[item_id] = 4
        self.bm_heat = min(150, self.bm_heat + 25)
        self.on_log(f"Black market: {item['name']} completed.")
        return True

    def _tick_bm_cooldowns(self):
        cd = getattr(self, "_bm_cooldowns", {})
        for k in list(cd):
            cd[k] -= 1
            if cd[k] <= 0:
                del cd[k]

    def _process_black_market_heat(self):
        self._tick_bm_cooldowns()
        heat = self.bm_heat
        self.bm_heat = max(0, heat - 8)
        if heat < 100:
            self.warned_bm_heat = False
            return
        if self.warned_bm_heat:
            self.running = False
            self.death_cause = "interpol_siege"
            self.on_log("INTERPOL and federal SWAT teams breach your compound.")
            self.on_game_over()
            return
        self.warned_bm_heat = True
        self.on_warning("Interpol Red Notice", "Your black market network has been traced.",
                        "Stop dealing immediately or a raid ends your empire tomorrow.")

    # =====================================================================
    # DEBT / LOANS
    # =====================================================================

    def credit_score(self):
        score = 850 - int(self.transgressions * 7) - self.loan_defaults * 100 + self.loans_repaid * 30
        return max(300, min(850, score))

    def bank_accessible(self, bank):
        if bank["name"] in self.bank_blacklist:
            return False, "Permanently blacklisted."
        score = self.credit_score()
        if score < bank["min_score"]:
            return False, f"Credit score too low ({score} — need {bank['min_score']})."
        return True, ""

    def take_loan(self, bank_name, option_idx):
        bank = next(b for b in gd.BANKS if b["name"] == bank_name)
        opt = gd.LOAN_OPTIONS[option_idx]
        ok, _ = self.bank_accessible(bank)
        if not ok or len(self.loans) >= self.max_loans:
            return False
        rate = opt["rate"] + bank["rate_bonus"]
        self.money += opt["amount"]
        self.market.money = self.money
        self.loans.append({"amount": opt["amount"], "remaining": float(opt["amount"]),
                            "rate": rate, "days_left": opt["days"], "grace_days": 0, "bank": bank_name})
        self.on_log(f"[{bank_name}] Loan approved: +${opt['amount']:,}")
        return True

    def repay_loan(self, idx):
        loan = self.loans[idx]
        if self.money < loan["remaining"]:
            return False
        self.money -= loan["remaining"]
        self.market.money = self.money
        self.loans_repaid += 1
        self.loans.pop(idx)
        return True

    def _process_loans(self):
        new_loans = []
        for loan in self.loans:
            loan["remaining"] += loan["remaining"] * loan["rate"]
            loan["days_left"] -= 1
            if loan["days_left"] <= 0:
                if self.money >= loan["remaining"]:
                    self.money -= loan["remaining"]
                    self.market.money = self.money
                    self.loans_repaid += 1
                elif self.money > 0 and loan.get("grace_days", 0) < 3:
                    paid = self.money
                    loan["remaining"] -= paid
                    self.money = 0
                    self.market.money = 0
                    loan["days_left"] = 3
                    loan["grace_days"] = loan.get("grace_days", 0) + 1
                    new_loans.append(loan)
                else:
                    self._apply_loan_default(loan)
            else:
                new_loans.append(loan)
        self.loans = new_loans

    def _apply_loan_default(self, loan):
        penalty = max(0, self.money * 0.25)
        self.money -= penalty
        self.market.money = self.money
        self.loan_defaults += 1
        self.add_transgression(10, 8)
        bank = next((b for b in gd.BANKS if b["name"] == loan.get("bank")), None)
        if bank and bank.get("blacklist_on_default"):
            self.bank_blacklist.add(bank["name"])
        if bank and bank.get("default_war"):
            self.add_transgression(20, 20)
        self.on_notify("Loan Default", f"Lost ${penalty:,.0f} (25% penalty).", "financial")

    # =====================================================================
    # LOBBY
    # =====================================================================

    def lobby_action(self, tier_id):
        tier = next(t for t in gd.LOBBY_TIERS if t["id"] == tier_id)
        if tier["once"] and tier_id == "senate_immunity" and self.lobby_immunity:
            return False
        if self.money < tier["cost"]:
            return False
        self.money -= tier["cost"]
        self.market.money = self.money
        eff = tier["effect"]
        if "transgression" in eff:
            self.transgressions = max(0, min(100, self.transgressions + eff["transgression"]))
        if "opinion" in eff:
            if eff["opinion"] == 999:
                self.public_opinion = min(100, max(self.public_opinion, 80))
            else:
                self.public_opinion = max(0, min(100, self.public_opinion + eff["opinion"]))
        if "immunity" in eff:
            self.lobby_immunity = True
        if "senator" in tier_id:
            self.senators_bribed += 1
        self.on_log(f"Lobby: {tier['name']} — ${tier['cost']:,} spent.")
        return True

    # =====================================================================
    # ASSETS
    # =====================================================================

    def buy_asset(self, asset_id):
        asset = gd.ASSET_BY_ID[asset_id]
        if asset_id in self.owned_assets or self.money < asset["cost"]:
            return False
        self.money -= asset["cost"]
        self.market.money = self.money
        self.owned_assets.add(asset_id)
        self.on_log(f"Purchased {asset['name']}.")
        return True

    def _apply_asset_costs(self):
        upkeep = sum(gd.ASSET_BY_ID[a]["upkeep"] for a in self.owned_assets)
        income = sum(gd.ASSET_BY_ID[a]["income"] for a in self.owned_assets)
        self.money += income - upkeep
        self.market.money = self.money

    # =====================================================================
    # PLEASURES
    # =====================================================================

    def indulge_pleasure(self, name):
        p = next(pl for pl in gd.PLEASURES if pl["name"] == name)
        if self.money < p["cost"]:
            return None
        self.money -= p["cost"]
        self.market.money = self.money
        self.add_happiness(p["happiness"])
        result = {"triggered_risk": False}
        if p["risk"] and random.random() < p["risk"]["chance"]:
            r = p["risk"]
            self.money += r["money"]
            self.market.money = self.money
            self.public_opinion = max(0, min(100, self.public_opinion + r["opinion"]))
            if r["transgression"]:
                self.add_transgression(r["transgression"], 0)
            result.update({"triggered_risk": True, "title": r["title"], "money": r["money"]})
            self.on_notify(r["title"], f"${r['money']:,}", "personal")
        self.on_log(f"Indulged: {name}")
        return result

    # =====================================================================
    # EXECUTIVE ORDERS / ELECTIONS / CABINET
    # =====================================================================

    def calculate_win_probability(self):
        pct = self.public_opinion * 0.6 + min(self.senators_bribed * 5, 30) + max(0, self.happiness - 50) * 0.2
        return max(5, min(90, pct))

    def run_election(self):
        win_chance = self.calculate_win_probability()
        won = random.uniform(0, 100) <= win_chance
        if won:
            self.is_president = True
            self.presidential_term += 1
            self.years_in_office = gd.TERM_LENGTH
            self.ever_president = True
            self._form_cabinet()
            self.on_notify("Elected!", f"President of {self.country}.", "election")
        else:
            self.on_notify("Election Lost", "Rebuild your image and try again.", "election")
        return won

    def _process_presidential_term(self):
        if not self.is_president:
            return
        self.years_in_office = max(0, self.years_in_office - 1)
        if self.years_in_office <= 0:
            self.is_president = False
            self.executive_orders = []
            self.cabinet = {}
            self.on_notify("Term Expired", "Presidential term complete.", "election")

    def sign_executive_order(self, template):
        if len(self.executive_orders) >= 3:
            return False
        order = {"type": template["type"], "value": template["value"], "description": template["label"]}
        self.executive_orders.append(order)
        self._apply_order_immediately(order)
        self.cabinet_react(template["type"])
        self.on_log(f"Executive Order signed: {template['label']}")
        return True

    def _apply_order_immediately(self, order):
        etype, val = order["type"], order["value"]
        if etype == "transgression_decay_bonus":
            self.transgressions = max(0, self.transgressions - val)
        elif etype == "public_opinion_daily":
            self.public_opinion = min(100, self.public_opinion + val)
        elif etype == "happiness_daily":
            self.happiness = min(100, self.happiness + val)
        elif etype == "daily_expense_multiplier":
            self.money += int(self.money * 0.01 * (1 - val))
            self.market.money = self.money

    def _apply_executive_order_effects(self):
        if not self.is_president:
            return
        for order in self.executive_orders:
            etype, val = order["type"], order["value"]
            if etype == "transgression_decay_bonus":
                self.transgressions = max(0, self.transgressions - val)
            elif etype == "public_opinion_daily":
                self.public_opinion = min(100, self.public_opinion + val)
            elif etype == "happiness_daily":
                self.happiness = min(100, self.happiness + val)
            elif etype == "income_multiplier":
                base = sum(op.get("income", 0) for op in self.oil_operations)
                self.money += int(base * (val - 1))
                self.market.money = self.money

    def get_executive_loan_rate_multiplier(self):
        mult = 1.0
        for o in self.executive_orders:
            if o["type"] == "loan_rate_multiplier":
                mult *= o["value"]
        return mult

    def _form_cabinet(self):
        self.cabinet = {}
        for spec in gd.ADVISOR_ROLES:
            self.cabinet[spec["role"]] = {"name": random.choice(spec["names"]), "approval": 55,
                                          "vacant": False, "vacant_days": 0}

    def cabinet_react(self, action_key):
        if not self.cabinet:
            return
        for role, delta in gd.CABINET_REACTIONS.get(action_key, {}).items():
            seat = self.cabinet.get(role)
            if seat and not seat.get("vacant"):
                seat["approval"] = max(0, min(100, seat["approval"] + delta))

    def _process_cabinet(self):
        if not self.is_president or not self.cabinet:
            return
        for role, seat in list(self.cabinet.items()):
            if seat.get("vacant"):
                seat["vacant_days"] += 1
                if seat["vacant_days"] >= 5:
                    spec = next(s for s in gd.ADVISOR_ROLES if s["role"] == role)
                    self.cabinet[role] = {"name": random.choice(spec["names"]), "approval": 50,
                                          "vacant": False, "vacant_days": 0}
                continue
            if seat["approval"] > 50:
                seat["approval"] -= 1
            elif seat["approval"] < 50:
                seat["approval"] += 1
            if seat["approval"] <= 15 and random.random() < 0.25:
                name = seat["name"]
                self.cabinet[role] = {"name": None, "approval": 0, "vacant": True, "vacant_days": 0}
                self.public_opinion = max(0, self.public_opinion - 8)
                self.add_transgression(5, 0)
                self.on_notify(f"{role} Resigns", f"{name} resigned. Opinion -8.", "election")
            elif seat["approval"] >= 85:
                if role == "Treasury Secretary":
                    self.money += 500_000
                    self.market.money = self.money
                elif role == "Chief of Staff":
                    self.happiness = min(100, self.happiness + 1)
                elif role == "Attorney General":
                    self.transgressions = max(0, self.transgressions - 1)
                elif role == "Press Secretary":
                    self.public_opinion = min(100, self.public_opinion + 1)

    # =====================================================================
    # WORK
    # =====================================================================

    def work(self):
        if self._last_work_year == self.days:
            return None
        self._last_work_year = self.days
        lo, hi = gd.WORK_RANGES[min(self.work_level, 3)]
        gain = random.randint(lo, hi)
        self.money += gain
        self.market.money = self.money
        self.on_log(f"Worked and earned ${gain:,}")
        return gain

    # =====================================================================
    # CASINO
    # =====================================================================

    def roulette_fire(self, bet):
        if bet <= 0 or bet > self.money:
            return None
        bullet = random.randint(0, 5)
        if bullet == 0:
            self.running = False
            self.death_cause = "roulette"
            self.on_log("You lost at Russian Roulette. RIP.")
            self.on_game_over()
            return {"survived": False}
        self.money += bet
        self.market.money = self.money
        return {"survived": True, "winnings": bet}

    def spin_slots(self, bet):
        if bet <= 0 or bet > self.money:
            return None
        result = tuple(random.choice(gd.SLOT_SYMBOLS) for _ in range(3))
        if result in gd.SLOT_PAYOUTS:
            label, mult = gd.SLOT_PAYOUTS[result]
            winnings = bet * mult
            self.money += winnings
            outcome = {"result": result, "label": label, "winnings": winnings}
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            winnings = bet * 2
            self.money += winnings
            outcome = {"result": result, "label": "Two of a kind!", "winnings": winnings}
        else:
            self.money -= bet
            outcome = {"result": result, "label": "No match", "winnings": -bet}
        self.market.money = self.money
        return outcome

    def poker_deal(self, bet):
        if bet <= 0 or bet > self.money:
            return None
        self.money -= bet
        self.market.money = self.money
        self.poker_bet = bet
        deck = [(r, s) for s in gd.SUITS for r in gd.RANKS]
        random.shuffle(deck)
        self.poker_hand = deck[:5]
        self._poker_deck_rest = deck[5:]
        self.poker_hold = [False] * 5
        return list(self.poker_hand)

    def poker_toggle_hold(self, idx):
        self.poker_hold[idx] = not self.poker_hold[idx]

    def poker_draw(self):
        for i in range(5):
            if not self.poker_hold[i]:
                self.poker_hand[i] = self._poker_deck_rest.pop()
        return self._evaluate_poker()

    def _evaluate_poker(self):
        hand = self.poker_hand
        ranks = sorted([gd.RANK_VAL[r] for r, s in hand], reverse=True)
        suits = [s for r, s in hand]
        flush = len(set(suits)) == 1
        straight = ranks == list(range(ranks[0], ranks[0] - 5, -1)) or ranks == [12, 3, 2, 1, 0]
        counts_map = {}
        for rv in ranks:
            counts_map[rv] = counts_map.get(rv, 0) + 1
        counts = sorted(counts_map.values(), reverse=True)
        name, mult = "High Card — no win", 0
        for hname, hmult, check in gd.POKER_HANDS:
            if check(ranks, counts, flush, straight):
                name, mult = hname, hmult
                break
        if mult == 0 and counts[0] == 2 and max(k for k, v in counts_map.items() if v == 2) >= 9:
            name, mult = "Jacks or Better!", 1
        bet = self.poker_bet
        if mult > 0:
            payout = bet * (mult + 1)
            self.money += payout
            profit = bet * mult
            outcome = {"name": name, "profit": profit}
        else:
            outcome = {"name": name, "profit": -bet}
        self.market.money = self.money
        return outcome

    def bj_deal(self, bet):
        if bet <= 0 or bet > self.money:
            return None
        self.money -= bet
        self.market.money = self.money
        self.bj_bet = bet
        cards = [(r, s) for s in gd.SUITS for r in gd.RANKS] * 2
        random.shuffle(cards)
        self.bj_deck = cards
        self.bj_player = [self.bj_deck.pop(), self.bj_deck.pop()]
        self.bj_dealer = [self.bj_deck.pop(), self.bj_deck.pop()]
        return {"player": list(self.bj_player), "dealer_up": self.bj_dealer[0]}

    def _bj_value(self, hand):
        total, aces = 0, 0
        for rank, suit in hand:
            if rank in ('J', 'Q', 'K'):
                total += 10
            elif rank == 'A':
                aces += 1
                total += 11
            else:
                total += int(rank)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def bj_hit(self):
        self.bj_player.append(self.bj_deck.pop())
        val = self._bj_value(self.bj_player)
        return {"player": list(self.bj_player), "value": val, "bust": val > 21}

    def bj_stand(self):
        while self._bj_value(self.bj_dealer) < 17:
            self.bj_dealer.append(self.bj_deck.pop())
        p_val, d_val = self._bj_value(self.bj_player), self._bj_value(self.bj_dealer)
        bet = self.bj_bet
        if d_val > 21 or p_val > d_val:
            payout = bet * 2
            self.money += payout
            outcome = "win"
        elif p_val == d_val:
            self.money += bet
            outcome = "push"
        else:
            outcome = "lose"
        self.market.money = self.money
        return {"outcome": outcome, "player": list(self.bj_player), "dealer": list(self.bj_dealer),
                "p_val": p_val, "d_val": d_val}

    # =====================================================================
    # RANDOM EVENTS  (curated subset of the desktop's 37)
    # =====================================================================

    def _random_events(self):
        r = random.randint(1, 20)
        if self.lobby_immunity and r != 1:
            self.lobby_immunity = False
            self.on_log("Senate Immunity blocked a bad event!")
            return

        if r == 1:
            self.money += 1_000_000
            self.on_notify("Inheritance!", "Grandma died and left you $1,000,000.", "event")
        elif r == 2:
            loss = int(self.money * random.uniform(0.3, 0.7))
            self.money -= loss
            self.apply_market_effect(["Finance"], 0.91, 2, "Tax fraud")
            self.add_transgression(10, 8)
            self.on_notify("Tax Fraud!", f"The IRS found out. Lost ${loss:,}.", "scandal")
        elif r == 3 and any(s["shares"] > 0 for s in self.market.stocks.values()):
            for name in self.market.stocks:
                self.market.stocks[name]["shares"] = 0
            self.apply_market_effect(["Finance"], 0.92, 3, "Advisor betrayal")
            self.on_notify("Betrayal!", "Your advisor liquidated all your shares!", "financial")
        elif r == 4:
            loss = 5_000_000
            self.money -= loss
            self.apply_market_effect(["Defense"], 0.91, 3, "Investigation")
            self.on_notify("Federal Investigation!", f"Assets frozen. Lost ${loss:,}.", "legal")
        elif r == 5:
            self.money += 2_000_000
            self.on_notify("Diamond in the Rough!", "A pencil became a diamond. +$2,000,000", "event")
        elif r == 6 and not self.pandemic:
            self.pandemic = True
            if "bunker" in self.owned_assets:
                self.on_notify("Pandemic? What Pandemic?", "Safe in your bunker. No damage.", "health")
            else:
                loss = int(self.money * 0.40)
                self.money *= 0.60
                self.apply_market_effect(["Healthcare"], 0.88, 3, "Pandemic")
                self.on_notify("Pandemic Investment!", f"Bad investment. Lost ${loss:,}.", "health")
        elif r == 7:
            loss = 10_000_000
            self.money -= loss
            self.apply_market_effect(["Finance", "Defense"], 0.93, 2, "Lobbyist caught")
            self.on_notify("Lobbyist Caught!", f"Filmed handing cash to a senator. -${loss:,}", "scandal")
        elif r == 8:
            loss = 15_000_000
            self.money -= loss
            self.apply_market_effect(["Energy"], 0.92, 3, "Climate lawsuit")
            self.add_transgression(10, 12)
            self.on_notify("Climate Lawsuit!", f"Sued by Pacific nations. -${loss:,}", "environment")
        elif r == 9 and not self.revolution_used:
            self.revolution_used = True
            self.apply_market_effect(["ALL"], 0.85, 5, "Revolution")
            self.public_opinion = max(0, self.public_opinion - 20)
            self.on_notify("Revolution!", "The people are furious. Markets crash 15%.", "revolution")
        elif r == 10:
            loss = 25_000_000
            self.money -= loss
            self.apply_market_effect(["Finance"], 1.04, 2, "M&A surge")
            self.on_notify("Hostile Takeover Attempt!", f"Survived, spent ${loss:,} in legal fees.", "financial")
        elif r == 11 and "supercar" in self.owned_assets:
            fine = 2_500_000
            self.money -= fine
            self.add_transgression(5, 4)
            self.on_notify("Street Racing Bust!", f"Caught racing. -${fine:,}", "legal")
        elif r == 12 and "penthouse" in self.owned_assets:
            dmg = random.randint(3_000_000, 9_000_000)
            self.money -= dmg
            self.add_transgression(7, 5)
            self.on_notify("Penthouse Party Gone Wrong!", f"Damages: ${dmg:,}", "scandal")
        elif r == 13 and self.factories:
            loss = 1_000_000
            self.money -= loss
            self.add_transgression(10, 12)
            self.on_notify("Factory Shutdown!", "Labor violations exposed. -$1,000,000", "scandal")
        elif r == 14:
            self.money -= 7_000_000
            self.apply_market_effect(["Finance"], 0.96, 1, "Legal uncertainty")
            self.on_notify("Bribed the Wrong Judge!", "Wrong courtroom. -$7,000,000", "legal")
        elif r == 15:
            gain = random.randint(500_000, 2_000_000)
            self.money += gain
            self.on_notify("Lucky Break", f"An unexpected windfall. +${gain:,}", "event")

        self.market.money = self.money

    # =====================================================================
    # DEATH / WIN CONDITIONS
    # =====================================================================

    def _check_win_condition(self):
        if not self.running or self.won_game or self.days < 100:
            return
        self.won_game = True
        self.running = False
        self.death_cause = "world_domination_win"
        bonus = 50_000_000
        self.money += bonus
        self.market.money = self.money
        self.on_log(f"CENTURY MARK REACHED. Victory bonus +${bonus:,}.")
        self.on_notify("World Domination!", "100 years of unchecked power.", "event")
        self.on_game_over()

    def _check_critical_stats(self):
        if self.happiness <= 0:
            if self.warned_happiness:
                self.running = False
                self.death_cause = "happiness"
                self.on_game_over()
                return
            self.warned_happiness = True
            self.on_warning("No Will to Live", "Happiness hit zero.", "Recover within 1 year or it's over.")
        else:
            self.warned_happiness = False

        if self.public_opinion <= 0:
            if self.warned_opinion:
                self.running = False
                self.death_cause = "opinion"
                self.on_game_over()
                return
            self.warned_opinion = True
            self.on_warning("Public Opinion Collapse", "Nobody wants anything to do with you.", "Recover within 1 year.")
        else:
            self.warned_opinion = False

        if self.transgressions >= 100:
            if self.warned_transgress:
                self.running = False
                self.death_cause = "transgressions"
                self.on_game_over()
                return
            self.warned_transgress = True
            self.on_warning("Crimes Uncoverable", "Every agency is building a case.", "Reduce within 1 year.")
        else:
            self.warned_transgress = False

    # =====================================================================
    # CAREER / SAVE / LEADERBOARD
    # =====================================================================

    def _load_legacy(self):
        try:
            with open(LEGACY_FILE) as f:
                return json.load(f).get("bonus", 0)
        except Exception:
            return 0

    def save_legacy(self):
        if self.days < 10:
            return
        bonus = min(50_000_000, int(self.days * 300_000))
        try:
            with open(LEGACY_FILE, "w") as f:
                json.dump({"bonus": bonus}, f)
        except Exception:
            pass

    def save_local_score(self):
        entries = []
        try:
            with open(LEADERBOARD_FILE) as f:
                entries = json.load(f)
        except Exception:
            pass
        entries.append({"name": self.username, "days": self.days})
        entries.sort(key=lambda x: x["days"], reverse=True)
        entries = entries[:50]
        try:
            with open(LEADERBOARD_FILE, "w") as f:
                json.dump(entries, f)
        except Exception:
            pass
        return entries

    def load_local_leaderboard(self):
        try:
            with open(LEADERBOARD_FILE) as f:
                return json.load(f)
        except Exception:
            return []

    def submit_global_score(self):
        def _post():
            try:
                payload = json.dumps({"name": self.username, "days": self.days,
                                       "country": self.country}).encode()
                req = urllib.request.Request(GLOBAL_LB_URL, data=payload,
                                              headers={"Content-Type": "application/json"}, method="POST")
                urllib.request.urlopen(req, timeout=4)
            except Exception:
                pass
        import threading
        threading.Thread(target=_post, daemon=True).start()

    def fetch_global_leaderboard(self, callback):
        def _fetch():
            try:
                with urllib.request.urlopen(GLOBAL_LB_URL, timeout=4) as resp:
                    data = json.loads(resp.read())
                callback(data)
            except Exception:
                callback(None)
        import threading
        threading.Thread(target=_fetch, daemon=True).start()

    def _load_career(self):
        try:
            with open(CAREER_FILE) as f:
                data = json.load(f)
        except Exception:
            data = {}
        data.setdefault("games_played", 0)
        data.setdefault("best_days", 0)
        data.setdefault("badges", [])
        return data

    def record_career_run(self):
        data = self._load_career()
        data["games_played"] += 1
        data["best_days"] = max(data["best_days"], self.days)
        earned = set(data["badges"])
        newly = []
        peak = max(self.net_worth_history) if self.net_worth_history else 0
        checks = {
            "first_blood": True,
            "survivor_50": self.days >= 50,
            "centurion": self.won_game,
            "untouchable": self.days >= 20 and self.transgressions <= 10,
            "kingpin": self.transgressions >= 90,
            "market_maker": peak >= 500_000_000,
            "warlord": len(self.bombed_countries) >= 5,
            "world_leader": self.ever_president,
        }
        for badge in gd.BADGES:
            if checks.get(badge["id"]) and badge["id"] not in earned:
                earned.add(badge["id"])
                newly.append(badge)
        data["badges"] = sorted(earned)
        try:
            with open(CAREER_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
        return newly

    def career_summary(self):
        return self._load_career()

    def end_run(self):
        """Call once when running flips to False — persists everything."""
        self.save_legacy()
        rank_entries = self.save_local_score()
        self.submit_global_score()
        badges = self.record_career_run()
        rank = next((i + 1 for i, e in enumerate(rank_entries)
                     if e["name"] == self.username and e["days"] == self.days), None)
        return rank, len(rank_entries), badges

    # =====================================================================
    # SAVE / LOAD (single mobile save slot)
    # =====================================================================

    _SAVE_FIELDS = [
        "username", "country", "game_mode", "money", "days", "happiness", "public_opinion",
        "transgressions", "wanted_level", "loans", "owned_assets", "oil_operations",
        "owned_islands", "alliance", "alliance_days", "sanctions", "militia", "factories",
        "net_worth_history",
    ]

    def save_game(self):
        data = {"saved_at": time.strftime("%Y-%m-%d %H:%M")}
        for field in self._SAVE_FIELDS:
            val = getattr(self, field, None)
            if isinstance(val, set):
                val = list(val)
            data[field] = val
        data["stock_portfolio"] = {n: s["shares"] for n, s in self.market.stocks.items() if s.get("shares", 0) > 0}
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return False
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
        except Exception:
            return False
        for field in self._SAVE_FIELDS:
            if field not in data:
                continue
            val = data[field]
            if field in ("owned_assets", "owned_islands"):
                val = set(val) if isinstance(val, list) else set()
            setattr(self, field, val)
        for name, shares in data.get("stock_portfolio", {}).items():
            if name in self.market.stocks:
                self.market.stocks[name]["shares"] = shares
        self.market.money = self.money
        self.running = True
        self._init_rivals()
        return True

    def has_save(self):
        return os.path.exists(SAVE_FILE)
