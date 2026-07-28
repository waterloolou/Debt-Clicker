"""
mobile/game_data.py — every pure game-balance data table, with zero
Tkinter dependency, so it can be imported on a real phone.

Values here are transcribed from the desktop mixins (world_map_mixin,
rivals_mixin, black_market_mixin, debt_mixin, lobby_mixin, cabinet_mixin,
career_mixin, factory_mixin, assets_mixin, militia_mixin, island_map_mixin,
pleasures_mixin) so the two versions play out the same way. Kept as a
separate module (rather than importing those mixins) because every one of
them does `import tkinter as tk` at module load time, which does not exist
on Android/iOS.
"""

# ---------------------------------------------------------------------
# World Map — resource-rich countries
# ---------------------------------------------------------------------

RESOURCE_DATA = {
    "Oil": {
        "market": ["Energy"],
        "countries": {
            "Kuwait":                   {"action_cost":   5_000_000, "income":   500_000, "days": 15},
            "United Arab Emirates":     {"action_cost":   8_000_000, "income":   600_000, "days": 15},
            "Qatar":                    {"action_cost":   8_000_000, "income":   700_000, "days": 20},
            "Angola":                   {"action_cost":   8_000_000, "income":   600_000, "days": 15},
            "Libya":                    {"action_cost":  10_000_000, "income":   800_000, "days": 15},
            "Algeria":                  {"action_cost":  12_000_000, "income":   800_000, "days": 15},
            "Nigeria":                  {"action_cost":  15_000_000, "income": 1_000_000, "days": 20},
            "Norway":                   {"action_cost":  28_000_000, "income": 1_500_000, "days": 15},
            "Kazakhstan":               {"action_cost":  18_000_000, "income": 1_200_000, "days": 20},
            "Mexico":                   {"action_cost":  22_000_000, "income": 1_500_000, "days": 20},
            "Brazil":                   {"action_cost":  20_000_000, "income": 1_300_000, "days": 20},
            "Venezuela":                {"action_cost":  25_000_000, "income": 2_000_000, "days": 20},
            "Iraq":                     {"action_cost":  30_000_000, "income": 2_000_000, "days": 25},
            "Iran":                     {"action_cost":  35_000_000, "income": 2_500_000, "days": 25},
            "Canada":                   {"action_cost":  40_000_000, "income": 2_500_000, "days": 25},
            "Saudi Arabia":             {"action_cost":  60_000_000, "income": 4_000_000, "days": 30},
            "Russia":                   {"action_cost": 100_000_000, "income": 6_000_000, "days": 20},
            "United States of America": {"action_cost": 200_000_000, "income":10_000_000, "days": 30},
        },
    },
    "Diamonds": {
        "market": ["Finance", "Entertainment"],
        "countries": {
            "Botswana":        {"action_cost":  15_000_000, "income":   900_000, "days": 20},
            "Russia":          {"action_cost":  80_000_000, "income": 3_000_000, "days": 25},
            "Canada":          {"action_cost":  30_000_000, "income": 1_200_000, "days": 20},
            "South Africa":    {"action_cost":  20_000_000, "income": 1_000_000, "days": 20},
            "Angola":          {"action_cost":  12_000_000, "income":   700_000, "days": 15},
            "Namibia":         {"action_cost":  10_000_000, "income":   600_000, "days": 15},
            "Dem. Rep. Congo": {"action_cost":  18_000_000, "income": 1_100_000, "days": 20},
            "Australia":       {"action_cost":  35_000_000, "income": 1_500_000, "days": 20},
            "Zimbabwe":        {"action_cost":  10_000_000, "income":   700_000, "days": 15},
        },
    },
    "Minerals": {
        "market": ["Technology", "Energy"],
        "countries": {
            "China":           {"action_cost": 150_000_000, "income": 8_000_000, "days": 30},
            "Chile":           {"action_cost":  25_000_000, "income": 1_500_000, "days": 20},
            "Peru":            {"action_cost":  20_000_000, "income": 1_200_000, "days": 20},
            "Dem. Rep. Congo": {"action_cost":  18_000_000, "income": 1_300_000, "days": 20},
            "Australia":       {"action_cost":  35_000_000, "income": 2_000_000, "days": 25},
            "Brazil":          {"action_cost":  25_000_000, "income": 1_500_000, "days": 20},
            "Russia":          {"action_cost":  90_000_000, "income": 5_000_000, "days": 25},
            "Kazakhstan":      {"action_cost":  20_000_000, "income": 1_200_000, "days": 20},
            "South Africa":    {"action_cost":  22_000_000, "income": 1_400_000, "days": 20},
            "Indonesia":       {"action_cost":  20_000_000, "income": 1_300_000, "days": 20},
        },
    },
    "Agriculture": {
        "market": ["Retail"],
        "countries": {
            "United States of America": {"action_cost": 180_000_000, "income": 7_000_000, "days": 25},
            "Brazil":                   {"action_cost":  22_000_000, "income": 1_500_000, "days": 20},
            "Argentina":                {"action_cost":  15_000_000, "income": 1_000_000, "days": 15},
            "Russia":                   {"action_cost":  85_000_000, "income": 4_000_000, "days": 20},
            "Canada":                   {"action_cost":  38_000_000, "income": 2_000_000, "days": 20},
            "Australia":                {"action_cost":  30_000_000, "income": 1_800_000, "days": 20},
            "Ukraine":                  {"action_cost":  12_000_000, "income":   900_000, "days": 15},
            "India":                    {"action_cost":  30_000_000, "income": 2_000_000, "days": 20},
            "China":                    {"action_cost": 130_000_000, "income": 6_000_000, "days": 25},
            "France":                   {"action_cost":  45_000_000, "income": 2_500_000, "days": 20},
        },
    },
    "Technology": {
        "market": ["Technology", "AI"],
        "countries": {
            "United States of America": {"action_cost": 200_000_000, "income":12_000_000, "days": 30},
            "China":                    {"action_cost": 160_000_000, "income": 9_000_000, "days": 30},
            "Taiwan":                   {"action_cost":  50_000_000, "income": 4_000_000, "days": 25},
            "South Korea":              {"action_cost":  55_000_000, "income": 4_000_000, "days": 25},
            "Japan":                    {"action_cost":  70_000_000, "income": 5_000_000, "days": 25},
            "Germany":                  {"action_cost":  60_000_000, "income": 4_500_000, "days": 25},
            "Netherlands":              {"action_cost":  45_000_000, "income": 3_000_000, "days": 20},
            "India":                    {"action_cost":  35_000_000, "income": 2_500_000, "days": 20},
        },
    },
    "Finance": {
        "market": ["Finance"],
        "countries": {
            "United States of America": {"action_cost": 200_000_000, "income":15_000_000, "days": 30},
            "United Kingdom":           {"action_cost":  80_000_000, "income": 6_000_000, "days": 25},
            "Switzerland":              {"action_cost":  60_000_000, "income": 5_000_000, "days": 25},
            "Luxembourg":               {"action_cost":  30_000_000, "income": 2_500_000, "days": 20},
            "Japan":                    {"action_cost":  65_000_000, "income": 5_000_000, "days": 25},
            "France":                   {"action_cost":  50_000_000, "income": 3_500_000, "days": 20},
            "Germany":                  {"action_cost":  55_000_000, "income": 4_000_000, "days": 20},
            "Singapore":                {"action_cost":  50_000_000, "income": 4_000_000, "days": 25},
            "Russia":                   {"action_cost":  90_000_000, "income": 5_000_000, "days": 20},
        },
    },
}

ACTIONS = {
    "Bomb":        {"cost_mult": 1.0,  "income_mult": 1.0, "days_mult": 1.0,
                     "transgression": 20, "opinion": 20, "happiness": 5, "tag": "[BOMB]"},
    "Stage a Coup": {"cost_mult": 0.35, "income_mult": 0.6, "days_mult": 0.7,
                     "transgression": 10, "opinion": 8, "happiness": 3, "tag": "[COUP]"},
}

RESOURCE_CRASH = {
    "Oil":         (["Energy"],                  0.88, 4),
    "Diamonds":    (["Finance", "Entertainment"], 0.90, 3),
    "Minerals":    (["Automotive", "Technology"], 0.87, 4),
    "Agriculture": (["Retail"],                  0.89, 3),
    "Technology":  (["Technology", "AI"],         0.86, 5),
    "Finance":     (["Finance"],                  0.85, 5),
}

ALLIANCE_DATA = {
    "USA":    {"countries": {"United States of America", "Canada", "United Kingdom",
                             "Australia", "Japan", "South Korea", "Germany", "France"},
               "cost": 50_000_000, "days": 30, "discount": 0.70,
               "perk": "+$750K/day, 30% op discount, rivals partially blocked"},
    "Russia": {"countries": {"Russia", "Kazakhstan", "Belarus", "Ukraine"},
               "cost": 50_000_000, "days": 30, "discount": 0.70,
               "perk": "+20 militia/day, 30% op discount, rivals partially blocked"},
    "China":  {"countries": {"China", "Taiwan", "South Korea", "Vietnam", "Indonesia", "India"},
               "cost": 50_000_000, "days": 30, "discount": 0.70,
               "perk": "+15% resource income, 30% op discount, rivals partially blocked"},
}

# ---------------------------------------------------------------------
# Rivals
# ---------------------------------------------------------------------

RIVAL_DEFS = [
    {"name": "Viktor Drago",      "money": 95_000_000},
    {"name": "Chen Wei",          "money": 120_000_000},
    {"name": "Elizabeth Harlow",  "money": 80_000_000},
    {"name": "Kenji Tanaka",      "money": 105_000_000},
]

PRESIDENT_RIVAL_DEFS = [
    {"name": "Vladimir Putin",        "money": 200_000_000_000},
    {"name": "Xi Jinping",            "money": 150_000_000_000},
    {"name": "General Marcus Okafor", "money":  90_000_000_000},
]

# ---------------------------------------------------------------------
# Black Market
# ---------------------------------------------------------------------

BLACK_MARKET_ITEMS = [
    {"id": "stolen_data",      "name": "Stolen Corporate Data",
     "desc": "Sell leaked CEO emails to rival corporations.",
     "gain": 8_000_000, "trans": 12, "opin": -8},
    {"id": "arms_smuggling",   "name": "Arms Smuggling",
     "desc": "Sell surplus military hardware to the highest bidder.",
     "gain": 10_000_000, "trans": 18, "opin": -15},
    {"id": "laundered_cash",  "name": "Laundered Cash",
     "desc": "Process dirty money through shell companies.",
     "gain": 20_000_000, "trans": 20, "opin": -18},
    {"id": "forged_docs",      "name": "Forged Documents",
     "desc": "Buy a clean identity. Costs money but wipes records.",
     "gain": -3_000_000, "trans": -15, "opin": 0},
    {"id": "organ_trafficking", "name": "Organ Trafficking",
     "desc": "The darkest trade. Staggeringly profitable.",
     "gain": 25_000_000, "trans": 30, "opin": -25},
]

# ---------------------------------------------------------------------
# Debt / Loans
# ---------------------------------------------------------------------

LOAN_OPTIONS = [
    {"label": "Emergency Cash",   "amount":    5_000_000, "rate": 0.030, "days":  4},
    {"label": "Personal Loan",    "amount":   25_000_000, "rate": 0.025, "days":  6},
    {"label": "Corporate Bond",   "amount":  100_000_000, "rate": 0.020, "days":  8},
    {"label": "Hedge Fund Line",  "amount":  300_000_000, "rate": 0.016, "days": 10},
    {"label": "Sovereign Debt",   "amount":  750_000_000, "rate": 0.012, "days": 14},
    {"label": "Bailout Package",  "amount": 2_000_000_000, "rate": 0.010, "days": 20},
]

BANKS = [
    {"name": "First National Bank",  "min_score": 700, "rate_bonus": 0.000,
     "blacklist_on_default": True,  "default_war": False},
    {"name": "Merchant Credit Corp", "min_score": 550, "rate_bonus": 0.004,
     "blacklist_on_default": True,  "default_war": False},
    {"name": "Offshore Capital Ltd", "min_score": 400, "rate_bonus": 0.010,
     "blacklist_on_default": False, "default_war": False},
    {"name": "Shadow Finance",       "min_score": 250, "rate_bonus": 0.018,
     "blacklist_on_default": False, "default_war": False},
    {"name": "Cartel Bank",          "min_score": 0,   "rate_bonus": 0.030,
     "blacklist_on_default": False, "default_war": True},
]

# ---------------------------------------------------------------------
# Lobby
# ---------------------------------------------------------------------

LOBBY_TIERS = [
    {"id": "bribe_official",     "name": "Bribe Local Official",
     "desc": "Reduces transgressions by 8.", "cost": 4_000_000, "once": False,
     "effect": {"transgression": -8}},
    {"id": "control_narrative",  "name": "Leak Positive Stories",
     "desc": "+20 Public Opinion.", "cost": 12_000_000, "once": False,
     "effect": {"opinion": 20}},
    {"id": "buy_senator_trans",  "name": "Buy a Senator [Records]",
     "desc": "-25 transgressions only.", "cost": 40_000_000, "once": False,
     "effect": {"transgression": -25}},
    {"id": "buy_senator_opin",   "name": "Buy a Senator [Image]",
     "desc": "+30 Public Opinion only.", "cost": 40_000_000, "once": False,
     "effect": {"opinion": 30}},
    {"id": "senate_immunity",    "name": "Senate Immunity Deal",
     "desc": "Next bad random event is completely blocked. One use.",
     "cost": 60_000_000, "once": True, "effect": {"immunity": 1}},
    {"id": "full_expunge",       "name": "Full Records Expunge",
     "desc": "Wipe your criminal record entirely.", "cost": 150_000_000, "once": False,
     "effect": {"transgression": -999}},
    {"id": "presidential_rehab", "name": "Presidential Rehabilitation",
     "desc": "Public Opinion set to 80.", "cost": 150_000_000, "once": False,
     "effect": {"opinion": 999}},
]

# ---------------------------------------------------------------------
# Cabinet (President mode)
# ---------------------------------------------------------------------

ADVISOR_ROLES = [
    {"role": "Chief of Staff",     "names": ["Marcus Webb", "Diane Foster", "Trevor Kaine"]},
    {"role": "Press Secretary",    "names": ["Nina Alvarez", "Colin Reyes", "Priya Sharma"]},
    {"role": "Attorney General",   "names": ["Harold Voss", "Miriam Cole", "Desmond Okoye"]},
    {"role": "Treasury Secretary", "names": ["Elaine Brooks", "Raj Patel", "Wendell Ashford"]},
]

CABINET_REACTIONS = {
    "daily_expense_multiplier":        {"Treasury Secretary": 8, "Chief of Staff": 3},
    "income_multiplier":               {"Treasury Secretary": 5},
    "transgression_decay_bonus":       {"Attorney General": 10, "Press Secretary": -5},
    "public_opinion_daily":            {"Press Secretary": 8},
    "loan_rate_multiplier":            {"Treasury Secretary": 6},
    "happiness_daily":                 {"Chief of Staff": 5},
    "wanted_fine_reduction":           {"Attorney General": -8, "Press Secretary": -4},
    "declare_state_of_emergency":      {"Chief of Staff": -15, "Attorney General": -12},
    "censor_media":                    {"Press Secretary": -10, "Attorney General": -6},
    "launch_propaganda_campaign":      {"Press Secretary": 6},
    "appoint_loyalist_official":       {"Chief of Staff": 5, "Attorney General": -8},
    "impose_sanctions":                {"Treasury Secretary": -5},
    "pass_infrastructure_legislation": {"Treasury Secretary": 8, "Chief of Staff": 4},
    "pass_corporate_tax_cut":          {"Treasury Secretary": 10, "Press Secretary": -5},
}

# ---------------------------------------------------------------------
# Career badges
# ---------------------------------------------------------------------

BADGES = [
    {"id": "first_blood", "name": "First Blood",  "desc": "Complete your first run."},
    {"id": "survivor_50", "name": "Half-Century",  "desc": "Survive 50 years in a single run."},
    {"id": "centurion",   "name": "Centurion",     "desc": "Reach the 100-year World Domination win."},
    {"id": "untouchable", "name": "Untouchable",   "desc": "Survive 20+ years with 10 or fewer transgressions."},
    {"id": "kingpin",     "name": "Kingpin",       "desc": "End a run with 90+ transgressions."},
    {"id": "market_maker","name": "Market Maker",  "desc": "Reach a net worth of $500,000,000+."},
    {"id": "warlord",     "name": "Warlord",       "desc": "Control 5+ resource-rich countries at once."},
    {"id": "world_leader","name": "World Leader",  "desc": "Win a presidential election."},
]

# ---------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------

FACTORY_TYPES = [
    {"id": "steel_mill",   "name": "Steel Mill",               "price":   500_000_000,
     "income":  6_000_000, "base_wage_cost": 1_200_000, "workers": 500},
    {"id": "oil_refinery", "name": "Oil Refinery",              "price":   900_000_000,
     "income": 10_000_000, "base_wage_cost":   900_000, "workers": 300},
    {"id": "tech_factory", "name": "Tech Manufacturing Plant",  "price": 1_400_000_000,
     "income": 15_000_000, "base_wage_cost":   800_000, "workers": 200},
    {"id": "pharma_plant", "name": "Pharmaceutical Plant",      "price": 1_800_000_000,
     "income": 20_000_000, "base_wage_cost":   700_000, "workers": 150},
    {"id": "arms_factory", "name": "Arms Factory",              "price": 3_000_000_000,
     "income": 35_000_000, "base_wage_cost":   500_000, "workers": 100, "trans_per_day": 1},
]

WORKER_TIERS = [
    {"id": "underpaid", "name": "Underpaid Labor",  "wage_mult": 0.20, "income_mult": 2.00,
     "opinion_per_day": -5,  "strike_chance": 0.45},
    {"id": "minimum",   "name": "Minimum Wage",      "wage_mult": 0.45, "income_mult": 1.40,
     "opinion_per_day": -2,  "strike_chance": 0.20},
    {"id": "standard",  "name": "Standard Workers",  "wage_mult": 1.00, "income_mult": 1.00,
     "opinion_per_day": 0,   "strike_chance": 0.05},
    {"id": "skilled",   "name": "Skilled Workforce", "wage_mult": 1.50, "income_mult": 0.90,
     "opinion_per_day": 0.5, "strike_chance": 0.01},
    {"id": "unionized", "name": "Unionized Labor",   "wage_mult": 2.80, "income_mult": 0.50,
     "opinion_per_day": 2.0, "strike_chance": 0.00},
]

FACTORY_BY_ID = {f["id"]: f for f in FACTORY_TYPES}
WORKER_BY_ID = {w["id"]: w for w in WORKER_TIERS}

# ---------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------

ASSETS = [
    {"id": "supercar",  "name": "Supercar Collection",  "cost":       500_000, "upkeep":     5_000, "income": 0},
    {"id": "penthouse", "name": "Luxury Penthouse",      "cost":     2_000_000, "upkeep":    20_000, "income": 0},
    {"id": "jet",       "name": "Private Jet",           "cost":     8_000_000, "upkeep":    80_000, "income": 0},
    {"id": "offshore",  "name": "Offshore Bank Account", "cost":    10_000_000, "upkeep":   100_000, "income": 0, "special": "tax_shield"},
    {"id": "yacht",     "name": "Mega Yacht",            "cost":    15_000_000, "upkeep":   150_000, "income": 0},
    {"id": "senator",   "name": "Bribed Senator",        "cost":    20_000_000, "upkeep":   500_000, "income": 0, "special": "legal_shield"},
    {"id": "media",     "name": "Media Empire",          "cost":    40_000_000, "upkeep":   800_000, "income": 1_500_000},
    {"id": "oil_rig",   "name": "Offshore Oil Rig",      "cost":    50_000_000, "upkeep": 1_000_000, "income": 2_000_000},
    {"id": "army",      "name": "Private Army",          "cost":    80_000_000, "upkeep": 2_000_000, "income": 0},
    {"id": "bunker",    "name": "Doomsday Bunker",       "cost":   100_000_000, "upkeep": 1_000_000, "income": 0, "special": "pandemic_immune"},
    {"id": "space",     "name": "Vanity Space Program",  "cost":   200_000_000, "upkeep": 5_000_000, "income": 3_000_000},
    {"id": "art",       "name": "Fine Art Collection",   "cost":    25_000_000, "upkeep":   300_000, "income":   500_000},
    {"id": "crypto",    "name": "Crypto Exchange",       "cost":    30_000_000, "upkeep":   400_000, "income": 1_000_000},
]

ASSET_BY_ID = {a["id"]: a for a in ASSETS}

# ---------------------------------------------------------------------
# Militia / War Room
# ---------------------------------------------------------------------

MILITIA_TIERS = [
    {"name": "Mercenary Squad",     "units":  15, "cost":  30_000_000},
    {"name": "Private Army",        "units":  40, "cost":  80_000_000},
    {"name": "Military Contractor", "units":  80, "cost": 160_000_000},
    {"name": "Elite Strike Force",  "units": 120, "cost": 280_000_000},
]

WAR_ACTIONS = [
    {"id": "spy",         "name": "Spy Report",     "units":   5, "desc": "Reveal the target's full stats."},
    {"id": "raid",        "name": "Raid Treasury",  "units":  15, "desc": "Steal 8-15% of their cash."},
    {"id": "assassinate", "name": "Hit Advisor",    "units":  12, "desc": "Force 2 bad events/day for 3 days."},
    {"id": "sabotage",    "name": "Sabotage Ops",   "units":  20, "desc": "Wipe out one resource operation."},
    {"id": "blockade",    "name": "Trade Blockade", "units":  25, "desc": "Cut resource income for 4 days."},
    {"id": "nuke",        "name": "Nuclear Strike", "units": 100, "desc": "Obliterate 40% of their fortune."},
]

# ---------------------------------------------------------------------
# Islands
# ---------------------------------------------------------------------

ISLANDS = [
    {"name": "Sandy Cay",           "loc": "Bahamas",              "price":        500_000, "upkeep":     5_000, "income":     5_000},
    {"name": "Bird Island",         "loc": "Belize",               "price":        800_000, "upkeep":     8_000, "income":     8_000},
    {"name": "Little Whale Cay",    "loc": "Bahamas",              "price":      2_000_000, "upkeep":    15_000, "income":    15_000},
    {"name": "Bell Island",         "loc": "Canada",               "price":      3_000_000, "upkeep":    20_000, "income":    20_000},
    {"name": "Diapori",             "loc": "Greece",               "price":      4_000_000, "upkeep":    30_000, "income":    30_000},
    {"name": "Rangyai",             "loc": "Thailand",             "price":      5_000_000, "upkeep":    40_000, "income":    40_000},
    {"name": "Thanda Island",       "loc": "Tanzania",             "price":      8_000_000, "upkeep":    60_000, "income":    60_000},
    {"name": "Cayo Espanto",        "loc": "Belize",               "price":     15_000_000, "upkeep":   100_000, "income":   100_000},
    {"name": "Tagomago",            "loc": "Ibiza, Spain",         "price":     18_000_000, "upkeep":   120_000, "income":   120_000},
    {"name": "Gladstone's Island",  "loc": "Australia",            "price":     12_000_000, "upkeep":    90_000, "income":    90_000},
    {"name": "Nukutepipi",          "loc": "French Polynesia",     "price":     22_000_000, "upkeep":   150_000, "income":   150_000},
    {"name": "Vomo Island",         "loc": "Fiji",                 "price":     28_000_000, "upkeep":   200_000, "income":   200_000},
    {"name": "Musha Cay",           "loc": "Bahamas",              "price":     37_000_000, "upkeep":   300_000, "income":   300_000},
    {"name": "Little Saint James",  "loc": "U.S. Virgin Islands",  "price":     45_000_000, "upkeep":   250_000, "income":   600_000},
    {"name": "North Island",        "loc": "Seychelles",           "price":     50_000_000, "upkeep":   400_000, "income":   400_000},
    {"name": "Laucala Island",      "loc": "Fiji",                 "price":     75_000_000, "upkeep":   500_000, "income":   500_000},
    {"name": "Necker Island",       "loc": "British Virgin Islands","price":   100_000_000, "upkeep":   800_000, "income":   800_000},
    {"name": "Mustique",            "loc": "St. Vincent",          "price":    150_000_000, "upkeep": 1_200_000, "income": 1_200_000},
    {"name": "Lanai",               "loc": "Hawaii, USA",          "price":    300_000_000, "upkeep": 2_000_000, "income": 2_000_000},
]

# ---------------------------------------------------------------------
# Pleasures
# ---------------------------------------------------------------------

PLEASURES = [
    {"name": "Smoking",           "cost":    150_000, "happiness": 12,
     "risk": {"chance": 0.35, "title": "Your Lungs Filed a Complaint", "money": -12_000_000, "opinion": -5, "transgression": 0}},
    {"name": "Drinking",         "cost":    250_000, "happiness": 18,
     "risk": {"chance": 0.40, "title": "You Called the PM 'Champ'", "money": -8_000_000, "opinion": -8, "transgression": 4}},
    {"name": "Luxury Cruise",    "cost":  3_000_000, "happiness": 30, "risk": None},
    {"name": "Trophy Hunting",   "cost":  6_000_000, "happiness": 35,
     "risk": {"chance": 0.55, "title": "PETA Found the Photos", "money": -5_000_000, "opinion": -20, "transgression": 8}},
    {"name": "Exotic Pet",       "cost":  5_000_000, "happiness": 28,
     "risk": {"chance": 0.30, "title": "Gerald Got Out", "money": -20_000_000, "opinion": -10, "transgression": 5}},
    {"name": "Gambling Binge",   "cost":  5_000_000, "happiness": 25,
     "risk": {"chance": 0.60, "title": "The System Did Not Work", "money": -18_000_000, "opinion": 0, "transgression": 0}},
    {"name": "Skydiving",        "cost":    500_000, "happiness": 20,
     "risk": {"chance": 0.20, "title": "The Parachute Had Notes", "money": -15_000_000, "opinion": 0, "transgression": 0}},
    {"name": "Fine Dining",      "cost":    800_000, "happiness": 15, "risk": None},
    {"name": "Private Concert",  "cost":  2_000_000, "happiness": 22, "risk": None},
    {"name": "Cosmetic Surgery", "cost":  3_000_000, "happiness": 20,
     "risk": {"chance": 0.30, "title": "The Surgeon Had a Sneezing Fit", "money": -10_000_000, "opinion": -12, "transgression": 0}},
]

# ---------------------------------------------------------------------
# Casino
# ---------------------------------------------------------------------

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['S', 'H', 'D', 'C']  # spade heart diamond club — plain letters,
                              # not the ♠♥♦♣ glyphs, since most Android
                              # system fonts (and Kivy's bundled font)
                              # don't reliably render them either.
RANK_VAL = {r: i for i, r in enumerate(RANKS)}

SLOT_SYMBOLS = ["cherry", "lemon", "orange", "grapes", "diamond", "seven"]
SLOT_PAYOUTS = {
    ("seven", "seven", "seven"):     ("JACKPOT 777!", 100),
    ("diamond", "diamond", "diamond"): ("Triple Diamond!", 50),
    ("cherry", "cherry", "cherry"):  ("Triple Cherry!", 10),
    ("lemon", "lemon", "lemon"):     ("Triple Lemon!", 10),
    ("orange", "orange", "orange"):  ("Triple Orange!", 10),
    ("grapes", "grapes", "grapes"):  ("Triple Grapes!", 10),
}

POKER_HANDS = [
    # (name, multiplier, check_fn(ranks_desc, counts_desc, flush, straight))
    ("Royal Flush!",     250, lambda r, c, f, s: f and s and r == [12, 11, 10, 9, 8]),
    ("Straight Flush!",   50, lambda r, c, f, s: f and s),
    ("Four of a Kind!",   25, lambda r, c, f, s: c[0] == 4),
    ("Full House!",        9, lambda r, c, f, s: c[:2] == [3, 2]),
    ("Flush!",             6, lambda r, c, f, s: f),
    ("Straight!",          4, lambda r, c, f, s: s),
    ("Three of a Kind!",   3, lambda r, c, f, s: c[0] == 3),
    ("Two Pair!",          2, lambda r, c, f, s: c[:2] == [2, 2]),
]

WORK_RANGES = [
    (10_000, 200_000),
    (1_000_000, 5_000_000),
    (20_000_000, 80_000_000),
    (150_000_000, 500_000_000),
]

# ---------------------------------------------------------------------
# Elections / Executive Orders
# ---------------------------------------------------------------------

ELECTION_THRESHOLD = 1_000_000_000
TERM_LENGTH = 4
MAX_TERMS = 2

EFFECT_RANGES = {
    "daily_expense_multiplier": (0.40, 0.95),
    "income_multiplier":        (1.10, 2.50),
    "transgression_decay_bonus": (1, 8),
    "public_opinion_daily":     (1, 10),
    "loan_rate_multiplier":     (0.30, 0.90),
    "happiness_daily":          (1, 8),
    "wanted_fine_reduction":    (0.30, 0.90),
}

EXECUTIVE_ORDER_TEMPLATES = [
    {"label": "Cut Government Spending 15%",   "type": "daily_expense_multiplier", "value": 0.85},
    {"label": "Boost Industrial Output 20%",   "type": "income_multiplier",         "value": 1.20},
    {"label": "Grant Clemency & Amnesty",       "type": "transgression_decay_bonus", "value": 5},
    {"label": "National Unity Campaign",        "type": "public_opinion_daily",      "value": 6},
    {"label": "Cap Loan Interest Rates",        "type": "loan_rate_multiplier",      "value": 0.70},
    {"label": "Fund National Wellbeing",        "type": "happiness_daily",           "value": 4},
    {"label": "Waive Law Enforcement Fines",    "type": "wanted_fine_reduction",     "value": 0.60},
]
