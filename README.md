# Debt Clicker

> You are in the top 1%. You have become corrupt. Random disasters will destroy your empire. How long can you last?

A dark-humour idle/clicker game built in Python with a live stock market, casino mini-games, a world resource map, and 13 deep gameplay systems.

---

## Features

### Core Loop
- **Live stock market** — 70+ real stocks across 10 categories (AI, Tech, Energy, Finance, Healthcare, Retail, Automotive, Defense, Entertainment, Space), seeded with 1 year of historical price data via yfinance
- **34 random events** — tax fraud, Ponzi schemes, space disasters, divorce scandals, pandemics, and worse
- **Casino** — Russian Roulette, Slot Machine, and 5-Card Draw Poker with full visuals
- **Work** — earn income directly to slow the bleed
- **Analog clock** — one full rotation per minute; reaching 12 advances the game day
- **Persistent leaderboard** — top 50 scores saved locally

### World Map
- **6 resource types** — Oil, Diamonds, Minerals, Agriculture, Technology, Finance
- **Bomb or Stage a Coup** in resource-rich countries to earn daily income
- **Alliance system** — ally with USA, Russia, or China for 30% cost discounts in their sphere of influence
- **Sanctions** — countries retaliate after bombings with daily economic penalties
- **Rival billionaires** — Viktor Drago, Chen Wei, and Elizabeth Harlow compete for the same countries in real time; buy them out or race them to the deal

### Economy
- **Assets** — buy luxury items (supercars, megayacht, private jet, doomsday bunker, private army, space program) with daily upkeep and passive income
- **Private Islands** — 18 real islands worldwide to purchase, each earning daily revenue
- **Debt & Loans** — borrow $10M–$200M with daily compounding interest; default costs 50% of your remaining funds
- **Stock Pump & Dump** — artificially inflate stocks you own, then dump them for 1.5x price before the crash

### Corruption Systems
- **Lobby System** — bribe officials, buy congressmen, get a Presidential Pardon, or pay $40M for a one-use Senate Immunity that blocks your next bad event
- **Black Market** — stolen data, arms smuggling, laundered cash, organ trafficking, and forged documents
- **Infamy Tiers** — 6 tiers from "Nobody" to "ENDGAME" based on transgression level
- **Wanted Level** — escalates from Media Attention → Senate Investigation → FBI Target → Interpol Red Notice, each adding a daily fine
- **War Events** — let public opinion reach 0 and a country declares war on you

### Meta
- **Legacy System** — survive 10+ days to bank a bonus (up to $50M) that carries into your next run
- **Net Worth Graph** — matplotlib chart of your money over every day you've survived
- **News Ticker** — scrolling headline bar that reports all major events in real time
- **Stat Bars** — live Happiness, Public Opinion, and Transgressions bars on the main screen
- **Wiki** — in-game help page covering every mechanic

---

## Requirements

- Python 3.9+
- [pip](https://pip.pypa.io/en/stable/)

---

## Installation

```bash
# Clone the repo
git clone https://github.com/waterloolou/Debt-Clicker.git
cd "Debt-Clicker"

# Install dependencies
pip install matplotlib yfinance geopandas shapely
```

> **tkinter** ships with the standard Python installer on Windows and macOS.
> On Linux: `sudo apt install python3-tk`

---

## Running the game

```bash
python main.py
```

---

## Project structure

```
Debt Clicker Python Project/
├── main.py                  # Entry point
├── game.py                  # DebtClicker class — game loop, clock, legacy, alliances, war
├── constants.py             # Stock categories, price ranges, leaderboard path
├── market.py                # StockMarket — buy/sell/create stocks
├── screens_mixin.py         # All UI screens, stat bars, news ticker, wiki
├── events_mixin.py          # 34 random events, popups, market effects
├── casino_mixin.py          # Casino lobby, Russian Roulette, Slots, Poker
├── stock_window_mixin.py    # Stock market window, graphs, pump/dump
├── assets_mixin.py          # Purchasable assets with upkeep and passive income
├── world_map_mixin.py       # World map, bomb/coup, alliances, sanctions, rivals
├── island_map_mixin.py      # Private island browser and purchase
├── lobby_mixin.py           # Lobby system — bribe politicians, buy immunity
├── black_market_mixin.py    # Black market — illegal deals for fast cash
├── debt_mixin.py            # Loan system with compounding interest
├── rivals_mixin.py          # AI rival billionaires competing for resources
├── leaderboard.json         # Auto-created on first play-through
└── legacy.json              # Auto-created — carries bonus to next run
```

---

## How to play

1. Enter your name, select your country, and press **Start Game**
2. The clock in the top-right counts down 60 real seconds per game day
3. Use **Work**, **Casino**, and the **Stock Market** to earn money
4. Open the **World Map** to seize resource countries via bombing or coups
5. Manage your **Debt**, run **Lobby** operations, and deal on the **Black Market**
6. Watch your **Transgressions** and **Public Opinion** — let them spiral and you face war, FBI investigations, and Interpol red notices
7. The game ends when your money hits $0 — your days survived are saved to the leaderboard
8. Survive long enough to build a **Legacy Bonus** for your next run

> Open the **Wiki** on the start screen for a full breakdown of every mechanic.
