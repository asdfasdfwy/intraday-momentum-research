from src.backtest import state
from src.backtest.signal import findsignal
import math


MAX_POSITIONS = 2
ALLOCATION = 0.5
COST_RATE = 30 / 10_000


def buy(ticker, boughtat, percchange, timestamp):
    available_allocation = min(
        state.portval * ALLOCATION,
        state.cash
    )

    number = math.floor(
        available_allocation /
        (boughtat * (1 + COST_RATE))
    )

    if number <= 0:
        return False

    notional = number * boughtat
    buy_cost = notional * COST_RATE
    cashneeded = notional + buy_cost

    if state.cash < cashneeded:
        return False

    tp = boughtat * (
        1 + percchange * 0.8 / 100
    )

    sl = boughtat * (
        1 - percchange * 0.5 / 100
    )

    state.portstocks[ticker] = [
        number,
        boughtat,
        0,
        tp,
        sl,
        buy_cost
    ]

    state.cash -= cashneeded
    state.portval -= buy_cost

    print(
        f"BUY {ticker} | time={timestamp} | "
        f"price={boughtat:.2f} | "
        f"shares={number} | "
        f"signal={percchange:.2f}% | "
        f"cost={buy_cost:.2f} | "
        f"TP={tp:.2f} | "
        f"SL={sl:.2f}"
    )

    return True


def sell(ticker, currentval, reason, timestamp):
    values = state.portstocks[ticker]

    shares = values[0]
    boughtat = values[1]
    minutes_held = values[2] + 1
    buy_cost = values[5]

    entry_notional = shares * boughtat
    exit_notional = shares * currentval

    sell_cost = exit_notional * COST_RATE
    proceeds = exit_notional - sell_cost

    gross_pnl = exit_notional - entry_notional
    total_cost = buy_cost + sell_cost
    net_pnl = gross_pnl - total_cost

    return_percent = (
        100
        * net_pnl
        / (entry_notional + buy_cost)
    )

    state.cash += proceeds
    state.portval += gross_pnl - sell_cost

    print(
        f"SELL {ticker} | time={timestamp} | "
        f"price={currentval:.2f} | "
        f"shares={shares} | "
        f"gross_P&L={gross_pnl:+.2f} | "
        f"cost={total_cost:.2f} | "
        f"net_P&L={net_pnl:+.2f} | "
        f"return={return_percent:+.2f}% | "
        f"held={minutes_held}min | "
        f"reason={reason} | "
        f"portfolio={state.portval:.2f}"
    )

    del state.portstocks[ticker]


def trademinute(time, daydf):
    timestamps = (
        daydf.index
        .get_level_values("timestamp")
        .unique()
    )

    timestamp = timestamps[time]
    stocks = daydf.loc[timestamp]

    is_last_minute = (
        time == len(timestamps) - 1
    )

    if time != 0:
        for index, row in state.minutedf.iterrows():
            symbol = row["symbol"]

            if symbol not in stocks.index:
                continue

            price = stocks.loc[symbol].close

            state.minutedf.at[index, "price"] = price

            history = state.minutedf.at[
                index,
                "prev5"
            ]

            if len(history) == 5:
                history.pop(0)

            history.append(price)

    for ticker, values in list(
        state.portstocks.items()
    ):
        if ticker not in stocks.index:
            continue

        price = stocks.loc[ticker].close

        if price >= values[3]:
            sell(
                ticker,
                price,
                "TAKE_PROFIT",
                timestamp
            )

        elif price <= values[4]:
            sell(
                ticker,
                price,
                "STOP_LOSS",
                timestamp
            )

        elif values[2] >= 59:
            sell(
                ticker,
                price,
                "TIME_LIMIT",
                timestamp
            )

        elif is_last_minute:
            sell(
                ticker,
                price,
                "END_OF_DAY",
                timestamp
            )

        else:
            state.portstocks[ticker][2] += 1

    if (
        len(state.portstocks) < MAX_POSITIONS
        and not is_last_minute
    ):
        signal = findsignal()

        if signal:
            ticker = signal[0]
            percchange = signal[1]

            if (
                ticker not in state.portstocks
                and ticker in stocks.index
            ):
                buy(
                    ticker,
                    stocks.loc[ticker].close,
                    percchange,
                    timestamp
                )