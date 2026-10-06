from src.backtest import state


def findsignal():
    signals = []

    for index, row in state.minutedf.iterrows():
        ticker = row["symbol"]

        if ticker in state.portstocks:
            continue

        prev5 = row["prev5"]

        minimum = min(prev5)
        price = row["price"]

        if minimum <= 0:
            continue

        if price > state.cash:
            continue

        change = price - minimum
        percchange = 100 * change / minimum

        if (
            percchange > 5
            and price > prev5[0]
        ):
            signals.append([
                ticker,
                percchange
            ])

    if not signals:
        return []

    return max(
        signals,
        key=lambda signal: signal[1]
    )