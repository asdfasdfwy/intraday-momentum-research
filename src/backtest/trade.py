from src.backtest import state
import math

def buy(ticker, boughtat):
    number = math.floor((state.portval*0.5)/boughtat)
    cashneeded = number*boughtat
    if state.cash >= cashneeded:
        state.portstocks[ticker] = [number, boughtat, 0]
        state.cash -= number*boughtat

def sell(ticker, currentval):
    profpershare = currentval - state.portstocks[ticker][1]
    state.portval += profpershare*state.portstocks[ticker][0]
    state.cash += state.portstocks[ticker][0]*currentval
    del state.portstocks[ticker]

def trademinute(time, df):
    timestamps = df.index.get_level_values("timestamp").unique()
    timestamp = timestamps[time]
    stocks = df.loc[timestamp]
    print("AAPL" in stocks.index)