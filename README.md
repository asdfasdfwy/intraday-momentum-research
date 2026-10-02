# Intraday Momentum Research

A Python research project for downloading US equity market data and backtesting an intraday momentum strategy.

> **Status:** Work in progress. The SIP data pipeline, portfolio state, and basic trade functions are implemented. Signal generation, execution modeling, and performance analysis are still under development.

## Research objective

The project investigates whether short-term price momentum becomes more informative when it is confirmed by unusually high trading volume.

The planned signal is:

- **Momentum:** the stock rises by more than 1% over five minutes.
- **Relative volume:** the latest one-minute volume exceeds 1.5 times the median volume for the same minute over the previous 20 trading days.
- **Ranking:** qualifying stocks are ranked using `relative volume × momentum`.
- **Selection:** the highest-ranked opportunity is traded.
- **Exits:** take profit, stop loss, a 15-minute time stop, or liquidation at the end of the regular session.

The intended universe excludes stocks below $5 and requires at least $50 million in daily trading value.

## Current functionality

- Retrieves the official US market calendar through Alpaca.
- Selects US equities using daily SIP bars.
- Downloads one-minute SIP bars for regular market hours.
- Stores one Parquet file per trading day.
- Converts New York market hours to UTC with daylight-saving-time support.
- Maintains shared cash, portfolio value, and open-position state.
- Provides basic buy and sell functions for the developing backtest engine.

## Repository structure

- `src/api.py` — loads credentials and creates Alpaca data and trading clients.
- `src/download/selectsymbols.py` — obtains trading days, retrieves daily bars, and applies the universe filters.
- `src/download/day.py` — saves filtered daily data as Parquet files.
- `src/download/minute.py` — downloads regular-session minute bars for the selected symbols.
- `src/backtest/state.py` — stores portfolio state.
- `src/backtest/trade.py` — contains the current buy, sell, and per-minute trading functions.
- `src/backtest/main.py` — loads each daily minute file and runs the backtest loop.
- `data/day/` — local daily Parquet files.
- `data/minute/` — local minute Parquet files.

The downloaded datasets are intentionally excluded from Git because of their size.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/asdfasdfwy/intraday-momentum-research.git
cd intraday-momentum-research
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

If your environment does not already contain a Parquet engine, install PyArrow:

```bash
python3 -m pip install pyarrow
```

### 4. Configure Alpaca credentials

Create a `.env` file in the repository root:

```env
API_KEY=your_alpaca_api_key
SECRET=your_alpaca_secret_key
```

The `.env` file is ignored by Git and should never be committed.

## Usage

Run commands from the repository root. Using module syntax ensures that imports beginning with `src` resolve correctly.

### Download daily data

```bash
python3 -m src.download.day
```

### Download minute data

```bash
python3 -m src.download.minute
```

Daily data should be downloaded before minute data because the daily bars define the stock universe.

### Run the developing backtest

```bash
python3 -m src.backtest.main
```

The program currently asks for the starting portfolio value through standard input.

## Data format

Files are stored by trading date:

```text
data/day/YYYY-MM-DD.parquet
data/minute/YYYY-MM-DD.parquet
```

Alpaca bars contain fields including:

- `open`
- `high`
- `low`
- `close`
- `volume`
- `trade_count`
- `vwap`

The bar DataFrames use `symbol` and `timestamp` as index levels. The backtest reorders them to `timestamp, symbol` so all available stocks can be processed minute by minute.

Minute bars are sparse: if Alpaca receives no qualifying trade for a symbol during a minute, that symbol-minute row may be absent.

## Time handling

Alpaca's calendar returns New York market opening and closing times without timezone information. The minute downloader explicitly assigns `America/New_York` and converts the values to UTC. This automatically accounts for daylight saving time.

Regular sessions normally contain 390 one-minute intervals. Scheduled early-close sessions contain approximately 210, so the completed backtest should iterate over the timestamps actually present rather than assume every session has 390 bars.

## Research limitations

The current repository is an early research implementation, not a production trading system. Important limitations include:

- The daily universe is currently selected using information from the same trading day. It must be shifted to the previous session before final testing to eliminate look-ahead bias.
- The current asset list may create survivorship or historical-universe bias.
- Transaction costs, slippage, spread, latency, and market impact are not yet modeled.
- Missing bars must be handled without inventing executable prices.
- API rate limits and interrupted downloads require stronger retry and resume handling.
- The signal, position-management rules, and performance statistics are not yet complete.

Results should not be interpreted until these issues are addressed.

## Roadmap

- Reuse saved daily files when downloading minute bars.
- Add robust exponential-backoff and resume behavior.
- Remove look-ahead bias from universe construction.
- Implement the 20-day same-minute relative-volume calculation.
- Implement five-minute momentum scoring and candidate ranking.
- Model commissions, spread, slippage, and execution constraints.
- Support early-close sessions and missing bars safely.
- Record trades and calculate returns, drawdown, Sharpe ratio, hit rate, and turnover.
- Separate in-sample development from out-of-sample evaluation.

## Disclaimer

This repository is for educational and research purposes only. It does not provide financial advice, and historical backtest results do not guarantee future performance.
