from src.backtest import state

def findsignal():
    df = state.minutedf
    signals = []
    changes = []
    for index, row in df.iterrows():
        prev5 = row["prev5"]
        minimum = min(prev5)
        price = row["price"]
        if price <= state.cash:
            change = price-minimum
            percchange = 100 * change / minimum
            if percchange > 5 and price > prev5[0]:
                signals.append(row["symbol"])
                changes.append(percchange)
    if len(signals) == 0:
        return []
    else:
        return [signals[changes.index(max(changes))], max(changes)]