from src.backtest import state
import math
from src.backtest.signal import findsignal

def buy(ticker, boughtat, percchange):
    number = math.floor(state.portval/boughtat)
    cashneeded = number*boughtat
    tp = boughtat + (boughtat * percchange * 0.8 / 100)
    sl = boughtat - (boughtat * percchange * 0.5 / 100)
    if state.cash >= cashneeded:
        state.portstocks[ticker] = [number, boughtat, 0, tp, sl]
        state.cash -= number*boughtat
    print(
            f"BUY {ticker} | price={boughtat:.2f} | "
            f"shares={number} | signal={percchange:.2f}% | "
            f"TP={tp:.2f} | SL={sl:.2f}"
        )

def sell(ticker, currentval):
    profpershare = currentval - state.portstocks[ticker][1]
    state.portval += profpershare*state.portstocks[ticker][0]
    state.cash += state.portstocks[ticker][0]*currentval
    del state.portstocks[ticker]

def trademinute(time, daydf):
    timestamps = daydf.index.get_level_values("timestamp").unique()
    timestamp = timestamps[time]
    stocks = daydf.loc[timestamp]
    if time != 0:
        for index, row in state.minutedf.iterrows():
            price = stocks.loc[row["symbol"]].close
            state.minutedf.at[index, "price"] = price
            if len(row["prev5"]) == 5:
                state.minutedf.at[index, "prev5"].pop(0)
            state.minutedf.at[index, "prev5"].append(price)
    if len(state.portstocks) == 0:
        signal = findsignal()
        if len(signal) != 0:
            buy(signal[0], stocks.loc[signal[0]].close, signal[1])
    else:
        ticker, values = next(iter(state.portstocks.items()))
        price = stocks.loc[ticker].close
        if price > values[3] or price < values[4] or values[2] == 14:
            sell(ticker, price)
        else:
            state.portstocks[ticker][2] += 1
    if timestamp == timestamps[-1]:
        ticker, values = next(iter(state.portstocks.items()))
        sell(ticker, stocks.loc[ticker].close)