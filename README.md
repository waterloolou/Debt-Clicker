# Debt Clicker

> You are in the top 1%. You have become corrupt. Random disasters will destroy your empire. How long can you last?

[![Download](https://img.shields.io/github/v/release/waterloolou/Debt-Clicker?label=Download&logo=github)](https://github.com/waterloolou/Debt-Clicker/releases/latest)
[![Build](https://img.shields.io/github/actions/workflow/status/waterloolou/Debt-Clicker/build-release.yml?label=Build)](https://github.com/waterloolou/Debt-Clicker/actions)

A dark-humour idle/clicker game built in Python with live stock markets, casino mini-games, a world resource map, multiplayer with real-time war mechanics, and 16 deep gameplay systems.

---

## Download (Windows)

1. Go to the [**Releases page**](https://github.com/waterloolou/Debt-Clicker/releases/latest)
2. Download **DebtClicker-Windows.zip**
3. Extract it anywhere
4. Run **DebtClicker.exe**

No Python installation required.

---

## Features

### Core Loop
- **Live stock market** — 70+ real stocks across 10 categories (AI, Tech, Energy, Finance, Healthcare, Retail, Automotive, Defense, Entertainment, Space), seeded with historical price data via yfinance
- **34+ random events** — tax fraud, Ponzi schemes, space disasters, divorce scandals, pandemics, and worse — fire at the **end of every game day**
- **Casino** — Russian Roulette, Slot Machine (coloured symbols, win sounds, flashing lights), and 5-Card Draw Poker (bet → see hand → draw)
- **Analog clock** — one full rotation per minute; reaching 12 advances the game day
- **Persistent leaderboard** — top 50 scores saved locally, with Infamy Title shown next to each score

### Single Player vs Multiplayer
- **Start screen** lets you choose Single Player or Multiplayer before entering the game
- **Single Player** — play against three AI rival billionaires; any country available
- **Multiplayer** — join a 3-player lobby via 4-letter code; rivals are real players; restricted to USA, China, or Russia
- **In-game chat** — live colour-coded chat window during multiplayer sessions (press Enter to send)

### World Map
- **6 resource types** — Oil, Diamonds, Minerals, Agriculture, Technology, Finance
- **Bomb or Stage a Coup** in resource-rich countries to earn daily income
- **Alliance system** — ally with USA, Russia, or China for cost discounts *and* attack interception (your alliance intelligence can block incoming rival attacks)
- **Sanctions** — countries retaliate after bombings with daily economic penalties
- **Rival billionaires** — Viktor Drago, Chen Wei, and Elizabeth Harlow compete aggressively: 15% daily chance to seize countries, 8% daily chance to directly attack you (smear campaigns, lawsuits, sabotage, staff poaching, regulatory tip-offs), and immediate retaliation if you bomb their territory

### Island Map
- **19 real private islands** worldwide, each with daily income
- **Little Saint James** (Jeffrey Epstein's island) — $45M, $600K/day income; owning it changes the Epstein event entirely
- **Zoom & pan** — scroll to zoom, right-click drag to pan, Caribbean/Pacific view buttons

### Economy
- **Assets** — supercars, megayacht, private jet, doomsday bunker, private army, space program — each with upkeep and passive income or special event protection
- **Debt & Loans** — borrow $10M–$200M with daily compounding interest; loans expiring within 5 days shown in red; default costs 50% of remaining funds
- **Stock Pump & Dump** — inflate stocks you own, then dump at 1.5× before the crash

### Corruption Systems
- **Lobby System** — each action changes only ONE stat (opinion OR transgressions, never both); more expensive than before
  - Bribe Official ($2M), Control Narrative ($8M), Buy Senator Records ($40M), Buy Senator Image ($40M), Senate Immunity ($60M), Full Records Expunge ($150M), Presidential Rehabilitation ($150M)
- **Black Market** — 4-day cooldown per item; stolen data, arms smuggling, laundered cash, organ trafficking, forged documents
- **Infamy Tiers** — 6 tiers from "Nobody" to "ENDGAME" based on transgression level; title shown next to leaderboard score
- **Wanted Level** — escalates from Media Attention → Senate Investigation → FBI Target → Interpol Red Notice

### Death Conditions & End Screens
- **4 ways to die**: Money hits $0, Happiness hits 0, Public Opinion hits 0, Transgressions hits 100
- **1-day warnings** — each condition gives a bold popup before killing you; fix it or it's over
- **Themed end screens** — each death cause has its own title, flavour text, icon, and colour scheme

### War Room (Multiplayer)
- **Buy militia** in 4 tiers: Mercenary Squad (15 units, $30M) → Elite Strike Force (120 units, $280M)
- **Deploy attacks**: Spy, Raid, Assassinate, Sabotage, Blockade, Nuke — each consumes units
- **Defense reduction** — every 20 militia units cuts incoming attack damage by 10% (up to 50%)
- **War declaration** — bombing a rival's home country triggers 15-day war tax ($1.5M/day each)

### Epstein Event
- Jeffrey Epstein texts you an iMessage-style invite; accept for happiness and cash, but risk exposure daily
- If you **own Little Saint James**, you can invite rivals and frame them — their reputation crashes, yours doesn't

### Meta
- **Legacy System** — survive 10+ days to bank a bonus (up to $50M) that carries into your next run
- **Net Worth Graph** — matplotlib chart of your money across every day survived
- **News Ticker** — scrolling headline bar reporting all events, market moves, and rival activity in real time
- **Wiki** — in-game help page covering every mechanic, accessible from the start screen

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
pip install -r requirements.txt
```

> **tkinter** ships with the standard Python installer on Windows and macOS.
> On Linux: `sudo apt install python3-tk`

---

## Running the game

```bash
python main.py
```

### Running a multiplayer server

```bash
python server.py
```

The server runs on port 5555. Players connect via the in-game Multiplayer lobby by entering the host's IP and a 4-letter room code.

---

## Project structure

```
Debt Clicker Python Project/
├── main.py                  # Entry point
├── game.py                  # DebtClicker class — game loop, clock, legacy, alliances
├── server.py                # TCP multiplayer server (port 5555, max 3 players/lobby)
├── network_client.py        # Client-side TCP connection with JSON message protocol
├── constants.py             # Stock categories, price ranges, leaderboard path
├── market.py                # StockMarket — buy/sell/create stocks
├── screens_mixin.py         # All UI screens, stat bars, news ticker, wiki, end screens
├── events_mixin.py          # 34+ random events, Epstein iMessage event, popups
├── casino_mixin.py          # Casino: Russian Roulette, Slots (coloured symbols), Poker
├── stock_window_mixin.py    # Stock market window, graphs, pump/dump
├── assets_mixin.py          # Purchasable assets with upkeep and passive income
├── world_map_mixin.py       # World map, bomb/coup, alliances, sanctions
├── island_map_mixin.py      # Island map with zoom/pan and 19 purchasable islands
├── lobby_mixin.py           # Lobby — bribe officials, senate immunity, pardons
├── black_market_mixin.py    # Black market with 4-day per-item cooldowns
├── debt_mixin.py            # Loan system with compounding interest
├── rivals_mixin.py          # AI rivals — territory seizure, direct attacks, retaliation
├── multiplayer_mixin.py     # Multiplayer lobby, network sync, chat, war declaration
├── militia_mixin.py         # War Room — buy militia, deploy attacks, receive attacks
├── leaderboard.json         # Auto-created on first play-through
└── legacy.json              # Auto-created — carries bonus to next run
```

---

## How to play

1. Enter your name, select your country, and press **Single Player** or **Multiplayer**
2. The clock in the top-right counts down 60 real seconds per game day
3. Use **Work**, **Casino**, and the **Stock Market** to earn money
4. Open the **World Map** to seize resource countries via bombing or coups
5. Manage **Debt**, run **Lobby** operations, and deal on the **Black Market**
6. Watch your **Happiness**, **Public Opinion**, and **Transgressions** — each triggers a death condition if it hits its limit; you get a 1-day warning
7. In multiplayer, use the **War Room** to build militia and deploy attacks on rivals
8. Your score (days survived) and **Infamy Title** are saved to the leaderboard

> Open the **Wiki** on the start screen for a full breakdown of every mechanic.
