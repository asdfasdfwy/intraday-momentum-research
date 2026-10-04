from src.backtest import state
from src.backtest.signal import findsignal
import math


def buy(ticker, boughtat, percchange, timestamp):
    number = math.floor(state.portval / boughtat)
    cashneeded = number * boughtat

    if number <= 0 or state.cash < cashneeded:
        return False

    tp = boughtat + (boughtat * percchange * 0.8 / 100)
    sl = boughtat - (boughtat * percchange * 0.5 / 100)

    state.portstocks[ticker] = [
        number,
        boughtat,
        0,
        tp,
        sl
    ]

    state.cash -= cashneeded

    print(
        f"BUY {ticker} | time={timestamp} | "
        f"price={boughtat:.2f} | shares={number} | "
        f"signal={percchange:.2f}% | "
        f"TP={tp:.2f} | SL={sl:.2f}"
    )

    return True


def sell(ticker, currentval, reason, timestamp):
    values = state.portstocks[ticker]

    shares = values[0]
    boughtat = values[1]
    minutes_held = values[2] + 1

    pnl_per_share = currentval - boughtat
    total_pnl = pnl_per_share * shares
    return_percent = 100 * pnl_per_share / boughtat

    state.portval += total_pnl
    state.cash += shares * currentval

    print(
        f"SELL {ticker} | time={timestamp} | "
        f"price={currentval:.2f} | shares={shares} | "
        f"P&L={total_pnl:+.2f} | "
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
    is_last_minute = time == len(timestamps) - 1

    if time != 0:
        for index, row in state.minutedf.iterrows():
            symbol = row["symbol"]
            price = stocks.loc[symbol].close

            state.minutedf.at[index, "price"] = price

            history = state.minutedf.at[index, "prev5"]

            if len(history) == 5:
                history.pop(0)

            history.append(price)

    if state.portstocks:
        ticker, values = next(iter(state.portstocks.items()))
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

    elif not is_last_minute:
        signal = findsignal()

        if signal:
            ticker = signal[0]
            percchange = signal[1]
            price = stocks.loc[ticker].close

            buy(
                ticker,
                price,
                percchange,
                timestamp
            )