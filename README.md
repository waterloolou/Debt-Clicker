# Debt Clicker

You are in the top 1%. You have become corrupt. Random disasters will destroy your empire. How long can you last?

A dark-humour idle/clicker game built in Python with a live stock market, casino mini-games, and a persistent leaderboard.

---

## Features

- **Live stock market** — 70+ real stocks across 10 categories (AI, Tech, Energy, Finance, Healthcare, Retail, Automotive, Defense, Entertainment, Space), seeded with 1 year of historical price data via yfinance
- **34 random events** — tax fraud, Ponzi schemes, space disasters, and worse
- **Casino** — Russian Roulette, Slot Machine, and 5-Card Draw Poker, each with full visuals
- **Analog clock** — one full rotation per minute; reaching 12 advances the game day
- **Persistent leaderboard** — top 50 scores saved to `leaderboard.json`
- **Dark UI** — matplotlib graphs with matching dark theme

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
pip install matplotlib yfinance
```

> tkinter ships with the standard Python installer on Windows and macOS.
> On Linux: `sudo apt install python3-tk`

---

## Running the game

```bash
python main.py
```

Or, if you have an existing shortcut pointing to the original file:

```bash
python debt_clicker.py
```

---

## Project structure

```
Debt Clicker Python Project/
├── main.py               # Entry point
├── game.py               # DebtClicker class — game loop, clock, data fetch
├── constants.py          # Stock categories, price ranges, leaderboard path
├── market.py             # StockMarket — buy/sell/create stocks
├── screens_mixin.py      # All UI screens (start, game, end, leaderboard)
├── events_mixin.py       # 34 random events, popups, market effects
├── casino_mixin.py       # Casino lobby, Russian Roulette, Slots, Poker
├── stock_window_mixin.py # Stock market window, graphs, price updates
├── leaderboard.json      # Auto-created on first play-through
└── debt_clicker.py       # Legacy entry point (forwards to main.py)
```

---

## How to play

1. Enter your name and press **Start Game**
2. The clock in the top-right counts down 60 seconds per day
3. Use **Work** to earn money, **Casino** to gamble, and **Stock Market** to invest
4. Random events fire every day — some help, most hurt
5. The game ends when your money hits $0
6. Your score (days survived) is saved to the leaderboard automatically
