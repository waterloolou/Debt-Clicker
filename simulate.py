"""
Headless simulation of Debt Clicker game logic.
Runs N games without any GUI, reports survival stats and flags exploits.
"""
import random, sys, types, collections

# ── Stub out tkinter so imports don't crash ────────────────────────────────
tk_stub = types.ModuleType("tkinter")
ttk_stub = types.ModuleType("tkinter.ttk")
for name in ["Tk","Frame","Label","Button","Entry","Text","Canvas","Toplevel",
             "Scrollbar","StringVar","BooleanVar","IntVar","DoubleVar","END",
             "scrolledtext","font","messagebox"]:
    setattr(tk_stub, name, lambda *a, **kw: None)
tk_stub.ttk = ttk_stub
for name in ["Combobox","Notebook","Style"]:
    setattr(ttk_stub, name, lambda *a, **kw: None)
sys.modules["tkinter"] = tk_stub
sys.modules["tkinter.ttk"] = ttk_stub
sys.modules["tkinter.scrolledtext"] = tk_stub
sys.modules["tkinter.font"] = tk_stub
sys.modules["tkinter.messagebox"] = tk_stub

import matplotlib
matplotlib.use("Agg")

# ── Minimal game simulation ───────────────────────────────────────────────
sys.path.insert(0, ".")

STARTING_MONEY = 100_000_000

def simulate_game(seed=None):
    if seed is not None:
        random.seed(seed)

    money = STARTING_MONEY
    days = 0
    flags = []

    # flags
    family = rich_relative = company = True
    revolution = mansion = pet = True
    epstein = subscription = space = ponzi = False
    oil_spill = carbon = insider_trading = pandemic = False
    market_effects = []
    public_opinion = 75
    is_president = False

    def lose_money():
        nonlocal money
        m = money
        if m < 50:           lost = random.randint(1, 25)
        elif m < 100:        lost = random.randint(10, 50)
        elif m < 1000:       lost = random.randint(100, 500)
        elif m < 10000:      lost = random.randint(100, 1000)
        elif m < 100000:     lost = random.randint(1000, 10000)
        else:                lost = random.randint(100, 10_000_000)
        money -= lost

    def random_events():
        nonlocal money, family, rich_relative, company, revolution
        nonlocal mansion, pet, epstein, subscription, space, ponzi
        nonlocal oil_spill, carbon, insider_trading, pandemic, public_opinion
        r = random.randint(1, 70)
        if r == 1 and family:
            family = False; money /= 2
        elif r == 2:
            money *= 0.30
        elif r == 3 and company:
            money -= 50_000
        elif r == 4 and rich_relative:
            rich_relative = False; money += 1_000_000
        elif r == 5:
            pass  # advisor liquidates stocks (no stock tracking here)
        elif r == 7 and not epstein:
            epstein = True; money -= 10_000_000
        elif r == 8:
            money -= 5_000_000
        elif r == 12 and revolution:
            # revolution — accept forces money = 10000
            revolution = False
            if random.random() < 0.5:
                money = 10_000
            else:
                money = -1  # declined, game over
        elif r == 17 and not space:
            space = True; money -= 500_000_000
        elif r == 20 and not ponzi:
            ponzi = True; money -= 20_000_000
        elif r == 21 and not oil_spill:
            oil_spill = True; money -= 50_000_000
        elif r == 34 and not pandemic:
            pandemic = True; money *= 0.60

    max_money = STARTING_MONEY
    death_cause = "broke"

    for year in range(1, 10001):
        days = year
        lose_money()
        random_events()
        # Check for negative-money edge cases
        if money > 1e15:
            flags.append(f"Year {year}: money exploded to ${money:.2e} (possible exploit)")
        max_money = max(max_money, money)
        if money <= 0:
            death_cause = "broke"
            break

    return {"days": days, "max_money": max_money, "death_cause": death_cause, "flags": flags}


def run_simulations(n=1000):
    results = []
    death_causes = collections.Counter()
    all_flags = []
    max_money_seen = 0
    max_money_game = 0

    for i in range(n):
        r = simulate_game(seed=i)
        results.append(r)
        death_causes[r["death_cause"]] += 1
        all_flags.extend(r["flags"])
        if r["max_money"] > max_money_seen:
            max_money_seen = r["max_money"]
            max_money_game = i

    days_list = [r["days"] for r in results]
    avg = sum(days_list) / len(days_list)
    median = sorted(days_list)[len(days_list)//2]
    top10 = sorted(days_list, reverse=True)[:10]

    print(f"\n{'='*55}")
    print(f"  DEBT CLICKER — {n} SIMULATION REPORT")
    print(f"{'='*55}")
    print(f"  Avg survival:    {avg:.1f} years")
    print(f"  Median survival: {median} years")
    print(f"  Longest 10:      {top10}")
    print(f"  Shortest:        {min(days_list)} years")
    print(f"\n  Death causes:")
    for cause, count in death_causes.most_common():
        print(f"    {cause}: {count} ({100*count/n:.1f}%)")
    print(f"\n  Max money ever seen: ${max_money_seen:,.0f} (game #{max_money_game})")
    if all_flags:
        print(f"\n  !! EXPLOIT FLAGS ({len(all_flags)} total):")
        for f in all_flags[:20]:
            print(f"    {f}")
    else:
        print(f"\n  OK No exploit flags triggered.")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    run_simulations(n)
